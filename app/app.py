from flask import Flask, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
import os

app = Flask(__name__)

# Connect to MongoDB database
client = MongoClient(os.environ.get("MONGO_URI"))
db = client['video_db']
videosCollection = db['videos']

@app.route('/')
def index():
    return 'Welcome to the Video API!'

@app.route('/api/v1/videos')
def get_videos():
    try:
        video_list = list(videosCollection.find())
        if not video_list:
            return jsonify({'error': 'No videos found'}), 404
        for video in video_list:
            # Convert the ObjectId to a string
            video['_id'] = str(video['_id'])
        return jsonify(video_list)
    except Exception as e:
        return jsonify({'error': 'Error fetching videos: {}'.format(str(e))}), 500


@app.route('/api/v1/videos/<string:video_id>', methods=['GET'])
def get_video(video_id):
    try:
        # Convert string to ObjectId
        video_id = ObjectId(video_id)
        video = videosCollection.find_one({'_id': video_id})
        # Check if a video with the specified ID was found
        if video is not None:
            # Convert the ObjectId to a string to include in the JSON response
            video['_id'] = str(video['_id'])
            return jsonify(video)
        else:
            # Return a 404 error response if the video was not found
            return jsonify({'error': 'Video not found'}), 404
    except InvalidId:
        # Return a 400 error response if the video ID is invalid
        return jsonify({'error': 'Invalid video ID'}), 400

if __name__ == '__main__':
    app.run(debug=True)