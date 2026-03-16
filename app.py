from functools import wraps
import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import (
    create_user,
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    init_db,
    seed_default_admin,
    update_bio,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")

DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("dashboard"))
        return view_func(*args, **kwargs)

    return wrapped


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3 or len(password) < 6:
            flash("Username >= 3 chars and password >= 6 chars.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        if not create_user(username, password_hash):
            flash("Username already exists.", "error")
            return render_template("register.html")

        flash("Register success. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        flash("Login success.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        flash("Session invalid. Please login again.", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)


@app.route("/profile", methods=["POST"])
@login_required
def update_profile():
    bio = request.form.get("bio", "").strip()
    update_bio(session["user_id"], bio)
    flash("Profile updated.", "success")
    return redirect(url_for("dashboard"))


#@app.route("/admin/users")
@app.route("/admin/users/<id>")
@login_required
# @admin_required
# def admin_users():
#     users = get_all_users()
#     return render_template("admin_users.html", users=users)
def admin_user_by_id(id):
    user = get_user_by_id(id)
    return render_template("dashboard.html", user=user)


@app.route("/bootstrap-admin")
def bootstrap_admin():
    if get_user_by_username(DEFAULT_ADMIN_USERNAME):
        flash("Admin already exists.", "error")
        return redirect(url_for("home"))

    create_user(
        DEFAULT_ADMIN_USERNAME,
        generate_password_hash(DEFAULT_ADMIN_PASSWORD),
        role="admin",
    )
    flash("Admin created. Change default password right away.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    seed_default_admin(
        DEFAULT_ADMIN_USERNAME,
        generate_password_hash(DEFAULT_ADMIN_PASSWORD),
    )
    app.run(debug=True)
