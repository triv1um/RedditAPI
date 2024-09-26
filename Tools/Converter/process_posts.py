#Converter based on posts

import json
import csv
import os
from datetime import datetime

# Define paths to input files and output CSV
posts_jsonl_file = r'F:\Github\RedditAPI\RawData\r_VisionPro_posts.jsonl'
comments_jsonl_file = r'F:\Github\RedditAPI\RawData\r_VisionPro_comments.jsonl'
csv_output_file = r'F:\Github\RedditAPI\ProcessedData\reddit_post_comment_details.csv'

# Ensure the output directory exists
output_dir = os.path.dirname(csv_output_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# Helper function to check if the body is "[deleted]" or "[removed]"
def is_body_deleted_or_removed(body):
    return body.strip().lower() in ['[deleted]', '[removed]']


# Convert Unix timestamp (UTC) to a readable date-time string
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
            score = post_data.get('score', 0)
            posts[post_id] = {'title': title, 'selftext': selftext, 'score': score, 'comments': []}
    return posts


# Step 2: Load comments and associate them with the respective posts
def load_comments_and_associate_with_posts(comments_file, posts):
    with open(comments_file, 'r', encoding='utf-8') as f:
        for line in f:
            comment_data = json.loads(line.strip())

            # Extract relevant comment fields
            body = comment_data.get('body', '')
            score = comment_data.get('score', 0)
            created_utc = comment_data.get('created_utc', None)
            link_id = comment_data.get('link_id', '').replace('t3_', '')  # Remove t3_ prefix to get the post ID

            # Skip deleted or removed comments
            if is_body_deleted_or_removed(body):
                continue

            # Convert the Unix timestamp (created_utc) to a readable format
            created_time = convert_unix_time(created_utc) if created_utc else ''

            # Associate the comment with its respective post
            if link_id in posts:
                posts[link_id]['comments'].append({'body': body, 'score': score, 'created_time': created_time})


# Step 3: Write the combined data (posts and comments) to CSV
def write_to_csv(posts, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)

        # Write header row
        writer.writerow(['post_title', 'post_selftext', 'num_comments', 'post_score', 'comment_body', 'comment_score',
                         'comment_time'])

        # Iterate over each post and write associated comments
        for post_id, post_data in posts.items():
            title = post_data['title']
            selftext = post_data['selftext']
            post_score = post_data['score']
            comments = post_data['comments']
            num_comments = len(comments)

            # If there are no comments, still write the post data
            if num_comments == 0:
                writer.writerow([title, selftext, num_comments, post_score, '', '', ''])
            else:
                # Write each comment, repeating post details (except for comment-specific fields)
                for i, comment in enumerate(comments):
                    writer.writerow([
                        title if i == 0 else '',  # Post title only once per set of comments
                        selftext if i == 0 else '',  # Selftext only once per set of comments
                        num_comments if i == 0 else '',  # Number of comments only once
                        post_score if i == 0 else '',  # Post score only once
                        comment['body'],  # Comment body
                        comment['score'],  # Comment score
                        comment['created_time']  # Comment time
                    ])


# Execution
posts_data = load_posts(posts_jsonl_file)
load_comments_and_associate_with_posts(comments_jsonl_file, posts_data)
write_to_csv(posts_data, csv_output_file)

print(f"CSV file successfully saved to {csv_output_file}")
