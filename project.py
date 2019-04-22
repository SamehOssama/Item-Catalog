from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Producer, Movie

from datetime import datetime

app = Flask(__name__)
engine = create_engine('sqlite:///movies.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/producer/')
def showProducers():
	producers = session.query(Producer).all()
	return render_template('producers.html', producers = producers)
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
		return render_template('newproducer.html')
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
		return render_template('editproducer.html', producer = producerToEdit)
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
		return render_template('deleteproducer.html', producer = producerToDelete)
		#return "This page will be for deleting producer {}".format(producer_id)


@app.route('/producer/<int:producer_id>/')
@app.route('/producer/<int:producer_id>/movie/')
def showMovies(producer_id):
	producer = session.query(Producer).filter_by(id = producer_id).one()
	movies = session.query(Movie).filter_by(producer_id = producer_id).order_by('released').all()
	return render_template('movies.html', producer = producer, movies = movies)
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
			poster = request.form['poster_url'], 
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
		return render_template('newmovie.html', producer = producer)
		#return "This page is for adding a new movie for producer {}".format(producer_id)

@app.route('/producer/<int:producer_id>/movie/<int:movie_id>/edit/', methods=['GET', 'POST'])
def editMovie(producer_id, movie_id):
	producer = session.query(Producer).filter_by(id = producer_id).one()
	movieToEdit = session.query(Movie).filter_by(id = menu_id).one()
	if request.method == 'POST':
		post = request.form
		if post['name'] and post['plot'] and post['runtime'] and post['released'] and post['poster_url']:
			movieToEdit.name = post['name']
			movieToEdit.plot = post['plot']
			movieToEdit.runtime = post['runtime']
			movieToEdit.released = post['released']
			movieToEdit.poster = post['poster_url']
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
		return render_template('editmovie.html', producer = producer, movie = movieToEdit)
		#return "This page is for editing movie {}".format(movie_id)

@app.route('/producer/<int:producer_id>/movie/<int:movie_id>/delete/', methods=['GET', 'POST'])
def deleteMovie(producer_id, movie_id):
	producer = session.query(Producer).filter_by(id = producer_id).one()
	movieToDelete = session.query(Movie).filter_by(id = menu_id).one()
	if request.method == 'POST':
		session.delete(movieToDelete)
		session.commit()
		#print(request.form['name'])
		return redirect(url_for('showMovies', producer_id = producer_id))
		#return "Deleting movie {0} for producer {1}".format(movie_id, producer_id)
	else:
		return render_template('deletemovie.html', producer = producer, movie = movieToDelete)
		#return "This page is for deleting movie {}".format(movie_id)


@app.route('/api/producers/')
def showProducersJSON():
	producers = session.query(Producer).all()
	return jsonify(Producers=[i.serialize for i in producers])

@app.route('/api/producers/<int:producer_id>/movies/')
def showMoviesJSON(producer_id):
	movies = session.query(Movie).filter_by(producer_id = producer_id).all()
	for i in movies:
		# stop the database from updating the movies query
		session.expunge(i) 
		# change release date (date obj) to a readable date format
		i.released = datetime.strftime(i.released, ".format(d .format(b .format(Y")
	return jsonify(Movies=[i.serialize for i in movies])

@app.route('/api/producers/<int:producer_id>/movies/<int:movie_id>/')
def showMovieJSON(producer_id, movie_id):
	movie = session.query(Movie).filter_by(id = movie_id).one()
	# stop the database from updating the movies query
	session.expunge(movie)
	# change release date (date obj) to a readable date format
	movie.released = datetime.strftime(movie.released, ".format(d .format(b .format(Y")
	return jsonify(Movie=movie.serialize)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.run(host = '0.0.0.0', port = 5000, debug = True)