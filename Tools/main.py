import praw
from datetime import datetime

# Initialize the Reddit instance with your credentials
reddit = praw.Reddit(
    client_id='6JC6JLRpB3GLyoo3vb5YBQ',
    client_secret='AvtLSyLwscCIcF4DgEoIgeHTUDTnqA',
    user_agent='UX_API',
    username="triv1um4",  # Replace with your Reddit username
    password="472569lsj"  # Replace with your Reddit password
)

# Define the subreddit you're interested in
subreddit_name = "VisionPro"  # Change this to your desired subreddit
subreddit = reddit.subreddit(subreddit_name)

# Fetch the creation time of the subreddit in UTC format
creation_timestamp = subreddit.created_utc

# Convert the Unix timestamp to a human-readable datetime format
creation_date = datetime.utcfromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Output the result
print(f"The subreddit r/{subreddit_name} was founded on: {creation_date} (UTC)")
