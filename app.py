#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    show = db.relationship('Show', backref='venues', lazy=True)

    def __repr__(self):
        return f'<Venue ID: {self.id}, Name: {self.name}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    show = db.relationship('Show', backref='artists', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, Name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))

    def __repr__(self):
        return f'<Show ID: {self.id}, Time: {self.start_time} , Venue ID: {self.venue_id}, Artist ID: {self.artist_id}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  getallstate = Venue.query.distinct(Venue.state, Venue.city).all()
  
  data=[]
  for uniquestate in getallstate:
    states = Venue.query.filter_by(state=uniquestate.state, city=uniquestate.city).all()

    state_data=[]
    for venue in states:
      venue_data = {'id': venue.id,
                    'name': venue.name,
                    'numof_upcm_shows' : Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()}
      state_data.append(venue_data)

    data.append({
     'city': venue.city,
     'state': venue.state,
     'venues': state_data
    })
   
  return render_template('pages/venues.html', areas=data);

  #data=[{
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "venues": [{
  #    "id": 1,
  #    "name": "The Musical Hop",
  #    "num_upcoming_shows": 0,
  #  }, {
  #    "id": 3,
  #    "name": "Park Square Live Music & Coffee",
  #    "num_upcoming_shows": 1,
  #  }]
  #}, {
  #  "city": "New York",
  #  "state": "NY",
  #  "venues": [{
  #    "id": 2,
  #    "name": "The Dueling Pianos Bar",
  #    "num_upcoming_shows": 0,
  #  }]
  #}]
  #return render_template('pages/venues.html', areas=data);
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', ' ')
  venuesearch = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  
  data=[]
  counter=0
  for venue in venuesearch:
      venue_data = {'id': venue.id,
                    'name': venue.name,
                    'numof_upcm_shows' : Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()}
      counter+=1
      data.append(venue_data)

  response = {
    'count': counter,
    'data': data
  }


  #response={
  #  "count": 1,
  #  "data": [{
  #    "id": 2,
  #    "name": "The Dueling Pianos Bar",
  #    "num_upcoming_shows": 0,
  #  }]
  #}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data={}
  venueshow = Venue.query.get(venue_id)
  
  pastshows = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
  past_show=[]
  for show in pastshows:
    past_show.append({'artist_id': show.artist_id,
                      'artist_name': show.artist.name,
                      'artist_image_link': show.artist.image_link,
                      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')}
                    )

  upcomingshows = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()
  upcoming_show=[]
  for show in upcomingshows:
    upcoming_show.append({'artist_id': show.artist_id,
                          'artist_name': show.artist.name,
                          'artist_image_link': show.artist.image_link,
                          'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')}
                        )
   
  data['id']= venueshow.id
  data['name']= venueshow.name
  data['genres']= venueshow.genres.strip('{}').split(',')
  data['address']= venueshow.address
  data['city']= venueshow.city
  data['state']= venueshow.state
  data['phone']= venueshow.phone
  data['website_link']= venueshow.website_link
  data['facebook_link']= venueshow.facebook_link
  data['seeking_talent']= venueshow.seeking_talent
  data['seeking_description']= venueshow.seeking_description
  data['image_link']= venueshow.image_link
  data['past_shows']= past_show
  data['upcoming_shows']= upcoming_show
  data['past_shows_count']= len(past_show)
  data['upcoming_shows_count']= len(upcoming_show)

  return render_template('pages/show_venue.html', venue=data)
  

  #data1={
  #  "id": 1,
  #  "name": "The Musical Hop",
  #  "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #  "address": "1015 Folsom Street",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "123-123-1234",
  #  "website": "https://www.themusicalhop.com",
  #  "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #  "seeking_talent": True,
  #  "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #  "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #  "past_shows": [{
  #    "artist_id": 4,
  #    "artist_name": "Guns N Petals",
  #    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #    "start_time": "2019-05-21T21:30:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data2={
  #  "id": 2,
  #  "name": "The Dueling Pianos Bar",
  #  "genres": ["Classical", "R&B", "Hip-Hop"],
  #  "address": "335 Delancey Street",
  #  "city": "New York",
  #  "state": "NY",
  #  "phone": "914-003-1132",
  #  "website": "https://www.theduelingpianos.com",
  #  "facebook_link": "https://www.facebook.com/theduelingpianos",
  #  "seeking_talent": False,
  #  "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #  "past_shows": [],
  #  "upcoming_shows": [],
  #  "past_shows_count": 0,
  #  "upcoming_shows_count": 0,
  #}
  #data3={
  #  "id": 3,
  #  "name": "Park Square Live Music & Coffee",
  #  "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #  "address": "34 Whiskey Moore Ave",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "415-000-1234",
  #  "website": "https://www.parksquarelivemusicandcoffee.com",
  #  "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #  "seeking_talent": False,
  #  "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #  "past_shows": [{
  #    "artist_id": 5,
  #    "artist_name": "Matt Quevedo",
  #    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #    "start_time": "2019-06-15T23:00:00.000Z"
  #  }],
  #  "upcoming_shows": [{
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-01T20:00:00.000Z"
  #  }, {
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-08T20:00:00.000Z"
  #  }, {
  #    "artist_id": 6,
  #    "artist_name": "The Wild Sax Band",
  #    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #    "start_time": "2035-04-15T20:00:00.000Z"
  #  }],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 1,
  #}
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website_link = request.form['website_link']
      seeking_talent = True if 'seeking_talent' in request.form else False 
      seeking_description = request.form['seeking_description']
      venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
      
      db.session.add(venue)
      db.session.commit()
  except:
      error = True
      print ('error 4')
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
    flash ('Error occured while adding ' + request.form['name'])
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
    flash ('Error occured while deleting ' + venue_id)
  if not error:
    flash('Venue ' + venue_id + ' was successfully removed!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = db.session.query(Artist).all()
  #data=[{
  #  "id": 4,
  #  "name": "Guns N Petals",
  #}, {
  #  "id": 5,
  #  "name": "Matt Quevedo",
  #}, {
  #  "id": 6,
  #  "name": "The Wild Sax Band",
  #}]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', ' ')
  artistsearch = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  
  data=[]
  counter=0
  for artist in artistsearch:
      artist_data = {'id': artist.id,
                    'name': artist.name,
                    'numof_upcm_shows' : Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > datetime.now()).count()}
      counter+=1
      data.append(artist_data)

  response = {
    'count': counter,
    'data': data
  }

  #response={
  #  "count": 1,
  #  "data": [{
  #    "id": 4,
  #    "name": "Guns N Petals",
  #    "num_upcoming_shows": 0,
  #  }]
  #}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  data={}
  artistshow = Artist.query.get(artist_id)
  pastshows = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
  print ('artistshow ', artistshow)
  past_show=[]
  for show in pastshows:
    past_show.append({'venue_id': show.venue_id,
                      'venue_name': show.venue.name,
                      'venue_image_link': show.venue.image_link,
                      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')}
                    )

  upcomingshows = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()

  upcoming_show=[]
  for show in upcomingshows:
    upcoming_show.append({'venue_id': show.venue_id,
                          'venue_name': show.venue.name,
                          'venue_image_link': show.venue.image_link,
                          'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')}
                        )
    
  print ('past show ', past_show)
  print ('upcoming show ', upcoming_show)
  
  data['id'] = artistshow.id
  data['name'] = artistshow.name
  data['genres'] = artistshow.genres.strip('{}').split(',')
  data['city'] = artistshow.city
  data['state'] = artistshow.state
  data['phone'] = artistshow.phone
  data['website'] = artistshow.website_link
  data['facebook_link'] = artistshow.facebook_link
  data['seeking_venue'] = artistshow.seeking_venue
  data['seeking_description'] = artistshow.seeking_description
  data['image_link'] = artistshow.image_link
  data['past_shows'] = past_show
  data['upcoming_shows'] = upcoming_show
  data['past_shows_count'] = len(past_show)
  data['upcoming_shows_count'] = len(upcoming_show)

  print ('data ', data)
  
  return render_template('pages/show_artist.html', artist=data)
  #data1={
  #  "id": 4,
  #  "name": "Guns N Petals",
  #  "genres": ["Rock n Roll"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "326-123-5000",
  #  "website": "https://www.gunsnpetalsband.com",
  #  "facebook_link": "https://www.facebook.com/GunsNPetals",
  #  "seeking_venue": True,
  #  "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #  "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #  "past_shows": [{
  #    "venue_id": 1,
  ##    "venue_name": "The Musical Hop",
  #    "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #    "start_time": "2019-05-21T21:30:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data2={
  #  "id": 5,
  #  "name": "Matt Quevedo",
  #  "genres": ["Jazz"],
  #  "city": "New York",
  #  "state": "NY",
  #  "phone": "300-400-5000",
  #  "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #  "seeking_venue": False,
  #  "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #  "past_shows": [{
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2019-06-15T23:00:00.000Z"
  #  }],
  #  "upcoming_shows": [],
  #  "past_shows_count": 1,
  #  "upcoming_shows_count": 0,
  #}
  #data3={
  #  "id": 6,
  #  "name": "The Wild Sax Band",
  #  "genres": ["Jazz", "Classical"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "432-325-5432",
  #  "seeking_venue": False,
  #  "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "past_shows": [],
  #  "upcoming_shows": [{
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-01T20:00:00.000Z"
  #  }, {
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-08T20:00:00.000Z"
  #  }, {
  #    "venue_id": 3,
  #    "venue_name": "Park Square Live Music & Coffee",
  #    "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #    "start_time": "2035-04-15T20:00:00.000Z"
  #  }],
  #  "past_shows_count": 0,
  #  "upcoming_shows_count": 3,
  #}
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  #return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.filter_by(id=artist_id).first()
  form = VenueForm(obj=artist)

  #artist={
  #  "id": 4,
  #  "name": "Guns N Petals",
  #  "genres": ["Rock n Roll"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "326-123-5000",
  #  "website": "https://www.gunsnpetalsband.com",
  #  "facebook_link": "https://www.facebook.com/GunsNPetals",
  #  "seeking_venue": True,
  #  "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #  "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  #}
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False  
  artist = Artist.query.get(artist_id)

  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('Error occured while updating Artist')
  if not error: 
    flash('Artist was successfully updated')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.filter_by(id=venue_id).first()
  form = VenueForm(obj=venue)
  
  #  "id": 1,
  #  "name": "The Musical Hop",
  #  "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #  "address": "1015 Folsom Street",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "123-123-1234",
  #  "website": "https://www.themusicalhop.com",
  #  "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #  "seeking_talent": True,
  #  "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #  "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  #}
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False  
  venue = Venue.query.get(venue_id)
  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash(f'Error occured while updating Venue')
  if not error: 
    flash(f'Venue was successfully updated')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  try: 
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres'),
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('Error occured while adding Artist ' + request.form['name'])
  if not error: 
    flash('Artist ' + request.form['name'] + ' was successfully added!')

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  showssearch = db.session.query(Show).join(Artist).join(Venue).all()

  data = []
  for show in showssearch: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  #data=[{
  #  "venue_id": 1,
  #  "venue_name": "The Musical Hop",
  #  "artist_id": 4,
  #  "artist_name": "Guns N Petals",
  #  "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #  "start_time": "2019-05-21T21:30:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 5,
  #  "artist_name": "Matt Quevedo",
  #  "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #  "start_time": "2019-06-15T23:00:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-01T20:00:00.000Z"
  #}, {
  #  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-08T20:00:00.000Z"
  #}, {
  ##  "venue_id": 3,
  #  "venue_name": "Park Square Live Music & Coffee",
  #  "artist_id": 6,
  #  "artist_name": "The Wild Sax Band",
  #  "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #  "start_time": "2035-04-15T20:00:00.000Z"
  #}]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try: 
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    print(request.form)

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('Error occured while adding show')
  if not error: 
    flash('Show was successfully added')
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
