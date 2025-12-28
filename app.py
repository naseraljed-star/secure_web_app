# Import Flask and tools I need for pages, forms, redirects and sessions
from flask import Flask, render_template, request, redirect, session
# Import SQLite so I can use a small local database file
import sqlite3
# Import the functions I use to hash and verify passwords
from werkzeug.security import generate_password_hash, check_password_hash
# Import escape function to prevent XSS attacks
from markupsafe import escape


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄ INITIAL SETUP ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄
# Create the Flask app object
app = Flask(__name__)
# Secret key for sessions (needed to keep session data secure)
app.secret_key = "secret123"


# Function to create the database tables if they are not there
def init_db():
    # Open connection to the SQLite database file
    conn = sqlite3.connect("app.db")
    # Create a cursor so I can run SQL queries
    cursor = conn.cursor()

    # Create the users table for storing registered users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT
        )
    """)

    # Create the logins table for tracking login attempts with IP and timestamp
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ip TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Save the changes to the database
    conn.commit()
    # Close the connection
    conn.close()


# Call the function once when the app starts
init_db()


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄ HOME ROUTE ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄
# Simple home page just to show the app is running
@app.route("/")
def home():
    # Return a basic text message on the home page
    return "Simple security demo app"


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄ REGISTER ROUTE ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄
# Route for user registration (GET to show form, POST to submit)
@app.route("/register", methods=["GET", "POST"])
def register():
    # If the user submitted the form
    if request.method == "POST":
        # Read username from the form
        username = request.form["username"]
        # Read email from the form
        email = request.form["email"]
        # Read password from the form
        password = request.form["password"]
        # Read confirm password from the form
        confirm = request.form["confirm"]

        # Check if the two passwords match
        if password != confirm:
            # If they don't match, show a simple message
            return "Passwords do not match."

        # Hash the password before saving it in the database 🔐🔐🔐
        hashed = generate_password_hash(password)

        # Open connection to the database
        conn = sqlite3.connect("app.db")
        # Create cursor for SQL operations
        cursor = conn.cursor()

        try:
            # Insert the new user record into the users table using placeholders
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)", # 🎯🎯🎯
                (username, email, hashed)
            )
            # Save the insert in the database
            conn.commit()
        except:
            # On any error (for example duplicate username) close and return a message
            conn.close()
            return "Username already exists."

        # Close the connection after successful registration
        conn.close()
        # Show a small confirmation with the username - NOW WITH XSS PROTECTION
        return f"Registered user: {escape(username)}" # 🥩🥩🥩🥩  I added protection that turns dangerous code into safe text. Scripts become words that can't run.

    # If the request is GET, just show the register page
    return render_template("register.html")


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄ LOGIN ROUTE ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄
# Route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # If the user submitted the login form
    if request.method == "POST":
        # Read username from the form
        username = request.form["username"]
        # Read password from the form
        password = request.form["password"]

        # Open connection to the database
        conn = sqlite3.connect("app.db")
        # Create a cursor to run SQL
        cursor = conn.cursor()

        # Get the stored hashed password for this username
        cursor.execute(
            "SELECT password FROM users WHERE username = ?",
            (username,)
        )
        # Fetch one row (None if user not found)
        row = cursor.fetchone()

        # If user exists and the password is correct
        if row and check_password_hash(row[0], password): # 🔐🔐 🔐🔐
            # Save the username in the session (user is now logged in)
            session["username"] = username
            # Log this login attempt with username and IP address
            cursor.execute(
                "INSERT INTO logins (username, ip) VALUES (?, ?)", # 🎯🎯🎯🎯
                (username, request.remote_addr)
            )
            # Commit the login record
            conn.commit()
            # Close the connection
            conn.close()
            # Send user to the dashboard
            return redirect("/dashboard")

        # If credentials are wrong or user not found, close DB and show error
        conn.close()
        return "Login failed: invalid username or password."

    # If it is a GET request, just show the login page
    return render_template("login.html")


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄ DASHBOARD ROUTE ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄
# Route for the user dashboard (protected page)
@app.route("/dashboard")
def dashboard():
    # If there is no username in the session, user is not logged in
    if "username" not in session: # 🔐🔐🔐🔐🔐
        # Simple message telling the user to log in first
        return "You are not logged in. Go to /login" # 🧩🧩🧩🧩

    # If logged in, show the dashboard template and pass the username - NOW WITH XSS PROTECTION
    return render_template("dashboard.html", username=escape(session["username"])) # 🥩🥩🥩


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄ LOGOUT ROUTE ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"
# Route to log the user out
@app.route("/logout")
def logout():
    # Clear all session data
    session.clear()
    # Confirm to the user that they logged out
    return "You have been logged out."


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄ INPUT TEST ROUTE ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"
# Route I use for a simple input test and basic XSS check
@app.route("/input_test", methods=["GET", "POST"])
def input_test():
    # Default message is None
    message = None
    # Default cleaned text is None
    cleaned = None

    # If the form was submitted
    if request.method == "POST":
        # Get the user input from the form, default to empty string
        text = request.form.get("user_input", "")
        # Very basic check for a script tag (simple XSS demo)
        if "<script>" in text.lower() or "</script>" in text.lower(): # 🥩🥩🥩🥩
            # If I see a script tag, I show this warning
            message = "XSS attempt blocked!"
        else:
            # Otherwise I treat it as safe text for this demo
            cleaned = text

    # Render the input_test page and pass the message and cleaned text
    return render_template("input_test.html", message=message, cleaned=cleaned)


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄ XSS DEMO ROUTE ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"
# Route I use just to demonstrate XSS behaviour in a controlled way
@app.route("/xss_demo", methods=["GET", "POST"])
def xss_demo():
    # Raw comment from the user (what they typed)
    raw_comment = ""
    # Safe comment (in a real app this would be escaped in the template)
    safe_comment = ""

    # If the form was submitted
    if request.method == "POST":
        # Read the comment text from the form
        user_input = request.form.get("comment", "")
        # Keep the raw version for display
        raw_comment = user_input
        # For this demo I keep the same value as "safe" version
        safe_comment = user_input

    # Render the XSS demo template with both raw and safe versions
    return render_template("xss_demo.html",
                           raw_comment=raw_comment,
                           safe_comment=safe_comment)


# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
# Run the Flask app if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)