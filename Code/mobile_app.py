from datetime import datetime

import uvicorn
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer
from mobile.constants import (
    BOOKINGS_HTML,
    HISTORY_HTML,
    INDEX_HTML,
    LOGIN_HTML,
    RECEIPT_HTML,
    REGISTER_HTML,
    SECRET_KEY,
    TIMEZONE,
)
from mobile.db_connector import (
    book_scooter,
    check_user,
    connect_db,
    create_tables,
    end_booking,
    generate_charging_stations,
    generate_scooters,
    get_charging_stations,
    get_scooters,
    get_user_active_bookings,
    get_user_booking_history,
    register_user,
    end_booking,
    start_drive,
    end_drive,
    nuke_db,
)
from mobile.helpers import clean_username


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
    return serializer.loads(session)


@app.get("/")
def read_root(request: Request) -> Response:
    session = get_session(request)
    return templates.TemplateResponse(
        INDEX_HTML, {"request": request, "session": session}
    )


@app.get("/login")
def login_form(request: Request) -> Response:
    if session := get_session(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        LOGIN_HTML, {"request": request, "session": session}
    )


@app.post("/login")
def login(
    request: Request, username: str = Form(...), password: str = Form(...)
) -> Response:
    username = clean_username(username)

    if not check_user(username, password):
        return templates.TemplateResponse(
            LOGIN_HTML,
            {
                "request": request,
                "session": {},
                "error": "Invalid credentials",
            },
        )

    response = RedirectResponse(url="/", status_code=302)
    session = serializer.dumps({"username": username})
    response.set_cookie("session", session)
    return response


@app.get("/register")
def register_form(request: Request) -> Response:
    if session := get_session(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        REGISTER_HTML, {"request": request, "session": session}
    )


@app.post("/register")
def register(
    request: Request, username: str = Form(...), password: str = Form(...)
) -> Response:
    username = clean_username(username)

    if not register_user(username, password):
        return templates.TemplateResponse(
            REGISTER_HTML,
            {
                "request": request,
                "session": {},
                "error": "Username already exists",
            },
        )

    response = RedirectResponse(url="/", status_code=302)
    session = serializer.dumps({"username": username})
    response.set_cookie("session", session)
    return response


@app.get("/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")
    return response


@app.get("/scooters", response_model=list[dict[str, float | int | str]])
def scooters(request: Request) -> JSONResponse:
    session = get_session(request)
    user_id = None
    conn, cur = connect_db()

    if session:
        user_id = cur.execute(
            "SELECT id FROM users WHERE username = ?", (session["username"],)
        ).fetchone()[0]

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
        return templates.TemplateResponse(
            INDEX_HTML,
            {
                "request": request,
                "session": {},
                "error": "You must be logged in to book a scooter.",
            },
        )

    conn, cur = connect_db()
    user_id = cur.execute(
        "SELECT id FROM users WHERE username = ?", (session["username"],)
    ).fetchone()[0]
    conn.close()
    booking_time = datetime.now(TIMEZONE).strftime(r"%Y-%m-%d %H:%M:%S")

    if book_scooter(user_id, scooter_id, booking_time):
        return templates.TemplateResponse(
            INDEX_HTML,
            {
                "request": request,
                "session": session,
                "message": f"Scooter {scooter_id} booked successfully!",
            },
        )
    return templates.TemplateResponse(
        INDEX_HTML,
        {
            "request": request,
            "session": session,
            "error": "Scooter is already booked or unavailable.",
        },
    )


@app.get("/bookings")
def bookings_page(request: Request) -> Response:
    if not (session := get_session(request)):
        return templates.TemplateResponse(
            LOGIN_HTML,
            {
                "request": request,
                "session": {},
                "error": "You must be logged in to view your bookings.",
            },
        )

    conn, cur = connect_db()
    user_id = cur.execute(
        "SELECT id FROM users WHERE username = ?", (session["username"],)
    ).fetchone()[0]
    conn.close()

    bookings = get_user_active_bookings(user_id)
    return templates.TemplateResponse(
        BOOKINGS_HTML,
        {"request": request, "session": session, "bookings": bookings},
    )


