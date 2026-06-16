from flask import Blueprint, render_template, request, redirect, url_for

main_bp = Blueprint('main', __name__)



@main_bp.route('/')
def index():
    return render_template('index.html')



@main_bp.route('/about')
def about():
    return render_template('about.html')



@main_bp.route('/lipsum')
def lipsum():
    return render_template('lipsum.html')



# ~ @main_bp.route('/form')
# ~ def form():
    # ~ return render_template('form.html')



@main_bp.route('/form', methods=['GET', 'POST'])
def submit_task():
    success = False

    if request.method == 'POST':
        # Get data from the form
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        age = request.form.get('age')
        message = request.form.get('message')

        # Here you can save it to a database, list, or file later
        print(f"""
    First Name ~ | ~ {fname}
    Last Name ~~ | ~ {lname}
    Age ~~~~~~~~ | ~ {age}
    Message ~~~~ | ~ {message}
        """)

        success = True
        
        return redirect(url_for('main.submit_task'))  # Refresh page

    return render_template('form.html', success=success)
