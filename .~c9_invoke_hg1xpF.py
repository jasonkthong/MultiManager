import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir

# Sending emails from Gmail with Python: https://www.tutorialspoint.com/python/python_sending_email.htm
# Python Documentation for sending HTML emails with alternative plain text form: 
# https://docs.python.org/3.3/library/email-examples.html
import smtplib


#  https://docs.python.org/3/library/datetime.html
#  http://www.pythonforbeginners.com/basics/python-datetime-time-examples
import time
import datetime

from helpers import *

# configure application
# http://stewartjpark.com/Flask-JSGlue/
app = Flask(__name__)


# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///inventory.db")

@app.route("/")
@login_required
def index():
    inv = db.execute("SELECT * FROM equipment")
    people = db.execute("SELECT * FROM photogs")
    return render_template("landing.html", inv=inv, people=people)
    

# https://www.tutorialspoint.com/python/python_sending_email.htm
# Info on securely sending mail: https://docs.python.org/3/library/smtplib.html
# https://docs.python.org/3/library/smtplib.html#smtplib.SMTPAuthenticationError
def send_email(sender, destination, message):
    send = sender[0]['email']
    sender_pass = sender[0]['password']
    dest = destination[0]['email']
    msg = message
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(send, sender_pass)
        try:
            server.sendmail(send, dest, msg)
        except smtplib.SMTPSenderRefused:
            return False
    except smtplib.SMTPAuthenticationError:
        return False


@app.route("/admin", methods=["GET", "POST"])
@login_required 
def admin():
    return render_template("admin.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            flash("You must input your username.")
            return render_template("login.html")

        # ensure password was submitted
        elif not request.form.get("password"):
            flash("You must input your password.")
            return render_template("login.html")


        # query database for username
        rows = db.execute("SELECT * FROM photogs WHERE username = :username", username=request.form.get("username").lower())

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]):
            flash("Invalid username and/or password.")
            return render_template("login.html")


        # remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["role"] = rows[0]["usertype"]
        session["first"] = rows[0]["first"]
        session["middle"] = rows[0]["middle"]
        session["last"] = rows[0]["last"]
        session["order"] = None
        session["code"] = None

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

    

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    if request.method == "POST":
        users = db.execute("SELECT username FROM photogs")
        usernames = set()
        for item in users:
            usernames.add(item['username'])
       
        # ensure username was submitted
        if not request.form.get("username"):
            flash("Please input a username.")
            return render_template("register.html")

        elif request.form["username"] in usernames:
            flash("Username already exists.")
            return render_template("register.html")
        
        if request.form.get("password") != request.form.get("password2"):
            flash("Passwords do not match.")
            return render_template("register.html")
            
        else:  
            # add user to the database
            rows = db.execute("INSERT INTO photogs (username, first, middle, last, phone, email, password, usertype, guard, position) VALUES (:username, :first, :middle, :last, :phone, :email, :password, :usertype, :guard, :position)", username=request.form["username"].lower(), first=request.form["first"], middle=request.form["middle"], last=request.form["last"], phone=request.form["phone"], email=request.form["email"], password=pwd_context.encrypt(request.form["password"]), usertype=request.form["usertype"], guard=request.form["guard"], position=request.form["position"])
    
            # remember which user has logged in
            session["user_id"] = rows
            session["role"] = request.form["usertype"]
            session["first"] = request.form["first"]
            session["middle"] = request.form["middle"]
            session["last"] = request.form["last"]
            session["order"] = None
            session["code"] = None
            
            # redirect user to home page
            return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", error=None)





@app.route("/order", methods=["GET", "POST"])
@login_required
def order():
    if request.method == "GET":
        if session["role"] != "Junior":
            return redirect(url_for("signout"))
        else:
            exec_list = db.execute("SELECT first, last, id FROM photogs WHERE usertype=:usertype", usertype='Exec')
            return render_template("order.html", exec_list=exec_list)
        
    elif request.method == "POST":
        # Setting an email subject: http://stackoverflow.com/questions/7232088/python-subject-not-shown-when-sending-email-using-smtplib-module
        order = db.execute("INSERT INTO orders (user_id, pitch_desc, execname) VALUES (:user_id, :pitch, :ex)", user_id=session['user_id'], ex=request.form['ex'], pitch=request.form['pitch'])
        if request.form.get("camera"):
            db.execute("UPDATE orders SET camera='1' WHERE order_id=:order_id", order_id=order)
        if request.form.get("lens"):
            db.execute("UPDATE orders SET lens='1' WHERE order_id=:order_id", order_id=order)
        if request.form.get("mic"):
            db.execute("UPDATE orders SET mic='1' WHERE order_id=:order_id", order_id=order)
        if request.form.get("tripod"):
            db.execute("UPDATE orders SET tripod='1' WHERE order_id=:order_id", order_id=order)
        if request.form.get("neededby"):
            db.execute("UPDATE orders SET neededby=:neededby WHERE order_id=:order_id", order_id=order, neededby=request.form['neededby'])
        you = db.execute("SELECT email FROM photogs WHERE id=:execname", execname=request.form.get("ex"))
        me = db.execute("SELECT * FROM emailinfo WHERE email = 'crimsonmultiemail@gmail.com'")
        message = "SUBJECT: Equipment Request\n\n You have a new equipment request from {} {}. The equipment is needed by {}. Please visit http://crimson-thong1.c9users.io/fulfill to see & fulfill the request.".format(session['first'], session['last'], request.form.get("neededby"))
        send_email(me, you, message)
        flash("Order Successful")
        return redirect(url_for("index"))

