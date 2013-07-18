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
 
SENDER = "tzwm.rss@gmail.com" 
PASSWORD = "wang1jun2zhe3_rss" 
RECIPIENT = 'tzwm.rss@gmail.com'

def getMD5(s):
    m = md5()
    m.update(s)

    return m.hexdigest()

class FeedItem():
    feedLink = ""
    lastMD5 = ""
    lastModified = ""
    feedD = ""
    infoLine = ""

    session = ""

    def __init__(self, inputLine, _session):
        self.session = _session
        self.infoLine = inputLine

        inputLine = inputLine.split(' ', 2)
        self.feedLink = inputLine[0]
        if len(inputLine) == 1:
            self.feedD = feedparser.parse(self.feedLink)
        if len(inputLine) == 2:
            self.lastMD5 = inputLine[1]
            self.feedD = feedparser.parse(self.feedLink)
        if len(inputLine) == 3:
            self.lastMD5 = inputLine[1]
            self.lastModified = inputLine[2]
            self.feedD = feedparser.parse(self.feedLink, modified=self.lastModified)

    def checkUpdate(self):
        if self.feedD.status == 304:
            return False 
        else:
            return True

    def checkItem(self, item):
        itemStr = item.published
        itemStr += item.link
        md5Str = getMD5(itemStr)
    
        return md5Str == self.lastMD5

    def sendItem(self, item):
        msg = MIMEMultipart()
        msg['From'] = SENDER
        msg['To'] = RECIPIENT
        message = item.description + '<\ br>' + item.link
        msg['Subject'] = item.title
        msg.attach(MIMEText(message.encode('utf8'), 'html'))
        #print(msg.as_string())
        self.session.sendmail(SENDER, RECIPIENT, msg.as_string())

    def saveStatus(self):
        if hasattr(self.feedD, 'modified'):
            self.lastModified = self.feedD.modified
        else:
            self.lastModified = ""
        self.infoLine = self.feedLink + ' ' + self.lastMD5 + ' ' + self.lastModified + '\n'

    def update(self):
        if not self.checkUpdate():
            return False

        ret = 0;
        if self.lastMD5 == "":
            ret = 1
    
        for feed in reversed(self.feedD.entries):
            if ret == 0:
                if self.checkItem(feed):
                    ret = 1
                continue
   
            self.sendItem(feed)

        if ret == 0:
            for feed in reversed(self.feedD.entries):
                self.sendItem(feed)

        feed = self.feedD.entries[0]
        self.lastMD5 = getMD5(feed.published + feed.link)
        self.saveStatus()

        return True


def main():
    reload(sys)
    sys.setdefaultencoding('utf8')

    lines = []
    o_file = open("rsslist.txt", "r")
    for line in o_file:
        lines.append(line.strip('\n'))
    o_file.close()

    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(SENDER, PASSWORD)

    o_file = open("rsslist.txt", "w")

    for line in lines:
        feedItem = FeedItem(line, session)
        ret = feedItem.update()
        o_file.write(feedItem.infoLine)
        if(ret):
            print("Update Finished")
        else:
            print("No Update")

    session.quit()
    o_file.close()

if __name__ == '__main__':
    main()

