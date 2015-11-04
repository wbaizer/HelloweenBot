Usage
-----

It's set up to be run by a cronfile, probably every minute or so at most.

Configuration
-------------

Configuration for the bot is set up in the settings.json file. The configuration file (which should be copied from settings.json.default) should contain the reddit bot username, password, the subreddit to post to, an approperate useragent, and the YouTube account to read from.

Dependencies
------------

Groompbot depends on the following external libraries:

* [praw](https://github.com/praw-dev/praw/) - Reddit library
* [gdata](http://code.google.com/p/gdata-python-client/) - Google Data API