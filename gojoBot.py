from queue import Empty
import random
import tweepy
import time
import schedule

# Twitter bot credentials
CONSUMER_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
CONSUMER_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ACCESS_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXX'
ACCESS_SECRET = 'XXXXXXXXXXXXXXXXXXXXX'

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# Constants
FILE_NAME = 'last_seen_id.txt'
REPLY_QUOTES = 'reply_quotes.txt'
TWEET_QUOTES = 'tweet_quotes.txt'
ARCHIVE = 'quote_archive.txt'
DANCE_GIF = 'gojo_dance.gif'
NUM_TWEETS = 5  # Replies to 5 tweets for now
CHARACTER_LIMIT = 221  # Adjusted from 280 with the addition of message: "Bestowing Gojo's.... You're welcome!" (59 chars)

recentQuotes = []  # Keeps track of recent quotes used for replies


# Read quote file and return a list of quotes
def read_quote_file(filename):
    quote_list = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if len(line) <= CHARACTER_LIMIT:
                quote_list.append(line)
            else:
                print(line)  # Print quotes that are too long
    quote_list.remove('')
    return quote_list


# Get a random quote from the quote list, ensuring it hasn't been used recently
def get_random_quote(quote_list, isTweet):
    if not isTweet:
        if recentQuotes:
            while True:
                quote = random.choice(quote_list)
                if quote not in recentQuotes:
                    break
        else:
            quote = random.choice(quote_list)
    else:
        quote = random.choice(quote_list)

    used_quotes(quote, quote_list, isTweet)
    return quote


# If a reply, add the retrieved quote to the recent quotes list.
# If a tweet, add the retrieved quote to the archive file and remove it from the tweet quotes file.
def used_quotes(quote, quote_list, isTweet):
    if isTweet:
        # Add used quote to the quote archive file
        with open(ARCHIVE, 'a') as f:
            f.write(quote + '\n')

        # Remove the quote from the tweet quotes list and rewrite the tweet quotes file
        quote_list.remove(quote)
        with open(TWEET_QUOTES, 'w') as f:
            f.write('\n'.join(quote_list))

    else:
        recentQuotes.append(quote)
        # Clear recent quotes once all quotes have been used and start over
        if len(recentQuotes) == len(quote_list):
            recentQuotes.clear()


# Read the last seen id from the file
def retrieve_last_seen_id(file_name):
    with open(file_name, 'r') as f:
        last_seen_id = int(f.read().strip())
    return last_seen_id


# Store the last seen id back in the file
def store_last_seen_id(last_seen_id, file_name):
    with open(file_name, 'w') as f:
        f.write(str(last_seen_id))


# Search for recent tweets with the hashtag 'GojoSatoru' or 'gojosatoru' and reply to each tweet
def search_and_reply(quote):
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    tweets = tweepy.Cursor(api.search_tweets, q='#GojoSatoru -filter:retweets OR #gojosatoru -filter:retweets',
                           lang='en', tweet_mode='extended').items(NUM_TWEETS)

    tweet_list = [tweet for tweet in tweets]

    for tweet in reversed(tweet_list):
        last_seen_id = tweet.id
        store_last_seen_id(last_seen_id, FILE_NAME)

        print('Tweet ID: ' + str(tweet.id))
        print('Username: ' + tweet.user.screen_name)
        print('Text: ' + tweet.full_text)

        # Reply to the tweet with a two-minute delay
        time.sleep(120)
        api.update_status('@' + tweet.user.screen_name +
                          ' bestowing Gojo\'s wisdom with a daily quote:\n' + quote, in_reply_to_status_id=tweet.id)


# Tweet a randomly chosen quote of the day
def tweet(quote):
    api.update_status('Gojo Sensei\'s Quote of the Week:\n' + quote)


# Reply with a dancing Gojo GIF if mentioned
def gojo_dance():
    print('Looking for dance commands...')
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(since_id=last_seen_id, tweet_mode='extended')

    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if 'dance' in mention.full_text.lower():
            print('Found dance command!')
            print('Gojo will dance now')
            api.update_status_with_media('@' + mention.user.screen_name, DANCE_GIF, in_reply_to_status_id=mention.id)


# Scheduled job to search and reply to tweets
def reply_job():
    reply_quotes = read_quote_file(REPLY_QUOTES)
    quote_for_reply = get_random_quote(reply_quotes, False)
    search_and_reply(quote_for_reply)


# Schedule the reply job to run daily at 12:00:00
schedule.every().day.at('12:00:00').do(reply_job)


# Scheduled job to tweet a quote
def tweet_job():
    tweet_quotes = read_quote_file(TWEET_QUOTES)
    quote_to_tweet = get_random_quote(tweet_quotes, True)
    tweet(quote_to_tweet)


# Schedule the tweet job to run weekly
schedule.every().week.do(tweet_job)


# Execute bot actions
while True:
    schedule.run_pending()  # Run scheduled tasks
    gojo_dance()
    time.sleep(15)
