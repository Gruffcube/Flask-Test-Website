from flask import Blueprint, render_template, request, redirect, url_for

main_bp = Blueprint('main', __name__)



@main_bp.route('/')
def index():
    return render_template('index.html')



@main_bp.route('/animal-information')
def animals():
    return render_template('animal_info.html')



@main_bp.route('/user-survey', methods=['POST', 'GET'])
def survey():
    success = False
    
    if request.method == 'POST':
        fname = request.form.get('fname', 'N/A')
        lname = request.form.get('lname', 'N/A')
        age = request.form.get('age', 'N/A')
        email = request.form.get('email', 'N/A')
        
        gender = request.form.get('gender', 'N/A')
        colour = request.form.get('colour', 'N/A')
        marital_status = request.form.get('marital_status', 'N/A')
        ethnicity = request.form.get('ethnicity', 'N/A')
        
        
        padding = 30
        print(f"""
    {'First Name':<{padding}} | {fname:<{padding}}
    {'Last Name':<{padding}} | {lname:<{padding}}
    {'Age':<{padding}} | {age:<{padding}}
    {'Email':<{padding}} | {email:<{padding}}
    
    {'Gender':<{padding}} | {gender:<{padding}}
    {'Favorite Colour':<{padding}} | {colour:<{padding}}
    {'Maritial Status':<{padding}} | {marital_status:<{padding}}
    {'Ethnicity':<{padding}} | {ethnicity:<{padding}}
        """)
        
        success = True
        
        return redirect(url_for('main.survey', success=True))
    
    
    if request.args.get('success') == 'True':
            success = True
    
    return render_template('survey.html', success=success)
