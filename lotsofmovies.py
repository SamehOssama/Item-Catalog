from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, User, Producer, Movie

from datetime import datetime

engine = create_engine('sqlite:///movies.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

def dateobj(dateToFormat): 
	"""format dates from "day(int) month(str) year(int)" to a python date object"""
	formatted = datetime.strptime(dateToFormat, "%d %b %Y")
	return formatted.date()

# Create dummy user
User1 = User(
	name="Sameh Ossama", 
	email="samehossama22@gmail.com",
	picture='https://www.google.com/url?sa=i&rct=j&q=&esrc=s&source=images&cd=&cad=rja&uact=8&ved=2ahUKEwjM2vu57uHhAhWmy4UKHdRbAtYQjRx6BAgBEAU&url=https%3A%2F%2Fwww.shutterstock.com%2Fnb%2Fvideo%2Fclip-1379626-silhouette-man-on-sunset-freedom-concept&psig=AOvVaw0e6mM-dRI6tk6dmrOXjGLt&ust=1555959323567448')

session.add(User1)
session.commit()


# Movies for Marvel Studios
producer1 = Producer(user_id=1, name="Marvel Studios")

session.add(producer1)
session.commit()

movie1 = Movie(
	user_id=1, 
	name="Thor: Ragnarok", 
	plot="Thor is imprisoned on the planet Sakaar, and must race against time to return to Asgard and stop Ragnarok, the destruction of his world, at the hands of the powerful and ruthless villain Hela.", 
	runtime="130", 
	released= dateobj("03 Nov 2017"), 
	poster="https://m.media-amazon.com/images/M/MV5BMjMyNDkzMzI1OF5BMl5BanBnXkFtZTgwODcxODg5MjI@._V1_SX300.jpg", 
	producer=producer1
)

session.add(movie1)
session.commit()

movie2 = Movie(
	user_id=1, 
	name="Black Panther", 
	plot="T'Challa, heir to the hidden but advanced kingdom of Wakanda, must step forward to lead his people into a new future and must confront a challenger from his country's past.", 
	runtime="134", 
	released=dateobj("16 Feb 2018"), 
	poster="https://m.media-amazon.com/images/M/MV5BMTg1MTY2MjYzNV5BMl5BanBnXkFtZTgwMTc4NTMwNDI@._V1_SX300.jpg", 
	producer=producer1
)

session.add(movie2)
session.commit()

movie3 = Movie(
	user_id=1, 
	name="Avengers: Infinity War", 
	plot="The Avengers and their allies must be willing to sacrifice all in an attempt to defeat the powerful Thanos before his blitz of devastation and ruin puts an end to the universe.", 
	runtime="149", 
	released=dateobj("27 Apr 2018"), 
	poster="https://m.media-amazon.com/images/M/MV5BMjMxNjY2MDU1OV5BMl5BanBnXkFtZTgwNzY1MTUwNTM@._V1_SX300.jpg", 
	producer=producer1
)

session.add(movie3)
session.commit()

movie4 = Movie(
	user_id=1, 
	name="Avengers: Endgame", 
	plot="After the devastating events of Avengers: Infinity War (2018), the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to undo Thanos' actions and restore order to the universe.", 
	runtime="181", 
	released=dateobj("25 Apr 2019"), 
	poster="https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SX300.jpg", 
	producer=producer1
)

session.add(movie4)
session.commit()


# Movies for Lionsgate Films
producer2 = Producer(user_id=1, name="Lionsgate Films")

session.add(producer2)
session.commit()

movie1 = Movie(
	user_id=1, 
	name="The Hunger Games", 
	plot="Katniss Everdeen voluntarily takes her younger sister's place in the Hunger Games: a televised competition in which two teenagers from each of the twelve Districts of Panem are chosen at random to fight to the death.", 
	runtime="142", 
	released=dateobj("23 Mar 2012"), 
	poster="https://m.media-amazon.com/images/M/MV5BMjA4NDg3NzYxMF5BMl5BanBnXkFtZTcwNTgyNzkyNw@@._V1_SX300.jpg", 
	producer=producer2
)

session.add(movie1)
session.commit()

movie2 = Movie(
	user_id=1, 
	name="The Hunger Games: Catching Fire", 
	plot="Katniss Everdeen and Peeta Mellark become targets of the Capitol after their victory in the 74th Hunger Games sparks a rebellion in the Districts of Panem.", 
	runtime="146", 
	released=dateobj("22 Nov 2013"), 
	poster="https://m.media-amazon.com/images/M/MV5BMTAyMjQ3OTAxMzNeQTJeQWpwZ15BbWU4MDU0NzA1MzAx._V1_SX300.jpg", 
	producer=producer2
)

session.add(movie2)
session.commit()

movie3 = Movie(
	user_id=1, 
	name="The Hunger Games: Mockingjay - Part 1", 
	plot="Katniss Everdeen is in District 13 after she shatters the games forever. Under the leadership of President Coin and the advice of her trusted friends, Katniss spreads her wings as she fights to save Peeta and a nation moved by her courage.", 
	runtime="123", 
	released=dateobj("21 Nov 2014"), 
	poster="https://m.media-amazon.com/images/M/MV5BMTcxNDI2NDAzNl5BMl5BanBnXkFtZTgwODM3MTc2MjE@._V1_SX300.jpg", 
	producer=producer2
)

session.add(movie3)
session.commit()

movie4 = Movie(
	user_id=1, 
	name="The Hunger Games: Mockingjay - Part 2", 
	plot="Katniss and a team of rebels from District 13 prepare for the final battle that will decide the future of Panem.", 
	runtime="137", 
	released=dateobj("20 Nov 2015"), 
	poster="https://m.media-amazon.com/images/M/MV5BNjQzNDI2NTU1Ml5BMl5BanBnXkFtZTgwNTAyMDQ5NjE@._V1_SX300.jpg", 
	producer=producer2
)

session.add(movie4)
session.commit()


# Movies for DreamWorks Animation
producer3 = Producer(user_id=1, name="DreamWorks Animation")

movie1 = Movie(
	user_id=1, 
	name="How to Train Your Dragon", 
	plot="A hapless young Viking who aspires to hunt dragons becomes the unlikely friend of a young dragon himself, and learns there may be more to the creatures than he assumed.", 
	runtime="98", 
	released=dateobj("26 Mar 2010"), 
	poster="https://m.media-amazon.com/images/M/MV5BMjA5NDQyMjc2NF5BMl5BanBnXkFtZTcwMjg5ODcyMw@@._V1_SX300.jpg", 
	producer=producer3
)

session.add(movie1)
session.commit()

movie2 = Movie(
	user_id=1, 
	name="How to Train Your Dragon 2", 
	plot="When Hiccup and Toothless discover an ice cave that is home to hundreds of new wild dragons and the mysterious Dragon Rider, the two friends find themselves at the center of a battle to protect the peace.", 
	runtime="102", 
	released=dateobj("13 Jun 2014"), 
	poster="https://m.media-amazon.com/images/M/MV5BMzMwMTAwODczN15BMl5BanBnXkFtZTgwMDk2NDA4MTE@._V1_SX300.jpg", 
	producer=producer3
)

session.add(movie2)
session.commit()

movie3 = Movie(
	user_id=1, 
	name="How to Train Your Dragon: The Hidden World", 
	plot="When Hiccup discovers Toothless isn't the only Night Fury, he must seek \"The Hidden World\", a secret Dragon Utopia before a hired tyrant named Grimmel finds it first.", 
	runtime="104", 
	released=dateobj("22 Feb 2019"), 
	poster="https://m.media-amazon.com/images/M/MV5BMjIwMDIwNjAyOF5BMl5BanBnXkFtZTgwNDE1MDc2NTM@._V1_SX300.jpg", 
	producer=producer3
)

session.add(movie3)
session.commit()



print("added movies items!")