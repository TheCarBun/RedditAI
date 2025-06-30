from agno.agent import Agent
from agno.models.google import Gemini
from instructions import instructions
import praw
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


def get_post_comments(post_url: str, limit=0):
    """Fetches comments for a given Reddit post URL

    Args:
        post_url (str): Reddit post URL
        limit (int, optional): _description_. Defaults to 0. `limit=None` tries to get all. `limit=0` removes them (only top-level without replies)

    Returns:
        _type_: _description_
    """
    print(">> Fetching comments for post: ", post_url)

    try:
        print(">> Trying using URL")
        submission = reddit.submission(url=post_url)
        print(">> Worked using URL")
    except Exception as e:
        print(">> Didn't work")
        print(f">> Error fetching submission for {post_url}: {e}")

    comments_data = []

    # limit=None tries to get all. limit=0 removes them (only top-level without replies)
    submission.comments.replace_more(limit)

    for comment in submission.comments.list():
        if comment.author is None and comment.body is None:
            continue

        comments_data.append({
            "submission_id": submission.id,
            "author": comment.author.name if comment.author else "[deleted]",
            "body": comment.body,
            "score": comment.score,
            "is_submitter": comment.is_submitter
        })
    print(">> Returning Comment Data")
    return comments_data


def get_post_details(post_url: str):
    try:
        submission = reddit.submission(url=post_url)

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
        return f"ERROR: Could not find Post Details with URL: {post_url}"


def run_reddit_ai(prompt: str):
    model = Gemini(
        id="gemini-2.5-flash",
        api_key=GEMINI_API_KEY
    )

    reddit_tools = [get_post_comments]

    agent = Agent(
        name="RedditAI",
        model=model,
        instructions=instructions,
        tools=reddit_tools,
        show_tool_calls=True,
        read_chat_history=True,
        markdown=True,
        debug_mode=True
    )

    response = agent.run(prompt)
    return response
