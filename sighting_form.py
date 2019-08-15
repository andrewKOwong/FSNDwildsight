from flask-wtf import FlaskForm
from WTForms import StringField, SubmitField, SelectField
from WTForms.validators import DataRequired, Length

class SightingForm(FlaskForm):
    # error messages, MS is short for message
    MS_REQ = "This field required!"
    MS_LEN = "Maximum %(max)d characters."
    # Form fields
    title = StringField('Title', validators=[DateRequired(message=MS_REQ), Length(max=250, message=MS_LEN)])
    description = StringField('Description', validators=[DateRequired(message=MS_REQ), Length(max=2000, message=MS_LEN)])
    location = StringField('Location', validators=[DateRequired(message=MS_REQ), Length(max=200, message=MS_LEN)])
    sighting_type = SelectField('Sighting Type')
    submit = SubmitField('Submit!')