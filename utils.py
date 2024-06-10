import os
import json
import logging
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import json_util
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnableSequence
from langchain_core.prompts import PromptTemplate
from prompts import profile_prompt_template, reaction_prompt_template
from PIL import Image
from io import BytesIO
import gridfs
from bson import json_util
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Load environment variables from .env file
load_dotenv()

proxycurl_api_key = os.getenv('PROXYCURL_API_KEY')

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=1,
    max_tokens=1024,
    max_retries=2,
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Create RunnableLambdas
profile_chain = profile_prompt_template | llm
reaction_chain = reaction_prompt_template | llm

# Get API key and MongoDB connection string from environment variables
proxycurl_api_key = os.getenv('PROXYCURL_API_KEY')
mongodb_uri = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
db = client["persuasion"]
collection = db["linkedin-profile"]
fs = gridfs.GridFS(db)

def fetch_and_save_profile_picture(profile_url):
    headers = {'Authorization': f'Bearer {proxycurl_api_key}'}
    api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/person/profile-picture'
    params = {'linkedin_person_profile_url': profile_url}

    try:
        response = requests.get(api_endpoint, params=params, headers=headers)
        response.raise_for_status()
        profile_pic_url = response.json().get("tmp_profile_pic_url")

        if profile_pic_url:
            image_response = requests.get(profile_pic_url)
            image_response.raise_for_status()

            # Check if the response content is an image
            content_type = image_response.headers['Content-Type']
            if 'image' not in content_type:
                logging.error(f"Invalid content type: {content_type}")
                return None

            try:
                image = Image.open(BytesIO(image_response.content))
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                # Save the image in GridFS
                image_id = fs.put(img_byte_arr, filename=f"{profile_url}.jpg")
                return image_id
            except Exception as e:
                logging.error(f"Error processing image: {e}")
                return None
        else:
            logging.error("No profile picture URL found in the response")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching profile picture: {e}")
        return None

def get_platform(profile_url):
    domain = urlparse(profile_url).netloc
    if 'linkedin' in domain:
        return 'linkedin', 'linkedin_profile_url'
    elif 'twitter' in domain or 'x.com' in domain:
        return 'twitter', 'twitter_profile_url'
    elif 'facebook' in domain:
        return 'facebook', 'facebook_profile_url'
    else:
        return None, None

def normalize_profile_url(profile_url, platform):
    if platform == 'twitter':
        return profile_url.replace('twitter.com', 'x.com')
    return profile_url.rstrip('/')

def fetch_profile_from_api(profile_url, platform_param):
    headers = {'Authorization': f'Bearer {proxycurl_api_key}'}
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    params = {platform_param: profile_url, 'fallback_to_cache': 'on-error'}
    
    try:
        response = requests.get(api_endpoint, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching profile from Proxycurl API: {e}")
        return None

def calculate_profile_completeness(demographic_profile):
    total_fields = len(demographic_profile)
    null_count = sum(1 for value in demographic_profile.values() if value is None)
    percent_complete = ((total_fields - null_count) / total_fields) * 100
    return null_count, total_fields, percent_complete