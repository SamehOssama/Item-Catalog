from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Producer, Movie

from datetime import datetime

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
engine = create_engine('sqlite:///movies.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Producer Menu Application"


def toDateStr(DB_output):
	""" Stop the database from updating the DB query 
	And change release date (date obj) to a readable date format. """
	strformat = '%d %b %Y'
	if isinstance(DB_output, list):# check to see if input is one column
		for i in DB_output:
			session.expunge(i)
			i.released = datetime.strftime(i.released, strformat)
	elif isinstance(DB_output, object):# check to see if input is multiple columns
		session.expunge(DB_output) 
		DB_output.released = datetime.strftime(DB_output.released, strformat)


# Create anti-forgery state token
@app.route('/login/')
def showLogin():
	# Create anti-forgery state token
	state = ''.join(random.choice(
			string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	print(state)
	return render_template('login.html', STATE = state)

#GOOGLE Sign-IN

@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	print("GCONNECT")
	if request.args.get('state') != login_session.get('state'):
		print("COMPARE STATES")
		print(request.args.get('state'))
		print(login_session.get('state'))
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	token = request.data

	try:
		# Specify the CLIENT_ID of the app that accesses the backend:
		print("checking ID Info")
		print("Token = " + token)
		print("Request = ")
		print(google_requests.Request())
		print("ID = " + CLIENT_ID)
		idinfo = id_token.verify_oauth2_token(
			token, google_requests.Request(), CLIENT_ID)
		print("ID info = ")
		print(idinfo)
		if idinfo['iss'] not in ['accounts.google.com',
								 'https://accounts.google.com']:
			print("Could not verify audience.")
			response = make_response(json.dumps(
				"Could not verify audience."), 401)

		# ID token is valid.
		# Get the user's Google Account ID from the decoded token.
		print("ID token is valid")
		username = idinfo['name']
		useremail = idinfo['email']
		userpicture = idinfo['picture']
		print("Verification: \nUsername = " + username + "\nuseremail = " + useremail + "\nuserpicture = " + userpicture)

	except ValueError:
		# Invalid token
		response = make_response(json.dumps("Invalid token."), 401)
		print("Invalid token.")

	login_session['access_token'] = token

	login_session['username'] = username
	login_session['picture'] = userpicture
	login_session['email'] = useremail
	# ADD PROVIDER TO LOGIN SESSION
	login_session['provider'] = 'google'

	output = ''
	output += '<h1>Welcome,'
	output += login_session['username']
	output += '!</h1>'
	print("done!")
	return output

@app.route('/disconnect')
def disconnect():
	if request.args.get('state') != login_session.get('state'):
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	print("DISCONNECT")
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			print('logging out of google')
			response = make_response(json.dumps('Successfully disconnected from Google.'), 200)
			response.headers['Content-Type'] = 'application/json'
			del login_session['provider']
			del login_session['username']
			del login_session['email']
			del login_session['picture']
			del login_session['access_token']
			del login_session['state']
			print("DELETED EVRYTHING")
	else :
		print("Not Logged In")
		redirect(url_for('showProducers'))
	return redirect(url_for('showProducers'))


@app.route('/')
@app.route('/producer/')
def showProducers():
	print(login_session)
	producers = session.query(Producer).all()
	return render_template('producers.html', producers = producers, STATE = login_session.get('state'))
	#return "This page will show all the producers"

@app.route('/producer/new/', methods=['GET', 'POST'])
def newProducer():
	if request.method == 'POST':
		#print(request.form['name'])
		newProducer = Producer(name = request.form['name'])
		session.add(newProducer)
		session.commit()
		return redirect(url_for('showProducers'))
		#return "Adding new producer"
	else:
		return render_template('newproducer.html', STATE = login_session.get('state'))
		#return "This page will be for adding a new producer"

@app.route('/producer/<int:producer_id>/edit/', methods=['GET', 'POST'])
def editProducer(producer_id):
	producerToEdit = session.query(Producer).filter_by(id=producer_id).one()
	if request.method == 'POST':
		if request.form['name']:
			#print(request.form['name'])
			producerToEdit.name = request.form['name']
		session.add(producerToEdit)
		session.commit()
		return redirect(url_for('showProducers'))
		#return "Editing producer {}".format(producer_id)
	else:
		return render_template('editproducer.html', producer = producerToEdit, STATE = login_session.get('state'))
		#return "This page will be for editing producer {}".format(producer_id)

@app.route('/producer/<int:producer_id>/delete/', methods=['GET', 'POST'])
def deleteProducer(producer_id):
	producerToDelete = session.query(Producer).filter_by(id = producer_id).one()
	if request.method == 'POST':
		#print(request.form['name'])
		session.delete(producerToDelete)
		session.commit()
		return redirect(url_for('showProducers'))
		#return "Deleting producer {}".format(producer_id)
	else:
		return render_template('deleteproducer.html', producer = producerToDelete, STATE=login_session.get('state'))
		#return "This page will be for deleting producer {}".format(producer_id)


@app.route('/producer/<int:producer_id>/')
@app.route('/producer/<int:producer_id>/movie/')
def showMovies(producer_id):
	producer = session.query(Producer).filter_by(id = producer_id).one()
	movies = session.query(Movie).filter_by(producer_id = producer_id).order_by('released').all()
	toDateStr(movies)
	return render_template('movies.html', producer = producer, movies = movies, STATE=login_session.get('state'))
	#return "This page is the movie list for producer {}".format(producer_id)

@app.route('/producer/<int:producer_id>/movie/new/', methods=['GET', 'POST'])
def newMovie(producer_id):
	producer = session.query(Producer).filter_by(id = producer_id).one()
	if request.method == 'POST':
		newMovie = Movie(
			name = request.form['name'], 
			plot = request.form['plot'], 
			runtime = request.form['runtime'], 
			released = request.form['released'], 
			poster = request.form['poster'], 
			producer_id = producer_id)
		session.add(newMovie)
		session.commit()
		# print('name = ' + request.form['name'])
		# print('plot = ' + request.form['plot'])
		# print('runtime = ' + str(request.form['runtime']))
		# print('released = ' + request.form['released'])
		# print('poster = ' + request.form['poster_url'])
		# print('producer_id = ' + str(producer_id))
		return redirect(url_for('showMovies', producer_id = producer_id))
		#return "Adding new movie for producer {}".format(producer_id)
	else:
		return render_template('newmovie.html', producer = producer, STATE=login_session.get('state'))
		#return "This page is for adding a new movie for producer {}".format(producer_id)

@app.route('/producer/<int:producer_id>/movie/<int:movie_id>/edit/', methods=['GET', 'POST'])
def editMovie(producer_id, movie_id):
	producer = session.query(Producer).filter_by(id = producer_id).one()
	movieToEdit = session.query(Movie).filter_by(id = movie_id).one()
	if request.method == 'POST':
		post = request.form
		if post['name'] and post['plot'] and post['runtime'] and post['released'] and post['poster_url']:
			movieToEdit.name = post['name']
			movieToEdit.plot = post['plot']
			movieToEdit.runtime = post['runtime']
			movieToEdit.released = post['released']
			movieToEdit.poster = post['poster']
		session.add(movieToEdit)
		session.commit()
		# print('name = ' + post['name'])
		# print('plot = ' + post['plot'])
		# print('runtime = ' + str(post['runtime']))
		# print('released = ' + post['released'])
		# print('poster = ' + post['poster_url'])
		# print('producer_id = ' + str(producer_id))
		return redirect(url_for('showMovies', producer_id = producer_id))
		#return "Editing movie {0} for produce {1}".format(movie_id, producer_id)
	else:
		return render_template('editmovie.html', producer = producer, movie = movieToEdit, STATE = login_session.get('state'))
		#return "This page is for editing movie {}".format(movie_id)

@app.route('/producer/<int:producer_id>/movie/<int:movie_id>/delete/', methods=['GET', 'POST'])
def deleteMovie(producer_id, movie_id):
	producer = session.query(Producer).filter_by(id = producer_id).one()
	movieToDelete = session.query(Movie).filter_by(id = movie_id).one()
	if request.method == 'POST':
		session.delete(movieToDelete)
		session.commit()
		#print(request.form['name'])
		return redirect(url_for('showMovies', producer_id = producer_id))
		#return "Deleting movie {0} for producer {1}".format(movie_id, producer_id)
	else:
		return render_template('deletemovie.html', producer = producer, movie = movieToDelete, STATE = login_session.get('state'))
		#return "This page is for deleting movie {}".format(movie_id)


@app.route('/api/producers/')
def showProducersJSON():
	producers = session.query(Producer).all()
	return jsonify(Producers=[i.serialize for i in producers])

@app.route('/api/producers/<int:producer_id>/movies/')
def showMoviesJSON(producer_id):
	movies = session.query(Movie).filter_by(producer_id = producer_id).all()
	toDateStr(movies)
	return jsonify(Movies=[i.serialize for i in movies])

@app.route('/api/producers/<int:producer_id>/movies/<int:movie_id>/')
def showMovieJSON(producer_id, movie_id):
	movie = session.query(Movie).filter_by(id = movie_id).one()
	toDateStr(movie)
	return jsonify(Movie=movie.serialize)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.run(host = '0.0.0.0', port = 5000, debug = True)