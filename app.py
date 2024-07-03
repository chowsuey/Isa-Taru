from flask import Flask, render_template, request, redirect, g, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
from flask_session import Session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("ProyectoCS50.db")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
@login_required
def index():
    return render_template('home.html')

#-------------------------------------------------------------------------------------
def validarContraSimbolo(password):
    return bool(re.match(r'^[a-zA-Z0-9@#$%^&+=]+$', password))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        user = request.form.get("user")
        passw = request.form.get("pass")
        pass2 = request.form.get("pass2")

        if not user or not passw or not pass2:
            flash("Por favor, complete todos los campos")
            print("Erorr1")
            return render_template("register.html")

        #Validacion mala
        # if not user.isalpha():
        #     flash("El nombre de usuario no puede contener números")
        #     print("Error 2")
        #     return render_template("register.html")

        if not validarContraSimbolo(passw):
            flash("La contraseña solo puede contener letras, números y los símbolos @#$%^&+=")
            print("Error3")
            return render_template("register.html")

        if passw != pass2:
            flash("Las contraseñas no coinciden")
            print("Error4")
            return render_template("register.html")

        hash = generate_password_hash(passw)
        try:
            cur = get_db().cursor()
            cur.execute("INSERT INTO Usuario (UserName, Password) VALUES (?, ?)", (user, hash))
            get_db().commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("El nombre de usuario ya está registrado")
            return render_template("register.html")

    return render_template("register.html")

#-------------------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Por favor, complete todos los campos")
            return render_template("login1.html")

        cur = get_db().cursor()
        cur.execute("SELECT * FROM Usuario WHERE UserName = ?", (username,))
        user = cur.fetchone()

        if user is None or not check_password_hash(user[2], password):
            flash("Nombre de usuario o contraseña incorrectos")
            return render_template("login1.html")

        session["user"] = user
        return redirect("/")
    
    
    return render_template("login1.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

# File "C:\Users\Jose Tercero\Documents\Isataru\Isa-Taru\app.py", line 57, in register
# cur.execute("INSERT INTO Usuario (UserName, Password) VALUES (?, ?)", (user, hash))
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# sqlite3.OperationalError: unable to open database file