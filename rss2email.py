import os, re
import sys
import ConfigParser
import smtplib 
import logging
import shutil
from hashlib import md5

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from xml.dom import minidom

import base.feedparser as feedparser
import base.log

def getMD5(s):
    m = md5()
    m.update(s)

    return m.hexdigest()

class FeedItem():
    lastMD5 = ""
    lastModified = ""

    def __init__(self, item, outputInfo, _session, _sender, _recipient, _rsslist):
        self.session = _session
        self.sender = _sender
        self.recipient = _recipient
        self.rsslist = _rsslist
        self.node = item 
        self.title = item.attrib['text']
        self.rssUrl = item.attrib['rssUrl']
        if 'lastMD5' in item.attrib.keys():
            self.lastMD5 = item.attrib['lastMD5']
        if 'lastModified' in item.attrib.keys():
            self.lastModified = item.attrib['lastModified']
        self.feedD = feedparser.parse(self.rssUrl, modified=self.lastModified)

        logging.info(outputInfo + ' ' + self.title + ':')

    def checkFeedStatus(self, feedD):
        if not hasattr(feedD, 'status'):
            logging.error('Error.')
            return False
        if feedD.status == 304:
            logging.info("No Update.")
            return False
        if feedD.status == 301:
            logging.error("The feed was permanently redirected to a new URL.")
            return False
        if feedD.status / 100 == 4:
            logging.error("Error:" + str(self.feedD.status))
            return False
        if feedD.status != 200:
            logging.error("Error:" + str(self.feedD.status))
            return False
        if len(feedD.entries) == 0:
            logging.error('Error: No RSS Items')
            return False

        return True

    def checkItem(self, item):
        itemStr = ''
        itemStr = itemStr + item.title
        if hasattr(item, 'link'):
            itemStr = itemStr + item.link
        md5Str = getMD5(itemStr)
    
        return md5Str == self.lastMD5

    def sendItem(self, item, number):
        msg = MIMEMultipart()
        msg['From'] = self.sender 
        msg['To'] = self.recipient 
        message = item.description + '<br /><br />' + item.link
        msg['Subject'] = '[' + self.title + '] ' + item.title
        msg.attach(MIMEText(message.encode('utf8'), 'html'))
        self.session.sendmail(self.sender, self.recipient, msg.as_string())
        logging.info('%s: %s', str(number), item.title)

    def saveXML(self):
        xml_string = ET.tostring(self.rsslist.getroot())
        doc = minidom.parseString(xml_string)
        o_file = open('rsslist.xml', 'w')
        o_file.write(doc.toprettyxml())
        o_file.close()

    def update(self):
        if not self.checkFeedStatus(self.feedD):
            return False

        number = 0
        if self.lastMD5 == "":
            hasLastMD5 = False
        else:
            hasLastMD5 = True
    
        for feed in reversed(self.feedD.entries):
            if hasLastMD5:
                if self.checkItem(feed):
                    hasLastMD5 = False
                continue
            
            if number >= 10:
                break
            number = number + 1
            self.sendItem(feed, number)
            if hasattr(feed, 'link'):
                self.lastMD5 = getMD5(feed.title + feed.link)
            else:
                self.lastMD5 = getMD5(feed.title)
            self.node.set('lastMD5', self.lastMD5)
            self.saveXML()

        if hasLastMD5:
            for feed in reversed(self.feedD.entries):
                if number >= 10:
                    break
                number = number + 1
                self.sendItem(feed, number)
            if hasattr(feed, 'link'):
                self.lastMD5 = getMD5(feed.title + feed.link)
            else:
                self.lastMD5 = getMD5(feed.title)
            self.node.set('lastMD5', self.lastMD5)
            self.saveXML()

        if hasattr(self.feedD, 'modified'):
            self.lastModified = self.feedD.modified
        else:
            self.lastModified = ""
        self.node.set('lastModified', self.lastModified)
        self.saveXML()

        logging.info("Updated %s items.", str(number))
        return True

def dfs_rss(num, root, tot, session, sender, recipient, rsslist):
    for item in root:
        if item.tag == 'body':
            continue
        if 'type' in item.attrib.keys():
            if root.tag != 'body':
                recipient_ = (recipient.split('@')[0] + 
                                '+' + root.attrib['text'] + 
                                '@' + recipient.split('@')[1])
            else:
                recipient_ = recipient
            num = num + 1
            outputStep = '(' + str(num) + '/' + str(tot) + ')'
            feedItem = FeedItem(item, outputStep, session, sender, recipient_, rsslist)
            ret = feedItem.update()
        else:
            if len(item.attrib['text']) != len(item.attrib['text'].encode('utf-8')):
                logging.error('The tag name can''t be Chinese')
                item.clear()
                continue
            num = dfs_rss(num, item, tot, session, sender, recipient, rsslist)
            item.clear()

    return num

def init():
    reload(sys)
    sys.setdefaultencoding('utf8')
    base.log.init()

    if not os.path.isfile('rsslist.xml'):
        logging.error('no rsslist file')
        sys.exit()

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
    tree = ET.ElementTree(file='rsslist.xml')
    logging.info('rsslist Got Successful.')

    return tree 

def destory(session, root_output):
    session.quit()
    
    xml_string = ET.tostring(root_output)
    doc = minidom.parseString(xml_string)
    o_file = open('rsslist.xml', 'w')
    o_file.write(doc.toprettyxml())
    o_file.close()

def main():
    init()
    session, sender, recipient = loginEmail()
    rsslist = getList()

    tot = 0
    for i in rsslist.iter(tag='item'):
        tot = tot +1

    dfs_rss(0, rsslist.find('body'), tot, session, sender, recipient, rsslist)

    destory(session, root_output)

if __name__ == '__main__':
    main()

