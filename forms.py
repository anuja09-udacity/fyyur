from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, validators
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, optional
from enumvalidation import Genre, State

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()           
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Regexp("^[0-9]*$", message="Phone number should only contain digits")]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
         choices=Genre.choices()
    )
    
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if all(elem in self.genres.data for elem in Genre.choices()):
            self.genres.errors.append('Invalid genre.')
            return False
        if all(elem in self.state.data for elem in Genre.choices()):
            self.state.errors.append('Invalid state.')
            return False
        # if pass validation
        return True


class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone', validators=[DataRequired(), Regexp("^[0-9]*$", message="Phone number should only contain digits")]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=Genre.choices()
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[optional(), URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if all(elem in self.genres.data for elem in Genre.choices()):
            self.genres.errors.append('Invalid genre.')
            return False
        if all(elem in self.state.data for elem in Genre.choices()):
            self.state.errors.append('Invalid state.')
            return False
        # if pass validation
        return True

