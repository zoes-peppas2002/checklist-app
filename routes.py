from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from run import app
from extensions import db
from models_def import User

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Λάθος στοιχεία σύνδεσης')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"[DEBUG] Ρόλος χρήστη: {current_user.role}")
    return render_template(
        'dashboard.html',
        username=current_user.username,
        role=current_user.role
    )


    
    
    
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return "Απαγορεύεται η πρόσβαση", 403

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Υπάρχει ήδη αυτό το username.')
            return redirect(url_for('admin_panel'))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Ο χρήστης δημιουργήθηκε επιτυχώς.')
        return redirect(url_for('admin_panel'))

    users = User.query.all()
    return render_template('admin.html', users=users)

