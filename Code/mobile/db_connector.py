import os
import secrets
import sqlite3
from datetime import datetime
from sqlite3 import Connection, Cursor, IntegrityError
from typing import Any

from mobile.constants import DATABASE_FILE, SCHEMA_FILE, TIMEZONE, DISCOUNT_RATE
from mobile.helpers import get_price, hash_password


def nuke_db() -> None:
    os.remove(DATABASE_FILE)
    conn, _ = connect_db()
    conn.close()


def connect_db() -> tuple[Connection, Cursor]:
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.execute("PRAGMA analysis_limit = 1000")
    return conn, cur


def create_tables() -> None:
    conn, cur = connect_db()

    with open(SCHEMA_FILE, encoding="utf-8") as file:
        cur.executescript(file.read())

    conn.commit()
    conn.close()


def check_user(username: str, password: str) -> bool:
    conn, cur = connect_db()
    row = cur.execute(
        "SELECT password_hash, salt FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if row is None:
        return False

    stored_hash, salt = row
    password_hash = hash_password(password, salt)
    return stored_hash == password_hash


def register_user(username: str, password: str) -> bool:
    # if not validate_password(username, password):
    #     return False

    conn, cur = connect_db()
    salt = secrets.token_urlsafe(8)
    password_hash = hash_password(password, salt)

    try:
        cur.execute(
            """
            INSERT INTO users (username, password_hash, salt)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, salt),
        )
    except IntegrityError:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def generate_scooters(center_lat: float, center_lng: float) -> None:
    conn, cur = connect_db()
    lat_delta = 1e-4
    ltd_delta = 4 * lat_delta

    for _ in range(2):
        lat = center_lat + (secrets.randbelow(200) - 100) * lat_delta
        lng = center_lng + (secrets.randbelow(200) - 100) * ltd_delta
        battery_level = secrets.randbelow(101)
        cur.execute(
            """
            INSERT INTO scooters (latitude, longitude, battery_level)
            VALUES (?, ?, ?)
            """,
            (lat, lng, battery_level),
        )

    conn.commit()
    conn.close()


def get_scooters() -> list[dict[str, Any]]:
    conn, cur = connect_db()
    rows = cur.execute(
        """
        SELECT id, latitude, longitude, battery_level, is_booked, is_driving
        FROM scooters
        WHERE battery_level > 20
        """
    ).fetchall()
    scooters = [
        {
            "id": row[0],
            "latitude": row[1],
            "longitude": row[2],
            "battery_level": row[3],
            "is_booked": bool(row[4]),
            "is_driving": bool(row[5]),
        }
        for row in rows
    ]
    conn.close()
    return scooters


def book_scooter(user_id: int, scooter_id: int, booking_time: str) -> bool:
    conn, cur = connect_db()
    existing_booking = cur.execute(
        """
        SELECT id FROM bookings
        WHERE scooter_id = ? AND end_time IS NULL
        """,
        (scooter_id,),
    ).fetchone()

    if existing_booking:
        conn.close()
        return False

    try:
        cur.execute(
            """
            INSERT INTO bookings (user_id, scooter_id, booking_time)
            VALUES (?, ?, ?)
            """,
            (user_id, scooter_id, booking_time),
        )
    except IntegrityError:
        conn.close()
        return False

    try:
        cur.execute(
            """
            UPDATE scooters
            SET is_booked = 1
            WHERE id = ?
            """,
            (scooter_id,),
        )
    except IntegrityError:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def end_booking(booking_id: int, end_time: str, apply_discount: bool) -> float:
    conn, cur = connect_db()

    # Oppdater booking
    cur.execute(
        """
        UPDATE bookings
        SET end_time = ?, is_active = 0
        WHERE scooter_id = ? AND end_time IS NULL
        """,
        (end_time, booking_id),
    )
    conn.commit()

    # Hent bookingen igjen
    row = cur.execute(
        """
        SELECT scooter_id, booking_time, end_time
        FROM bookings
        WHERE scooter_id = ?
        """,
        (booking_id,),
    ).fetchone()

    if row is None:
        conn.close()
        return 0.0

    scooter_id, booking_time, actual_end_time = row

    # Ny: sjekk at `actual_end_time` og `booking_time` faktisk finnes
    if not actual_end_time or not booking_time:
        conn.close()
        return 0.0

    # Oppdater scooter-status
    cur.execute(
        """
        UPDATE scooters
        SET is_booked = 0
        WHERE id = ?
        """,
        (scooter_id,),
    )
    conn.commit()

    # Trygg parsing
    booking_time_dt = (
        datetime.fromisoformat(booking_time)
        if isinstance(booking_time, str)
        else booking_time
    ).astimezone(TIMEZONE)

    end_time_dt = (
        datetime.fromisoformat(actual_end_time)
        if isinstance(actual_end_time, str)
        else actual_end_time
    ).astimezone(TIMEZONE)

    discount = 0
    if apply_discount:
        discount = DISCOUNT_RATE

    minutes = (end_time_dt - booking_time_dt).total_seconds() / 60
    price = get_price(minutes, discount)

    cur.execute(
        """
        UPDATE bookings
        SET price = ?
        WHERE id = ?
        """,
        (price, booking_id),
    )
    conn.commit()
    conn.close()
    return price


def get_user_bookings(user_id: int) -> dict[str, float | int | str]:
    conn, cur = connect_db()
    row = cur.execute(
        """
        SELECT b.id, s.latitude, s.longitude, s.battery_level, b.booking_time, b.end_time, b.price
        FROM bookings AS b JOIN scooters AS s ON b.scooter_id = s.id
        WHERE b.user_id = ?
        """,
        (user_id,),
    ).fetchone()
    conn.close()

    if row is None:
        return {}

    booking_time: str = row[4]
    end_time: str = row[5]
    booking: dict[str, float | int | str] = {
        "id": row[0],
        "latitude": row[1],
        "longitude": row[2],
        "battery_level": row[3],
        "booking_time": booking_time,
        "end_time": end_time,
        "price": row[6],
    }

    return booking


def get_user_active_bookings(
    user_id: int,
) -> list[dict[str, float | int | str]]:
    conn, cur = connect_db()
    rows = cur.execute(
        """
        SELECT b.id, s.latitude, s.longitude, s.battery_level, b.booking_time
        FROM bookings AS b
        JOIN scooters AS s ON b.scooter_id = s.id
        WHERE b.user_id = ? AND b.is_active = 1
        """,
        (user_id,),
    ).fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "latitude": row[1],
            "longitude": row[2],
            "battery_level": row[3],
            "booking_time": row[4],
        }
        for row in rows
    ]


def get_user_drive_history(
    user_id: int,
) -> list[dict[str, float | int | str]]:
    conn, cur = connect_db()
    rows = cur.execute(
        """
<<<<<<< HEAD
        SELECT d.scooter_id, s.latitude, s.longitude, s.battery_level, d.driving_time, d.end_time
=======
        SELECT d.id, s.latitude, s.longitude, s.battery_level, d.driving_time, d.end_time, d.price
>>>>>>> discount2
        FROM drives AS d
        JOIN scooters AS s ON d.scooter_id = s.id
        WHERE d.user_id = ? AND d.is_active = 0
        """,
        (user_id,),
    ).fetchall()
    conn.close()

    history: list[dict[str, float | int | str]] = []

    for row in rows:
        booking_time = datetime.fromisoformat(row[4]).astimezone(TIMEZONE)
        end_time = datetime.fromisoformat(row[5]).astimezone(TIMEZONE)
        history.append(
            {
                "id": row[0],
                "latitude": row[1],
                "longitude": row[2],
                "battery_level": row[3],
                "booking_time": booking_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "price": row[6],
            }
        )

    return history


def generate_charging_stations(center_lat: float, center_lng: float) -> None:
    conn, cur = connect_db()
    lat_delta = 1e-4
    lng_delta = 4 * lat_delta

    for _ in range(10):
        lat = center_lat + (secrets.randbelow(200) - 100) * lat_delta
        lng = center_lng + (secrets.randbelow(200) - 100) * lng_delta
        cur.execute(
            """
            INSERT INTO charging_stations (latitude, longitude)
            VALUES (?, ?)
            """,
            (lat, lng),
        )

    conn.commit()
    conn.close()


def get_charging_stations() -> list[dict[str, float]]:
    conn, cur = connect_db()
    rows = cur.execute(
        """
        SELECT id, latitude, longitude
        FROM charging_stations
        """
    ).fetchall()
    stations = [
        {"id": row[0], "latitude": row[1], "longitude": row[2]} for row in rows
    ]
    conn.close()
    return stations


def start_drive(user_id: int, scooter_id: int, start_time: str) -> bool:
    conn, cur = connect_db()
    # End any existing booking before starting a drive
    existing_booking = cur.execute(
        """
        SELECT scooter_id FROM drives
        WHERE scooter_id = ? AND end_time IS NULL
        """,
        (scooter_id,),
    ).fetchone()

    if existing_booking:
        conn.close()
        return False

    try:
        cur.execute(
            """
            INSERT INTO drives (user_id, scooter_id, driving_time)
            VALUES (?, ?, ?)
            """,
            (user_id, scooter_id, start_time),
        )
    except IntegrityError:
        conn.close()
        return False

    try:
        cur.execute(
            """
            UPDATE scooters
            SET is_driving = 1, is_booked = 0
            WHERE id = ?
            """,
            (scooter_id,),
        )
    except IntegrityError:
        conn.close()
        return False

    conn.commit()
    conn.close()
    return True


def end_drive(scooter_id: int, end_time: str, apply_discount: bool) -> float:
    conn, cur = connect_db()

    # Update the drive record
    cur.execute(
        """
        UPDATE drives
        SET end_time = ?, is_active = 0
        WHERE scooter_id = ? AND end_time IS NULL
        """,
        (end_time, scooter_id),
    )
    conn.commit()

    # Fetch the updated drive details
    row = cur.execute(
        """
        SELECT scooter_id, driving_time, end_time
        FROM drives
        WHERE scooter_id = ?
        """,
        (scooter_id,),
    ).fetchone()

    if row is None:
        conn.close()
        return 0.0

    # Extract data and validate
    scooter_id_from_drive, driving_time, end_time = row
    if not driving_time or not end_time:
        conn.close()
        return 0.0

    # Update the scooter status
    cur.execute(
        """
        UPDATE scooters
        SET is_driving = 0, is_booked = 0
        WHERE id = ?
        """,
        (scooter_id_from_drive,),
    )
    conn.commit()

    discount = 0
    if apply_discount:
        discount = DISCOUNT_RATE

    # Calculate duration and price
    driving_time = datetime.fromisoformat(driving_time).astimezone(TIMEZONE)
    end_time_date = datetime.fromisoformat(end_time).astimezone(TIMEZONE)
    minutes = (end_time_date - driving_time).total_seconds() / 60
<<<<<<< HEAD

    return get_price(minutes)
=======
    price = get_price(minutes, discount)

    cur.execute(
        """
        UPDATE drives
        SET price = ?
        WHERE scooter_id = ?
        """,
        (price, scooter_id_from_drive),
    )
    conn.commit()
    conn.close()
    return price
>>>>>>> discount2
