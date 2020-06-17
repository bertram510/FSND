#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Show {self.id} {self.start_time}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # date = dateutil.parser.parse(value.strftime(%c))
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return value
  # return babel.dates.format_datetime(date, format)

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
  venueList = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  current_time = datetime.now().strftime('%c')
  city = ''
  state = ''
  data = []
  index = -1
  for venue in venueList:
    upcoming_shows = Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > current_time).all()

    if (city == venue.city) and (state == venue.state):
      data[index]["venues"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(upcoming_shows)
      })
      
    else:
      index = index + 1
      city = venue.city
      state = venue.state
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  data = []
  venueList = Venue.query.filter(Venue.name.contains(request.form['search_term'])).all()
  for venue in venueList:
    data.append({
      "id": venue.id,
      "name": venue.name
    })

  response = {
    "count": len(venueList),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  data = {}
  if venue:
    data["id"] = venue_id
    data["name"] = venue.name
    data["genres"] = venue.genres
    data["address"] = venue.address
    data["city"] = venue.city
    data["state"] = venue.state
    data["phone"] = venue.phone
    data["website"] = venue.website
    data["facebook_link"] = venue.facebook_link
    data["seeking_talent"] = venue.seeking_talent
    data["seeking_description"] = venue.seeking_description
    data["image_link"] = venue.image_link
    upcomingShowList = []
    pastShowList = []
    current_time = datetime.now().strftime('%c')
    upcomingShows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
    for upcomingShow in upcomingShows:
      upcomingShowList.append({
        "artist_id": upcomingShow.artist.id,
        "artist_name": upcomingShow.artist.name,
        "artist_image_link": upcomingShow.artist.image_link,
        "start_time": upcomingShow.start_time
      })
    data["upcoming_shows"] = upcomingShowList
    data["upcoming_shows_count"] = len(upcomingShowList)
    pastShows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
    for pastShow in pastShows:
      pastShowList.append({
        "artist_id": pastShow.artist.id,
        "artist_name": pastShow.artist.name,
        "artist_image_link": pastShow.artist.image_link,
        "start_time": pastShow.start_time
      })
    data["past_shows"] = pastShowList
    data["past_shows_count"] = len(pastShowList)
    
    return render_template('pages/show_venue.html', venue=data)
  else:
    return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    venue = Venue(name = name, city = city, state = state, address = address, phone = phone, genres = genres, facebook_link = facebook_link)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  except():
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    if venue:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      flash('Venue ' + name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    # Always close database session.
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artistList = Artist.query.order_by(Artist.name).all()
  for artist in artistList:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  data = []
  artistList = Artist.query.filter(Artist.name.contains(request.form['search_term'])).all()
  for artist in artistList:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  response = {
    "count": len(artistList),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  data = {}
  if artist:
    data["id"] = artist_id
    data["name"] = artist.name
    data["genres"] = artist.genres
    data["city"] = artist.city
    data["state"] = artist.state
    data["phone"] = artist.phone
    data["website"] = artist.website
    data["facebook_link"] = artist.facebook_link
    data["seeking_venue"] = artist.seeking_venue
    data["seeking_description"] = artist.seeking_description
    data["image_link"] = artist.image_link
    upcomingShowList = []
    pastShowList = []
    current_time = datetime.now().strftime('%c')
    upcomingShows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
    for upcomingShow in upcomingShows:
      upcomingShowList.append({
        "venue_id": upcomingShow.venue.id,
        "venue_name": upcomingShow.venue.name,
        "venue_image_link": upcomingShow.venue.image_link,
        "start_time": upcomingShow.start_time
      })
    data["upcoming_shows"] = upcomingShowList
    data["upcoming_shows_count"] = len(upcomingShowList)
    pastShows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
    for pastShow in pastShows:
      pastShowList.append({
        "venue_id": pastShow.venue.id,
        "venue_name": pastShow.venue.name,
        "venue_image_link": pastShow.venue.image_link,
        "start_time": pastShow.start_time
      })
    data["past_shows"] = pastShowList
    data["past_shows_count"] = len(pastShowList)
    
    return render_template('pages/show_artist.html', artist=data)
  else:
    return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist:
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  return render_template('errors/404.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  if artist:
    setattr(artist, 'name', request.form.get('name'))
    setattr(artist, 'genres', request.form.get('genres'))
    setattr(artist, 'city', request.form.get('city'))
    setattr(artist, 'state', request.form.get('state'))
    setattr(artist, 'phone', request.form.get('phone'))
    setattr(artist, 'facebook_link', request.form.get('facebook_link'))
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
  return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.facebook_link.data = venue.facebook_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  if venue:
    setattr(venue, 'name', request.form.get('name'))
    setattr(venue, 'genres', request.form.get('genres'))
    setattr(venue, 'city', request.form.get('city'))
    setattr(venue, 'state', request.form.get('state'))
    setattr(venue, 'address', request.form.get('address'))
    setattr(venue, 'phone', request.form.get('phone'))
    setattr(venue, 'facebook_link', request.form.get('facebook_link'))
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
  return render_template('errors/404.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    artist = Artist(name = name, city = city, state = state, phone = phone, genres = genres, facebook_link = facebook_link)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully listed!')
  except():
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  showList = Show.query.order_by(Show.start_time).all()
  for show in showList:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']
    show = Show(venue_id = venue_id, artist_id = artist_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except():
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
