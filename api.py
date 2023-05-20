from flask import Flask, request, jsonify, session,make_response
from flask_restful import Api, Resource, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os.path
app = Flask(__name__, template_folder="templates")
app.secret_key = 'my'

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(basedir, "f11f.db")
db = SQLAlchemy(app)
api = Api(app)


class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String,  nullable=False)
    email = db.Column(db.String)
    mobile = db.Column(db.Integer)
    tickets = db.relationship("Show", secondary="Tickets")

class Tickets(db.Model):
    __tablename__ = 'Tickets'
    ticket_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tuser_id = db.Column(db.Integer, db.ForeignKey("User.user_id"),nullable=False)
    tshow_id = db.Column(db.Integer, db.ForeignKey("Show.show_id"),nullable=False)
    tvenue_id = db.Column(db.Integer, db.ForeignKey("Venue.venue_id"),nullable=False)
    number_of_tickets=db.Column(db.Integer,  nullable=False)

class Show(db.Model):
    __tablename__ = 'Show'
    show_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer,  nullable=False)
    tags = db.Column(db.String,nullable=False)
    timing = db.Column(db.String,nullable=False)
    ticketprice=db.Column(db.Integer,nullable=False)
    venues = db.relationship("Venue", secondary="Enroll")
    buyers = db.relationship("User", secondary="Tickets")
    tickets = db.relationship("Tickets", backref="show")

class Venue(db.Model):
    __tablename__ = 'Venue'
    venue_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    place = db.Column(db.String,  nullable=False)
    location = db.Column(db.String,  nullable=False)
    capacity = db.Column(db.Integer)
    shows = db.relationship("Show", secondary="Enroll")

class Enroll(db.Model):
    __tablename__ = 'Enroll'
    enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    evenue_id = db.Column(db.Integer, db.ForeignKey("Venue.venue_id"),nullable=False)
    eshow_id = db.Column(db.Integer, db.ForeignKey("Show.show_id"),nullable=False)

class Rating(db.Model):
    __tablename__ = 'Rating'
    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('Show.show_id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.venue_id'))
    show_rating = db.Column(db.Integer)
    show_comment = db.Column(db.String)
    venue_rating = db.Column(db.Integer)
    venue_comment = db.Column(db.String)

admins = {
    "nils": "nil123"
}

class Venuee(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='Name of the venue is required.')
    parser.add_argument('place', type=str, required=True, help='Place of the venue is required.')
    parser.add_argument('location', type=str, required=True, help='Location of the venue is required.')
    parser.add_argument('capacity', type=int, required=True, help='Capacity of the venue is required.')

    # Endpoint for adding a venue
    def post(self):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')

        args = self.parser.parse_args()
        name = args['name']
        place = args['place']
        location = args['location']
        capacity = args['capacity']

        # Create a new venue object
        venue = Venue(name=name, place=place, location=location, capacity=capacity)

        # Add the venue object to the database
        db.session.add(venue)
        db.session.commit()

        return make_response(jsonify({'message': 'Venue added successfully.'}), 200)
    
    def get(self, venue_id):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')

        venue = Venue.query.filter_by(venue_id=venue_id).first()

        if not venue:
            abort(404, message='Venue not found.')

        venue_data = {
            'name': venue.name,
            'place': venue.place,
            'location': venue.location,
            'capacity': venue.capacity
        }

        return make_response(jsonify(venue_data), 200)
    

    # Endpoint for updating a venue by ID
    def put(self, venue_id):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')

        venue = Venue.query.filter_by(venue_id=venue_id).first()

        if not venue:
            abort(404, message='Venue not found.')

        args = self.parser.parse_args()
        venue.place = args['place']
        venue.location = args['location']
        venue.capacity = args['capacity']

        db.session.commit()

        return make_response(jsonify({'message': 'Venue updated successfully.'}), 200)

    # Endpoint for deleting a venue by ID
    def delete(self, venue_id):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')

        venue = Venue.query.filter_by(venue_id=venue_id).first()

        if not venue:
            abort(404, message='Venue not found.')

        shows = Show.query.join(Enroll).join(Venue).filter(Venue.venue_id == venue_id).all()
        for show in shows:
            tickets = Tickets.query.filter_by(tshow_id=show.show_id).all()
            for ticket in tickets:
                db.session.delete(ticket)
            db.session.commit()
            db.session.delete(show)
        db.session.commit()

        db.session.delete(venue)
        db.session.commit()

        return make_response(jsonify({'message': 'Venue deleted successfully.'}), 200)

