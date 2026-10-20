import sqlite3

DATABASE = "hotel_booking.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Hotels table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            rating REAL,
            image TEXT
        )
    """)

    # Rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER NOT NULL,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            available INTEGER DEFAULT 1,
            FOREIGN KEY (hotel_id) REFERENCES hotels(id)
        )
    """)

    # Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            hotel_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            guests INTEGER NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (hotel_id) REFERENCES hotels(id),
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    """)

    connection.commit()

    # Add hotels only if database is empty
    cursor.execute("SELECT COUNT(*) FROM hotels")
    hotel_count = cursor.fetchone()[0]

    if hotel_count == 0:

        hotels = [
            (
                "Ocean View Hotel",
                "Puri",
                "A comfortable hotel near the beach.",
                4.5,
                "https://images.unsplash.com/photo-1566073771259-6a8506099945"
            ),
            (
                "Bhubaneswar Grand",
                "Bhubaneswar",
                "Modern hotel in the heart of Bhubaneswar.",
                4.3,
                "https://images.unsplash.com/photo-1564501049412-61c2a3083791"
            ),
            (
                "Konark Heritage Hotel",
                "Konark",
                "Heritage-style hotel near Konark.",
                4.2,
                "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb"
            ),
            (
                "Cuttack Palace",
                "Cuttack",
                "Comfortable rooms with modern facilities.",
                4.0,
                "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa"
            ),
            (
                "Sea Breeze Resort",
                "Puri",
                "Beachside resort suitable for family stays.",
                4.6,
                "https://images.unsplash.com/photo-1571896349842-33c89424de2d"
            )
        ]

        cursor.executemany("""
            INSERT INTO hotels
            (name, location, description, rating, image)
            VALUES (?, ?, ?, ?, ?)
        """, hotels)

        connection.commit()

        # Get hotel IDs
        cursor.execute("SELECT id FROM hotels")
        hotel_ids = [row["id"] for row in cursor.fetchall()]

        # Rooms for each hotel
        room_types = [
            ("Standard Room", 1500),
            ("Deluxe Room", 2500),
            ("Suite", 4000)
        ]

        for hotel_id in hotel_ids:

            for room_type, price in room_types:

                cursor.execute("""
                    INSERT INTO rooms
                    (hotel_id, room_type, price, available)
                    VALUES (?, ?, ?, ?)
                """, (
                    hotel_id,
                    room_type,
                    price,
                    1
                ))

        connection.commit()

    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")