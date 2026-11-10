
import re
import bcrypt
import streamlit as st

from config import get_db_connection


def create_users_table():
    """Create the users table if it does not exist."""

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()
        cursor.close()

    finally:
        connection.close()


def register_user(full_name, email, password):
    """Validate details and register a new user."""

    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name:
        return False, "Please enter your full name."

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    # Convert the password into a secure hash.
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (full_name, email, password_hash)
        )

        connection.commit()

        return True, "Account created successfully. You can now log in."

    except Exception as error:
        connection.rollback()

        # MySQL error 1062 means a duplicate unique value.
        if getattr(error, "errno", None) == 1062:
            return False, "An account with this email already exists."

        raise

    finally:
        connection.close()


def authenticate_user(email, password):
    """Check a user's email and password."""

    email = email.strip().lower()

    connection = get_db_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, full_name, email, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()
        cursor.close()

        if user is None:
            return None

        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if not password_matches:
            return None

        # Do not keep the password hash in the session.
        return {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"]
        }

    finally:
        connection.close()


def show_authentication_page():
    """Display registration and login forms."""

    st.title("🩺 Welcome to HealthMate AI")
    st.write("Register for an account or log in to continue.")

    login_tab, register_tab = st.tabs(
        ["Log In", "Create Account"]
    )

    with login_tab:
        with st.form("login_form"):
            email = st.text_input(
                "Email address",
                key="login_email"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            submitted = st.form_submit_button(
                "Log In",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if not email.strip() or not password:
                    st.warning("Enter your email and password.")

                else:
                    try:
                        user = authenticate_user(email, password)

                        if user:
                            st.session_state["user"] = user
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

                    except Exception:
                        st.error(
                            "Unable to connect to the database. "
                            "Check your MySQL settings."
                        )

    with register_tab:
        with st.form("register_form"):
            full_name = st.text_input("Full name")

            email = st.text_input(
                "Email address",
                key="register_email"
            )

            password = st.text_input(
                "Create password (at least 8 characters)",
                type="password",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Create Account",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if password != confirm_password:
                    st.error("Your passwords do not match.")

                else:
                    try:
                        success, message = register_user(
                            full_name,
                            email,
                            password
                        )

                        if success:
                            st.success(message)
                        else:
                            st.warning(message)

                    except Exception:
                        st.error(
                            "Registration failed. "
                            "Check your database connection and settings."
                        )


def require_login():
    """Stop a page from displaying to a logged-out visitor."""

    if not st.session_state.get("user"):
        st.warning("Please log in to access this page.")
        st.stop()
