import snscrape.modules.twitter as sntwitter
import pandas as pd

# Create a list to store the tweets
tweets = []

# Use snscrape to get tweets from a specific user
for i, tweet in enumerate(sntwitter.TwitterUserScraper('WysokieNapiecie').get_items()):
    if tweet.date < pd.Timestamp('2016-01-01'):
        break
    tweets.append(tweet)

# Print the tweets
for tweet in tweets:
    print(tweet.date, tweet.content)
