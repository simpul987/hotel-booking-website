from flask import Flask, render_template, request, redirect, url_for, session
from database import get_connection, initialize_database

app = Flask(__name__)

app.secret_key = "hotel_booking_secret_key"

# Initialize database
initialize_database()


# ---------------- HOME ----------------

@app.route("/")
def home():

    location = request.args.get("location", "").strip()

    connection = get_connection()

    if location:
        hotels = connection.execute("""
            SELECT *
            FROM hotels
            WHERE location LIKE ?
        """, (
            "%" + location + "%",
        )).fetchall()

    else:
        hotels = connection.execute("""
            SELECT *
            FROM hotels
        """).fetchall()

    connection.close()

    return render_template(
        "index.html",
        hotels=hotels,
        location=location
    )


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        connection = get_connection()

        try:

            connection.execute("""
                INSERT INTO users
                (name, email, password)
                VALUES (?, ?, ?)
            """, (
                name,
                email,
                password
            ))

            connection.commit()
            connection.close()

            return redirect(url_for("login"))

        except Exception:

            connection.close()

            return "Email already registered."

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_connection()

        user = connection.execute("""
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
        """, (
            email,
            password
        )).fetchone()

        connection.close()

        if user:

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        return "Invalid email or password."

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- HOTEL LIST ----------------

@app.route("/hotels")
def hotels():

    location = request.args.get("location", "").strip()

    connection = get_connection()

    if location:

        hotels = connection.execute("""
            SELECT *
            FROM hotels
            WHERE location LIKE ?
        """, (
            "%" + location + "%",
        )).fetchall()

    else:

        hotels = connection.execute("""
            SELECT *
            FROM hotels
        """).fetchall()

    connection.close()

    return render_template(
        "hotels.html",
        hotels=hotels,
        location=location
    )


# ---------------- HOTEL DETAILS ----------------

@app.route("/hotel/<int:hotel_id>")
def hotel_details(hotel_id):

    connection = get_connection()

    hotel = connection.execute("""
        SELECT *
        FROM hotels
        WHERE id = ?
    """, (
        hotel_id,
    )).fetchone()

    rooms = connection.execute("""
        SELECT *
        FROM rooms
        WHERE hotel_id = ?
        AND available = 1
    """, (
        hotel_id,
    )).fetchall()

    connection.close()

    if hotel is None:
        return "Hotel not found."

    return render_template(
        "hotel_details.html",
        hotel=hotel,
        rooms=rooms
    )


# ---------------- BOOKING ----------------

@app.route("/booking/<int:room_id>", methods=["GET", "POST"])
def booking(room_id):

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = get_connection()

    room = connection.execute("""
        SELECT rooms.*, hotels.name AS hotel_name
        FROM rooms
        JOIN hotels
        ON rooms.hotel_id = hotels.id
        WHERE rooms.id = ?
    """, (
        room_id,
    )).fetchone()

    connection.close()

    if room is None:
        return "Room not found."

    if request.method == "POST":

        check_in = request.form["check_in"]
        check_out = request.form["check_out"]
        guests = int(request.form["guests"])

        # Simple price calculation
        total_price = room["price"]

        connection = get_connection()

        cursor = connection.execute("""
            INSERT INTO bookings
            (
                user_id,
                hotel_id,
                room_id,
                check_in,
                check_out,
                guests,
                total_price
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            room["hotel_id"],
            room_id,
            check_in,
            check_out,
            guests,
            total_price
        ))

        booking_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return redirect(
            url_for(
                "confirmation",
                booking_id=booking_id
            )
        )

    return render_template(
        "booking.html",
        room=room
    )


# ---------------- CONFIRMATION ----------------

@app.route("/confirmation/<int:booking_id>")
def confirmation(booking_id):

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = get_connection()

    booking = connection.execute("""
        SELECT
            bookings.*,
            hotels.name AS hotel_name,
            rooms.room_type
        FROM bookings

        JOIN hotels
        ON bookings.hotel_id = hotels.id

        JOIN rooms
        ON bookings.room_id = rooms.id

        WHERE bookings.id = ?
        AND bookings.user_id = ?
    """, (
        booking_id,
        session["user_id"]
    )).fetchone()

    connection.close()

    if booking is None:
        return "Booking not found."

    return render_template(
        "confirmation.html",
        booking=booking
    )


# ---------------- MY BOOKINGS ----------------

@app.route("/my-bookings")
def my_bookings():

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = get_connection()

    bookings = connection.execute("""
        SELECT
            bookings.*,
            hotels.name AS hotel_name,
            hotels.location,
            rooms.room_type
        FROM bookings

        JOIN hotels
        ON bookings.hotel_id = hotels.id

        JOIN rooms
        ON bookings.room_id = rooms.id

        WHERE bookings.user_id = ?

        ORDER BY bookings.id DESC
    """, (
        session["user_id"],
    )).fetchall()

    connection.close()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )


if __name__ == "__main__":
    app.run(debug=True)