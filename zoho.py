import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3

user = "SECRET"
password = "SECRET"


def send_mail(to, subject, body):
    if already_sent(to):
        print("already emailed %s! Not emailing them again." % to)
        return
    sent_from = user
    msg = MIMEMultipart()
    msg["From"] = "!!Con <julia@exclamation.foundation>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    server = smtplib.SMTP_SSL("smtp.zoho.com", 465)
    server.ehlo()
    server.login(user, password)
    server.sendmail(sent_from, [to, "julia@exclamation.foundation"], msg.as_string())
    server.close()
    print("Successfully sent email to %s!." % to)
    record(to, subject, body)


def already_sent(to):
    conn = sqlite3.connect("./emails.sqlite")
    with conn:
        cur = conn.cursor()
        results = cur.execute("select * from emails where recipient = ?", (to,))
        return len(cur.fetchall()) > 0


def record(to, subject, body):
    conn = sqlite3.connect("./emails.sqlite")
    with conn:
        conn.execute(
            "create table if not exists emails (recipient text not null, subject text, body text);"
        )
        conn.execute(
            "insert into emails(recipient, subject, body) values (?, ?, ?);",
            [to, subject, body],
        )
