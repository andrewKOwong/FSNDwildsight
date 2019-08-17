#!/usr/bin/env python3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class SightingForm(FlaskForm):
    # error messages, MS is short for message
    MS_REQ = "This field required!"
    MS_LEN = "Maximum %(max)d characters."
    # Form fields
    title = StringField('Title', validators=[DataRequired(message=MS_REQ), Length(max=250, message=MS_LEN)])
    description = StringField('Description', validators=[Length(max=2000, message=MS_LEN)])
    location = StringField('Location', validators=[DataRequired(message=MS_REQ), Length(max=200, message=MS_LEN)])
    sighting_type = SelectField('Sighting Type', coerce=int, validators=[DataRequired(message=MS_REQ)])
    submit = SubmitField('Submit!')