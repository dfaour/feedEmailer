# feedEmailer
Copyright (c) 2017 David Faour - GPL 3

This script will check a given RSS feed for any new posts, and if there are any, send an email with the title, link,
and description to your email. It's a useful way to keep up-to-date on RSS feeds that are infrequently updated for those of
us that prefer email to 'Smart Bookmarks' or dedicated feed readers.

I strongly recommend creating a single-use gmail address for sending the emails (as to avoid having to set up or use your own
SMTP server). See feed.py for more information and to fill out other settings.

This script is probably best used as a cron job set to run every day or so.

Usage:

python3 feed.py http://www.example.com/rss ExampleRSSFeed

