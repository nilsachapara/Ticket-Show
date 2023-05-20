from flask import Flask, redirect, render_template, request,session
from flask_sqlalchemy import SQLAlchemy
import os.path
from sqlalchemy import func,or_
from datetime import datetime
import matplotlib.pyplot as plt

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
app.secret_key = "mysecretkey"
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
    tuser_id = db.Column(db.Integer, db.ForeignKey("User.user_id"),
                            nullable=False)
    tshow_id = db.Column(db.Integer, db.ForeignKey("Show.show_id"),
                           nullable=False)
    tvenue_id = db.Column(db.Integer, db.ForeignKey("Venue.venue_id"),
                           nullable=False)
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
    evenue_id = db.Column(db.Integer, db.ForeignKey("Venue.venue_id"),
                            nullable=False)
    eshow_id = db.Column(db.Integer, db.ForeignKey("Show.show_id"),
                           nullable=False)
    
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

db.create_all()
@app.route('/')
def blogin():
    return render_template('blogin.html')

@app.route('/Adminlogin', methods=["GET", "POST"])
def adminlog():
    if request.method == "POST":
        usern = request.form["username"]
        upass = request.form["pass"]
        if(usern=='nils' and upass=='nil123'):
            session["username"] = usern
            return redirect('/adminindex')
        else:
            return render_template('login.html',u='Admin',q='username or password is incorrect')
    return render_template('login.html',u='Admin')

@app.route('/Userlogin', methods=["GET", "POST"])
def userlog():
    if request.method == "POST":
        log = request.form["lo"]
        usern = request.form["username"]
        upass = request.form["pass"]
        if log=='Register':
            if User.query.filter(User.Username == usern).first():
                return render_template("login.html",u='User',q='username is already exists,Please try another username')
            s = User(Username=usern, password=upass)
            db.session.add(s)
            db.session.commit()
            session["username"] = usern
            return render_template('uindex.html',usern=usern)

        else:
            if User.query.filter(User.Username == usern and User.password==upass).first():
                session["username"] = usern

                return redirect('/userindex')
            else:
                return render_template("login.html",u='User',q='username or password is incorrect')
    return render_template('login.html',u='User')

@app.route('/adminindex')
def aindex():
    if "username" not in session:
        return redirect('/adminlogin')
    data = Venue.query.all()
    show = Show.query.all()
    return render_template('aindex.html',show=show,venue=data,usern=session["username"])

@app.route('/userindex')
def uindex():
    if "username" not in session:
        return redirect('/Userlogin')
    data = Venue.query.all()
    show = Show.query.all()
    tickets = Tickets.query.all()
    return render_template('uindex.html',show=show,venue=data,tickets=tickets,usern=session["username"])

@app.route('/search')
def search():
    if "username" not in session:
        return redirect('/Userlogin')
    query = request.args.get('q')
    venue_list = Venue.query.filter(or_(Venue.location.ilike(f'%{query}%'), Venue.place.ilike(f'%{query}%'))).all()
    show_list = Show.query.all()

    return render_template('uindex.html', venue=venue_list, show=show_list, usern=session["username"],qq=query)


@app.route('/logout/<string:q>/<string:user>')
def logout(user,q):
    session.pop("username", None)
    if q=='u':
        return redirect('/Userlogin')
    return redirect('/Adminlogin')

@app.route('/addvenue', methods=["GET", "POST"])
def addvenue():
    if "username" not in session:
        return redirect('/adminlogin')
    if request.method == "POST":
        name = request.form["venuename"]
        place = request.form["place"]
        location = request.form["location"]
        capacity = request.form["capacity"]
        if Venue.query.filter(Venue.name == name).first():
            return render_template('venueform.html',usern=session["username"],q='This vanue is already created.')
        s = Venue(name=name, place=place,location=location,capacity=capacity)
        db.session.add(s)
        db.session.commit()
        return redirect('adminindex')
    return render_template('venueform.html',usern=session["username"])

