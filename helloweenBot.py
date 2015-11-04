#YouTube-to-Reddit bot v2.2 - HTML scraper edition
#by Dan Barbier - reddit.com/u/brocube
#for use with reddit.com/u/HelloweenBot

#node
#get video post history
#video_history.txt is a comma-delimited list of youtube video GUID's
var fs = require("fs");

var videoHistory;

var receivedChunks = "";
var videoHistoryReadStream = fs.createReadStream("./video_history.txt", {encoding: "utf8"});
videoHistoryReadStream
	.on("error", function (err) {
		console.log("videoHistoryReadStream failed: " + err);
	})
	.on("readable", function () {
		var chunk;
		while (null !== (chunk = videoHistoryReadStream.read())) {
			receivedChunks += chunk;
		}
	})
	.on("end", function () {
		videoHistory = receivedChunks.split(",");
		if (!Array.isArray(videoHistory)) {
			return this.emit("error", new Error("videoHistory isn't an array"));
		}
		if (videoHistory.length < 1) {
			return this.emit("error", new Error("videoHistory is empty"));
		}
		console.log("videoHistory loaded with " + videoHistory.length + " items");
		startHTMLPull();
});

#rawjs - reddit API wrapper
#npm install raw.js
#https://www.reddit.com/r/rawjs/wiki/documentation/methods/submit
#https://www.reddit.com/dev/api#POST_api_submit
#shoutout to https://www.reddit.com/r/rawjs/comments/23qmme/simple_bot_to_make_an_automated_submission_to_a/
#to use - create an app with type "script" - https://ssl.reddit.com/prefs/apps/
var rawjs = require("raw.js");

var credentials = { #removed from public code. Make sure to put your own info here if you clone this!
	"username": "HelloweenBot",
	"password": "Helloween4545"
};

var oAuth2 = { #removed from public code. Make sure to put your own info here if you clone this!
	"id": "",
	"secret": "",
	"redir": ""
};

var reddit = new rawjs("youtube-to-reddit bot");
reddit.setupOAuth2(oAuth2.id, oAuth2.secret, oAuth2.redir);

function postToReddit (url, title) {
	var submission = {
		"url": url,
		"r": "helloween4545",
		"title": title
	};
	reddit.auth(credentials, function (err, res) {
		if (err) {
			console.log("reddit.auth failed: " + err);
		} else {
			console.log("reddit.auth succeeded: " + res);
			reddit.captchaNeeded(function (err, required) {
				if (err) {
					console.log("reddit.captchaNeeded failed: " + err);
				} else {
					if (required) {
						console.log("can not submit because captcha is needed");
					} else {
						reddit.submit(submission, function (err, id) {
							console.log("posting to reddit:\n  link: " + url + "\n  title: " + title);
							if (err) {
								console.log("reddit.submit failed: " + err);
							} else {
								console.log("reddit.submit succeeded!");
							}
						});
					}
				}
			});
		}
	});
}

#htmlparser2 - html parser
#//npm install htmlparser2
#//https://github.com/fb55/htmlparser2

#//(in conjuntion with) request - simple http request client
#//npm install request
#//https://www.npmjs.com/package/request
var htmlparser = require("htmlparser2");
var request = require("request");

function startHTMLPull () {
	setInterval(function () {
		var htmlItems = [];

		var parser = new htmlparser.Parser({
			onerror: function (err) {
				console.log("htmlParser had error: " + err);
			},
			onopentag: function (name, attributes) {
				if (name === "a" && attributes.class === "yt-uix-sessionlink yt-uix-tile-link  spf-link  yt-ui-ellipsis yt-ui-ellipsis-2") {
					var videoObject = {
						"guid": "yt:video:" + attributes.href.slice(9), #for compatibility, spoof the GUID to match youtube's xml by adding "yt:video:"
						"link": "https://www.youtube.com" + attributes.href,
						"title": attributes.title
					};
					htmlItems.push(videoObject);
				}
			},
			onend: function () {
				if (htmlItems.length < 1 || htmlItems[0].guid.length < 10) {
					return this.emit("error", new Error("No HTML found!"));
				} else {
					for (var i in htmlItems) {
						if (videoHistory.indexOf(htmlItems[i].guid) === -1) {
							#update history
							videoHistory.push(htmlItems[i].guid);
							#save video history
							fs.writeFile("./video_history.txt", videoHistory, function (err) {
								if (err) {
									console.log("writeFile for video_history.txt failed: " + err);
								}
							});
							#finally, post to reddit!
							console.log("posting to reddit:", htmlItems[i].link, "-", htmlItems[i].title);
							postToReddit(htmlItems[i].link, htmlItems[i].title);
						}
					}
				}
			}
		}, {decodeEntities: true});

		var youtubeRequest = request("https://www.youtube.com/user/Helloween4545/videos?sort=dd&view=0&flow=list", function (err, res, body) {
			if (err) {
				console.log("request callback failed: " + err);
			}
			parser.write(body);
			parser.end();
		});

		youtubeRequest.on("error", function (err) {
			console.log("request failed: " + err);
		});
		youtubeRequest.on("response", function (res) {
			if (res.statusCode != 200) {
				return youtubeRequest.emit("error", new Error("Bad status code: " + res.statusCode));
			}
		});
	}, 30000);
}

console.log("\n...booting the Helloween4545 Youtube-To-Reddit Scraper Bot");