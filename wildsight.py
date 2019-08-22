#!/usr/bin/env python3
from builtins import type as typeof # For debugging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from database_setup import Sighting, SightingType, Base, User

from sighting_form import SightingForm

from flask import Flask, escape, render_template, request, redirect, url_for, flash, jsonify

# User session management
from flask import session as login_session
# Import for anti-forgery state token
import random
import string

# aborting bad login calls
from flask import abort

# Import for OAuth login implementation
from oauth2client.client import credentials_from_clientsecrets_and_code
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

# Client ID for Google signin
CLIENT_ID = json.loads(
    open('DO_NOT_COMMIT_client_secrets.json', 'r').read())['web']['client_id']

# Use of Flask-SQLAlchemy is recommended to avoid # multi threading issues.
# See https://docs.sqlalchemy.org/en/13/orm/contextual.html 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wildsight.db'
db = SQLAlchemy(app)
session = db.session

@app.route('/gsignin', methods=['POST'])
def gsignin():
    # Validate anti-CSRF token
    if request.args.get('csrf_token') != login_session['csrf_token']:
        abort(403)
    # Check for presence of 'X-Requested-With' header as
    # anti-CSRF measure.
    if not request.headers.get('X-Requested-With'):
        abort(403)
    
    # Obtain the auth code
    auth_code = request.data

    # JSON client secrets file from Google
    CLIENT_SECRETS_FILE = 'DO_NOT_COMMIT_client_secrets.json'

    # Upgrade the auth code into a credentials
    try: 
        credentials = credentials_from_clientsecrets_and_code(
            filename=CLIENT_SECRETS_FILE,
            scope=['profile', 'email'],
            code=auth_code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("Couldn't get access token from auth code"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    ## Check that the access token is valid via Google API
    access_token = credentials.access_token
    # Google token verification url
    url = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}".format(access_token)
    # Request to google's server that returns a JSON response
    h = httplib2.Http()
    # 2nd item contains a dict of useful results
    # (1st item is header)
    # Curiously, if there is an error, the response isn't a raw string 
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there is an error, abort with useful information
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = "application/json"
        return response

    ## Check if the token is for the right user
    g_id = credentials.id_token['sub']
    if result['user_id'] != g_id:
        response = make_response(json.dumps("Token ID does not match user", 401))
        response.headers['Content-Type'] = "application/json"
        return response

    ## Check if token matches this app's client ID
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Incorrect token for this app.", 401))
        response.headers['Content-Type'] = "application/json"
        return response

    ## Check to see if user is already signed in
    stored_access_token = login_session.get('access_token')
    stored_g_id = login_session.get('g_id')
    if stored_access_token is not None and g_id == stored_g_id:
        response = make_response(json.dumps("User already signed in.", 200))
        response.headers['Content-Type'] = "application/json"
        return response

    ## Otherwise store this new access token
    login_session['access_token'] = credentials.access_token
    login_session['g_id'] = g_id

    ## Attach user info to the session
    login_session['user_name'] = credentials.id_token['name']
    login_session['email'] = credentials.id_token['email']
    # URL string for Google server with picture
    login_session['picture'] = credentials.id_token['picture']

    ## Check to see if user already exists in user db,
    ## Otherwise create a new user
    user_id = get_user_id(login_session['email'])
    if user_id is None:
        user_id = create_user(login_session)
    ## Attach the user id
    login_session['user_id'] = user_id


    flash("Welcome {}!".format(login_session['user_name']))
    # Return blank html, as login page will handle redirect
    return "<html></html>"

## Helper functions for creating/checking for new users
def create_user(login_session):
    new_user = User(name=login_session['user_name'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def get_user_info(user_id):
    return session.query(User).filter_by(id=user_id).one()

def get_user_id(email):
    # If can't find email, then return None
    try:
        return session.query(User).filter_by(email=email).one()
    except:
        return None


@app.route('/gsignout', methods=['POST'])
def gsignout():
    access_token = login_session.get['access_token']
    if access_token is None:
        response = make_response(json.dumps('Current user not signed in/connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Login page
@app.route('/login')
def show_login():
    # SystemRandom provides more secure randomness from OS for anti-CSRF forgery token
    csrf_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
             for _ in range(32))
    login_session['csrf_token'] = csrf_token
    return render_template('login.html', csrf_token=csrf_token)


# Home page displays categories of sighting types
@app.route('/')
def home():
    #sighting_type = session.query(SightingType).first()
    #sightings = session.query(Sighting).filter_by(sighting_type_id = sighting_type.id)
    types = session.query(SightingType) # Sighting Types are pre-ordered before db creation
    sightings = session.query(Sighting)
    return render_template('index.html', sightings=sightings, types=types)

# Displays sightings of a particular type
@app.route('/types/<type_id>/')
def type_home(type_id):
    type_name = session.query(SightingType).filter_by(id=type_id).one().type
    sightings = session.query(Sighting).filter_by(sighting_type_id=type_id)
    # current_user_id allows Jinja template to check
    # which sightings belong to a logged in user,
    # and displays editing/deletion links accordingly.
    current_user_id = login_session.get('user_id')
    
    return render_template('type_home.html', sightings=sightings,
                                             type_name=type_name, 
                                             current_user_id=current_user_id)

# Placeholder pages to create, edit, and delete pages
@app.route('/submit_sighting/', methods = ['GET', 'POST'])
def create_sighting():
    # Check that user is logged in, if not redirect to login page
    if 'user_name' not in login_session:
        return redirect('/login')

    # Initialize sighting type choices for form
    sighting_types = session.query(SightingType)
    form = SightingForm()
    form.sighting_type_id.choices = [(type.id, type.type) for type in sighting_types]
    # Handle incoming POST form submission
    if form.validate_on_submit():
        new_sighting = Sighting(title = form.title.data,
                                description = form.description.data,
                                location = form.location.data,
                                sighting_type_id = form.sighting_type_id.data
                                )
        session.add(new_sighting)
        session.commit()
        flash("New sighting created!")
        return redirect(url_for('home'))             
    # Otherwise render the new sighting page, with or without form data recycling
    else:
        return render_template('new_sighting.html', form=form)

@app.route('/types/<type_id>/<int:sighting_id>/edit/', methods=['GET', 'POST'])
def edit_sighting(type_id, sighting_id):
    # Check that user is logged in, if not redirect to login page
    if 'user_name' not in login_session:
        return redirect('/login')

    # Check that the user is the owner of the sighting
    # If not, return them to type home w/ flash
    current_user = login_session.get('user_id')
    sighting = session.query(Sighting).filter_by(id=sighting_id).one()
    if current_user != sighting.user_id:
        flash("Sorry, only the owner of a sighting can edit.")
        return redirect(url_for('type_home', type_id=type_id))

    # Pre fill form with either incoming form data (i.e. from POST),
    # Or falling back onto a db query (object handles are the same)
    
    form = SightingForm(request.form, obj=sighting)
    # Initialize sighting type choices for form
    sighting_types = session.query(SightingType) 
    form.sighting_type_id.choices = [(type.id, type.type) for type in sighting_types]
    # Handle incoming POST form submission
    if request.method == 'POST' and form.validate_on_submit():
        # As object handles are the same, can use populate_obj()
        form.populate_obj(sighting)
        session.add(sighting)
        session.commit()
        flash("Sighting edited!")
        return redirect(url_for('type_home', type_id=type_id))   
    # Otherwise display the editing form
    else:
        return render_template('edit_sighting.html', form=form, type_id=type_id)

@app.route('/types/<type_id>/<int:sighting_id>/delete/', methods=['GET', 'POST'])
def delete_sighting(type_id, sighting_id):
    # Check that user is logged in, if not redirect to login page
    if 'user_name' not in login_session:
        return redirect('/login')

    # Check that the user is the owner of the sighting
    # If not, return them to type home w/ flash
    current_user = login_session.get('user_id')
    sighting = session.query(Sighting).filter_by(id=sighting_id).one()
    if current_user != sighting.user_id:
        flash("Sorry, only the owner of a sighting can delete.")
        return redirect(url_for('type_home', type_id=type_id))

    
    if request.method == 'POST':
        session.delete(sighting)
        session.commit()
        flash("Sighting deleted!")
        return redirect(url_for('type_home', type_id=type_id))
    else:
        return render_template('delete_sighting.html', 
                                sighting_title=sighting.title,
                                type_id=type_id)

## JSON APIs
# JSON API for all sightings
@app.route('/all/JSON/')
def all_JSON():
    sightings = session.query(Sighting)
    return jsonify(sightings=[i.serialize for i in sightings])

# JSON API for getting sightings of a particular type
@app.route('/types/<type_id>/JSON/')
def type_home_JSON(type_id):
    sightings = session.query(Sighting).filter_by(sighting_type_id=type_id)
    return jsonify(sightings=[i.serialize for i in sightings])

# JSON API for a specific sighting
@app.route('/types/<type_id>/<int:sighting_id>/JSON/')
def sighting_JSON(type_id, sighting_id):
    current_sighting = session.query(Sighting).filter_by(id=sighting_id).one()
    return jsonify(sightings=current_sighting.serialize) 


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'placeholder_secret_key'
    app.run(host = '0.0.0.0', port = 5000)