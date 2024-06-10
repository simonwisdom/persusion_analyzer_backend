import json
import logging
import datetime
from flask import request, jsonify
from pymongo import MongoClient
from bson import json_util
from utils import get_platform, normalize_profile_url, profile_chain, reaction_chain, client, db, collection
from prompts import profile_prompt_template, reaction_prompt_template


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Define a function to save data to a file
def save_data_to_file(filename, data):
    with open(filename, 'a') as f:
        f.write(f"{datetime.datetime.now()}\n")
        f.write(f"{json.dumps(data, indent=4)}\n")

def analyze_profile_endpoint():
    demographic_profile = request.json.get('profileData')
    profile_url = request.json.get('profileUrl')
    platform, _ = get_platform(profile_url)
    normalized_profile_url = normalize_profile_url(profile_url, platform)

    # Check if the profile analysis already exists in the MongoDB collection
    existing_profile = collection.find_one({'profile_url': normalized_profile_url})
    if existing_profile and 'psychological_profile' in existing_profile:
        logging.debug(f"Profile analysis found in MongoDB for profile URL: {normalized_profile_url}")
        return jsonify(json.loads(json_util.dumps(existing_profile)))

    # Run the profile chain to get the psychological profile
    profile_prompt_input = {"demographic_profile": json.dumps(demographic_profile)}

    # Save input data
    save_data_to_file('profile_chain_input.json', {"demographic_profile": json.dumps(demographic_profile)})
    
    formatted_prompt = profile_prompt_template.format(**profile_prompt_input)
    logging.debug("Full prompt sent to profile_chain: %s", formatted_prompt)

    # Run the profile chain to get the psychological profile
    profile_result = profile_chain.invoke(profile_prompt_input)
    profile_content = profile_result.content

    # Save output data
    save_data_to_file('profile_chain_output.json', profile_content)
    
    logging.debug("Profile content: %s", profile_content)

    if not profile_content:
        logging.error("Profile content is empty")
        return jsonify({"error": "Profile content was empty"}), 500

    # Extract JSON from profile content
    try:
        profile_response = json.loads(profile_content)
        psychological_profile = profile_response['psychological_profile']
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return jsonify({"error": "Error decoding JSON from profile content"}), 500

    # Run the reaction chain using the psychological profile and demographic profile to get the persuasion plan
    reaction_prompt_input = {
        "demographic_profile": json.dumps(demographic_profile),
        "psychological_profile": json.dumps(psychological_profile)
    }

    formatted_reaction_prompt = reaction_prompt_template.format(**reaction_prompt_input)
    logging.debug("Full prompt sent to reaction_chain: %s", formatted_reaction_prompt)

    reaction_result = reaction_chain.invoke(reaction_prompt_input)
    reaction_content = reaction_result.content
    logging.debug("Reaction content: %s", reaction_content)
    
    if not reaction_content:
        logging.error("Reaction content is empty")
        return jsonify({"error": "Reaction content was empty"}), 500
    
    # Extract JSON from reaction content
    try:
        reaction_content = json.loads(reaction_content)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from reaction content: {e}")
        return jsonify({"error": "Error decoding JSON from reaction content"}), 500


    data_to_store = {
        'psychological_profile': psychological_profile,
        'persuasion_plan': reaction_content,
    }

    try:
        # Update the existing document with the new analysis data
        collection.update_one(
            {'profile_url': normalized_profile_url},
            {'$set': data_to_store}
        )
        logging.debug(f"Document updated with profile URL: {normalized_profile_url}")
    except Exception as e:
        logging.error(f"An error occurred while updating the document: {e}")

    return jsonify({
        'demographic_profile': json.loads(json_util.dumps(demographic_profile)),
        'psychological_profile': psychological_profile,
        'persuasion_plan': reaction_content,
    })