@app.route("/fulfill", methods=["GET", "POST"])
@login_required
def fulfill():
    if request.method == "GET":
        if session["role"] == "Exec":
            # Pull out all the orders that have been sent to this user
            # http://www.w3schools.com/sql/sql_join_inner.asp
            order = db.execute("SELECT orders.order_id, orders.pitch_desc, photogs.first, photogs.last, photogs.phone, orders.receivedat, orders.camera, orders.mic, orders.tripod, orders.lens, orders.neededby FROM orders INNER JOIN photogs ON orders.user_id = photogs.id AND orders.execname = :exec_id AND orders.fulfilled =:value", exec_id=session['user_id'], value=0)
            return render_template("fulfill.html", order=order)
        else:
            flash("Access Denied")
            return redirect(url_for("index"))

        

@app.route("/moditem", methods=['GET', 'POST'])
@login_required
def moditem():
    if request.method=="GET":
        if session["role"] == "Exec":
            code = request.args.get("q")
            session["code"] = code
            equipment = db.execute("SELECT * FROM equipment WHERE code=:code", code=code)
            return render_template("moditem.html", equipment=equipment)
        else:
            flash("Access Denied")
            return redirect(url_for("index"))

    else:
        code = session["code"]
        if request.form.get("name"):
                newname = request.form['name']
                db.execute("UPDATE equipment SET name=:newname WHERE code=:code", code=code, newname=newname)
        if request.form.get("notes"):
            newnotes = request.form['notes']
            db.execute("UPDATE equipment SET notes=:newnotes WHERE code=:code", code=code, newnotes=newnotes)
        if request.form.get("type"):
            newtype = request.form['type']
            db.execute("UPDATE equipment SET type=:newtype WHERE code=:code", code=code, newtype=newtype)
        if request.form.get("status"):  
            newstatus = request.form['status']
            db.execute("UPDATE equipment SET status=:newstatus WHERE code=:code", code=code, newstatus=newstatus)
        return redirect(url_for("index"))


        
@app.route("/signout", methods=["GET", "POST"])
@login_required
def signout():
    if session["role"] != "Exec":
        flash("Access Denied")
        return redirect(url_for("index"))

    else:
        if request.method == "GET":
            cameras = db.execute("SELECT * FROM equipment WHERE type = 'camera' AND status = '1'")
            lens = db.execute("SELECT * FROM equipment WHERE type = 'lens' AND status = '1'")
            tripod = db.execute("SELECT * FROM equipment WHERE type = 'tripod' AND status = '1'")
            mic = db.execute("SELECT * FROM equipment WHERE type = 'lens' AND status = '1'")
            return render_template("signout.html", cameras=cameras, lens=lens, mic=mic, tripod=tripod)
            
        else:
            # TO DO: REWRITE AS A FOR LOOP WITH A DICTIONARY (unsure how to right now)
            cam_code = None
            lens_code = None
            mic_code = None
            tri_code = None
            order_id = db.execute("INSERT INTO orders (user_id, pitch_desc, execname, pickedupat) VALUES (:user, :pitch, :ex, :time)", user = session["user_id"], pitch=request.form["pitch"], ex = session["user_id"], time = time.strftime('%Y-%m-%d %H:%M:%S'))
            if request.form.get("camera"):
                cam_code = request.form['camera']
                db.execute("UPDATE equipment SET status='0', order_id=:order_id WHERE code = :code", code=cam_code, order_id=order_id)
            if request.form.get("lens"):
                lens_code = request.form['lens']
                db.execute("UPDATE equipment SET status='0', order_id=:order_id WHERE code = :code", code=lens_code, order_id=order_id)
            if request.form.get("mic"):
                mic_code = request.form['mic']
                db.execute("UPDATE equipment SET status='0', order_id=:order_id WHERE code = :code", code=mic_code, order_id=order_id)
            if request.form.get("tripod"):
                tri_code = request.form["tripod"]
                db.execute("UPDATE equipment SET status='0', order_id=:order_id WHERE code = :code", code=tri_code, order_id=order_id)    
            # Format time correctly for SQL: http://stackoverflow.com/questions/16359143/inserting-datetime-into-mysql-db
            db.execute("UPDATE orders SET camera=:camera, lens=:lens, mic=:mic, tripod=:tri WHERE order_id=:order_id", camera = cam_code, lens = lens_code, mic=mic_code, tri = tri_code, order_id=order_id)
            return redirect(url_for("index"))
        

            

