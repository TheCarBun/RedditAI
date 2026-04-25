import requests, os
from dotenv import load_dotenv
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

emotion_map = {
    "joy" : "😄", 
    "sadness": "🙁", 
    "anger": "😠", 
    "fear": "😨", 
    "disgust": "🤢",
    "surprise": "😯", 
    "trust": "🤝", 
    "anticipation": "🤔",
    "neutral": "😐",
}

def send_post_update(post_url, post_details, summary_data="Not Available"):
    if not DISCORD_WEBHOOK_URL:
        print("No Discord Webhook URL provided. Post updates will be skipped.")
        return
    
    print("Sending post details and summary to Discord.")

    # Format emotions list as a comma-separated string
    emotions = summary_data.get("emotion_detection", [])
    emotion_str = " ".join([f"{emotion_map[emotion]} {emotion}" for emotion in emotions]) if emotions else "N/A"

    # Format toxicity as percentage
    toxicity = summary_data.get("toxicity_detection")
    toxicity_str = f"{int(toxicity * 100)}%" if toxicity is not None else "N/A"

    # Buid Description
    description = f'### Short Summary\n> {summary_data.get("short_summary", "Reddit Post Summary")}\n\n### AI Take\n> {summary_data.get("ai_take", "N/A")}\n\n> **Sentiment:** {summary_data.get("sentiment_analysis", "N/A")}\n> **Emotion:** {emotion_str}\n> **Toxicity:** {toxicity_str}'
    
    try:
        payload = {
            "username": "RedditAI",
            "embeds": [
                {
                    "color": 11927296,
                    "title": post_details.get("title", "Reddit Post Title"),
                    "description": description,
                    "url": post_url,
                    "fields": [
                        {
                            "name": "Upvotes",
                            "value": f'<:green_dot:1116646722534383708> {str(post_details.get("upvotes", "N/A"))}',
                            "inline": True
                        },
                        {
                            "name": "Downvotes",
                            "value": f'<:red_dot:1116646834128031774> {str(post_details.get("downvotes", "N/A"))}',
                            "inline": True
                        },
                        {
                            "name": "Comments",
                            "value": f'<:yellow_dot:1116646882819711036> {str(post_details.get("num_comments", "N/A"))}',
                            "inline": True
                        }
                    ],
                    "author": {
                        "name": f"u/{post_details.get('author', 'unknown')} in r/{post_details.get('subreddit', 'unknown')}"
                    },
                    "footer": {
                        "text": post_details.get("created_date", "created at")
                    }
                }
            ]
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print("Post update sent successfully.")
    except Exception as e:
        print(f"Error sending post update: {e}")

if __name__ == "__main__":
    # Testing the function
    dummy_details = {
        "title": "Dummy Title",
        "upvotes": 100,
        "downvotes": 3,
        "num_comments": 50,
        "author": "test_user",
        "subreddit": "test_sub",
        "url": "https://reddit.com",
        "created_date": "2023-01-01 18:14:00"
    }
    dummy_summary = {
        "short_summary": "This is a test summary",
        "sentiment_analysis": "positive",
        "emotion_detection": ["joy", "surprise"],
        "toxicity_detection": 0.1,
        "ai_take": "Dummy AI Take"
    }
    send_post_update("https://www.reddit.com", dummy_details, dummy_summary)