# Endpoint for admin login
class VenueList(Resource):
    # Endpoint for getting a list of all venues
    def get(self):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')

        venues = Venue.query.all()
        venue_list = []
        for venue in venues:
            venue_data = {
                'venue_id': venue.venue_id,
                'name': venue.name,
                'place': venue.place,
                'location': venue.location,
                'capacity': venue.capacity,
                'shows': [show.name for show in venue.shows]
            }
            venue_list.append(venue_data)

        return make_response(jsonify({'venues': venue_list}), 200)

class AdminLogin(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        if not username or not password:
            abort(400, message='Username and password are required.')

        if username in admins and admins[username] == password:
            session['username'] = username  # Start a session for the authenticated admin
            
            return make_response(jsonify({'message': 'Login successful.'}), 200)
        else:
            abort(401, message='Invalid username or password.')

# Endpoint for getting the currently logged in admin
class Admin(Resource):
    def get(self):
        username = session.get('username')

        if not username:
            abort(401, message='Not logged in.')

        return make_response(jsonify({'username': username}), 200)
    
class UserRegistration(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username is required.')
    parser.add_argument('password', type=str, required=True, help='Password is required.')

    def post(self):
        data = self.parser.parse_args()
        username = data['username']
        password = data['password']

        # Check if user already exists
        if User.query.filter_by(Username=username).first():
            return {'message': 'User already exists.'}, 400

        # Create a new user object
        user = User(Username=username, password=password)

        # Add the user object to the database
        session['username'] = username
        db.session.add(user)
        db.session.commit()

        return make_response(jsonify({'message': 'User registered successfully.'}), 201)

# Endpoint for user login
class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username is required.')
    parser.add_argument('password', type=str, required=True, help='Password is required.')

    def post(self):
        data = self.parser.parse_args()
        username = data['username']
        password = data['password']

        # Check if user exists
        user = User.query.filter_by(Username=username).first()
        if not user:
            return make_response(jsonify({'message': 'Invalid credentials.'}), 401)

        # Check if password is correct
        if not user.password == password:
            return make_response(jsonify({'message': 'Invalid credentials.'}), 401)

        # Generate access token
        session['username'] = username
        return make_response(jsonify({'message': 'User login successfully.'}), 201)

    
class Logout(Resource):
    def post(self):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')
        session.clear()
        return make_response(jsonify({'message': 'Logged out successfully.'}), 200)
    
class UserProfile(Resource):
    def get(self):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')
        user = User.query.filter_by(Username=username).first()

        if user is None:
            abort(404, message='User not found.')

        return make_response(jsonify({'username': user.Username, 'email': user.email, 'mobile': user.mobile}), 200)

    def put(self):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')
        user = User.query.filter_by(Username=username).first()

        if user is None:
            abort(404, message='User not found.')

        data = request.get_json()
        email = data.get('email', user.email)
        mobile = data.get('mobile', user.mobile)

        user.email = email
        user.mobile = mobile

        db.session.commit()

        return make_response(jsonify({'message': 'User profile updated.'}), 200)
    

class ShowVenue(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='Name of the show is required.')
    parser.add_argument('rating', type=int, required=True, help='Rating of the show is required.')
    parser.add_argument('tags', type=str, required=True, help='Tags of the show is required.')
    parser.add_argument('timing', type=str, required=True, help='Timing of the show is required.')
    parser.add_argument('ticketprice', type=int, required=True, help='Ticket price of the show is required.')

    # Endpoint for adding a show to a venue
    def post(self, venue_name):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')

        venue = Venue.query.filter_by(name=venue_name).first()

        if not venue:
            abort(404, message=f'Venue {venue_name} not found.')

        args = self.parser.parse_args()
        name = args['name']
        rating = args['rating']
        tags = args['tags']
        timing = args['timing']
        ticketprice = args['ticketprice']

        # Create a new show object
        show = Show(name=name, rating=rating, tags=tags, timing=timing, ticketprice=ticketprice)

        # Add the show object to the database and link it to the venue
        venue.shows.append(show)
        db.session.add(show)
        db.session.commit()

        return make_response(jsonify({'message': 'Show added successfully.'}), 200)

    # Endpoint for getting all shows of a venue
    def get(self, venue_name):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')
        venue = Venue.query.filter_by(name=venue_name).first()

        if not venue:
            abort(404, message=f'Venue {venue_name} not found.')

        shows = venue.shows
        if not shows:
            return make_response(jsonify({'message': f'{venue.name} has no show.'}), 200)
        shows_list = []
        for show in shows:
            show_dict = {'show_id': show.show_id,
                        'name': show.name,
                        'rating': show.rating,
                        'tags': show.tags,
                        'timing': show.timing,
                        'ticketprice': show.ticketprice}
            shows_list.append(show_dict)
        return make_response(jsonify({'shows': shows_list}), 200)

    # Endpoint for updating a show of a venue
    def put(self, venue_name, show_name):
        username = session.get('username')

        if not username:
            abort(401, message='Not logged in.')

        venue = Venue.query.filter_by(name=venue_name).first()

        if not venue:
            abort(404, message=f'Venue {venue_name} not found.')

        show = Show.query.filter_by(name=show_name).first()

        if not show:
            abort(404, message=f'Show {show_name} not found.')

        args = self.parser.parse_args()
        show.name = args['name']
        show.rating = args['rating']
        show.tags = args['tags']
        show.timing = args['timing']
        show.ticketprice = args['ticketprice']

        db.session.commit()

        return make_response(jsonify({'message': 'Show updated successfully.'}), 200)
    
    def delete(self, venue_name, show_name):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')

        venue = Venue.query.filter_by(name=venue_name).first()
        show = Show.query.filter_by(name=show_name).first()

        if not venue:
            abort(404, message=f'Venue {venue_name} not found.')
        
        if not show:
            abort(404, message=f'Show {show_name} not found.')

        if show in venue.shows:
            venue.shows.remove(show)
            db.session.commit()

        return make_response(jsonify({'message': f'Show {show_name} removed from venue {venue_name}.'}), 200)
    
class Bookk(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('no_of_tickets', type=int, required=True, help='Number of tickets is required.')

    def post(self, venue_name, show_name):
        username = session.get('username')

        if not username:
            abort(401, message='Not logged in.')

        venue = Venue.query.filter_by(name=venue_name).first()
        if not venue:
            abort(404, message=f'Venue {venue_name} not found.')

        show = Show.query.filter_by(name=show_name).first()
        if not show:
            abort(404, message=f'Show {show_name} not found.')

        args = self.parser.parse_args()
        no_of_tickets = args['no_of_tickets']

        if no_of_tickets <= 0:
            abort(400, message='Number of tickets should be greater than zero.')

        tickets_sold = db.session.query(func.sum(Tickets.number_of_tickets)).filter_by(tshow_id=show.show_id).scalar() or 0
        tickets_available = venue.capacity - tickets_sold

        if no_of_tickets > tickets_available:
            abort(400, message='Number of tickets requested is greater than available tickets.')

        user = User.query.filter_by(Username=username).first()

        ticket = Tickets(tuser_id=user.user_id, tshow_id=show.show_id, tvenue_id=venue.venue_id, number_of_tickets=no_of_tickets)
        db.session.add(ticket)
        db.session.commit()

        return make_response(jsonify({'message': f'{username} , you booked {no_of_tickets} tickets for {show.name} at {venue.name}.'}), 200)
    def get(self, venue_name, show_name):

        venue = Venue.query.filter_by(name=venue_name).first()
        if not venue:
            abort(404, message=f'Venue {venue_name} not found.')

        show = Show.query.filter_by(name=show_name).first()
        if not show:
            abort(404, message=f'Show {show_name} not found.')

        tickets_sold = db.session.query(func.sum(Tickets.number_of_tickets)).filter_by(tshow_id=show.show_id).scalar() or 0
        tickets_available = venue.capacity - tickets_sold

        return make_response(jsonify({'message': f'{tickets_available} tickets available for {show.name} at {venue.name}.'}), 200)
    
class Bookings(Resource):
    def get(self):
        username = session.get('username')
        if not username:
            abort(401, message='Not logged in.')
        user = User.query.filter_by(Username=username).first()
    
        tickets = user.tickets
        if not tickets:
            return make_response(jsonify({'message': f'{user.Username} has no bookings.'}), 200)
        result = []
        tickets = Tickets.query.filter_by(tuser_id=user.user_id).join(Show, Tickets.tshow_id==Show.show_id).join(Venue, Tickets.tvenue_id==Venue.venue_id).add_columns(Venue.name, Show.name, Show.timing, Tickets.ticket_id,Tickets.number_of_tickets).all()
        for ticket in tickets:
            result.append({
                'ticket_id': ticket[4],
                'show_name': ticket[2],
                'venue_name': ticket[1],
                'number_of_tickets': ticket[5]
            })
        return make_response(jsonify({'bookings': result}), 200)

api.add_resource(Venuee, '/venue','/venue/<int:venue_id>')
api.add_resource(VenueList, '/venues')
api.add_resource(AdminLogin, '/admin/login')
api.add_resource(Admin, '/admin/me')
api.add_resource(Logout, '/logout')
api.add_resource(UserRegistration, '/user/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserProfile, '/user/me')
api.add_resource(ShowVenue, '/show/<string:venue_name>', '/show/<string:venue_name>/<string:show_name>')
api.add_resource(Bookk, '/book/<string:venue_name>/<string:show_name>')
api.add_resource(Bookings, '/bookings')

if __name__ == '__main__':
    app.run(debug=True)