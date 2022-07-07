# Author: Guanyi Cao
# Date: July 7, 2022
# Based on tutorial by CS Dojo and modified for my own purposes.

from queue import Empty
import random
import tweepy
import time
import schedule

# twitter bot credentials
CONSUMER_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
CONSUMER_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ACCESS_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXX'
ACCESS_SECRET = 'XXXXXXXXXXXXXXXXXXXXX'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth) 

# constants
FILE_NAME = 'last_seen_id.txt'
REPLY_QUOTES = 'reply_quotes.txt'
TWEET_QUOTES = 'tweet_quotes.txt'
ARCHIVE = 'quote_archive.txt'
DANCE_GIF = 'gojo_dance.gif'
NUM_TWEETS = 5 # replies to 5 tweets for now
CHARACTER_LIMIT = 221 # adjusted from 280 w/ addition of message: "Bestowing Gojo's.... You're welcome!" (59 chars)

recentQuotes = [] # keeps track of recent quotes used for replies

# read in quote file
# only take in quotes short enough
def read_quote_file(filename):
    quote_list = []
    file1 = open(filename, 'r')
    
    while True:
        # Get next line from file
        line = file1.readline().strip()
        # ensure it is short enough for a tweet
        if (len(line) <= CHARACTER_LIMIT):
            quote_list.append(line)
        else:
            print(line) # prints quotes that are too long
        
        # if line is empty
        # end of file is reached
        if not line:
            break
    
    file1.close()
    quote_list.remove('')
    return quote_list


# retrieves a random quote from list of quotes,
# ensures new quote hasn't been retrieved recently
def get_random_quote(quote_list, isTweet):
    if not isTweet:
        if recentQuotes is Empty:
            quote = random.choice(quote_list)
        else:
            while True:
                quote = random.choice(quote_list)
                if recentQuotes.count(quote) == 0:
                    break
    else:
        quote = random.choice(quote_list)
    
    used_quotes(quote, quote_list, isTweet)
    return quote


# if a reply, adds retrieved quote to recent quotes list
# if a tweet, adds retrieved quote into archive file, 
# and removes it from tweet quotes file
def used_quotes(quote, quote_list, isTweet):
    if isTweet:
        # adds used quote into quote archive file
        f = open(ARCHIVE, 'a')
        f.write(quote + '\n')
        f.close()
        
        # removes from tweet quotes list
        # rewrites tweet quotes file
        quote_list.remove(quote)
        f = open(TWEET_QUOTES, 'w')
        for line in quote_list:
            f.write(line + '\n')
        f.close()
    
    else:
        recentQuotes.append(quote)
        # clears recent quotes once all quotes have been used and starts over
        if len(recentQuotes) == len(quote_list):
            recentQuotes.clear()


# reads id from file and returns it
def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

# stores last seen id back in file
def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

# retrieves <NUM_TWEETS> recent tweets with the hashtag 'GojoSatoru' or 'gojosatoru'
# replies to each tweet w/ randomly chosen quote from quotes list
def search_and_reply(quote):
    # retrieves tweets
    tweets = tweepy.Cursor(api.search_tweets, q='#GojoSatoru -filter:retweets' 
    or '#gojosatoru -filter:retweets', lang='en', tweet_mode='extended').items(NUM_TWEETS)
    
    tweet_list = [tweet for tweet in tweets]
    
    for tweet in reversed(tweet_list):
        # ensures bot doesn't reply twice by storing last seen id
        last_seen_id = tweet.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        
        print('tweet id: ' +str(tweet.id))
        print('username: ' +tweet.user.screen_name)
        print('text: '+tweet.full_text)
        
        # replies to tweet with a two minute delay
        time.sleep(120)
        api.update_status('@' + tweet.user.screen_name 
        + ' bestowing Gojo\'s wisdom with a daily quote:\n' +quote, in_reply_to_status_id=tweet.id)


# tweets randomly chosen quote of the day
def tweet(quote):
    api.update_status('Gojo Senseii\'s Quote of the Day:\n' + quote)

# replies with dancing gojo GIF if mentioned
def gojo_dance():
    print('looking for dance commands...')
    # use tweet id 1543426093255987200 for testing.
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    
    mentions = api.mentions_timeline(since_id=last_seen_id, tweet_mode='extended')
    
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if 'dance' in mention.full_text.lower():
            print('found dance command!')
            print('gojo will dance now')
            api.update_status_with_media('@' + mention.user.screen_name, DANCE_GIF, in_reply_to_status_id=mention.id)


# EXECUTING
# -----------------------------------------
# performs all actions associated with search and reply
def reply_job():
    # get quotes for replies, retrieves random quote
    replyQuotes = read_quote_file(REPLY_QUOTES)
    quoteForReply = get_random_quote(replyQuotes, False)

    # searches for relevant tweets and replies to each
    search_and_reply(quoteForReply) 

schedule.every().day.at('12:00:00').do(reply_job)


# performs all actions associated with tweets on main page
def tweet_job():
    # get quotes for tweets, retrieves random quote
    tweetQuotes = read_quote_file(TWEET_QUOTES)
    quoteToTweet = get_random_quote(tweetQuotes, True)
    tweet(quoteToTweet)

schedule.every().week.do(tweet_job)


# execute bot actions
while True:
    schedule.run_pending() # run scheduled tasks

    gojo_dance()
    time.sleep(15)