@app.route("/addeq", methods=["GET","POST"])
@login_required
def addeq():
    if request.method == "GET":
        if session["role"] != "Exec":
            flash("Access Denied")
            return redirect(url_for("index"))
    
        else:
            return render_template("addeq.html")
    else:
        db.execute("INSERT INTO equipment (code, name, type, notes, status) VALUES (:code, :name, :typ, :notes, :status)", code=request.form.get("code"), name=request.form.get("name"), typ=request.form.get("type"), notes=request.form.get("notes"), status='1')
        flash("Item Added")
        return redirect(url_for("index"))
        
            
@app.route("/orderterms")
@login_required
def orderterms():
    if request.method == "GET":
        return render_template("orderterms.html")
    else:
        return render_template("orderterms.html")
        
@app.route("/registerterms")
def registerterms():
    if request.method == "GET":
        return render_template("registerterms.html")
    else:
        return render_template("registerterms.html")
        
        
@app.route("/fulfillment", methods=['GET', 'POST'])
def fulfillment():
    if request.method == "GET":
        if session["role"] == "Exec":
            order_id = request.args.get("q")
            order = db.execute("SELECT * FROM orders WHERE order_id = :order_id", order_id=order_id)
            if order[0]["fulfilled"] != 1:
                cameras = db.execute("SELECT * FROM equipment WHERE type = 'camera' AND status = '1'")
                lenses = db.execute("SELECT * FROM equipment WHERE type = 'lens' AND status = '1'")
                tripods = db.execute("SELECT * FROM equipment WHERE type = 'tripod' AND status = '1'")
                mics = db.execute("SELECT * FROM equipment WHERE type = 'mic' AND status = '1'")
                lockers = db.execute("SELECT * FROM lockers WHERE status = '1'")
                session["order"] = order[0]
                return render_template("fulfillment.html", order=order, cameras=cameras, lenses=lenses, tripods=tripods, mics=mics, lockers=lockers)
            else:
                return redirect(url_for("index"))
        else:
                flash("Access Denied")
                return redirect(url_for("index"))

    else:
        if session["order"] != None:
            order = session["order"]
            order_id = order["order_id"]
            comper_id = order["user_id"]
            if request.form.get("camera"):
                db.execute("UPDATE orders SET camera=:cam WHERE order_id=:order_id", order_id=order_id, cam=request.form['camera'])
                db.execute("UPDATE equipment SET status=:value, order_id=:order_id WHERE code=:cam", value="0", order_id=order_id, cam=request.form['camera'])
            if request.form.get("lens"):
                db.execute("UPDATE orders SET lens=:lens WHERE order_id=:order_id", order_id=order_id, lens=request.form['lens'])
                db.execute("UPDATE equipment SET status=:value, order_id=:order_id WHERE code=:lens", value="0", order_id=order_id, lens=request.form['lens'])
            if request.form.get("mic"):
                db.execute("UPDATE orders SET mic=:mic WHERE order_id=:order_id", order_id=order_id, mic=request.form['mic'])
                db.execute("UPDATE equipment SET status=:value, order_id=:order_id WHERE code=:mic", value="0", order_id=order_id, mic=request.form['mic'])
            if request.form.get("tripod"):
                db.execute("UPDATE orders SET tripod=:tri WHERE order_id=:order_id", order_id=order_id, tri=request.form['tri']) 
                db.execute("UPDATE equipment SET status=:value, order_id=:order_id WHERE code=:tri", value="0", order_id=order_id, tri=request.form['tripod'])
            if request.form.get("locker"):
                locker = request.form["locker"]
                db.execute("UPDATE lockers SET status='0' WHERE name=:name", name=locker)
            db.execute("UPDATE orders SET fulfilled=:value, inlockerat=:time, lockernum=:lockernum WHERE order_id=:order_id", order_id=order_id, value='1', time=time.strftime('%Y-%m-%d %H:%M:%S'), lockernum=request.form.get("locker"))
            you = db.execute("SELECT email FROM photogs WHERE id=:comper_id", comper_id=comper_id)
            me = db.execute("SELECT * FROM emailinfo WHERE email = 'crimsonmultiemail@gmail.com'")
            message = "SUBJECT: Equipment Request Fulfilled\n\n{} {} has left equipment for you in Locker {}.\nPlease visit http://crimson-thong1.c9users.io/myorders to confirm pickup".format(session['first'], session['last'], locker)
            send_email(me, you, message)
            
            session["order"] = None
            return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
            
