import json
import csv
import os

# Input and Output file paths
original_jsonl_file = r'F:\Github\RedditAPI\RawData\r_VisionPro_posts.jsonl'
converted_jsonl_file = r'F:\Github\RedditAPI\RawData\r_VisionPro_posts_utf8.jsonl'
csv_output_file = r'F:\Github\RedditAPI\Title&content\reddit_titles_selftexts.csv'

# Step 0: Ensure the output folder exists
output_dir = os.path.dirname(csv_output_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# Helper: Check if the selftext is "[deleted]" or "[removed]"
def is_selftext_deleted_or_removed(selftext):
    return selftext.strip().lower() in ['[deleted]', '[removed]']


# Step 1: Convert to UTF-8 encoded JSONL if needed
def convert_to_utf8(input_file, output_file):
    with open(input_file, 'r', encoding='latin1') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            outfile.write(line)


# Step 2: Extract data and write to CSV, skipping deleted/removed posts
def jsonl_to_csv(jsonl_file, csv_file):
    with open(jsonl_file, 'r', encoding='utf-8') as infile, open(csv_file, 'w', newline='',
                                                                 encoding='utf-8') as outfile:
        writer = csv.writer(outfile)

        # Write headers (assuming you wantconverter.py title and selftext fields)
        writer.writerow(['title', 'selftext'])

        filtered_count = 0  # For tracking how many posts are skipped

        for line in infile:
            # Parse the JSON object in the current line
            post_data = json.loads(line.strip())

            # Extract relevant fields (adjust the keys based on actual JSON structure)
            title = post_data.get('title', '')
            selftext = post_data.get('selftext', '')

            # Skip entries where the selftext is "[deleted]" or "[removed]"
            if is_selftext_deleted_or_removed(selftext):
                filtered_count += 1
                continue

            # Write row to CSV
            writer.writerow([title, selftext])

        print(f"Filtered {filtered_count} posts with deleted or removed selftext.")


# Execution
convert_to_utf8(original_jsonl_file, converted_jsonl_file)
jsonl_to_csv(converted_jsonl_file, csv_output_file)

print("Conversion complete!")
