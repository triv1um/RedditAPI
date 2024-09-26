import json
import csv
import os
from datetime import datetime

# Define paths to input files for posts and comments
posts_jsonl_file = r'F:\Github\RedditAPI\RawData\r_VisionPro_posts.jsonl'
comments_jsonl_file = r'F:\Github\RedditAPI\RawData\r_VisionPro_comments.jsonl'
csv_output_file = r'F:\Github\RedditAPI\ProcessedData\reddit_comments_with_posts.csv'

# Ensure the output directory exists
output_dir = os.path.dirname(csv_output_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# Helper function to check if the body is "[deleted]" or "[removed]"
def is_body_deleted_or_removed(body):
    return body.strip().lower() in ['[deleted]', '[removed]']


# Helper function to convert Unix timestamp to a readable date-time string
def convert_unix_time(utc_timestamp):
    return datetime.utcfromtimestamp(utc_timestamp).strftime('%Y-%m-%d %H:%M:%S')


# Step 1: Load all posts into a dictionary for quick lookup
def load_posts(posts_file):
    posts = {}
    with open(posts_file, 'r', encoding='utf-8') as f:
        for line in f:
            post_data = json.loads(line.strip())
            post_id = post_data.get('id', '')
            title = post_data.get('title', '')
            selftext = post_data.get('selftext', '')
            posts[post_id] = {'title': title, 'selftext': selftext}
    return posts


# Step 2-4: Process comments and write data to CSV
def process_comments_and_write_csv(comments_file, posts, output_csv):
    with open(comments_file, 'r', encoding='utf-8') as infile, open(output_csv, 'w', newline='',
                                                                    encoding='utf-8') as outfile:
        writer = csv.writer(outfile)

        # Write header row for CSV
        writer.writerow(['comment_body', 'comment_score', 'comment_time', 'post_title', 'post_selftext'])

        # Process each line in the comments JSONL file
        for line in infile:
            comment_data = json.loads(line.strip())

            # Extract comment details
            body = comment_data.get('body', '')
            score = comment_data.get('score', 0)
            created_utc = comment_data.get('created_utc', None)
            link_id = comment_data.get('link_id', '').replace('t3_', '')  # Remove t3_ prefix to get the post ID

            # Skip deleted or removed comments
            if is_body_deleted_or_removed(body):
                continue

            # Convert comment time to human-readable format
            created_time = convert_unix_time(created_utc) if created_utc else ''

            # Get post details (from loaded posts data)
            post_details = posts.get(link_id, {'title': '', 'selftext': ''})
            post_title = post_details['title']
            post_selftext = post_details['selftext']

            # Write relevant fields to CSV, ensuring every comment is followed by the post it belongs to
            writer.writerow([body, score, created_time, post_title, post_selftext])


# Execution
posts_data = load_posts(posts_jsonl_file)
process_comments_and_write_csv(comments_jsonl_file, posts_data, csv_output_file)

print(f"CSV file successfully saved to {csv_output_file}")
