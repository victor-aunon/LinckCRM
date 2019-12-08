from flask_mail import Message
from flask import render_template, current_app
from threading import Thread
from app import mail


def send_async_mail(app, msg):
    # Flask uses contexts to avoid having to pass arguments across functions
    # It requires an application context to be in place to work, because that
    # allows them to find the Flask application instance without it being passed
    # as an argument. The reason many extensions need to know the application
    # instance is because they have their configuration stored in the app.config object. 
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_mail, args=(current_app._get_current_object(), msg)).start()