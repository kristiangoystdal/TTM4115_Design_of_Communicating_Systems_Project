from collections.abc import Mapping
from datetime import datetime
from sqlite3 import Cursor

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, URLSafeSerializer
from paho.mqtt.client import Client
from pydantic import BaseModel

from mobile.constants import INDEX_HTML, SECRET_KEY, TIMEZONE
from mobile.db_connector import (
    book_scooter,
    check_user,
    connect_db,
    create_tables,
    end_booking,
    end_drive,
    generate_charging_stations,
    generate_scooters,
    get_charging_stations,
    get_scooters,
    get_user_active_bookings,
    get_user_drive_history,
    nuke_db,
    register_user,
    start_drive,
)
from mobile.helpers import clean_username, to_datetime
from scooter.constants import BROKER, PORT


client = Client()
client.connect(BROKER, PORT, 60)


class AuthRequest(BaseModel):
    username: str
    password: str


class DiscountRequest(BaseModel):
    apply_discount: bool


class Discount(BaseModel):
    on_charging_station: bool


app = FastAPI()
app.mount(
    "/assets",
    StaticFiles(directory="mobile/templates/dist_vue/assets"),
    name="assets",
)
app.mount(
    "/favicon.ico",
    StaticFiles(directory="mobile/templates/dist_vue"),
    name="favicon",
)


templates = Jinja2Templates(directory="mobile/templates/dist_vue")
serializer = URLSafeSerializer(SECRET_KEY)


def get_session(request: Request) -> dict[str, str]:
    if (session := request.cookies.get("session")) is None:
        return {}
    return serializer.loads(session)  # type: ignore


def fetch_user_id(cur: Cursor, session: Mapping[str, str]) -> int | None:
    if not session or "username" not in session:
        return None

    row = cur.execute(
        "SELECT id FROM users WHERE username = ?", (session["username"],)
    ).fetchone()

    return row[0] if row else None


@app.get("/")
def read_root(request: Request) -> Response:
    print("📥 Request to /")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
def login_form(request: Request) -> Response:
    if session := get_session(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        INDEX_HTML, {"request": request, "session": session}
    )


@app.post("/login")
def login(data: AuthRequest) -> Response:
    username = clean_username(data.username)

    if not check_user(username, data.password):
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)

    session = serializer.dumps({"username": username})
    response = JSONResponse({"message": "Login successful"})
    response.set_cookie("session", session)
    return response


@app.get("/register")
def register_form(request: Request) -> Response:
    if session := get_session(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        INDEX_HTML, {"request": request, "session": session}
    )


@app.post("/register")
def register(data: AuthRequest) -> Response:
    username = clean_username(data.username)

    if not register_user(username, data.password):
        return JSONResponse(
            {"error": "Username already exists"}, status_code=409
        )

    session = serializer.dumps({"username": username})
    response = JSONResponse({"message": "Registration successful"})
    response.set_cookie("session", session)
    return response


@app.post("/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")
    return response


def get_me(request: Request) -> dict[str, str]:
    if not (session_cookie := request.cookies.get("session")):
        raise HTTPException(status_code=401, detail="Not logged in")

    try:
        session_data = serializer.loads(session_cookie)
    except BadSignature as e:
        raise HTTPException(status_code=401, detail="Invalid session") from e

    return {"username": session_data["username"]}


@app.get("/scooters", response_model=list[dict[str, float | int | str]])
def scooters(request: Request) -> JSONResponse:
    session = get_session(request)
    user_id = None
    conn, cur = connect_db()

    if session:
        user_id = fetch_user_id(cur, session)

    all_scooters = get_scooters()
    rows = cur.execute(
        "SELECT scooter_id FROM bookings WHERE user_id = ? AND end_time IS NULL",
        (user_id,),
    ).fetchall()
    conn.close()

    user_booked_scooters = {row[0] for row in rows}
    filtered_scooters: list[dict[str, float | int | str]] = []

    for scooter in all_scooters:
        if scooter["id"] in user_booked_scooters:
            scooter["is_user_booked"] = True
            filtered_scooters.append(scooter)
        elif not scooter["is_booked"]:
            scooter["is_user_booked"] = False
            filtered_scooters.append(scooter)

    return JSONResponse(content=filtered_scooters)


@app.post("/book/{scooter_id}")
def book_scooter_route(request: Request, scooter_id: int) -> Response:
    if not (session := get_session(request)):
        return JSONResponse(
            {"error": "You must be logged in."}, status_code=401
        )

    conn, cur = connect_db()
    user_id = fetch_user_id(cur, session)
    conn.close()

    booking_time = datetime.now(TIMEZONE).strftime(r"%Y-%m-%d %H:%M:%S")

    if user_id:
        mqtt_topic = f"escooter/{scooter_id}"
        client.publish(mqtt_topic, "reserve")

    if book_scooter(user_id, scooter_id, booking_time):
        return JSONResponse({"success": True, "message": "Scooter booked"})
    return JSONResponse(
        {"error": "Scooter already booked or unavailable."}, status_code=400
    )


@app.get("/bookings")
def bookings_page(request: Request) -> Response:
    if not (session := get_session(request)):
        return templates.TemplateResponse(
            INDEX_HTML,
            {
                "request": request,
                "session": {},
                "error": "You must be logged in to view your bookings.",
            },
        )

    conn, cur = connect_db()

    if not (user_id := fetch_user_id(cur, session)):
        return JSONResponse(
            {"error": "Invalid session or user"}, status_code=401
        )

    conn.close()

    bookings = get_user_active_bookings(user_id)
    return templates.TemplateResponse(
        INDEX_HTML,
        {"request": request, "session": session, "bookings": bookings},
    )


