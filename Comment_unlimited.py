import requests
import json
import praw
import time
from datetime import datetime

# Initialize the Reddit instance with your credentials
reddit = praw.Reddit(
    client_id='6JC6JLRpB3GLyoo3vb5YBQ',
    client_secret='AvtLSyLwscCIcF4DgEoIgeHTUDTnqA',
    user_agent='UX_API',
    username="triv1um4",  # Use your own Reddit username
    password="472569lsj"  # Use your own Reddit password
)

# Define the subreddit and date range
subreddit_name = "VisionPro"
start_date_str = "2024-03-01"
end_date_str = "2024-04-01"
start_timestamp = int(datetime.strptime(start_date_str, '%Y-%m-%d').timestamp())
end_timestamp = int(datetime.strptime(end_date_str, '%Y-%m-%d').timestamp())

# Define Pushshift URL and parameters
pushshift_url = 'https://api.pushshift.io/reddit/submission/search/'
params = {
    'subreddit': subreddit_name,
    'after': start_timestamp,
    'before': end_timestamp,
    'sort': 'asc',  # Sort by ascending to go from oldest to newest
    'size': 100  # Fetch 100 posts at a time
}


# Function to fetch posts from Pushshift
def fetch_posts_from_pushshift(params):
    response = requests.get(pushshift_url, params=params)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Failed to fetch data from Pushshift: {response.status_code}")
        return []


# Function to convert Unix timestamp to human-readable date
def unix_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


# Fetch posts from Pushshift within the date range
pushshift_posts = fetch_posts_from_pushshift(params)

if len(pushshift_posts) == 0:
    print("No posts found in the given date range.")
else:
    print(f"Found {len(pushshift_posts)} posts from Pushshift.")

#### Now, Proceed With PRAW to Collect Comments ####

# Prepare a list to store all submissions and their comments
all_data = []


def log(message):
    print(f"[LOG] {message}")


# Function to collect comments recursively with additional metadata
def collect_comments(comments, level=0):
    collected_comments = []
    for comment in comments:
        if isinstance(comment, praw.models.MoreComments):
            continue  # Skip 'MoreComments' objects, we'll handle them via replace_more()

        collected_comment = {
            'body': comment.body,
            'author_id': str(comment.author),
            'created_utc': comment.created_utc,
            'ups': comment.ups,
            'downs': getattr(comment, 'downs', 0),  # Some comments may not have downvotes
            'level': level,  # Depth in comment tree
            'replies': collect_comments(comment.replies, level + 1) if hasattr(comment, 'replies') else []
        }
        collected_comments.append(collected_comment)

    return collected_comments


# Function to process each submission and collect comments using PRAW
def process_submission_with_praw(submission_id):
    try:
        submission = reddit.submission(id=submission_id)
        log(f"Collecting comments for submission: {submission.title}")

        # Load all comments for this submission
        submission.comments.replace_more(limit=None)

        # Collect data for this submission
        submission_data = {
            'title': submission.title,
            'url': submission.url,
            'created_utc': submission.created_utc,
            'ups': submission.ups,
            'downs': getattr(submission, 'downs', 0),
            'comments': collect_comments(submission.comments)  # Get all comments under this submission
        }

        return submission_data

    except Exception as e:
        log(f"An error occurred while processing submission '{submission_id}': {str(e)}")
        return None


# Process all posts fetched from Pushshift
for post in pushshift_posts:
    submission_data = process_submission_with_praw(post['id'])

    if submission_data:
        all_data.append(submission_data)

    time.sleep(2)  # Sleep to avoid hitting rate limits

# Save to JSON file
if all_data:
    output_filename = f"{subreddit_name}_comments_{start_date_str}_to_{end_date_str}.json"
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)
    log(f"All data saved to {output_filename}")
else:
    log("No data was collected.")

