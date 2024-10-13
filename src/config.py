import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai


def configure_app(app):
    """Configure the Flask app with logging and OpenAI client."""
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    app.config["GEMINI_CLIENT"] = genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    



