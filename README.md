# [RedditAI](reddit-ai-one.vercel.app)

🎃 **RedditAI** is a Flask web app that leverages Google Gemini and the Reddit API to fetch Reddit post comments and generate AI-powered summaries or insights. It is designed for easy exploration and summarization of Reddit discussions.

## Features

- 🔍 Fetches Reddit post comments using the Reddit API (via [PRAW](https://praw.readthedocs.io/)).
- 🤖 Summarizes or analyzes Reddit threads using Google Gemini (via [agno](https://github.com/agnodice/agno)).
- 🖥️ Simple, interactive web interface built with Flask.
- 🛠️ Modular design for easy extension and debugging.

## How It Works

1. **User Input:** Enter a Reddit post URL in the app.
2. **Fetching Comments:** The app retrieves all comments for the post using the Reddit API.
3. **AI Summarization:** Comments are passed to a Gemini-powered agent, which generates a summary or insight.
4. **Display:** The result is shown in markdown format in the app.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/TheCarBun/RedditAI.git
cd reddit-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies include:

- `flask`
- `praw`
- `agno`
- `google-genai`
- `python-dotenv`
- `markdown`

### 3. Configure Environment Variables

Create a `.env` file in the project root with your API keys:

```env
CLIENT_ID=your_reddit_client_id
CLIENT_SECRET=your_reddit_client_secret
USER_AGENT=your_reddit_user_agent
GEMINI_API_KEY=your_gemini_api_key
```

You can obtain Reddit API credentials from [Reddit Apps](https://www.reddit.com/prefs/apps) and Gemini API keys from Google.

### 4. Run the App

```bash
python app.py
```

The app will start on `http://localhost:5000`.

## Usage

1. Open the app in your browser at `http://localhost:5000`.
2. Paste a Reddit post URL (e.g., `https://www.reddit.com/r/Python/comments/xxxxxx/...`).
3. Click **Summarize**.
4. View the AI-generated summary or analysis.

## Project Structure

```
reddit-ai/
├── app.py           # Flask app entry point
├── reddit_ai.py     # Reddit API utilities and AI integration
├── instructions.py  # (Custom instructions for the agent)
├── requirements.txt
├── templates/
│   ├── index.html
│   └── summary.html
└── README.md
```

## Code Overview

### `reddit_ai.py`

- Handles Reddit API authentication and data fetching.
- `get_post_comments`: Fetches all comments for a given post.
- `get_post_details`: Fetches post metadata.
- `run_reddit_ai`: Runs the Gemini-powered agent.

### `app.py`

- Sets up the Flask UI and routes.
- Handles user input and displays results.
- Integrates with the Reddit and Gemini agent utilities.

## Customization

- **Instructions:** Modify `instructions.py` to change how the agent summarizes or analyzes posts.
- **Tools:** Add more tools to the agent for extended functionality.

## Notes

- The app runs in read-only mode for Reddit.
- Ensure your API keys are kept secret and not committed to version control.

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Enjoy exploring Reddit with AI!**
