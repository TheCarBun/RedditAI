from google.genai import Client, types
from instructions import instructions
from schema import OutputSchema
import praw
import json
from datetime import datetime

import os
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

if reddit.read_only:
    print(">> Reddit API running in read-only mode.")


def get_post_submission(post_url: str):
    try:
        print(">> Fetching comments for post: ", post_url)
        submission = reddit.submission(url=post_url)
        return submission
    except Exception as e:
        print(f">> Error fetching submission for {post_url}: {e}")
        return None

# def get_subreddit_posts(subreddit_name, limit=10, sort_by='hot'):
#     subreddit = reddit.subreddit(subreddit_name)
#     posts = []

#     if sort_by == 'hot':
#         submissions = subreddit.hot(limit=limit)
#     elif sort_by == 'new':
#         submissions = subreddit.new(limit=limit)
#     elif sort_by == 'top':
#         submissions = subreddit.top(limit=limit)
#     elif sort_by == 'controversial':
#         submissions = subreddit.controversial(limit=limit)
#     elif sort_by == 'rising':
#         submissions = subreddit.rising(limit=limit)
#     else:
#         print(f"Warning: Invalid sort_by '{sort_by}'. Defaulting to 'hot'.")
#         submissions = subreddit.hot(limit=limit)

#     for submission in submissions:
#         posts.append({
#             "id": submission.id,
#             "title": submission.title,
#             "score": submission.score,
#             "num_comments": submission.num_comments,
#             "url": submission.url,
#             "author": submission.author.name if submission.author else "deleted",
#             "created_utc": submission.created_utc,
#             "selftext": submission.selftext if submission.is_self else "",  # Body of text posts
#             "is_original_content": submission.is_original_content,
#             "over_18": submission.over_18,
#             "stickied": submission.stickied,
#             "link_flair_text": submission.link_flair_text,
#             "upvote_ratio": submission.upvote_ratio
#         })

#     return posts


def get_post_comments(submission, limit=0):
    """Fetches comments for a given Reddit post URL

    Args:
        post_url (str): Reddit post URL
        limit (int, optional): _description_. Defaults to 0. `limit=None` tries to get all. `limit=0` removes them (only top-level without replies)

    Returns:
        _type_: _description_
    """

    try:
        print(">> Trying using URL")
        # limit=None tries to get all. limit=0 removes them (only top-level without replies)
        submission.comments.replace_more(limit)
        comments = submission.comments.list()
        print(f">> Fetched {len(comments)} comments from post")
        return comments
    except Exception as e:
        print(">> Didn't work")
        return None


def get_most_upvoted_and_downvoted_comments(comments: list):
    # --- Finding the Most Upvoted Comment ---
    most_upvoted_comment = None
    max_score = -float('inf')  # Start with the lowest possible number

    # --- Finding the Most Downvoted Comment ---
    most_downvoted_comment = None
    min_score = float('inf')   # Start with the highest possible number

    for comment in comments:
        # We check comment.score, which is the net upvotes (upvotes - downvotes)

        # Check for Most Upvoted
        if comment.score > max_score:
            max_score = comment.score
            most_upvoted_comment = comment

        # Check for Most Downvoted
        if comment.score < min_score:
            min_score = comment.score
            most_downvoted_comment = comment

    # --- Print Results ---
    print("\n--- Results ---")

    if most_upvoted_comment:
        print(f"Most Upvoted Comment Score: {most_upvoted_comment.score}")
        print(
            f"Most Upvoted Comment Body: {most_upvoted_comment.body[:100]}...")
    else:
        print("No comments found for most upvoted.")

    if most_downvoted_comment:
        print(
            f"\nMost Downvoted Comment Score: {most_downvoted_comment.score}")
        print(
            f"Most Downvoted Comment Body: {most_downvoted_comment.body[:100]}...")
    else:
        print("No comments found for most downvoted.")

    return most_upvoted_comment, most_downvoted_comment


