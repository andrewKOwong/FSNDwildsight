#!/usr/bin/env python3
from builtins import type as typeof # For debugging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from database_setup import Sighting, SightingType, Base

from sighting_form import SightingForm

from flask import Flask, escape, render_template, request, redirect, url_for, flash
app = Flask(__name__)

# Use of Flask-SQLAlchemy is recommended to avoid # multi threading issues.
# See https://docs.sqlalchemy.org/en/13/orm/contextual.html 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wildsight.db'
db = SQLAlchemy(app)
session = db.session

# Old non Flask SQLAlchemy code
#from sqlalchemy.orm import sessionmaker
#engine = create_engine('sqlite:///wildsight.db')
#Base.metadata.bind = engine
#DBSession = sessionmaker(bind=engine)
#session = DBSession()

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
    return render_template('type_home.html', sightings=sightings, type_name=type_name)

# Placeholder pages to create, edit, and delete pages
@app.route('/submit_sighting/', methods = ['GET', 'POST'])
def create_sighting():
    # Initialize sighting type choices for form
    sighting_types = session.query(SightingType)
    form = SightingForm()
    form.sighting_type_id.choices = [(type.id, type.type) for type in sighting_types]
    # Handle incoming POST form submission
    if form.validate_on_submit():
        new_sighting = Sighting(title = form.title.data,
                                description = form.description.data,
                                location = form.location.data,
                                sighting_type = session.query(SightingType).filter_by(id=form.sighting_type_id.data).one())
        session.add(new_sighting)
        session.commit()
        flash("New sighting created!")
        return redirect(url_for('home'))             
    # Otherwise render the new sighting page, with or without form data recycling
    else:
        return render_template('new_sighting.html', form=form)

@app.route('/types/<type_id>/<int:sighting_id>/edit/', methods=['GET', 'POST'])
def edit_sighting(type_id, sighting_id):
    # Pre fill form with either incoming form data (i.e. from POST),
    # Or falling back onto a db query (object handles are the same)
    current_sighting = session.query(Sighting).filter_by(id=sighting_id).one()
    form = SightingForm(request.form, obj=current_sighting)

    #if request.method == 'POST':
    #    form = SightingForm(request.form)
    #else:
    #    current_sighting = session.query(Sighting).filter_by(id=sighting_id).one()
    #    form = SightingForm(obj=current_sighting)
    # Initialize sighting type choices for form
    sighting_types = session.query(SightingType) 
    form.sighting_type_id.choices = [(type.id, type.type) for type in sighting_types]
    # Handle incoming POST form submission
    if request.method == 'POST' and form.validate_on_submit():
        # As object handles are the same, can use populate_obj()
        form.populate_obj(current_sighting)
        session.add(current_sighting)
        session.commit()
        flash("Sighting edited!")
        return redirect(url_for('type_home', type_id=type_id))   
    # Otherwise display the editing form
    else:
        return render_template('edit_sighting.html', form=form, type_id=type_id)

@app.route('/sightings/<type>/<int:id>/delete/', methods=['GET','POST'])
def delete_sighting(type, id):
    sighting = session.query(Sighting).filter_by(id=id).one()
    if request.method == 'POST':
        session.delete(sighting)
        session.commit()
        flash("Sighting deleted!")
        return redirect(url_for('home'))
    else:
        return render_template('delete_sighting.html', sighting=sighting)

# Displays types available
@app.route('/types/')
def list_types():
    types = session.query(SightingType)
    output = ''
    for i in types:
        output += i.type
        output += '</br>'
    return output

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'placeholder_secret_key'
    app.run(host = '0.0.0.0', port = 5000)