@app.route('/addshow/<string:venuee>', methods=["GET", "POST"])
def addshow(venuee):
    if "username" not in session:
        return redirect('/adminlogin')
    if request.method == "POST":
        name = request.form["showname"]
        rating = request.form["rating"]
        time1 = request.form["timing1"]
        time = datetime.strptime(time1, '%H:%M')
        time1 = time.strftime('%I:%M %p')
        time2 = request.form["timing2"]
        time = datetime.strptime(time2, '%H:%M')
        time2 = time.strftime('%I:%M %p')
        timing=str(time1)+' - '+str(time2)
        tags = request.form["tags"]
        price = request.form["price"]
        venue = Venue.query.filter_by(name=venuee).first()
        show = Show(name=name,rating=rating,timing=timing,tags=tags,ticketprice=price)

       # check if a show with the same name exists for the same venue
        if not Show.query.filter_by(name=name).join(Enroll).filter(Enroll.evenue_id == venue.venue_id).first():
            db.session.add(show)
            db.session.commit()
            # add the show to the venue's shows collection
            venue.shows.append(show)
            db.session.commit()
            return redirect('/adminindex')
        return render_template('showform.html',usern=session["username"],q='This show is already created.')     
        
    return render_template('showform.html',usern=session["username"],ve=venuee)

@app.route('/book/<string:userr>/<int:venuee>/<int:showw>', methods=["GET", "POST"])
def book(userr,venuee,showw):
    show=Show.query.filter_by(show_id=showw).first()
    venue=Venue.query.filter_by(venue_id=venuee).first()
    user=User.query.filter_by(Username=userr).first()
    if "username" not in session:
        return redirect('/Userlogin')
    # Get the data from the request
    user_id = user.user_id
    show_id = show.show_id
    venue_id = venue.venue_id
    sold_tickets = db.session.query(db.func.sum(Tickets.number_of_tickets)).filter_by(tshow_id=show_id).scalar()
    if sold_tickets is None:
            sold_tickets = 0
    available_tickets=venue.capacity - sold_tickets
    if request.method == "POST":
        num_tickets = request.form['number_of_tickets']

        # Check if the venue has enough capacity
        if venue.capacity < int(num_tickets):
            return render_template('book.html',usern=session["username"],ve=venue,show=show,available_tickets=available_tickets,q='Sorry, the venue does not have enough capacity.')

        # Check if there are enough tickets available
        if available_tickets - int(num_tickets) < 0 :
            return render_template('book.html',usern=session["username"],ve=venue,show=show,available_tickets=available_tickets,q='Sorry, there are not enough tickets available.')

        # Book the ticket
        ticket = Tickets(tuser_id=user_id, tshow_id=show_id, tvenue_id=venue_id, number_of_tickets=num_tickets)
        db.session.add(ticket)
        db.session.commit()

        return redirect('/booking/'+user.Username)
    return render_template('book.html',usern=session["username"],ve=venue,show=show,available_tickets=available_tickets)

@app.route('/booking/<string:user>', methods=["GET", "POST"])
def booking(user):
    if "username" not in session:
        return redirect('/Userlogin')
    user=User.query.filter_by(Username=user).first()
    tickets = Tickets.query.filter_by(tuser_id=user.user_id).join(Show, Tickets.tshow_id==Show.show_id).join(Venue, Tickets.tvenue_id==Venue.venue_id).add_columns(Venue.name, Show.name, Show.timing, Tickets.ticket_id).all()

    return render_template('booking.html',usern=session["username"],tickets=tickets,user=user) 

