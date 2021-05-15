from flask import render_template, current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, Personalization, Email, From, Bcc, Subject, ReplyTo


# Generic method to send email via Sendgrid
def send_email(recipients, subject, text_body, html_body, send_admin=False):
    message = Mail()

    # personalization is used so you can't see other people sent email
    for r in recipients:
        person = Personalization()
        person.add_to(Email(r))
        message.add_personalization(person)

    if send_admin:
        admin_list = current_app.config['MAIL_ADMINS'].split(';')
        message.bcc = [Bcc(a) for a in admin_list]
        
    message.subject = Subject(subject)
    message.from_email = From(
        current_app.config['MAIL_FROM'], 'My site')
    message.reply_to = ReplyTo(
        current_app.config['MAIL_REPLY_TO'], 'My Site Reply')

    message.content = [
        Content('text/html', html_body),
        Content('text/txt', text_body)
    ]

    try:
        sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(e)
        return False


# Send register successful email
def send_reg_email(user):
    recipients = [user.email]
    return send_email(
        recipients=recipients,
        subject='Welcome to ...',
        text_body=render_template('email_reg.txt',
                                  user=user),
        html_body=render_template('email_reg.html',
                                  user=user),
        send_admin=True)


# Send forgot password email
def send_forgotpwd_email(user):
    token = user.get_temp_token(
        expires_in=current_app.config['FORGOT_PASSWORD_TOKEN_EXPIRE']
    )
    recipients = [user.email]
    return send_email(
        recipients=recipients,
        subject='Reset your password from ...',
        text_body=render_template('email_pwdreset.txt',
                                  user=user, token=token),
        html_body=render_template('email_pwdreset.html',
                                  user=user, token=token),
        send_admin=False)



