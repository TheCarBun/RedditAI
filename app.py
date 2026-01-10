from flask import Flask, render_template, request
from reddit_ai import reddit_ai_response, get_post_details, get_post_comments, get_post_submission, reddit as praw_initialized
import json


app = Flask(__name__)

if praw_initialized is None:
    print("WARNING: PRAW was not initialized successfully")

# --- Flask Routes ---


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    reddit_url = request.form.get('reddit_url')

    if not reddit_url:
        return render_template('summary.html', error="Please enter a Reddit URL.")

    post_details_dict = {}
    post_comments = []
    summary_data = None
    error_message = None

    # Fetching Post Details
    try:
        submission = get_post_submission(reddit_url)
        if submission:
            post_details_dict = get_post_details(submission)
            post_comments = get_post_comments(submission, limit=75)
        else:
            error_message = "Could not find submission."
    except Exception as e:
        print(f"Error fetching post details: {e}")
        error_message = f"🚫 Error fetching post details: `{e}`"
        post_details_dict = {"title": f"Error fetching post details: {e}"}

    # Fetching Summary from Agno Reddit Agent
    if not error_message:
        try:
            agent_response = reddit_ai_response(post_details_dict, post_comments)
            if agent_response and agent_response.text:
                try:
                    summary_data = json.loads(agent_response.text)
                except json.JSONDecodeError:
                    print("Error decoding JSON from agent response")
                    summary_data = None
                    error_message = "Failed to parse AI response."
            else:
                summary_data = None
                error_message = "No response from AI agent."

        except Exception as e:
            print(f"Error during agent execution: {e}")
            summary_data = None
            if error_message:
                error_message += f"\nAnd summary generation failed: `{e}`"
            else:
                error_message = f"Summary generation failed: `{e}`"

    return render_template('summary.html',
                           post_details=post_details_dict,
                           summary_data=summary_data,
                           original_url=reddit_url,
                           error=error_message)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
