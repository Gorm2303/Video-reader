import pytest
from bson.objectid import ObjectId
from pymongo import MongoClient
from app import app, db, videosCollection

@pytest.fixture(scope='module')
def test_client():
    flask_app = app
    testing_client = flask_app.test_client()
    # Establish a test MongoDB connection and populate the database with test data
    test_client = MongoClient('mongodb+srv://admin:admin@cluster0.acahawh.mongodb.net/?retryWrites=true&w=majority')
    test_db = test_client['testdb']
    test_collection = test_db['video_metadata']
    test_data = [
        {'_id': ObjectId('60e2538a0b140ddc5ec78d95'), 'title': 'Test Video 1', 'description': 'This is a test'},
        {'_id': ObjectId('60e253d90b140ddc5ec78d96'), 'title': 'Test Video 2', 'description': 'This is also a test'},
        {'_id': ObjectId('60e254230b140ddc5ec78d97'), 'title': 'Test Video 3', 'description': 'This is yet another test'},
    ]
    test_collection.insert_many(test_data)
    # Use the test MongoDB connection and database for the Flask app
    db = test_db
    videosCollection = test_collection
    yield testing_client
    # Remove the test data from the test database after the tests are complete
    test_collection.delete_many({})

def test_get_videos(test_client):
    response = test_client.get('/videos')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert len(response.json) == 3
    assert response.json[0]['title'] == 'Test Video 1'

def test_get_video(test_client):
    # Test with a valid video ID
    response = test_client.get('/videos/60e2538a0b140ddc5ec78d95')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json['title'] == 'Test Video 1'

    # Test with an invalid video ID
    response = test_client.get('/videos/invalid_id')
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    assert response.json['error'] == 'Invalid video ID'

    # Test with a nonexistent video ID
    response = test_client.get('/videos/60e2e4c10b140ddc5ec78d9e')
    assert response.status_code == 404
    assert response.content_type == 'application/json'
    assert response.json['error'] == 'Video not found'
