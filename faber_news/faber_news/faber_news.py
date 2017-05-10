from flask import Flask, url_for, session, redirect, escape, request, g, abort, render_template, flash
import os
import sqlite3
import bcrypt
import sys

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'faber_news.db'),
	SECRET_KEY='bBL\xad\x99\x14m\xd3\x0f\xb4@?B?nh$\x9d\xf6\x07&?_h\xd3'
))
app.config.from_envvar('FABER_NEWS_SETTINGS', silent=True)

def init_db():
	try:
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()
	except:
		print('Error initializating DB...')
		db.rollback()

@app.cli.command('initdb')
def initdb_command():
	init_db()
	print("SQLite3 Database Initialized!")

def connect_db():
	try:
		rv = sqlite3.connect(app.config['DATABASE'])
		rv.row_factory = sqlite3.Row
		return rv
	except:
		print('Error connecting to DB...')
		return None

def get_db():
	try:
		if not hasattr(g, 'sqlite.db'):
			g.sqlite_db = connect_db()
		return g.sqlite_db
	except:
		print('Error getting DB...')
		return None

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite.db'):
		g.sqlite_db.close()
		session.pop('logged_in', None)


########### VIEWS ###########

@app.route('/')
def show_articles():
	try:
		db = get_db()
		cur = db.execute('SELECT * FROM articles ORDER BY upvotes DESC')
		articles = cur.fetchall()
	except:
		print ("Unexpected error:", sys.exc_info()[0])
		return 'Error connecting with DB!'
	return render_template('show_articles.html', articles=articles)


@app.route('/add', methods=['GET', 'POST'])
def add_article():
	if request.method == 'POST':
		try:
			db = get_db()
			db.execute('INSERT into articles (title, body, upvotes, downvotes) VALUES (?, ?, ?, ?)',
				[request.form['title'], request.form['body'], 0, 0])
			db.commit()
			flash('New article published with sucess!')
			return redirect(url_for('show_articles'))
		except:
			db.rollback()
			return 'Error connecting with DB!'
	else:
		return render_template('submit_article.html', error=None)


########### REGISTER / LOGIN / LOGOUT ###########

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		email = request.form['email']
		username = request.form['username']
		db = get_db()
		cur = db.execute('SELECT * FROM users WHERE email = ?', [email])
		print("len cur.fetchall = " + str(len(cur.fetchall())))
		if len(cur.fetchall()) == 0:
			cur = db.execute('SELECT * FROM users WHERE username = ?', [username])
			if len(cur.fetchall()) == 0:
				# Proceeds registration
				password = request.form['password']
				encrypted_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
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
			return render_template('register.html', error="Email already in use. Please try again.")
	else:
		return render_template('register.html', error=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password'].encode('utf-8')
		db = get_db()
		cur = db.execute('SELECT * FROM users WHERE username = ?', [username])
		rv = cur.fetchall()
		if len(rv) == 0:
			return render_template('login.html', error='Username not found. Please sign up first!')
		else:
			if rv[0][3] == bcrypt.hashpw(password, rv[0][3].encode('utf-8')):
				session['logged_in'] = True
				flash('Logged in with success!')
				return redirect(url_for('show_articles'))
			else:
				return render_template('login.html', error='Wrong credentials')
	else:
		return render_template('login.html', error=None)


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_articles'))


@app.route('/upvote/<article_id>')
def upvote(article_id):
	if session.get('logged_in'):
		try:
			db = get_db()
			cur = db.execute('UPDATE articles SET upvotes = upvotes + 1 WHERE id = ?', [article_id])
			db.commit()
			flash('Article upvoted!')
			return redirect(url_for('show_articles'))
		except:
			return render_template('show_articles.html', error="Error connecting with DB!")
	else:
		flash('You must be logged in to vote.')
		return redirect(url_for('show_articles'))


@app.route('/downvote/<article_id>')
def downvote(article_id):
	if session.get('logged_in'):
		try:
			db = get_db()
			cur = db.execute('UPDATE articles SET downvotes = downvotes + 1 WHERE id = ?', [article_id])
			flash('Article downvoted!')
			return redirect(url_for('show_articles'))
		except:
			return render_template('show_articles.html', error="Error connecting with DB!")
	else:
		flash('You must be logged in to vote.')
		return redirect(url_for('show_articles'))


@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
	if request.method == 'POST':
		db = get_db()
		username = request.form['username']
		email = request.form['email']
		cur = db.execute('SELECT password FROM users WHERE username = ? AND email = ?', [username, email])
		if len(cur.fetchall()) != 0:
			flash('Success! A password reset link was sent to your email because we hashed and salted your previous password :)')
			return render_template('login.html')
		else:
			return render_template('forgot_password.html', error="No account found with those credentials. Try again.")
	else:
		return render_template('forgot_password.html', error=None)


@app.route('/article/<article_id>', methods=['GET'])
def view_article(article_id):
	if request.method == 'GET':
		db = get_db()
		cur = db.execute('SELECT title, body, upvotes, downvotes FROM articles WHERE id = ?', [article_id])
		data = cur.fetchall()
		#print(cur.fetchall()[0]['title'])
		if len(data) != 0:
			print ("data = " + data[0]['title'])
			return render_template('view_article.html', title=data[0]['title'], body=data[0]['body'], id=article_id, upvotes=data[0]['upvotes'], downvotes=data[0]['downvotes'])
		else:
			flash('No such article exists.')
			return redirect(url_for('show_articles'))
	else:
		return "ok"
