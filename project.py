from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, User, Producer, Movie

app = Flask(__name__)
engine = create_engine('sqlite:///movies.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()





if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.run(host = '0.0.0.0', port = 5000, debug = True)