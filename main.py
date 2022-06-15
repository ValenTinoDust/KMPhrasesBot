# import libraries
import os
import openai
import tweepy
import schedule
import time
import json
from replit import db
from random import randint
from datetime import datetime
from server import keep_alive

# Getting Twitter keys
TWITTER_CONSUMER_KEY = os.environ['Twitter API Key']
TWITTER_CONSUMER_KEY_SECRET = os.environ['Twitter API Key Secret']
TWITTER_ACCESS_TOKEN = os.environ['Twitter Access Token']
TWITTER_ACCESS_TOKEN_SECRET = os.environ['Twitter Access Token Secret']
TWITTER_BEARER_TOKEN = os.environ['Twitter Bearer Token']
TWITTER_USER_ID = os.environ['Twitter User ID']
# Getting openai keys
AI_SECRET_KEY = os.environ['OpenAI API Secret Key']

# Logging in Twitter client
api = tweepy.API(wait_on_rate_limit=True)
client = tweepy.Client(consumer_key=TWITTER_CONSUMER_KEY,
                      consumer_secret=TWITTER_CONSUMER_KEY_SECRET,
                      access_token=TWITTER_ACCESS_TOKEN,
                      access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                      bearer_token=TWITTER_BEARER_TOKEN)
# Logging in openai
openai.api_key = AI_SECRET_KEY

MAX_CHARACTERS = 280

def update_prompts():
  # Opening JSON file
  with open('prompts.json') as f:
    # returns JSON object as a dictionary
    data = json.load(f)
  # updates database prompt values
  db['prompts'] = data['prompts']
  # closes json file
  f.close()
  
def get_random(max):
  return randint(0, max)

def get_prompt():
  prompts = db['prompts']
  length = len(prompts)
  random = get_random(length)
  prompt = prompts[random]
  return prompt

def follow_back():
  followers = client.get_users_followers(id=TWITTER_USER_ID)
  if not followers.data:
    return print('No followers')
  for follower in followers.data:
    client.follow_user(target_user_id=follower.id)

def like_mentions():
  mentions = client.get_users_mentions(id=TWITTER_USER_ID)
  for tweet in mentions.data:
    client.like(tweet_id=tweet.id)

def send_daily_tweet():
  prompt = 'Tweet something cool about ' + get_prompt()
  print(prompt)
  response = openai.Completion.create(engine='text-davinci-001', prompt=prompt, max_tokens=30)
  tweet = response['choices'][0]['text']
  if(len(tweet) > MAX_CHARACTERS):
    tweet = tweet[0:(MAX_CHARACTERS + 1)]
  client.create_tweet(text=tweet)

def main():
  # if prompts json != database json then update prompts
  now = datetime.now()
  current_time = now.strftime("%H:%M:%S")
  print("Current Time =", current_time)
  update_prompts()
  
  schedule.every().day.at('18:05').do(send_daily_tweet)
  schedule.every().day.at('10:25').do(send_daily_tweet)
  schedule.every().day.at('08:35').do(send_daily_tweet)
  schedule.every().day.at('00:10').do(send_daily_tweet)
  schedule.every(20).minutes.do(like_mentions)
  schedule.every(20).minutes.do(follow_back)
  
  while True:
    schedule.run_pending()
    time.sleep(5)

keep_alive()
main()

