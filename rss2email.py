import os, re
import sys
import smtplib 
import logging
from hashlib import md5

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import base.feedparser as feedparser
import base.log

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
 
SENDER = "tzwm.rss@gmail.com" 
PASSWORD = "" 
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

    def __init__(self, inputLine, _session, outputInfo):
        self.session = _session
        self.infoLine = inputLine

        inputLine = inputLine.strip('\n')
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

        logging.info(outputInfo + ' ' + self.feedD.feed.title + ':')

    def checkUpdate(self):
        #if self.feedD.status == 304:
            #return False 
        #else:
            #return True
        return True

    def checkItem(self, item):
        itemStr = item.published
        itemStr += item.link
        md5Str = getMD5(itemStr)
    
        return md5Str == self.lastMD5

    def sendItem(self, item, number):
        msg = MIMEMultipart()
        msg['From'] = SENDER
        msg['To'] = RECIPIENT
        message = item.description + '<br /><br />' + item.link
        msg['Subject'] = item.title
        msg.attach(MIMEText(message.encode('utf8'), 'html'))
        self.session.sendmail(SENDER, RECIPIENT, msg.as_string())
        logging.info('%s: %s', str(number), item.title)

    def saveStatus(self):
        if hasattr(self.feedD, 'modified'):
            self.lastModified = self.feedD.modified
        else:
            self.lastModified = ""
        self.infoLine = self.feedLink + ' ' + self.lastMD5 + ' ' + self.lastModified + '\n'

    def update(self):
        if not self.checkUpdate():
            return False

        number = 0
        ret = 0;
        if self.lastMD5 == "":
            ret = 1
    
        for feed in reversed(self.feedD.entries):
            if ret == 0:
                if self.checkItem(feed):
                    ret = 1
                continue
            
            number = number + 1
            self.sendItem(feed, number)

        if ret == 0:
            for feed in reversed(self.feedD.entries):
                self.sendItem(feed, number)

        feed = self.feedD.entries[0]
        self.lastMD5 = getMD5(feed.published + feed.link)
        self.saveStatus()

        if number == 0:
            logging.info("No Update.")
            return False
        else:
            logging.info("Updated %s items.", str(number))
            return True

def main():
    reload(sys)
    sys.setdefaultencoding('utf8')
    base.log.init()
    logging.info('rss2email is running...')

    lines = []
    o_file = open("rsslist.txt", "r")
    for line in o_file:
        if line.strip('\n') == '':
            continue
        lines.append(line)
    o_file.close()
    logging.info('rsslist got successful.')

    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo
    try:
        session.login(SENDER, PASSWORD)
    except Exception, data:
        logging.error('Email Login Error.')
        return
    logging.info('Email Login Successful.')

    o_file = open("rsslist.txt", "w")

    num = 0
    for line in lines:
        num = num + 1
        outputStep = '(' + str(num) + '/' + str(len(lines)) + ')'
        feedItem = FeedItem(line, session, outputStep)
        ret = feedItem.update()
        o_file.write(feedItem.infoLine)

    session.quit()
    o_file.close()

if __name__ == '__main__':
    main()

