import pytest
import os
import json
from bson.objectid import ObjectId
from pymongo import MongoClient
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def setup_db():
    # Connect to MongoDB database
    mongo_uri = os.environ.get("MONGO_URI")
    mongo_client = MongoClient(mongo_uri)
    db = mongo_client['video_db']
    videos_collection = db['videos']

    # Insert sample data
    sample_video = {'title': 'Test Video', 'description': 'This is a test video'}
    inserted_video = videos_collection.insert_one(sample_video)

    return videos_collection, inserted_video

def teardown_db(videos_collection, inserted_video):
    # Clean up the test data
    videos_collection.delete_one({'_id': inserted_video.inserted_id})

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Welcome to the Video API!' in response.get_data(as_text=True)

def test_get_videos(client):
    response = client.get('/api/v1/videos')
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert isinstance(data, list)

def test_get_video(client):
    videos_collection, inserted_video = setup_db()

    video_id = str(inserted_video.inserted_id)
    response = client.get(f'/api/v1/videos/{video_id}')
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert data['_id'] == video_id

    teardown_db(videos_collection, inserted_video)

def test_get_video_invalid_id(client):
    response = client.get('/api/v1/videos/invalid_id')
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert data['error'] == 'Invalid video ID'

def test_get_video_not_found(client):
    non_existent_id = str(ObjectId())
    response = client.get(f'/api/v1/videos/{non_existent_id}')
    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert data['error'] == 'Video not found'

