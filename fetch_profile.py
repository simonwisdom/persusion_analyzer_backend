import logging
import json
from flask import request, jsonify
from bson import json_util
from utils import get_platform, normalize_profile_url, fetch_profile_from_api, calculate_profile_completeness, collection

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_profile_endpoint():
    profile_url = request.json['profileUrl']
    platform, platform_param = get_platform(profile_url)
    if not platform:
        return jsonify({"error": "Unsupported profile URL"}), 400

    normalized_profile_url = normalize_profile_url(profile_url, platform)

    # Check if the profile already exists in the MongoDB collection
    existing_profile = collection.find_one({'profile_url': normalized_profile_url})
    if existing_profile:
        logging.debug(f"Profile found in MongoDB for URL: {normalized_profile_url}")
        return jsonify(json.loads(json_util.dumps(existing_profile)))

    profile_data = fetch_profile_from_api(normalized_profile_url, platform_param)
    if not profile_data:
        return jsonify({"error": "Error fetching profile data"}), 500

    # # Fetch and save the profile picture
    # profile_pic_id = fetch_and_save_profile_picture(normalized_profile_url)
    # if not profile_pic_id:
    #     logging.error("Failed to fetch and save profile picture")
    #     profile_pic_id = None

    demographic_profile = {
        'Name': f"{profile_data.get('first_name')} {profile_data.get('last_name')}",
        'Headline': profile_data.get('headline'),
        'Location': f"{profile_data.get('city')}, {profile_data.get('state')}, {profile_data.get('country')}",
        'Industry': profile_data.get('occupation'),
        'Summary': profile_data.get('summary'),
        'Email': profile_data.get('personal_email'),
        'Website': profile_data.get('profile_pic_url'),
        'Phone Numbers': profile_data.get('personal_contact_number'),
        # 'Profile Picture ID': profile_pic_id,
        'Skills': profile_data.get('skills'),
        'Accomplishment Courses': profile_data.get('accomplishment_courses'),
        'Accomplishment Honors Awards': profile_data.get('accomplishment_honors_awards'),
        'Accomplishment Organisations': profile_data.get('accomplishment_organisations'),
        'Accomplishment Patents': profile_data.get('accomplishment_patents'),
        'Accomplishment Projects': profile_data.get('accomplishment_projects'),
        'Accomplishment Publications': profile_data.get('accomplishment_publications'),
        'Accomplishment Test Scores': profile_data.get('accomplishment_test_scores'),
        'Activities': profile_data.get('activities'),
        'Articles': profile_data.get('articles'),
        'Background Cover Image URL': profile_data.get('background_cover_image_url'),
        'Certifications': profile_data.get('certifications'),
        'Connections': profile_data.get('connections'),
        'Country Full Name': profile_data.get('country_full_name'),
        'Education': profile_data.get('education'),
        'Experiences': profile_data.get('experiences'),
        'First Name': profile_data.get('first_name'),
        'Follower Count': profile_data.get('follower_count'),
        'Full Name': profile_data.get('full_name'),
        'Groups': profile_data.get('groups'),
        'Languages': profile_data.get('languages'),
        'Last Name': profile_data.get('last_name'),
        'Occupation': profile_data.get('occupation'),
        'People Also Viewed': profile_data.get('people_also_viewed'),
        'Profile Pic URL': profile_data.get('profile_pic_url'),
        'Public Identifier': profile_data.get('public_identifier'),
        'Recommendations': profile_data.get('recommendations'),
        'Similarly Named Profiles': profile_data.get('similarly_named_profiles'),
        'State': profile_data.get('state'),
        'Volunteer Work': profile_data.get('volunteer_work')
    }
    
    null_count, total_fields, percent_complete = calculate_profile_completeness(demographic_profile)
    demographic_profile['Null Count'] = null_count
    demographic_profile['Total Fields'] = total_fields
    demographic_profile['Percent Complete'] = percent_complete

    # Insert the demographic profile into MongoDB
    collection.insert_one({'demographic_profile': demographic_profile, 'profile_url': normalized_profile_url})

    return jsonify(json.loads(json_util.dumps(demographic_profile)))