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
		i.released = datetime.strftime(i.released, "%d %b %Y")
	return jsonify(Movies=[i.serialize for i in movies])

@app.route('/api/producers/<int:producer_id>/movies/<int:movie_id>/')
def showMovieJSON(producer_id, movie_id):
	movie = session.query(Movie).filter_by(id = movie_id).one()
	# stop the database from updating the movies query
	session.expunge(movie)
	# change release date (date obj) to a readable date format
	movie.released = datetime.strftime(movie.released, "%d %b %Y")
	return jsonify(Movie=movie.serialize)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.run(host = '0.0.0.0', port = 5000, debug = True)