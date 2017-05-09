from flask import Flask, url_for, session, redirect, escape, request

app = Flask(__name__)
app.secret_key = 'bBL\xad\x99\x14m\xd3\x0f\xb4@?B?nh$\x9d\xf6\x07&?_h\xd3'


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