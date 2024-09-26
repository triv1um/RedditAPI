import praw
import csv
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

# Define the subreddit you want to collect data from
subreddit_name = "VisionPro"
subreddit = reddit.subreddit(subreddit_name)

# Prepare a list to store all submissions and their comments
all_data = []


# Function to log progress messages
def log(message):
    print(f"[LOG] {message}")


# Function to collect comments recursively with additional metadata
def collect_comments(comments, submission_title, submission_url, submission_created_utc):
    collected_comments = []
    for comment in comments:
        if isinstance(comment, praw.models.MoreComments):
            continue  # Skip 'MoreComments' objects

        collected_comment = {
            'submission_title': submission_title,
            'submission_url': submission_url,
            'submission_created_utc': submission_created_utc,
            'comment_author_id': str(comment.author),  # Author ID of the comment
            'comment_body': comment.body,  # Comment Body
            'comment_created_utc': comment.created_utc,  # Timestamp of comment creation
            'comment_ups': comment.ups,  # Number of upvotes
            'comment_downs': getattr(comment, 'downs', 0),  # Number of downvotes
            'comment_parent_id': comment.parent_id,  # Parent ID to maintain comment thread structure
            'comment_level': 0  # Top-level comments have level 0
        }
        collected_comments.append(collected_comment)

        # Recursively process replies (nested comments)
        if hasattr(comment, 'replies'):
            replies = collect_comments(comment.replies, submission_title, submission_url, submission_created_utc)
            # Increase depth level for nested comments
            for reply in replies:
                reply['comment_level'] += 1
            collected_comments.extend(replies)

    return collected_comments


# Function to process each submission and collect comments
def process_submission(submission):
    try:
        log(f"Processing submission: {submission.title} (Created: {datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')})")

        # Collect metadata for the submission (post)
        submission_data = {
            'title': submission.title,
            'author': str(submission.author),
            'created_utc': submission.created_utc,
            'url': submission.url,
            'selftext': submission.selftext,  # The post's text content
            'ups': submission.ups,
            'downs': getattr(submission, 'downs', 0),
            'num_comments': submission.num_comments,
            'score': submission.score
        }

        # Fetch all comments for this submission
        submission.comments.replace_more(limit=None)
        comments = collect_comments(submission.comments, submission.title, submission.url, submission.created_utc)

        return submission_data, comments

    except Exception as e:
        log(f"An error occurred while processing submission '{submission.title}': {str(e)}")
        return None, None


# Function to auto-save every 10 posts
def auto_save_to_csv(posts_data, comments_data, csv_file_posts, csv_file_comments, save_count):
    log(f"Auto-saving data after processing {save_count} posts...")

    fieldnames_posts = ['title', 'author', 'created_utc', 'url', 'selftext', 'ups', 'downs', 'num_comments', 'score']
    fieldnames_comments = ['submission_title', 'submission_url', 'submission_created_utc',
                           'comment_author_id', 'comment_body', 'comment_created_utc',
                           'comment_ups', 'comment_downs', 'comment_parent_id', 'comment_level']

    # Save posts data
    with open(csv_file_posts, mode='a', newline='', encoding='utf-8') as posts_file:
        writer_posts = csv.DictWriter(posts_file, fieldnames=fieldnames_posts)
        if save_count == 10:  # Write header only once
            writer_posts.writeheader()
        for post in posts_data:
            writer_posts.writerow(post)

    # Save comments data
    with open(csv_file_comments, mode='a', newline='', encoding='utf-8') as comments_file:
        writer_comments = csv.DictWriter(comments_file, fieldnames=fieldnames_comments)
        if save_count == 10:  # Write header only once
            writer_comments.writeheader()
        for comment in comments_data:
            writer_comments.writerow(comment)

    log("Auto-save completed.")


# Main function to scrape posts and comments, with auto-save every 10 posts
def scrape_subreddit(subreddit, csv_file_posts, csv_file_comments):
    submission_count = 0
    posts_data = []  # Temporary storage for posts
    comments_data = []  # Temporary storage for comments

    try:
        for submission in subreddit.new(limit=None):  # You can specify the limit or leave it as None to scrape all
            post_data, submission_comments = process_submission(submission)

            if post_data and submission_comments:
                posts_data.append(post_data)
                comments_data.extend(submission_comments)
                submission_count += 1

            # Auto-save every 10 submissions
            if submission_count % 10 == 0:
                auto_save_to_csv(posts_data, comments_data, csv_file_posts, csv_file_comments, submission_count)
                posts_data.clear()  # Clear temporary storage after saving
                comments_data.clear()

            time.sleep(1)  # Sleep for a short duration to avoid hitting rate limits

        # Final save at the end (if there's any unsaved data left)
        if posts_data or comments_data:
            auto_save_to_csv(posts_data, comments_data, csv_file_posts, csv_file_comments, submission_count)

        log("Data collection completed.")

    except Exception as e:
        log(f"An error occurred during scraping: {str(e)}")


# Run the scraper
csv_file_posts = "visionpro_posts.csv"
csv_file_comments = "visionpro_comments.csv"
scrape_subreddit(subreddit, csv_file_posts, csv_file_comments)
