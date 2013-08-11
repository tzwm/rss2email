import os, re
import sys
import ConfigParser
import smtplib 
import logging
from hashlib import md5

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import base.feedparser as feedparser
import base.log

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

    def __init__(self, inputLine, _session, outputInfo, _sender, _recipient):
        self.session = _session
        self.infoLine = inputLine
        self.sender = _sender
        self.recipient = _recipient

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
        msg['From'] = self.sender 
        msg['To'] = self.recipient 
        message = item.description + '<br /><br />' + item.link
        msg['Subject'] = item.title
        msg.attach(MIMEText(message.encode('utf8'), 'html'))
        self.session.sendmail(self.sender, self.recipient, msg.as_string())
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

def init():
    reload(sys)
    sys.setdefaultencoding('utf8')
    base.log.init()
    logging.info('rss2email is running...')

def loginEmail():
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    smtp_server = cf.get("email config", "server")
    smtp_port = cf.get("email config", "port")
    sender = cf.get("sender", "email")
    password = cf.get("sender", "password")
    recipient = cf.get("recipient", "email")

    session = smtplib.SMTP(smtp_server, smtp_port)
    session.ehlo()
    session.starttls()
    session.ehlo
    try:
        session.login(sender, password)
    except Exception, data:
        logging.error('Email Login Error.')
        return
    logging.info('Email Login Successful.')

    return (session, sender, recipient)

def getList():
    lines = []
    o_file = open("rsslist.txt", "r")
    for line in o_file:
        if line.strip('\n') == '':
            continue
        lines.append(line)
    o_file.close()
    logging.info('rsslist Got Successful.')

    return lines

def destory(session, o_file):
    session.quit()
    o_file.close()

def main():
    init()
    session, sender, recipient = loginEmail()
    rsslist = getList()

    o_file = open("rsslist.txt", "w")
    num = 0
    for line in rsslist:
        num = num + 1
        outputStep = '(' + str(num) + '/' + str(len(rsslist)) + ')'
        feedItem = FeedItem(line, session, outputStep, sender, recipient)
        ret = feedItem.update()
        o_file.write(feedItem.infoLine)

    destory(session, o_file)

if __name__ == '__main__':
    main()

