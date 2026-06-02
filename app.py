from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'sl137'

def init_db():
    with sqlite3.connect('AI-toolshub.db') as con:
        cur = con.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS USERS (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            with sqlite3.connect('AI-toolshub.db') as con:
                cur = con.cursor()
                cur.execute('''
                    INSERT INTO USERS
                    (username, email, password)
                    VALUES (?, ?, ?)
                ''', (username, email, password))
                con.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template(
                'register.html',
                error="Email already registered!"
            )
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('AI-toolshub.db') as con:
            cur = con.cursor()
            cur.execute('''
                SELECT * FROM USERS
                WHERE email=? AND password=?
            ''', (email, password))
            user = cur.fetchone()
        if user:
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return render_template(
                'login.html',
                error="Invalid email or password!"
            )
    return render_template('login.html')
@app.route("/forgotpassword", methods=["GET","POST"])
def forgotpassword():
    if request.method == "POST":
        email = request.form["email"]
        newpassword = request.form["newpassword"]
        confirmpassword = request.form["confirmpassword"]
        if newpassword == confirmpassword:
            with sqlite3.connect('AI-toolshub.db') as con:
                cur = con.cursor()
                cur.execute(
                "UPDATE USERS SET password=? WHERE email=?",
                (newpassword, email)
            )
            con.commit()
            con.close()
            return redirect(url_for("login"))
        else:
            return "Passwords do not match"
    return render_template("forgotpassword.html")
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/study')
def study():
    return render_template('study.html')
@app.route('/coding')
def coding():
    return render_template('coding.html')
@app.route('/design')
def design():
    return render_template('design.html')
@app.route('/career')
def career():
    return render_template('career.html')
@app.route('/document')
def document():
    return render_template('document.html')
@app.route('/tools')
def tools():
    category=request.args.get("category")
    tool=request.args.get("tools")
    return render_template("tools.html",category=category,tool=tool)
@app.route('/prompts')
def prompts():
    category=request.args.get("category")
    tool=request.args.get("tools")
    return render_template("prompts.html",category=category,tool=tool)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__== "__main__":
    init_db()
    app.run(debug=True)