@app.post("/end_booking/{booking_id}")
def end_booking_route(request: Request, booking_id: int) -> Response:
    if not (session := get_session(request)):
        return templates.TemplateResponse(
            LOGIN_HTML,
            {
                "request": request,
                "session": {},
                "error": "You must be logged in to end a booking.",
            },
        )

    end_time = datetime.now(TIMEZONE).isoformat()
    price = end_booking(booking_id, end_time)

    conn, cur = connect_db()
    booking = cur.execute(
        """
        SELECT b.id, b.booking_time, b.end_time, s.latitude, s.longitude
        FROM bookings AS b
        JOIN scooters AS s ON b.scooter_id = s.id
        WHERE b.id = ?
        """,
        (booking_id,),
    ).fetchone()
    conn.close()

    if not booking:
        return JSONResponse(
            content={"error": "Failed to end booking"}, status_code=400
        )

    booking_time = datetime.fromisoformat(booking[1]).astimezone(TIMEZONE)
    end_time_date = datetime.fromisoformat(booking[2]).astimezone(TIMEZONE)
    minutes = (end_time_date - booking_time).total_seconds() / 60

    booking_details = {
        "id": booking[0],
        "booking_time": booking_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time_date.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": round(minutes),
        "price": round(price, 2),
    }

    return templates.TemplateResponse(
        RECEIPT_HTML,
        {
            "request": request,
            "session": session,
            "booking": booking_details,
        },
    )


@app.get("/history")
def history_page(request: Request) -> Response:
    if not (session := get_session(request)):
        return templates.TemplateResponse(
            LOGIN_HTML,
            {
                "request": request,
                "session": {},
                "error": "You must be logged in to view your booking history.",
            },
        )

    conn, cur = connect_db()
    user_id = cur.execute(
        "SELECT id FROM users WHERE username = ?", (session["username"],)
    ).fetchone()[0]
    conn.close()

    history = get_user_booking_history(user_id)
    return templates.TemplateResponse(
        HISTORY_HTML,
        {"request": request, "session": session, "history": history},
    )


@app.get("/charging_stations", response_model=list[dict[str, float]])
def charging_stations() -> JSONResponse:
    stations_data = get_charging_stations()
    return JSONResponse(content=stations_data)


@app.post("/start_drive/{scooter_id}")
def start_drive_route(request: Request, scooter_id: int) -> Response:
    if not (session := get_session(request)):
        return templates.TemplateResponse(
            LOGIN_HTML,
            {
                "request": request,
                "session": {},
                "error": "You must be logged in to start a drive.",
            },
        )

    conn, cur = connect_db()
    user_id = cur.execute(
        "SELECT id FROM users WHERE username = ?", (session["username"],)
    ).fetchone()[0]
    conn.close()
    booking_time = datetime.now(TIMEZONE).strftime(r"%Y-%m-%d %H:%M:%S")

    if start_drive(user_id, scooter_id, booking_time):
        return templates.TemplateResponse(
            INDEX_HTML,
            {
                "request": request,
                "session": session,
                "message": f"Scooter {scooter_id} started successfully!",
            },
        )
    return templates.TemplateResponse(
        INDEX_HTML,
        {
            "request": request,
            "session": session,
            "error": "Scooter is already started or unavailable.",
        },
    )


@app.post("/end_drive/{scooter_id}")
def end_drive_route(request: Request, scooter_id: int) -> Response:
    if not (session := get_session(request)):
        return templates.TemplateResponse(
            LOGIN_HTML,
            {
                "request": request,
                "session": {},
                "error": "You must be logged in to end a drive.",
            },
        )

    end_time = datetime.now(TIMEZONE).isoformat()
    price = end_drive(scooter_id, end_time)

    conn, cur = connect_db()
    drive = cur.execute(
        """
        SELECT d.id, d.driving_time, d.end_time, s.latitude, s.longitude
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

    driving_time = datetime.fromisoformat(drive[1]).astimezone(TIMEZONE)
    end_time_date = datetime.fromisoformat(drive[2]).astimezone(TIMEZONE)
    minutes = (end_time_date - driving_time).total_seconds() / 60

    drive_details = {
        "id": drive[0],
        "driving_time": driving_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time_date.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": round(minutes),
        "price": round(price, 2),
    }

    return templates.TemplateResponse(
        RECEIPT_HTML,
        {
            "request": request,
            "session": session,
            "booking": drive_details,
        },
    )


def main() -> None:
    nuke_db()
    create_tables()
    generate_scooters(center_lat=63.422, center_lng=10.395)
    generate_charging_stations(center_lat=63.422, center_lng=10.395)
    uvicorn.run("mobile_app:app", host="127.0.0.1", port=8_000, reload=True)


if __name__ == "__main__":
    main()
