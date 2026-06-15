from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from datetime import timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = 'sl137'
app.permanent_session_lifetime=timedelta(days=30)

def init_db():
    with sqlite3.connect('AI-toolshub.db') as con:
        cur = con.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS USERS (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS FAVOURITES(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            item_type TEXT,
            item_url TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS RECENT_TOOLS(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    tool_name TEXT,
                    tool_url TEXT,
                    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            session.permanent=True
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
@app.route('/visit_tool')
def visit_tool():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tool_name=request.args.get('name')
    tool_url=request.args.get('url')
    user_id=session['user_id']
    with sqlite3.connect('AI-toolshub.db')as con:
        cur=con.cursor()
        cur.execute(""" INSERT INTO RECENT_TOOLS(user_id,tool_name,tool_url)VALUES(?,?,?)""",(user_id,tool_name,tool_url))
        con.commit()
    return redirect(tool_url)
@app.route('/recent_tools')
def recent_tools():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id=session['user_id']
    with sqlite3.connect('AI-toolshub.db')as con:
        cur=con.cursor()
        cur.execute("""SELECT tool_name,tool_url FROM RECENT_TOOLS WHERE user_id=? ORDER BY visited_at DESC LIMIT 20""",(user_id,))
        recent=cur.fetchall()
    return render_template('recent_tools.html',recent=recent)
@app.route('/tools')
def tools():
    category=request.args.get("category")
    tool=request.args.get("tools")
    favourites=[]
    if 'user_id' in session:
        with sqlite3.connect('AI-toolshub.db')as con:
            cur=con.cursor()
            cur.execute('''SELECT item_name FROM FAVOURITES WHERE user_id=?''',(session['user_id'],))
            favourites=[row[0] for row in cur.fetchall()]
    return render_template("tools.html",category=category,tool=tool,favourites=favourites)
@app.route('/prompts')
def prompts():
    category=request.args.get("category")
    tool=request.args.get("tools")
    return render_template("prompts.html",category=category,tool=tool)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
@app.route('/favourites',methods=['POST'])
def favourite():
    print("FAVOURITE ROUTE CALLED")
    if 'user_id' not in session:
        return {'status':'error'}
    item_name=request.form['item_name']
    item_type=request.form['item_type']
    item_url=request.form.get('item_url')
    with sqlite3.connect('AI-toolshub.db') as con:
        cur=con.cursor()
        cur.execute('''SELECT * FROM FAVOURITES WHERE user_id=? AND item_name=?''',(session['user_id'],item_name))
        existing=cur.fetchone()
        if existing:
            cur.execute('''DELETE FROM FAVOURITES WHERE user_id=? AND item_name=?''',(session['user_id'],item_name))
            con.commit()
            return jsonify({'status':'removed'})
        else:
            cur.execute('''INSERT INTO FAVOURITES(user_id,item_name,item_type,item_url)VALUES(?,?,?,?)''',(session['user_id'],item_name,item_type,item_url))
            con.commit()
            return jsonify({'status':'added'})
@app.route('/myfavourites')
def myfavourites():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect('AI-toolshub.db') as con:
        cur = con.cursor()
        cur.execute(
            '''
            SELECT item_name,item_type,item_url FROM FAVOURITES WHERE user_id=?''', (session['user_id'],)
        )

        favourites = cur.fetchall()
        return render_template('favourites.html',favourites=favourites
    )

if __name__== "__main__":
    init_db()
    app.run(debug=True)