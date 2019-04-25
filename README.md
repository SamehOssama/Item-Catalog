
# Item Catalog
_*by Sameh Koleid*_
## Project Description
This is the 2nd project from Udacity's fullstack nanodegree program. It consists of developing an application that provides a list of items within a variety of categories from a RESTful flask web application as well as provide a user registration and authentication system. 
It also has JSON endpoints to get data as needed from the database.
* Note: 
  * Registered users will have the ability to post, edit and delete their own items.
  * Unregistered users will be only able too see the content created by other users without the ability to create/edit/delete.
 #### For this project I have chosen a movies' catalog
## Content

  
* templates/
--- deletemovie.html
--- deleteproducer.html
--- editmovie.html
--- editproducer.html
--- header.html
--- login.html
--- main.html
--- movies.html
--- newmovie.html
--- newproducer.html
--- producers.html
--- public_movies.html
--- public_producers.html
* screenshots/
--- movie_delete.png
--- movie_edit.png
--- movie_json.png
--- movies_json.png
--- movies.png
--- movies_signedin.png
--- producers.png
--- producers_json.png
--- producers_signedin.png
* static/
--- image/
---  --- movies-banner.jpg
--- css/
---  --- style.css
* client_secrets.json
* db_setup.py
* lotsofmovies.py
* project.py
* README.md
### Dependencies
* [python 3](https://www.python.org/downloads/)
* [Virtual Box](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Git Bash](https://git-scm.com/downloads) (for windows users)
* Flask `pip3 install Flask`
* SQLAlchemy `pip3 install SQLAlchemy`
* Google authentication `pip3 install --upgrade google-auth`
### Instructions
1. Download VirtualBox and Vagrant and install them.
1. Download and Unzip the configuration file for the Vagrant VM [FSND-Virtual-Machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip).
2. inside the `vagrant` subdirectory, run the command `vagrant up` then `vagrant ssh` and then `cd \vagrant`.
3.  Clone or download this repository.
4. cd to the `itemcatalog` folder.
5. Type `python3 project.py` to run the program.
6. Finally, open your browser and visit http://localhost:5000/ .

