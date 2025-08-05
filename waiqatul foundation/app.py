from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv("app.env")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # Use secure key in production

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///volunteers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)
mail = Mail(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Volunteer model
class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(20))
    gender = db.Column(db.String(10), nullable=False)
    interest = db.Column(db.String(50), nullable=False)
    why = db.Column(db.Text, nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        gender = request.form['gender']
        interest = request.form['interest']
        why = request.form['why']


        # Save the volunteer to the database
        new_volunteer = Volunteer(
            name=name, email=email, phone=phone,
            dob=dob, gender=gender, interest=interest, why=why
        )
        db.session.add(new_volunteer)
        db.session.commit()

        try:
            # Email to organization (from org, reply-to volunteer)
            org_msg = Message(
                subject="🎉 New Volunteer Registration - Waqiatul Cares",
                sender=email,
                recipients=[os.getenv('MAIL_USERNAME')],
                reply_to=email
            )
            org_msg.body = f"""Hello Waqiatul Team,

You have a new volunteer submission! 🎉

Here are the details:

Name: {name}
Email: {email}
Phone: {phone}
Date of Birth: {dob}
Gender: {gender}
Area of Interest: {interest}

Motivation:
{why}

Please reach out to them promptly to welcome them aboard.

Warm regards,
Your Website Bot 🤖
"""
            mail.send(org_msg)

            # Confirmation email to volunteer
            user_msg = Message(
                subject="Thank You for Volunteering with Waqiatul Cares!",
                sender=os.getenv('MAIL_USERNAME'),
                recipients=[email]
            )
            user_msg.body = f"""Dear {name},

Thank you so much for your interest in volunteering with Waqiatul Cares Foundation!

We have received your application and will get in touch with you shortly. Your willingness to contribute to our cause means the world to us. 🌍

In the meantime, feel free to follow us on our social platforms and stay updated on our activities.

Warm regards,  
The Waqiatul Cares Foundation  
📧 {os.getenv('MAIL_USERNAME')}
"""
            mail.send(user_msg)

            flash('Thank you for volunteering! A confirmation email has been sent to you.', 'success')
            return redirect('/thank-you')

        except Exception as e:
            logger.error(f"Error sending emails: {e}")
            flash('Your submission was received, but there was an issue sending confirmation emails.', 'danger')

    return render_template('volunteer.html')


@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == "__main__":
    app.run(debug=True)
