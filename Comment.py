import json
import praw
import time

# Initialize the Reddit instance with your credentials
reddit = praw.Reddit(
    client_id='6JC6JLRpB3GLyoo3vb5YBQ',
    client_secret='AvtLSyLwscCIcF4DgEoIgeHTUDTnqA',
    user_agent='UX_API',
    username="triv1um4",
    password="472569lsj"
)

# Define the subreddit you want to collect comments from
subreddit_name = "VisionPro"  # Change this to your desired subreddit
subreddit = reddit.subreddit(subreddit_name)

# Prepare a list to store all submissions and their comments
all_data = []


# Function to log progress messages
def log(message):
    print(f"[LOG] {message}")


# Function to collect comments recursively with additional metadata
def collect_comments(comments, level=0):
    collected_comments = []
    for comment in comments:
        if isinstance(comment, praw.models.MoreComments):
            continue

        collected_comment = {
            'body': comment.body,
            'author_id': str(comment.author),  # Author ID
            'created_utc': comment.created_utc,  # Timestamp
            'ups': comment.ups,  # Number of upvotes
            'downs': comment.downs,  # Number of downvotes
            'level': level,  # Position in the comment tree
            'replies': collect_comments(comment.replies, level + 1) if hasattr(comment, 'replies') else []
        }
        collected_comments.append(collected_comment)

    return collected_comments


# Function to fetch submissions with rate limit handling
def fetch_submissions_with_backoff(subreddit, max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            return list(subreddit.new(limit=None))  # Attempt to fetch submissions
        except praw.exceptions.APIException as e:
            if e.error_type == "RATELIMIT":
                wait_time = 2 ** attempts  # Exponential backoff
                log(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                time.sleep(wait_time)
                attempts += 1
            else:
                raise  # Reraise if not a rate limit issue
    raise Exception("Max attempts reached without success.")


# Collecting comments from multiple submissions
try:
    log("Starting data collection...")

    submissions = fetch_submissions_with_backoff(subreddit)  # Fetch submissions with backoff handling

    for submission in submissions:
        log(f"Processing submission: {submission.title}")

        submission_data = {
            'title': submission.title,
            'url': submission.url,
            'comments': collect_comments(submission.comments)
        }

        all_data.append(submission_data)

        # Save periodically to avoid losing progress
        if len(all_data) % 10 == 0:  # Every 10 submissions
            with open(f"{subreddit_name}_comments_partial.json", "w", encoding="utf-8") as json_file:
                json.dump(all_data, json_file, ensure_ascii=False, indent=4)
            log(f"Partial data saved to '{subreddit_name}_comments_partial.json'")

        time.sleep(2)  # Sleep to prevent hitting rate limits

    log("Data collection completed.")

    # Final save
    if all_data:
        with open(f"{subreddit_name}_comments.json", "w", encoding="utf-8") as json_file:
            json.dump(all_data, json_file, ensure_ascii=False, indent=4)
        log(f"Comments have been saved to '{subreddit_name}_comments.json'")
    else:
        log("No data collected to save.")

except Exception as e:
    log(f"An error occurred: {str(e)}")
