from flask import Flask, jsonify
from pymongo import MongoClient, errors
from bson.objectid import ObjectId

app = Flask(__name__)

# Connect to MongoDB database
client = MongoClient('localhost', 27017, username='root', password='root')
db = client['video_db']
videosCollection = db['videos']


@app.route('/')
def index():
    return 'Welcome to the Video API!'

@app.route('/videos')
def get_videos():
    video_list = list(videosCollection.find)
    return jsonify(video_list)

@app.route('/videos/<string:video_id>', methods=['GET'])
def get_video(video_id):
    try:
        # Convert the video_id string to a BSON ObjectId
        video_id = ObjectId(video_id)
        # Find the video metadata document with the matching ObjectId
        video = videosCollection.find_one({'_id': video_id})
        # Check if a video with the specified ID was found
        if video is not None:
            # Convert the ObjectId to a string to include in the JSON response
            video['_id'] = str(video['_id'])
            # Return the video metadata as a JSON response
            return jsonify(video)
        else:
            # Return a 404 error response if the video was not found
            return jsonify({'error': 'Video not found'}), 404
    except errors.InvalidId:
        # Return a 400 error response if the video ID is invalid
        return jsonify({'error': 'Invalid video ID'}), 400

if __name__ == '__main__':
    app.run(debug=True)