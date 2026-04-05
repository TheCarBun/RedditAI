from httpcore import __name
import requests, os
from dotenv import load_dotenv
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_post_update(post_title, post_url, short_summary):
    if not DISCORD_WEBHOOK_URL:
        print("No Discord Webhook URL provided. Post updates will be skipped.")
        return
    
    print("Sending post url and summary.")
    try:
        payload = {
            "username": "RedditAI",
            "embeds": [
                {
                    "color": 16743478,
                    "title": post_title,
                    "description": short_summary,
                    "url": post_url
                }
            ]

        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print("Post update sent successfully.")
    except Exception as e:
        print(f"Error sending post update: {e}")

if __name__ == "__main__":
    # Testing the function
    send_post_update("Test Title", "https://www.reddit.com", "Test: Short summary")