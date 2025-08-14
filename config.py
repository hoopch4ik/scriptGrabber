from dotenv import load_dotenv
import os

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")
LOGGING_INFO_FILE = "app.log"
LAST_ID_POSTS_FILE = "__lastIds__.json"
