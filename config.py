import os
from dotenv import load_dotenv

# Load .env from absolute path on PythonAnywhere, relative path locally
if os.path.exists("/home/KidsDoc"):
    load_dotenv('/home/KidsDoc/KidsDoc/.env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided in .env file.")
