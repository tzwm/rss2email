import os, re
import sys
import smtplib 

import base.feedparser as feedparser

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
 
sender = "" 
password = "" 
recipient = 'tzwm.rss@gmail.com'

def main():
    reload(sys)
    sys.setdefaultencoding('utf8')

    sender = raw_input("sender is:")
    password = raw_input("password of sender:")

    o_file = open("rsslist.txt", "r")
    line = o_file.readline()
    o_file.close()

    line = line.split(' ', 1)
    rss_add = line[0]
    if len(line) < 2:
        d = feedparser.parse(rss_add)
    else:
        rss_modified = line[1]
        d = feedparser.parse(rss_add, modified=rss_modified)
    
    if d.status == 304:
        print("no update")
        return;


    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password)

    for feed in reversed(d.entries):
    #for feed in d.entries:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        message = feed.description
        msg['Subject'] = feed.title
        msg.attach(MIMEText(message.encode('utf8'), 'html'))
        #print(msg.as_string())
        session.sendmail(sender, recipient, msg.as_string())
    
    session.quit()

    o_file = open("rsslist.txt", "w")
    o_file.write(rss_add)
    o_file.write(' ')
    o_file.write(d.modified)

if __name__ == '__main__':
    main()