@app.route('/profile/<string:user>', methods=["GET", "POST"])
def profile(user):
    if "username" not in session:
        return redirect('/Userlogin')
    new = User.query.filter_by(Username=user).first()
    if request.method == "POST":
        if User.query.filter_by(Username=request.form["user"]).first() and new.Username != request.form["user"]:
            return render_template('profile.html',user=new,q='This username is already exists. Please choose other.')

        new.Username = request.form["user"]
        new.password = request.form["pass"]
        new.email = request.form["email"]
        new.mobile = request.form["mobile"]

        db.session.commit()
        session["username"] = new.Username
        session.pop("user", None)
        return redirect('/userindex')
    return render_template('profile.html',user=new)

@app.route('/summary')
def summary():
    if "username" not in session:
        return redirect('/adminlogin')
    #-----------------------------------fig1-----------------------------------------------------------
    
    venues = Venue.query.all()
    venue_names = [venue.name for venue in venues]
    venue_show_counts = [len(venue.shows) for venue in venues]

    # Use Matplotlib to create the chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(venue_names, venue_show_counts,color='black')
    ax.set_xlabel("Venue",fontsize=18, fontweight='bold', color='#03a9f4')
    ax.set_ylabel("Number of Shows",fontsize=18, fontweight='bold', color='#03a9f4')
    ax.set_title("Shows per Venue",fontsize=22, fontweight='bold', color='#03a9f4')
    ax.tick_params(axis='x',labelsize=12, colors='white') 
    ax.tick_params(axis='y',labelsize=12, colors='white')
    fig.patch.set_facecolor('#333')
    ax.patch.set_facecolor('#555')
    if len(venue_names) > 10:
        plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    filename1 = "static/images/venue_chart1.png"
    fig.savefig(filename1)

    #-----------------------------------fig2-----------------------------------------------------------

    shows = Show.query.all()
    show_names = []
    show_tickets_sold = []

    for show in shows:
        
        total_tickets_sold = sum(ticket.number_of_tickets for ticket in show.tickets)   
        show_names.append(show.name)
        show_tickets_sold.append(total_tickets_sold)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(show_names, show_tickets_sold,color='black')
    ax.set_xlabel("Show",fontsize=18, fontweight='bold', color='#03a9f4')
    ax.set_ylabel("Number of Tickets",fontsize=18, fontweight='bold', color='#03a9f4')
    ax.set_title("Tickets Sold per Show",fontsize=22, fontweight='bold', color='#03a9f4')
    ax.tick_params(axis='x',labelsize=12, colors='white') 
    ax.tick_params(axis='y', labelsize=12,colors='white')
    if len(show_names) > 10:
        plt.xticks(rotation=45, ha='right')
    fig.patch.set_facecolor('#333')
    ax.patch.set_facecolor('#555')
    plt.tight_layout()
    filename2 = "static/images/tickets_chart2.png"
    fig.savefig(filename2)
    #-----------------------------------fig3-----------------------------------------------------------

    show_names = []
    show_revenues = []

    for show in shows:
        total_revenue = 0
        for ticket in show.tickets:
            total_revenue += ticket.number_of_tickets * show.ticketprice

        show_names.append(show.name)
        show_revenues.append(total_revenue)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(show_names, show_revenues,color='black')
    ax.set_xlabel("Show",fontsize=18, fontweight='bold', color='#03a9f4')
    ax.set_ylabel("Revenue",fontsize=18, fontweight='bold', color='#03a9f4')
    ax.set_title("Revenue per Show",fontsize=22, fontweight='bold', color='#03a9f4')
    ax.tick_params(axis='x',labelsize=12, colors='white') 
    ax.tick_params(axis='y',labelsize=12, colors='white')
    fig.patch.set_facecolor('#333')
    ax.patch.set_facecolor('#555')
    if len(show_names) > 10:
        plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    filename3 = "static/images/chart3.png"
    fig.savefig(filename3)
    return render_template("summary.html", chart1=filename1, chart2=filename2, chart3=filename3,usern=session["username"])