@app.post("/end_booking/{booking_id}")
def end_booking_route(
    request: Request, booking_id: int, data: DiscountRequest
) -> Response:
    if not get_session(request):
        return JSONResponse(
            {"error": "You must be logged in to end a booking."},
            status_code=401,
        )

    end_time = datetime.now(TIMEZONE).isoformat()
    price = end_booking(booking_id, end_time, data.apply_discount)

    conn, cur = connect_db()
    booking = cur.execute(
        """
        SELECT b.scooter_id, b.booking_time, b.end_time, s.latitude, s.longitude
        FROM bookings AS b
        JOIN scooters AS s ON b.scooter_id = s.id
        WHERE b.scooter_id = ?
        """,
        (booking_id,),
    ).fetchone()
    conn.close()

    if not booking:
        return JSONResponse(
            content={"error": "Failed to end booking"}, status_code=400
        )

    booking_time = to_datetime(booking[1]).astimezone(TIMEZONE)
    end_time_date = to_datetime(booking[2]).astimezone(TIMEZONE)

    minutes = (end_time_date - booking_time).total_seconds() / 60

    booking_details = {
        "id": booking[0],
        "booking_time": booking_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time_date.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": round(minutes),
        "price": price,
    }

    mqtt_topic = f"escooter/{booking[0]}"
    client.publish(mqtt_topic, "cancel")

    return JSONResponse(content={"success": True, "booking": booking_details})


@app.get("/history")
def history_page(request: Request) -> Response:
    if not (session := get_session(request)):
        return JSONResponse(
            {"error": "You must be logged in to view your booking history."},
            status_code=401,
        )

    conn, cur = connect_db()
    user_id = fetch_user_id(cur, session)
    if not user_id:
        return JSONResponse(
            {"error": "Invalid session or user"}, status_code=401
        )

    conn.close()

    history = get_user_drive_history(user_id)
    return JSONResponse(content={"success": True, "history": history})


@app.get("/charging_stations", response_model=list[dict[str, float]])
def charging_stations() -> JSONResponse:
    stations_data = get_charging_stations()
    return JSONResponse(content=stations_data)


@app.post("/start_drive/{scooter_id}")
def start_drive_route(request: Request, scooter_id: int) -> Response:
    if not (session := get_session(request)):
        return JSONResponse(
            {"error": "You must be logged in to start a drive."},
            status_code=401,
        )

    conn, cur = connect_db()
    user_id = fetch_user_id(cur, session)
    if not user_id:
        return JSONResponse(
            {"error": "Invalid session or user"}, status_code=401
        )

    conn.close()
    booking_time = datetime.now(TIMEZONE).strftime(r"%Y-%m-%d %H:%M:%S")

    mqtt_topic = f"escooter/{scooter_id}"
    client.publish(mqtt_topic, "unlock")

    if start_drive(user_id, scooter_id, booking_time):
        return JSONResponse(
            {"success": True, "message": "Scooter started successfully"}
        )
    return JSONResponse(
        {"error": "Scooter already booked or unavailable."}, status_code=400
    )


@app.post("/end_drive/{scooter_id}")
def end_drive_route(
    request: Request, scooter_id: int, data: DiscountRequest
) -> Response:
    if not get_session(request):
        return JSONResponse(
            {"error": "You must be logged in to end a drive."},
            status_code=401,
        )
    print("Ending drive with applying discount:", data.apply_discount)

    price = end_drive(
        scooter_id, datetime.now(TIMEZONE).isoformat(), data.apply_discount
    )

    conn, cur = connect_db()
    drive = cur.execute(
        """
        SELECT d.scooter_id, d.driving_time, d.end_time
        FROM drives AS d
        JOIN scooters AS s ON d.scooter_id = s.id
        WHERE d.scooter_id = ?
        """,
        (scooter_id,),
    ).fetchone()

    conn.close()

    if not drive:
        return JSONResponse(
            content={"error": "Failed to end drive"}, status_code=400
        )

    # Correct parsing – handles both str and datetime
    driving_time_raw = drive[1]
    end_time_raw = drive[2]

    driving_time = (
        datetime.fromisoformat(driving_time_raw)
        if isinstance(driving_time_raw, str)
        else driving_time_raw
    )

    end_time_date = (
        datetime.fromisoformat(end_time_raw)
        if isinstance(end_time_raw, str)
        else end_time_raw
    )

    # Convert to correct timezone
    driving_time = driving_time.astimezone(TIMEZONE)
    end_time_date = end_time_date.astimezone(TIMEZONE)
    minutes = (end_time_date - driving_time).total_seconds() / 60

    drive_details = {
        "scooter_id": drive[0],
        "driving_time": driving_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time_date.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": round(minutes),
        "price": price,
    }

    mqtt_topic = f"escooter/{drive[0]}"
    client.publish(mqtt_topic, "lock")

    return JSONResponse(content={"success": True, "drive": drive_details})


def main() -> None:
    nuke_db()
    create_tables()
    generate_scooters(center_lat=63.422, center_lng=10.395)
    generate_charging_stations(center_lat=63.422, center_lng=10.395)

    uvicorn.run(
        "mobile_app:app",
        host="127.0.0.1",
        port=8_000,
        reload=True,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
    )


if __name__ == "__main__":
    main()
