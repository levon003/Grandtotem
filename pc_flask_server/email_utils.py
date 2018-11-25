
from flask import (
    Blueprint, g, redirect, render_template, request, url_for, make_response, send_file, send_from_directory, current_app
)

import requests
import smtplib
import os

from email.mime.multipart  import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

USERNAME = "csci5127.grandtotem@gmail.com"
# PASSWORD = "abcd_1234"


def get_password():
    password_filename = current_app.config["PASSWORD_FILE"]
    password_filepath = os.path.join(current_app.instance_path, password_filename)
    with open(password_filepath, 'r') as infile:
        pwd = infile.readline().strip()
        assert pwd != ""
        return pwd


def send_mail(to, subject, text, files=[]):
    assert type(to) == list
    assert type(files) == list

    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'% os.path.basename(file))
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME, get_password())
    server.sendmail(USERNAME, to, msg.as_string())
    server.quit()
    print('sent email successfully')
