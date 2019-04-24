import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
	"""create User table"""
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

class Producer(Base):
	"""create Producer table"""
	__tablename__ = 'producer'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	user_id = Column(Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"))
	user = relationship(User)

	# We added this serialize function to be able to send JSON objects in a serializable format
	@property
	def serialize(self):

		return {
			'id' : self.id,
			'name' : self.name
		}
 
class Movie(Base):
	"""create Movie table"""
	__tablename__ = 'movie'

	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	plot = Column(String(300))
	runtime = Column(Integer)
	released = Column(Date)
	poster = Column(String(250))
	producer_id = Column(Integer,ForeignKey('producer.id'))
	producer = relationship(Producer) 
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)
	 
	# We added this serialize function to be able to send JSON objects in a serializable format
	@property
	def serialize(self):
	   
	   return {
	   		'id' : self.id,
			'name' : self.name,
			'plot' : self.plot,
			'runtime' : self.runtime,
			'released' : self.released,
			'poster' : self.poster
		}

engine = create_engine('sqlite:///movies.db')

Base.metadata.create_all(engine)