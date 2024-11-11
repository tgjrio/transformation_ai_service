import os
from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
GCS_BUCKET = os.getenv("GCS_BUCKET")

OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY) 
