from flask import Flask, url_for, session, redirect, escape, request, g, abort, render_template, flash
import os
import sqlite3
import bcrypt

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'faber_news.db'),
	SECRET_KEY='bBL\xad\x99\x14m\xd3\x0f\xb4@?B?nh$\x9d\xf6\x07&?_h\xd3'
))
app.config.from_envvar('FABER_NEWS_SETTINGS', silent=True)

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	init_db()
	print("SQLite3 Database Initialized!")

def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	if not hasattr(g, 'sqlite.db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite.db'):
		g.sqlite_db.close()

########### VIEWS ###########

@app.route('/')
def show_articles():
	try:
		db = get_db()
		cur = db.execute('SELECT title, text FROM articles ORDER BY upvotes DESC')
		articles = cur.fetchall()
	except:
		return 'Error connecting with DB!'
	return render_template('show_articles.html', articles=articles)


@app.route('/add', methods=['POST'])
def add_article():
	if not session.get('logged_in'):
		abort(401)
	try:
		db = get_db()
		db.execute('INSERT into articles (title, text, upvotes, downvotes) VALUES (?, ?, ?, ?)',
			[request.form['title'], request.form['title'], 0, 0])
		db.commit()
	except:
		db.rollback()
		return 'Error connecting with DB!'
	flash('New article published with sucess!')
	return redirect(url_for('show_articles'))


########### REGISTER / LOGIN / LOGOUT ###########

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		email = request.form['email']
		username = request.form['username']
		try:
			db = get_db()
			cur = db.execute('SELECT * FROM users WHERE email = ?', [email, one=True])
			if cur is None:
				cur = db.execute('SELECT * FROM users WHERE username = ?',, [username, one=True])
				if cur is None:
					# Proceeds registration
					password = request.form['password']
					encrypted_pw = bcrypt.hashpw(password, bcrypt.gensalt(10))
					try:
						cur = db.execute('INSERT INTO users(username, email, password) VALUES (?, ?, ?)', [username, email, encrypted_pw])
						db.commit()
						flash('Signed up with sucess!')
						return redirect(url_for('show_articles'))
					except:
						db.rollback()
						return render_template('register.html', error='Error connecting with DB!')
				else:
					return render_template('register.html', error="Username already in use.")
			else:
				return render_template('register.html', error="Email already in use.")
		except:
			return render_template('register.html', error='Error connecting with DB!')
	else:
		return render_template('register.html', error="Error! Should be GET not POST...")


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		try:
			db = get_db()
			cur = db.execute('SELECT password FROM users WHERE username = ?', [username, one=True])
			if cur is None:
				return render_template('login.html', error='Username not found. Please sign up first!')
			else:
				data = cur.fetchall()
				print(data)
				return render_template('login.html', error='testing password')
		except:
			return render_template('login.html', error='Error connecting with DB!')
	else:
		return render_template('login.html', error="Error! Should be GET not POST...")


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_articles'))