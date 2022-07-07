# Warbler-twitter-clone
Warbler is an improved Twitter clone with added functionality!


<img width="1092" alt="warbler" src="https://user-images.githubusercontent.com/28359915/177471832-d5d0b006-186a-44cb-acbb-cfacb1f677e7.png">

# Setup

__Create a Python virtual environment:__

:class: console

  $ python3 -m venv venv
  
  $ source venv/bin/activate(venv) 
  
  $ pip install -r requirements.txt
  
__Set up the database:__

(venv) $ createdb warbler

(venv) $ python seed.py

__Start the server:__

(venv) $ flask run

# Libraries Ultilized

__WTForms__

__SQLAlchemy__

__Flask-Bcrypt__