@app.route("/myorders", methods=["GET", "POST"])
@login_required
def myorders():
    orders = db.execute("SELECT * FROM orders WHERE user_id=:user AND completed = '0'", user=session['user_id'])
    return render_template("myorders.html", orders=orders)


@app.route("/pickup", methods=["GET"])
@login_required
def pickup():
    if request.method == "GET":
        order_id = request.args.get("q")
        db.execute("UPDATE orders SET pickedup='1', pickedupat=:time WHERE order_id = :order_id", order_id=order_id, time = time.strftime('%Y-%m-%d %H:%M:%S'))
        flash("Picked Up!")
        return redirect(url_for("index"))

    
@app.route("/return", methods=["GET"])
@login_required
def returned():
    if request.method == "GET":
        order_id = request.args.get("q")
        db.execute("UPDATE orders SET returned='1', returnedat=:time WHERE order_id = :order_id", order_id=order_id, time = time.strftime('%Y-%m-%d %H:%M:%S'))
        flash("Returned!")
        return redirect(url_for("index"))
  
@app.route("/dayslot", methods=["GET"])
@login_required
def dayslot():
        if request.method == 'GET':
            if session['role'] != 'Exec':
                flash("Access Denied!")
                return redirect(url_for("index"))
            else:
                equipment = db.execute("SELECT photogs.id, photogs.first, photogs.middle, photogs.last, photogs.phone, orders.order_id, orders.user_id, equipment.code, equipment.name, equipment.type, equipment.order_id, equipment.status FROM orders INNER JOIN equipment ON orders.order_id = equipment.order_id INNER JOIN photogs ON orders.user_id = photogs.id")
                lockers = db.execute("SELECT * FROM lockers WHERE status='0'")
                openorders = db.execute("SELECT orders.order_id, photogs.first, photogs.middle, photogs.last, orders.pitch_desc FROM orders INNER JOIN photogs ON photogs.id = orders.user_id WHERE orders.completed='0'")
                return render_template("dayslot.html", equipment=equipment, lockers=lockers, openorders=openorders)
            
@app.route("/mainlocker", methods=["GET"])
@login_required
def mainlocker():
        if request.method == 'GET':
            if session['role'] != 'Exec':
                flash("Access Denied!")
                return redirect(url_for("index"))
            else:
                code = request.args.get("q")
                db.execute("UPDATE equipment SET status='1', order_id = '0' WHERE code=:code", code=code)
                flash("Item Returned To Main Locker")
                return redirect(url_for("dayslot"))
                
                
@app.route("/freeup", methods=["GET"])
@login_required
def freeup():
    if request.method == 'GET':
        if session['role'] != 'Exec':
            flash("Access Denied")
            return redirect(url_for("index"))
        else:
            q = request.args.get("q")
            db.execute("UPDATE lockers SET status='1' WHERE name=:q", q=q)
            flash("Locker Freed Up")
            return redirect(url_for("dayslot"))
            
@app.route("/complete", methods=["GET"])
@login_required
def complete():
    if request.method == 'GET':
        if session['role'] != 'Exec':
            flash("Access Denied")
            return redirect(url_for("index"))
        else:
            q = request.args.get("q")
            db.execute("UPDATE orders SET completed='1', completedat=:time WHERE order_id=:q", q=q, time=time.strftime('%Y-%m-%d %H:%M:%S'))
            flash("Order Completed")
            return redirect(url_for("dayslot"))
            
@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    if request.method == 'GET':
        if session['role'] != 'Exec':
            flash("Access Denied")
            return redirect(url_for("index"))
        else:
            orders = db.execute("SELECT orders.user_id, orders.pitch_desc, orders.camera, orders.mic, orders.lens, orders.tripod, orders.pickedupat, orders.returnedat, orders.completedat, orders.lockernum, photogs.first, photogs.middle, photogs.last FROM orders INNER JOIN photogs ON photogs.id = orders.user_id")
            return render_template("history.html", orders=orders)
            


@app.route("/modprof", methods=['GET', 'POST'])