from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import yagmail
# Sending emails from Gmail with Python: https://www.tutorialspoint.com/python/python_sending_email.htm
# Python Documentation for sending HTML emails with alternative plain text form: 
# https://docs.python.org/3.3/library/email-examples.html
import smptlib


#  https://docs.python.org/3/library/datetime.html
#  http://www.pythonforbeginners.com/basics/python-datetime-time-examples
import time
import datetime

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

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
    """Here we need to put in a table displaying the inventory!"""
    inv = db.execute("SELECT * FROM equipment")
    return render_template("landing.html", inv = inv)

def send_email(sender, dest, subject, message):
    try:
        smptObj = smtplib.SMTP('smtp.gmail.com')
        smtpObj.sendmail(sender, dest, message)
        
   


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
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM photogs WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["role"] = rows[0]["usertype"]
        session["first"] = rows[0]["first"]
        session["middle"] = rows[0]["middle"]
        session["last"] = rows[0]["last"]

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

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
            
        elif not request.form.get("password2"):
            return apology("please re-enter password")
        if request.form.get("password") != request.form.get("password2"):
            return apology("passwords do not match")
            
        else:  
            # add user to the database
            rows = db.execute("INSERT INTO photogs (username, first, middle, last, phone, email, password, usertype, guard) VALUES (:username, :first, :middle, :last, :phone, :email, :password, :usertype, :guard)", username=request.form["username"], first=request.form["first"], middle=request.form["middle"], last=request.form["last"], phone=request.form["phone"], email=request.form["email"], password=pwd_context.encrypt(request.form["password"]), usertype=request.form["usertype"], guard=request.form["guard"])
    
            # remember which user has logged in
            session["user_id"] = rows
            session["role"] = request.form["usertype"]
            session["first"] = request.form["first"]
            session["middle"] = request.form["middle"]
            session["last"] = request.form["last"]
    
            # redirect user to home page
            return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


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
        
        order = db.execute("INSERT INTO orders (user_id, pitch_desc, execname, complete) VALUES (:user_id, :pitch, :ex, 'FALSE')", user_id=session['user_id'], ex=request.form['ex'], pitch=request.form['pitch'])
        if request.form.get("camera"):
            db.execute("UPDATE orders SET camera='1' WHERE order_id=:order_id", order_id=order)
        if request.form.get("lens"):
            db.execute("UPDATE orders SET lens='1' WHERE order_id=:order_id", order_id=order)
        if request.form.get("mic"):
            db.execute("UPDATE orders SET mic='1' WHERE order_id=:order_id", order_id=order)
        if request.form.get("tripod"):
            db.execute("UPDATE orders SET lens='1' WHERE order_id=:order_id", order_id=order)
        exec_email = db.execute("SELECT email FROM photogs WHERE id=:execname", execname=request.form.get("ex"))
        print("{}".format(exec_email[0]['email']))
        # mail feature from https://github.com/kootenpv/yagmail
        # we want to abstract this out to make it useable in other contexts
        # also hard-coding passwords into source code is sub-optimal practice so I'll put them in a table in the database!
        # send_email('crimsonmultiemail@gmail.com', 'crimsonmultiemail123', 'megan.ross@thecrimson.com', 'hello', 'this is an email')
        
        return redirect(url_for("index"))

@app.route("/fulfill", methods=["GET", "POST"])
@login_required
def fulfill():
    if request.method == "GET":
        if session["role"] == "Exec":
            # Pull out all the orders that have been sent to this user
            # http://www.w3schools.com/sql/sql_join_inner.asp
            order = db.execute("SELECT orders.order_id, orders.pitch_desc, photogs.first, photogs.last, photogs.phone, orders.receivedat, orders.camera, orders.lens FROM orders INNER JOIN photogs ON orders.user_id = photogs.id AND orders.execname = :exec_id", exec_id=session['user_id'])
            return render_template("fulfill.html", order=order)
        else:
            return apology("Access Denied")
        

@app.route("/pickup", methods=["GET", "POST"])
@login_required
def pickup():
    if request.method == "GET":
        # FINISH THIS
        order_id = request.args.get("q")
        order = db.execute("SELECT * FROM orders WHERE order_id = :order_id", order_id=order_id)
        return render_template("pickup.html", order=order)
        
@app.route("/signout", methods=["GET", "POST"])
@login_required
def signout():
    if session["role"] != "Exec":
        return apology("Access Denied")
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
            
            if request.form.get("camera"):
                cam_code = request.form['camera']
                db.execute("UPDATE equipment SET status='0' WHERE code = :code", code=cam_code)
            if request.form.get[("lens"):
                lens_code = request.form['lens']
                db.execute("UPDATE equipment SET status='0' WHERE code = :code", code=lens_code)
            if request.form.get("mic"):
                mic_code = request.form['mic']
                db.execute("UPDATE equipment SET status='0' WHERE code = :code", code=mic_code)
            if request.form["tripod"] != None:
                tri_code = request.form.get("tripod"):
                db.execute("UPDATE equipment SET status='0' WHERE code = :code", code=tri_code)    
            # Format time correctly for SQL: http://stackoverflow.com/questions/16359143/inserting-datetime-into-mysql-db
            db.execute("INSERT INTO orders (user_id, pitch_desc, execname, camera, lens, mic, tripod, pickedupat) VALUES (:user, :pitch, :ex, :camera, :lens, :mic, :tri, :time)", user = session["user_id"], pitch=request.form["pitch"], ex = session["user_id"], camera = cam_code, lens = lens_code, mic=mic_code, tri = tri_code, time = time.strftime('%Y-%m-%d %H:%M:%S'))
            return redirect(url_for("index"))
        
@app.route("/manageinv", methods=["GET"])
@login_required
def manageinv():
    if session["role"] != "Exec":
        return apology("Access Denied")
    else:
        if request.method == "GET":
            inv_list = db.execute("SELECT * FROM equipment")
            return render_template("manageinv.html", inv_list=inv_list)
            

@app.route("/addeq", methods=["GET","POST"])
@login_required
def addeq():
    if session["role"] != "Exec":
        return apology("Access Denied")
    else:
        if request.method == "GET":
            return render_template("addeq.html")
            
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
        
