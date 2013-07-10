import os, re
import sys
import smtplib 

import base.feedparser as feedparser

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from hashlib import md5

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
 
sender = "" 
password = "" 
recipient = 'tzwm.rss@gmail.com'

lastMD5 = ""

def getMD5(s):
    m = md5()
    m.update(s)

    return m.hexdigest()


def checkItemUpdate(item):
    itemStr = item.published
    itemStr += item.link
    md5Str = getMD5(itemStr)

    return md5Str == lastMD5

def main():
    reload(sys)
    sys.setdefaultencoding('utf8')

    sender = raw_input("sender is:")
    password = raw_input("password of sender:")

    o_file = open("rsslist.txt", "r")
    line = o_file.readline()
    o_file.close()

    line = line.split(' ', 2)
    rss_add = line[0]
    global lastMD5
    if len(line) < 2:
        d = feedparser.parse(rss_add)
    else:
        lastMD5 = line[1]
        rss_modified = line[2]
        d = feedparser.parse(rss_add, modified=rss_modified)

    
    if d.status == 304:
        print("no update")
        return;


    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password)

    ret = 0;
    if lastMD5 == "":
        ret = 1

    for feed in reversed(d.entries):
    #for feed in d.entries:
        if ret == 0:
            if checkItemUpdate(feed):
                ret = 1
            continue

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        message = feed.description
        msg['Subject'] = feed.title
        msg.attach(MIMEText(message.encode('utf8'), 'html'))
        #print(msg.as_string())
        session.sendmail(sender, recipient, msg.as_string())

    feed = d.entries[0]
    lastMD5 = getMD5(feed.published + feed.link)
    session.quit()

    o_file = open("rsslist.txt", "w")
    o_file.write(rss_add)
    o_file.write(' ')
    o_file.write(lastMD5)
    o_file.write(' ')
    o_file.write(d.modified)
    o_file.close()

if __name__ == '__main__':
    main()

