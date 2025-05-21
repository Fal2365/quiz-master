from flask import current_app as app, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models.model import db,User
from datetime import datetime

#verified
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


#verified
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        user = db.session.query(User).filter(User.username == email).first()
        

        if user:
            if check_password_hash(user.password, password):
                login_user(user) 
                if user.id == 1:
                    return redirect(url_for("admin_dashboard"))
                return redirect(url_for('dashboard'))
            else:
                return render_template("login.html", alert = "Password Not Matched...")
        else:
            return render_template("login.html", alert = "Not a Verified User...") 
           
    return redirect(url_for('dashboard'))


#verified
@app.route("/signup", methods = ['POST', 'GET'])
def signup(): 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conformpassword = request.form['conformpassword']
        full_name = request.form['fullname']
        qualification = request.form['qualification']
        dob_str = request.form['dob']
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        hashed_password = generate_password_hash(password)

        if any(not field for field in [username, password, conformpassword, full_name, qualification, dob_str]):
            return render_template("signup.html", alert="Enter All Fields...")

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template('signup.html', alert="User Already Exists...")
        
        elif password != conformpassword:
            return render_template('signup.html', alert = "Password and Conform Password are not same...")
        
        elif len(full_name) <=4:
            return render_template('signup.html', alert = "Enter a valid Full Name")

        else:
            new_user = User(username=username, password=hashed_password, full_name = full_name, qualification= qualification, dob= dob)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! ", "success")
            return render_template("signup.html")
        
    return render_template("signup.html")



#verified   
@app.route('/logout' , methods = ['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
