#!/usr/bin/python3

from flask import (
            Flask, render_template, request, redirect, url_for,
            flash, jsonify, session as login_session, make_response
            )
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Producer, Movie

from datetime import datetime
import random
import string

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import httplib2
import json
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database
engine = create_engine('sqlite:///movies.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# #############################-Helper Functions-##############################


def toDateStr(DB_output):
    """ Stop the database from updating the DB query
    And change release date (date obj) to a readable date format. """
    strformat = '%d %b %Y'
    if isinstance(DB_output, list):
        # check to see if input is one column
        for i in DB_output:
            session.expunge(i)
            i.released = datetime.strftime(i.released, strformat)
    elif isinstance(DB_output, object):
        # check to see if input is multiple columns
        session.expunge(DB_output)
        DB_output.released = datetime.strftime(DB_output.released, strformat)

# ##############################-User Functions-###############################


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    user = session.query(User).filter_by(email=email).first()
    if user:
        return user.id
    else:
        return None

# ###########################-Login Related Routes-############################


@app.route('/login/')
def showLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# GOOGLE Sign-IN
@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token
    if request.args.get('state') != login_session.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    token = request.data

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            print("Could not verify audience.")
            response = make_response(json.dumps(
                "Could not verify audience."), 401)

        # ID token is valid.
        # Get the user's Google Account ID from the decoded token.
        username = idinfo['name']
        useremail = idinfo['email']
        userpicture = idinfo['picture']

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

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(useremail)
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("You Are Now Logged In As {}.".format(login_session['username']))
    return "Login Successful"

# Log out part
@app.route('/disconnect')
def disconnect():
    # Validate state token
    if request.args.get('state') != login_session.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if 'provider' in login_session:
        if login_session['provider'] == 'google':

            response = make_response(
                json.dumps('Successfully disconnected from Google.'), 200)
            response.headers['Content-Type'] = 'application/json'

            del login_session['provider']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['access_token']
            del login_session['state']

            flash("You Have Successfully Been Signed Out From Google")
    else:
        flash("You Were Not Logged In To Begin With!")
        redirect(url_for('showProducers'))

    return redirect(url_for('showProducers'))

# ############################-Producer Web Pages-#############################


@app.route('/')
@app.route('/producer/')
def showProducers():
    # get producers data
    producers = session.query(Producer).order_by('name').all()

    if 'username' not in login_session:
        # render a template without create/update/delete
        return render_template('public_producers.html', producers=producers)
    else:
        # render a template with full functionalities
        return render_template('producers.html', producers=producers,
                               STATE=login_session.get('state'))


@app.route('/producer/new/', methods=['GET', 'POST'])
def newProducer():
    # check if user is logged in
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    if request.method == 'POST':
        # make sure user inserted a name
        if request.form['name']:
            # add new movie
            newProducer = Producer(name=request.form['name'],
                                   user_id=login_session['user_id'])
            session.add(newProducer)
            session.commit()

            flash('New Producer {} Successfully Created'.format(
                newProducer.name))
            return redirect(url_for('showProducers'))
        else:
            flash("Add a producer name")
            return redirect(url_for('newProducer',
                            STATE=login_session.get('state')))
    else:
        return render_template('newproducer.html',
                               STATE=login_session.get('state'))


@app.route('/producer/<int:producer_id>/edit/', methods=['GET', 'POST'])
def editProducer(producer_id):
    # check if user is logged in
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    # get producer data
    producerToEdit = session.query(Producer).filter_by(id=producer_id).one()

    # check if user is the owner of this producer
    if producerToEdit.user_id != login_session['user_id']:
        return ("<script>function myFunction() {"
                + "alert('You are not authorized to edit this producer."
                + "Please add your own producer in order to delete.');"
                + "window.location.href = '/producer';}"
                + "</script><body onload='myFunction()'>")

    if request.method == 'POST':
        if request.form['name']:
            # edit producer data
            producerToEdit.name = request.form['name']
        session.add(producerToEdit)
        session.commit()

        flash('Producer Successfully Edited')
        return redirect(url_for('showProducers'))
    else:
        return render_template('editproducer.html', producer=producerToEdit,
                               STATE=login_session.get('state'))


@app.route('/producer/<int:producer_id>/delete/', methods=['GET', 'POST'])
def deleteProducer(producer_id):
    # check if user is logged in
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    # get producer data
    producerToDelete = session.query(Producer).filter_by(id=producer_id).one()

    # check if signed in user is the owner of this producer
    if producerToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction() {"
                + "alert('You are not authorized to delete this producer. "
                + "Please add your own producer in order to delete.');"
                + "window.location.href = '/producer';}"
                + "</script><body onload='myFunction()'>")

    if request.method == 'POST':
        # print(request.form['name'])
        session.delete(producerToDelete)

        # get movies from producer
        producerMovies = session.query(Movie).filter_by(
            producer_id=producer_id).all()
        # delete all prducer movies
        for i in producerMovies:
            session.delete(i)
        session.commit()

        flash('Producer Successfully Deleted')
        return redirect(url_for('showProducers'))
    else:
        return render_template('deleteproducer.html',
                               producer=producerToDelete,
                               STATE=login_session.get('state'))

# #############################-Movie Web Pages-###############################

# display the movies for the producer
@app.route('/producer/<int:producer_id>/')
@app.route('/producer/<int:producer_id>/movie/')
def showMovies(producer_id):
    # get producer data
    producer = session.query(Producer).filter_by(id=producer_id).one()

    # get the creator data
    creator = getUserInfo(producer.user_id)

    # get movies from producer
    movies = session.query(Movie).filter_by(producer_id=producer_id).order_by(
        'released').all()

    # get the number of movies from producer
    count = session.query(Movie).filter_by(producer_id=producer_id).count()

    # change the date object to a string
    toDateStr(movies)

    if ('username' not in login_session or
       creator.id != login_session['user_id']):
        # render a template without create/update/delete
        return render_template('public_movies.html', producer=producer,
                               movies=movies, count=count, creator=creator)
    else:
        # render a template with full functionalities
        return render_template('movies.html', producer=producer,
                               movies=movies, count=count,
                               STATE=login_session.get('state'))


@app.route('/producer/<int:producer_id>/movie/new/', methods=['GET', 'POST'])
def newMovie(producer_id):
    # check if user is logged in
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    # get producer data
    producer = session.query(Producer).filter_by(id=producer_id).one()

    if request.method == 'POST':
        # make sure no input is empty
        if (request.form['name'] and request.form['plot'] and
           request.form['runtime'] and request.form['released']
           and request.form['poster']):
            # check if runtime is empty or an int value
            if not request.form['runtime'].isdigit():
                flash("Runtime should be a number")
                return redirect(
                    url_for('newMovie', producer_id=producer_id,
                            producer=producer,
                            STATE=login_session.get('state')))
            # Add new movie
            newMovie = Movie(
                name=request.form['name'],
                plot=request.form['plot'],
                runtime=request.form['runtime'],
                released=datetime.strptime(
                    request.form['released'], '%Y-%m-%d'),
                poster=request.form['poster'],
                producer_id=producer_id,
                user_id=login_session['user_id'])
            session.add(newMovie)
            session.commit()
            flash('New Movie {0} Successfully Created for Producer {1}'
                  .format(newMovie.name, producer.name))
            return redirect(url_for('showMovies', producer_id=producer_id))
        else:
            flash('Please fill all the inputs')
            return redirect(
                url_for('newMovie', producer_id=producer_id,
                        producer=producer, STATE=login_session.get('state')))
    else:
        return render_template('newmovie.html',
                               producer_id=producer_id, producer=producer,
                               STATE=login_session.get('state'))


@app.route('/producer/<int:producer_id>/movie/<int:movie_id>/edit/',
           methods=['GET', 'POST'])
def editMovie(producer_id, movie_id):
    # make sure the user is logged in
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    # get producer data
    producer = session.query(Producer).filter_by(id=producer_id).one()

    # get movie data
    movieToEdit = session.query(Movie).filter_by(id=movie_id).one()

    # check if signed in user is the owner of this producer
    if movieToEdit.user_id != login_session['user_id']:
        return ("<script>function myFunction() {"
                + "alert('You are not authorized to edit movies from this "
                + "producer. Please add your own producer in order to edit "
                + "movies.');window.location.href = '/producer';}"
                + "</script><body onload='myFunction()'>")

    if request.method == 'POST':
        post = request.form
        # edit movie data
        if post['name']:
            movieToEdit.name = post['name']
        if post['plot']:
            movieToEdit.plot = post['plot']
        if post['poster']:
            movieToEdit.poster = post['poster']
        if post['released']:
            # change date format from str to date object
            movieToEdit.released = datetime.strptime(
                post['released'], '%Y-%m-%d')
        # check if runtime is empty or an int value
        if post['runtime'] and not post['runtime'].isdigit():
            flash("Runtime Should Be A Number Or Left Empty")
            return redirect(
                url_for('editMovie', producer_id=producer_id,
                        movie_id=movie_id, producer=producer,
                        movie=movieToEdit, STATE=login_session.get('state')))
        elif post['runtime']:
            movieToEdit.runtime = post['runtime']
        session.add(movieToEdit)
        session.commit()

        flash('Movie Successfully Edited')
        return redirect(url_for('showMovies', producer_id=producer_id))
    else:
        return render_template('editmovie.html',
                               producer=producer, movie=movieToEdit,
                               STATE=login_session.get('state'))


@app.route('/producer/<int:producer_id>/movie/<int:movie_id>/delete/',
           methods=['GET', 'POST'])
def deleteMovie(producer_id, movie_id):
    # make sure the user is logged in
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    # get producer data
    producer = session.query(Producer).filter_by(id=producer_id).one()

    # get movie data
    movieToDelete = session.query(Movie).filter_by(id=movie_id).one()

    # check if signed in user is the owner of this producer
    if movieToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction() {"
                + "alert('You are not authorized to delete movies from this "
                + "producer. Please add your own producer in order to delete "
                + "movies.');window.location.href = '/producer';}"
                + "</script><body onload='myFunction()'>")

    if request.method == 'POST':
        session.delete(movieToDelete)
        session.commit()

        flash('Movie Successfully Deleted')
        return redirect(url_for('showMovies', producer_id=producer_id))
    else:
        return render_template('deletemovie.html',
                               producer=producer, movie=movieToDelete,
                               STATE=login_session.get('state'))

# ############################-JSON API Endpoint-##############################


@app.route('/api/producers/')
def showProducersJSON():
    # get producers data
    producers = session.query(Producer).all()
    return jsonify(Producers=[i.serialize for i in producers])


@app.route('/api/producers/<int:producer_id>/movies/')
def showMoviesJSON(producer_id):
    # get movies data
    movies = session.query(Movie).filter_by(producer_id=producer_id).all()

    # change the date object to a string
    toDateStr(movies)
    return jsonify(Movies=[i.serialize for i in movies])


@app.route('/api/producers/<int:producer_id>/movies/<int:movie_id>/')
def showMovieJSON(producer_id, movie_id):
    # get movie data
    movie = session.query(Movie).filter_by(id=movie_id).one()

    # change the date object to a string
    toDateStr(movie)
    return jsonify(Movie=movie.serialize)

# #########################-########################-##########################


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000, debug=True)
