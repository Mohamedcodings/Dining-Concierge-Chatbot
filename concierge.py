from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient
import openai
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # This will enable CORS for all domains and routes

# MongoDB setup
mongo_client = MongoClient('mongodb+srv://#########################')
db = mongo_client['paris_dining']
collection = db['restaurants']

# OpenAI API setup
openai.api_key = '###########################@'

# Yelp Fusion API setup
yelp_api_key = '##########################'
headers = {'Authorization': f'Bearer {yelp_api_key}'}

def fetch_restaurants(location='Paris'):
    """ Fetches restaurants data from Yelp and stores it in MongoDB. """
    url = 'https://api.yelp.com/v3/businesses/search'
    params = {'location': location, 'categories': 'restaurants', 'limit': 50}
    response = requests.get(url, headers=headers, params=params)

    # Check the response status code before attempting to parse it as JSON
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")
        return  # Exit the function if the response is not successful

    try:
        restaurants = response.json().get('businesses', [])
        for restaurant in restaurants:
            collection.update_one({'id': restaurant['id']}, {'$set': restaurant}, upsert=True)
    except ValueError as e:  # Catches JSON decoding errors
        print(f"Error parsing JSON: {e}")

@app.route('/update_data', methods=['GET'])
def update_data():
    """ Endpoint to update restaurant data in the database. """
    fetch_restaurants()
    return jsonify({"message": "Data updated successfully"}), 200


def generate_response(query):
    """Generates a structured list of recommended restaurants using OpenAI's GPT-4 model."""
    prompt = f"List restaurants in Paris for someone who likes {query}. For each, provide the restaurant name followed by a colon and a brief description."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message['content']
        recommendations = []
        for line in raw_text.strip().split('\n'):
            if ':' in line:  # Expecting a colon to separate the name and description
                name, description = line.split(':', 1)
                recommendations.append({"name": name.strip(), "description": description.strip()})
    except Exception as e:
        return [{"name": "Error", "description": f"Failed to generate response: {str(e)}"}]

    return recommendations


# Flask route remains the same
@app.route('/recommend', methods=['POST'])
def recommend():
    user_query = request.json.get('query')
    recommendations = generate_response(user_query)
    return jsonify({"recommendations": recommendations})



if __name__ == '__main__':
    app.run(debug=True)
