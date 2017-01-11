import praw

reddit = praw.Reddit(client_id='Ho_FIRMXbFiY3w', client_secret=None,
                     user_agent='linux:meme_get:v1.0 (by /u/memegenmemegen)')

results = reddit.subreddit('memes').hot(limit=10)

for a in results:
    print(a.title)
    print(a.url)
