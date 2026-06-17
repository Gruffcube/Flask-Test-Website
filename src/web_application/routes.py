from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import random
import string
from . import database as db
from english_words import get_english_words_set



main_bp = Blueprint('main', __name__)



@main_bp.context_processor
def inject_global_data():
    session.permanent = True
    
    current_theme = session.get('theme', 'light')
    access_token = session.get('access_token', None)
    user_id = session.get('user_id', None)
    enlarged_text = session.get('enlarged_text', 'false')
    
    
    if user_id is not None:
        token_valid = db.verify_user_access_token(user_id, access_token)
        
        if not token_valid:
            print(user_id)
            print(access_token)
            
            session['user_id'] = None
            session['access_token'] = None
            
            user_id = None
            access_token = None
    
    
    if user_id is not None:
        fname, lname = db.get_first_last_name_from_user_id(user_id)
        full_name=f"{fname.title()} {lname.title()}"
    
    else:
        full_name = None
    
    
    
    return dict(theme=current_theme, access_token=access_token, full_name=full_name, enlarged_text=enlarged_text)



@main_bp.route('/')
def index():
    
    return render_template('index.html', random_jargon = random_jargon)



@main_bp.route('/animal-information')
def animals():
    return render_template('animal_info.html')



@main_bp.route('/user-survey', methods=['POST', 'GET'])
def survey():
    global past_survey_results_dict
    
    success = False
    
    if request.method == 'POST':
        fname = request.form.get('fname', 'N/A').strip().title()
        lname = request.form.get('lname', 'N/A').strip().title()
        age = request.form.get('age', 'N/A').strip()
        email = request.form.get('email', 'N/A').strip().lower()
        
        gender = request.form.get('gender', 'N/A').strip().lower()
        colour = request.form.get('colour', 'N/A').strip().lower()
        marital_status = request.form.get('marital_status', 'N/A').strip().lower()
        ethnicity = request.form.get('ethnicity', 'N/A').strip().title()
        
        
        padding = 30
        
        result_string = f"""
    {'First Name':<{padding}} | {fname:<{padding}}
    {'Last Name':<{padding}} | {lname:<{padding}}
    {'Age':<{padding}} | {age:<{padding}}
    {'Email':<{padding}} | {email:<{padding}}
    
    {'Gender':<{padding}} | {gender:<{padding}}
    {'Favorite Colour':<{padding}} | {colour:<{padding}}
    {'Maritial Status':<{padding}} | {marital_status:<{padding}}
    {'Ethnicity':<{padding}} | {ethnicity:<{padding}}
        """
        
        print(result_string)
        
        past_survey_results_dict[email] = {
        'fname': fname,
        'lname': lname,
        'age': age,
        'email': email,
        'gender': gender,
        'colour': colour,
        'marital_status': marital_status,
        'ethnicity': ethnicity
        }
        
        success = True
        
        return redirect(url_for('main.survey', success=True))
    
    
    if request.args.get('success') == 'True':
            success = True
    
    return render_template('survey.html', success=success)



@main_bp.route('/random-words')
def random_words():
    word_list = []
    
    for i in range(random.randint(1, 10000)):
        word_list.append(random.choice(word_pool))
    
    return render_template('random_words.html', word_list = word_list)



@main_bp.route('/past-survey-results')
def past_survey_results():
    return render_template('past_survey_results.html', results=list(past_survey_results_dict.values()))



@main_bp.route('/settings', methods=["POST", "GET"])
def settings():
    success = False
    
    if request.method == "POST":
        theme = request.form.get('theme')
        enlarged_text = request.form.get('enlarged_text')
        
        session['theme'] = theme
        session['enlarged_text'] = enlarged_text
        
        
        return redirect(request.referrer or url_for('main.index'))
    
    
    return render_template('settings.html', success=success)
    


@main_bp.route('/my-account')
def my_account():
    return render_template('my_account.html')



@main_bp.route('/sign-up', methods=["POST", "GET"])
def sign_up():
    success = False
    
    if request.method == "POST":
        fname = str(request.form.get('fname')).strip().lower()
        lname = str(request.form.get('lname')).strip().lower()
        email = str(request.form.get('email')).strip().lower()
        password = str(request.form.get('password')).strip()
        password_conf = str(request.form.get('password_conf')).strip()
        
        # Input validation
        
        for item in {fname, lname, email, password}:
            if item is None or item.strip() in {"None", ""}:
                flash("All fields must be completed", "error") 
                return redirect(url_for('main.sign_up'))
            
            if not item.isprintable:
                flash("Input contains unsupported characters", "error") 
                return redirect(url_for('main.sign_up'))
            
            if 64 < len(item):
                flash("Maximum length for input is 64 characters", "error") 
                return redirect(url_for('main.sign_up'))
        
        
        for item in {fname, lname, email}:
            if ' ' in item.strip():
                flash("First name, last name, and email cannot contain spaces", "error") 
                return redirect(url_for('main.sign_up'))
        
        
        if password != password_conf:
            flash("Passwords do not match", "error") 
            return redirect(url_for('main.sign_up'))
        
        if len(password) < 6:
                flash("Password must be at least 6 characters", "error") 
                return redirect(url_for('main.sign_up'))
        
        
        # Create the account
        
        account_creation_result = db.create_account(fname, lname, email, password)
        
        
        if account_creation_result[1] == 'error':
            flash(account_creation_result[0], "error") 
            return redirect(url_for('main.sign_up'))
        
        print(f"user_id = {account_creation_result[0]}")
        
        session['access_token'] = db.create_user_access_token(account_creation_result[0])
        session['user_id'] = account_creation_result[0]
        
        success = True
        
        return redirect(url_for('main.my_account', success=True))
    
    return render_template('sign_up.html')



@main_bp.route('/log-in', methods=["POST", "GET"])
def log_in():
    success = False
    
    if request.method == "POST":
        email = str(request.form.get('email')).strip().lower()
        password = str(request.form.get('password')).strip()
        
        for item in {email, password}:
            if item.strip() in {"None", ""}:
                flash("Please fill in all fields", "error") 
                return redirect(url_for('main.log_in'))
        
        login_result = db.try_log_in(email, password)
        
        if login_result[1] == 'error':
            flash(login_result[0], 'error') 
            return redirect(url_for('main.log_in'))
        
        session['user_id'] = login_result[0][0]
        session['access_token'] = login_result[0][1]
        
        success = True
        
        return redirect(url_for('main.my_account', success=True))
    
    
    return render_template('log_in.html')



@main_bp.route('/logout')
def logout():
    db.remove_access_token(session['user_id'], session['access_token'])
    
    session['access_token'] = None
    session['user_id'] = None
    
    return redirect(url_for('main.my_account'))



past_survey_results_dict = {}
word_pool = tuple(get_english_words_set(['web2'], lower=True))
random_jargon = " oh and ".join(random.choice(word_pool) for i in range(random.randint(40000, 60000)))

print(f"Word pool length: {len(word_pool)}")

db.get_db_connection()
