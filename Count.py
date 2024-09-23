import praw

# Initialize the Reddit instance with your credentials
reddit = praw.Reddit(
    client_id='6JC6JLRpB3GLyoo3vb5YBQ',
    client_secret='AvtLSyLwscCIcF4DgEoIgeHTUDTnqA',
    user_agent='UX_API',
    username="triv1um4",
    password="472569lsj"
)

# Define the subreddit you want to analyze
subreddit_name = "VisionPro"  # Change this to your desired subreddit
subreddit = reddit.subreddit(subreddit_name)


def count_comments_in_subreddit(subreddit):
    total_comments = 0
    try:
        # Iterate through the submissions in the subreddit
        for submission in subreddit.new(limit=None):  # You can also use .hot() or .top()
            # Replace "None" with a specific limit if needed
            submission.comments.replace_more(limit=None)  # Load all comments
            total_comments += len(submission.comments.list())  # Count all comments

        print(f"Total comments in r/{subreddit_name}: {total_comments}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Call the function to count comments
count_comments_in_subreddit(subreddit)
