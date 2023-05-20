Ticket Booking System
This is a web application that allows users to book tickets for various shows and events happening in different venues. The application allows the users to browse through different shows, select their preferred shows and venues, book tickets, and make payments online.

Requirements
To use this API, you will need:
Python 3.x installed on your system
The Flask web framework installed
The necessary packages installed, which can be installed using the requirements.txt file

Installation
Clone this repository to your local machine.
Install the required packages by running the following command:
pip install -r requirements.txt
Start the Flask server by running the following command:
python main.py
The API will now be accessible at http://127.0.0.1:5000/.

API Endpoints
This API supports the following endpoints:
Venues
* GET /venues: Retrieves a list of all venues.
* GET /venue/<int:venue_id>: Retrieves a specific venue by ID.
* POST /venue: Creates a new venue.
* PUT /venue/<int:venue_id>: Updates a specific venue by ID.
* DELETE /venue/<int:venue_id>: Deletes a specific venue by ID.
Shows
* GET /show/<string:venue_name>: Retrieves a list of all shows for a specific venue.
* GET /show/<string:venue_name>/<string:show_name>: Retrieves a specific show for a specific venue.
* POST /show: Creates a new show.
* PUT /show/<int:show_id>: Updates a specific show by ID.
* DELETE /show/<int:show_id>: Deletes a specific show by ID.
Bookings
* GET /bookings: Retrieves a list of all bookings.
* POST /book/<string:venue_name>/<string:show_name>: Books a show at a specific venue.
Authentication
* POST /user/register: Registers a new user.
* POST /login: Logs in a user and returns an access token.
* GET /user/me: Retrieves the details of the logged-in user.
* POST /admin/login: Logs in an admin user and returns an access token.
* GET /admin/me: Retrieves the details of the logged-in admin user.
All endpoints require authentication, except for the registration and login endpoints.

Features
* Users can sign up and log in to the system.
* Users can browse through different shows and venues.
* Users can select a show and venue, choose the number of tickets and book them.
* Users can pay for the tickets online.
* Admin can add new shows and venues to the system.
* Admin can edit and delete existing shows and venues.
* Admin can view the list of users who have booked tickets for a particular show.

Technologies
* Flask web framework
* SQLAlchemy
* HTML, CSS, Bootstrap
* JavaScript
* SQLite

Usage
User
* Sign up or log in to the system.
* Browse through different shows and venues.
* Select a show and venue, choose the number of tickets and book them.
* Pay for the tickets online.
* View the list of booked tickets.

Admin
* Log in to the system as an admin.
* Add new shows and venues to the system.
* Edit and delete existing shows and venues.
* View the list of users who have booked tickets for a particular show.
