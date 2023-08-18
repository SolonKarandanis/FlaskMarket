from flask_mail import Message
from flask import render_template
from market import mail
from market.data_access.models.models import User
from market import app
from threading import Thread


class EmailService:

    def send_async_email(self, msg):
        with app.app_context():
            mail.send(msg)

    def send_email(self, subject, sender, recipients, text_body, html_body):
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        Thread(target=self.send_async_email, args=( msg)).start()

    def send_password_reset_email(self, user: User):
        token = user.get_reset_password_token()
        self.send_email('[FlaskMarket] Reset Your Password',
                        sender=app.config['ADMINS'][0],
                        recipients=[user.email],
                        text_body=render_template('email/reset_password.txt',
                                                  user=user, token=token),
                        html_body=render_template('email/reset_password.html',
                                                  user=user, token=token)
                        )