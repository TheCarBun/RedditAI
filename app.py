from flask import Flask, render_template, request

from reddit_ai import run_reddit_ai, get_post_details, reddit as praw_initialized

import markdown
from dotenv import load_dotenv
load_dotenv()


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
    summary_html = ""
    error_message = None

    # Fetching Post Details
    try:
        post_details_dict = get_post_details(reddit_url)
    except Exception as e:
        print(f"Error fetching post details: {e}")
        error_message = f"🚫 Error fetching post details: `{e}`"
        post_details_dict = {"title": f"Error fetching post details: {e}"}

    # Fetching Summary from Agno Reddit Agent
    try:
        agent_response = run_reddit_ai(reddit_url)
        summary_html = markdown.markdown(agent_response.content)
    except Exception as e:
        print(f"Error during agent execution: {e}")
        summary_error_md = f"### 🚫 Summary Error Occurred\n\n😔 An error occurred while generating the summary: `{e}`. The post details might still be available."
        summary_html = markdown.markdown(summary_error_md)
        if error_message:
            error_message += f"\nAnd summary generation failed: `{e}`"
        else:
            error_message = f"Summary generation failed: `{e}`"

    return render_template('summary.html',
                           post_details=post_details_dict,
                           summary_html=summary_html,
                           original_url=reddit_url,
                           error=error_message)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
