from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Secret key for session management
app.secret_key = 'your_secret_key'


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)


# Function to create default admin user
def create_default_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('defaultpassword')  # Set default password here
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with default password: 'defaultpassword'")


# Routes
@app.route('/')
def home():
    pages = Page.query.all()
    return render_template('home.html', pages=pages)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Redirect to dashboard if already logged in
    if 'username' in session:
        return redirect(url_for('admin_dashboard'))

    # Handle POST request for login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # Check if user exists and if the password matches
        if user and check_password_hash(user.password, password):
            session['username'] = username  # Store username in session
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials, please try again."

    # Render login page
    return render_template('login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('admin'))
    pages = Page.query.all()
    return render_template('admin.html', pages=pages)


@app.route('/admin/config', methods=['GET', 'POST'])
def config_page():
    if 'username' not in session:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        db_url = request.form['db_url']
        with open('config.py', 'w') as config_file:
            config_file.write(f"SQLALCHEMY_DATABASE_URI = '{db_url}'")
        return redirect(url_for('admin_dashboard'))
    return render_template('config.html')


@app.route('/admin/new_page', methods=['GET', 'POST'])
def new_page():
    if 'username' not in session:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_page = Page(title=title, content=content)
        db.session.add(new_page)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('new_page.html')

@app.route('/page/<int:page_id>')
def view_page(page_id):
    page = Page.query.get_or_404(page_id)
    return render_template('view_page.html', page=page)

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures all tables are created
        create_default_admin()  # Ensures default admin user is created
    app.run(debug=True)