@app.route('/delete/<string:venue>/<string:name>')
def delete(name,venue):
    if "username" not in session:
        return redirect('/adminlogin')
    if venue=='venue':
        s = Venue.query.filter_by(name=name).first()
        shows = Show.query.join(Enroll).join(Venue).filter(Venue.name == name).all()
        for show in shows:
            tickets = Tickets.query.filter_by(tshow_id=show.show_id).all()
            for ticket in tickets:
                db.session.delete(ticket)
            db.session.commit()
            db.session.delete(show)
        db.session.commit()
        

    else:
        s = Show.query.join(Enroll).join(Venue).filter(Show.name == name, Venue.name == venue).first()
        tickets = Tickets.query.filter_by(tshow_id=s.show_id).all()
        for ticket in tickets:
            db.session.delete(ticket)
        db.session.commit()
    db.session.delete(s)
    db.session.commit()
    return redirect('/adminindex')

@app.route("/edit/<string:venue>/<string:name>", methods=["GET", "POST"])
def edit(name,venue):
    if "username" not in session:
        return redirect('/adminlogin')
    if venue=='venue':
        s = Venue.query.filter_by(name=name).first()
        if request.method == "POST":
            s.capacity = request.form["capacity"]
            db.session.commit()
            return redirect('/adminindex')
        return render_template('venueform.html',usern=session["username"],s=s)
    else:
        s = Show.query.join(Enroll).join(Venue).filter(Show.name == name, Venue.name == venue).first()
        if request.method == "POST":
            s.rating = request.form["rating"]
            time1 = request.form["timing1"]
            time = datetime.strptime(time1, '%H:%M')
            time1 = time.strftime('%I:%M %p')
            time2 = request.form["timing2"]
            time = datetime.strptime(time2, '%H:%M')
            time2 = time.strftime('%I:%M %p')
            s.timing=str(time1)+' - '+str(time2)
            s.tags = request.form["tags"]
            s.ticketprice = request.form["price"]
            db.session.commit()
            return redirect('/adminindex')
        time1 = s.timing.split(' - ')[0]
        time = datetime.strptime(time1, '%I:%M %p')  # convert time string to datetime object
        time1 = time.strftime('%H:%M')
        time2 = s.timing.split(' - ')[1]
        time = datetime.strptime(time2, '%I:%M %p')  # convert time string to datetime object
        time2 = time.strftime('%H:%M')
        
        return render_template('showform.html',usern=session["username"],ve=venue,show=s,time1=time1,time2=time2)
    
@app.route("/rate/<int:user>/<string:venue>/<string:show>", methods=["GET", "POST"])
def rate(venue,show,user):
    if "username" not in session:
        return redirect('/adminlogin')
    s=Show.query.join(Enroll).join(Venue).filter(Show.name == show, Venue.name == venue).first()
    v=Venue.query.filter_by(name=venue).first()
    u = User.query.filter_by(user_id=user).first()
    r=Rating.query.filter_by(user_id=user, show_id=s.show_id, venue_id=v.venue_id).first()
    if r:
        if request.method == "POST":
            r.show_rating = request.form["show_rating"]
            r.show_comment = request.form["show_comment"]
            r.venue_rating = request.form["venue_rating"]
            r.venue_comment = request.form["venue_comment"]
            db.session.commit()
            return redirect(f'/booking/{u.Username}')
        return render_template('rate.html',usern=session["username"],s=s,v=v,r=r,u=u)

    if request.method == "POST":
        show_rating = request.form["show_rating"]
        show_comment = request.form["show_comment"]
        venue_rating = request.form["venue_rating"]
        venue_comment = request.form["venue_comment"]

        rate = Rating(user_id=user, show_id=s.show_id, venue_id=v.venue_id, show_rating=show_rating,show_comment=show_comment,venue_rating=venue_rating,venue_comment=venue_comment)
        db.session.add(rate)
        db.session.commit()
        return redirect(f'/booking/{u.Username}')
    
    return render_template('rate.html',usern=session["username"],s=s,v=v,u=u)
    

if __name__ == '__main__':
    
    app.run(debug=True)