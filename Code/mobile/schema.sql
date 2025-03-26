CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scooters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    battery_level INTEGER NOT NULL,
    is_booked INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS charging_stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    scooter_id INTEGER NOT NULL,
    booking_time TEXT NOT NULL,
    end_time TEXT,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
            ON DELETE NO ACTION
            ON UPDATE CASCADE,
    FOREIGN KEY (scooter_id)
        REFERENCES scooters (id)
            ON DELETE NO ACTION
            ON UPDATE CASCADE
);
