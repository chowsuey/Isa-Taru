from flask import Flask, render_template, request, redirect, g, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import re
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/img/uploads' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


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
def index():
    if "user_id" in session:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM Productos WHERE UsuarioID =?", (session["user_id"],))
        productos = cur.fetchall()
        return render_template('home.html', productos=productos)
    else:
        return render_template('login1.html')

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
            return render_template("register.html")

        if not validarContraSimbolo(passw):
            return render_template("register.html")

        if passw != pass2:
            return render_template("register.html")

        hash = generate_password_hash(passw)
        try:
            cur = get_db().cursor()
            cur.execute("INSERT INTO Usuario (UserName, Password) VALUES (?, ?)", (user, hash))
            get_db().commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login1.html")

        cur = get_db().cursor()
        cur.execute("SELECT * FROM Usuario WHERE UserName =?", (username,))
        user = cur.fetchone()

        if user is None or not check_password_hash(user[2], password):
            return render_template("home.html")

        session["user_id"] = user[0] 
        session["username"] = user[1]

        return redirect("/agregar_telefono") 
    return render_template("home.html")


@app.route('/agregar_telefono', methods=['GET', 'POST'])
def agregar_telefono():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        imagen = request.files['imagen']

        cur = get_db().cursor()
        cur.execute("SELECT Precio FROM Productos WHERE Precio =?", (precio,))
        if cur.fetchone():
            # El precio ya existe, no se puede insertar
            return render_template('home.html', error="El precio ya existe")

        if imagen:
            filename = imagen.filename
            imagen.save(os.path.join('static/img/productos', filename))
            imagen_path = 'static/img/productos/' + filename

        cur.execute("INSERT INTO Productos (Nombre, Precio, Imagen) VALUES (?,?,?)",
                    (nombre, precio, imagen_path))
        get_db().commit()

        return render_template('home.html', imagen_path=imagen_path)
    else:
        return redirect('/')


@app.route('/')
def home():
    if "user_id" in session:
        cur = get_db().cursor()
        cur.execute("SELECT * FROM Productos WHERE UsuarioID =?", (session["user_id"],))
        productos = cur.fetchall()
        return render_template('home.html', productos=productos)
    else:
        return render_template('login1.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)