#!/usr/bin/python3
#Copyright (C) 2017 David Faour - GPL 3.0

import feedparser
import time
import sys
import sqlite3 as lite
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

##############

# I strongly suggest you create a new, single-purpose Gmail account for the purposes of sending the notification email (eg, your-name-notifications@gmail.com). Password below must be stored in plain text so I strongly suggest you do NOT use your regular email.
#If you use gmail, you must allow less secure apps to access the account (which shouldn't matter since this is a single-purpose account, right?) https://support.google.com/accounts/answer/6010255?hl=en
gmail_user = '' # Login username for the address the notification email will be sent FROM
gmail_password = '' # password for this email address

#1 = on, 0 = off: log to feed.log so you can verify if things are working
log = 1
logfile = "./feed.log"

#Who you want to appear in the 'From' field of the email
fromField = ''

#The email address you want notification emails sent to:
send_to = ''

db = "./feeds.db"

################

def in_db(url):
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM feeds WHERE url = '" + url + "';")
        exist = cur.fetchone()
        if exist is None:
            return False
        else:
            return True

###############

#Make sure script was called correctly
try:
    feedURL = sys.argv[1]
    feedName = sys.argv[2]
except:
    print("Usage: ./feeds.py http://www.example.com/rss-feed Feed_Title")
    exit()

#Change to location of script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#Try to open the DB. If it doesn't exist, create the DB and initialize it
if os.path.exists(db)==True:
    con = lite.connect(db)
    con.text_factory = str
else:
    os.system("touch " + db)
    con = lite.connect(db)
    con.text_factory = str
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE feeds (url string);")
        con.commit()
    con.close()
    con = lite.connect(db)
    con.text_factory = str

#Open URL and make sure it returns a valid response
feed = feedparser.parse(feedURL)
if (len(feed.entries) == 0):
    if (log == 1):
        f = open(logfile, "a+")
        f.write("[" + time.strftime("%Y-%m-%d %H:%M:%S") + "]: Feed " + feedName + " (" + feedURL + ") was empty or corrupt. Likely bad URL or poor network connection.\n")
        f.close()
    exit()

newPostURLs = []
newPostTitles = []
newPostDescription = []
newPostDate = []

#Check each link to see if it's already  in the DB. If it is, skip it; if not, take note of it and add it to the DB
for post in feed.entries:
    url = post.link
    if in_db(url):
        pass
    else:
        newPostURLs.append(url)
        newPostTitles.append(post.title)
        newPostDescription.append(post.description)
        #newPostDate.append(post.pubDate)   # For some reason this didn't seem to work?
        # Write new posts to the database:
        with con:
            cur = con.cursor()
            cur.execute("INSERT INTO feeds VALUES('" + url + "');")
            con.commit()

# Exit without doing anything if there are no new posts
if (len(newPostURLs) == 0):
    if (log == 1):
        f = open(logfile, "a+")
        f.write("[" + time.strftime("%Y-%m-%d %H:%M:%S") + "]: No new posts on feed " + feedName + " (" + feedURL + ").\n")
        f.close()
    exit()

# Bit of grammar
if (len(newPostURLs) == 1):
    verb = "is"
    plural = ""
else:
    verb = "are"
    plural = "s"

# If there are new posts, create the email: 

msg = MIMEMultipart('alternative')
msg['Subject'] = str(len(newPostURLs)) + " New Post" + plural + " from " + feedName
msg['From'] = fromField
msg['To'] = send_to

body = ""

index = 0

for i in newPostURLs:
    body = body + str(index + 1) + ". <a href='" + newPostURLs[index] + "'>" + newPostTitles[index] + "</a> - " + newPostDescription[index] + "<br><br>"
    index = index + 1

body = body + "This email was generated on " + time.strftime("%Y-%m-%d %H:%M:%S") + ". </body></html>"

text = """\
<html>
<head></head>
<body>
<p>There %s %s new post%s on %s:</p><br>

%s
""" % (verb, str(len(newPostTitles)), plural, feedName, body)

try:
    email_msg = MIMEText(text, 'html')

    msg.attach(email_msg)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(fromField, send_to, msg.as_string())
    server.close()
    if (log == 1):
        f.open(logfile, "a+")
        f.write("[" + time.strftime("%Y-%m-%d %H:%M:%S") + "]: " + str(len(newPostURLs)) + " new posts on feed " + feedName + " (" + feedURL + ") and email sent to " + send_to + ".\n")
except:
    if (log == 1):
        f.open(logfile, "a+")
        f.write("[" + time.strftime("%Y-%m-%d %H:%M:%S") + "]: " + str(len(newPostURLs)) + " new posts on feed " + feedName + " (" + feedURL + ") but email failed.\n")
        f.close()