def get_most_controversial_comment(comments: list):
    def calculate_controversy_proxy(comment):
        """
        A simple proxy for controversy: a score close to zero with lots of replies.
        This gives preference to comments that sparked debate (low score, high reply count).
        """
        score_closeness_to_zero = abs(
            comment.score) + 1  # Add 1 to avoid division by zero

        # We want to maximize the debate-sparking: high replies, low score
        if score_closeness_to_zero < 50:  # Only consider those close to 0 net score
            return (len(comment.replies.list()) * 10) / score_closeness_to_zero
        return 0  # Exclude comments that are overwhelmingly positive or negative

    most_controversial_comment = None
    max_controversy = -float('inf')

    for comment in comments:
        # Skip comments that don't have replies/are too new (optional but recommended)
        if comment.score < 5 and len(comment.replies.list()) < 5:
            continue

        controversy_value = calculate_controversy_proxy(comment)

        if controversy_value > max_controversy:
            max_controversy = controversy_value
            most_controversial_comment = comment

    if most_controversial_comment:
        print(
            f"\nMost Controversial Comment Score: {most_controversial_comment.score}")
        print(
            f"Most Controversial Comment Body: {most_controversial_comment.body[:100]}...")
        return most_controversial_comment


def get_post_details(submission):
    try:
        upvotes = 'N/A'
        downvotes = 'N/A'

        score = submission.score
        upvote_ratio = submission.upvote_ratio

        if score is not None and upvote_ratio is not None:
            denominator = (2 * upvote_ratio) - 1

            if abs(denominator) < 1e-9:  # Check if denominator is effectively zero
                if score == 0:
                    upvotes = 0
                    downvotes = 0
                else:
                    # This is a rare, problematic case (e.g., score non-zero but upvote_ratio is 0.5)
                    upvotes = 'Error'
                    downvotes = 'Error'
                    print(
                        f"Warning: Unexpected scenario - score {score} with upvote_ratio {upvote_ratio}")
            else:
                calculated_upvotes = score * (upvote_ratio / denominator)
                calculated_downvotes = calculated_upvotes - score

                # Reddit's numbers are integers, so round them
                upvotes = int(round(calculated_upvotes))
                downvotes = int(round(calculated_downvotes))

                # Ensure non-negative numbers, as fuzzing can sometimes result in slightly negative
                upvotes = max(0, upvotes)
                downvotes = max(0, downvotes)

        post_details = {
            "title": submission.title,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "num_comments": submission.num_comments,
            "author": submission.author.name if submission.author else 'u/deleted',
            "subreddit": submission.subreddit.display_name,
            "url": submission.url,
            "created_date": datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        }

        print("Found Post: ", post_details)
        return post_details
    except Exception as e:
        return f"ERROR: Could not find Post Details: {e}"


def reddit_ai_response(post_details, comments: list, user_api_key=None, model="gemini-2.5-flash"):
    # Process comments into author and body
    if comments is None:
        return None
    else:
        comments_data = []
        for comment in comments:
            if comment.author is None and comment.body is None:
                continue

            comments_data.append({
                "author": comment.author.name if comment.author else "[deleted]",
                "body": comment.body
            })
        print(">> Returning Comment Data")

        # ----------- GEMINI PROCESSING -----------
        api_key_to_use = user_api_key.strip() if user_api_key and user_api_key.strip() else GEMINI_API_KEY
        
        if not api_key_to_use:
            raise ValueError("No Gemini API key provided. Please provide one in the UI or set the GEMINI_API_KEY environment variable.")
            
        client = Client(api_key=api_key_to_use)

        try:
            prompt = f"Post Details:\n {post_details}\n\nComments:\n{comments_data}"
            response = client.models.generate_content(
                model=model,
                contents=types.Part.from_text(text=prompt),
                config=types.GenerateContentConfig(
                    system_instruction=instructions,
                    temperature=0.2,
                    response_mime_type='application/json',
                    response_schema=OutputSchema,
                )
            )

            print("\n\n", "---"*5, "AI RESPONSE",
                  "---"*5, f"\n\n{response.text}", )
            return response

        except json.decoder.JSONDecodeError:
            print("Unable to decode JSON")


def main():
    url = input("Enter Reddit URL: ")
    submission = get_post_submission(url)
    if submission:
        post_details = get_post_details(submission)
        comments = get_post_comments(submission)
        get_most_upvoted_and_downvoted_comments(comments)
        get_most_controversial_comment(comments)
        reddit_ai_response(post_details, comments)


if __name__ == "__main__":
    main()
