from flask import Flask, url_for, session, redirect, escape, request, g, abort, render_template, flash
import os
import sqlite3

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'faber_news.db'),
	SECRET_KEY='bBL\xad\x99\x14m\xd3\x0f\xb4@?B?nh$\x9d\xf6\x07&?_h\xd3',
	USERNAME='simoes',
	PASSWORD='simoes'
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


@app.route('/')
def index():
	return "Faber news!"

@app.route('/post/<int:post_id>')
def show_post(post_id):
	return "Post %d" % post_id

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))