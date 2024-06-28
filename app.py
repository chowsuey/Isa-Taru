from flask import Flask, render_template, request, redirect, g, flash
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
def index():
    return render_template('login1.html')

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
            return render_template("register.html")

        if not user.isalpha():
            flash("El nombre de usuario no puede contener números")
            return render_template("register.html")

        if not validarContraSimbolo(passw):
            flash("La contraseña solo puede contener letras, números y los símbolos @#$%^&+=")
            return render_template("register.html")

        if passw != pass2:
            flash("Las contraseñas no coinciden")
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

        flash("Inicio de sesión exitoso")
        return redirect("/login")
    
    
    return render_template("login1.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)



# File "C:\Users\Jose Tercero\Documents\Isataru\Isa-Taru\app.py", line 57, in register
# cur.execute("INSERT INTO Usuario (UserName, Password) VALUES (?, ?)", (user, hash))
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# sqlite3.OperationalError: unable to open database file