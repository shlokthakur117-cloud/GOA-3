import os
import pytest
import requests
from app.face.engine import FaceEngine

@pytest.fixture(scope="module")
def sample_images():
    # Download a couple of sample images for testing
    img1_url = "https://raw.githubusercontent.com/serengil/deepface/master/tests/dataset/img1.jpg"
    img2_url = "https://raw.githubusercontent.com/serengil/deepface/master/tests/dataset/img2.jpg"
    
    os.makedirs("data/temporary", exist_ok=True)
    img1_path = "data/temporary/test_img1.jpg"
    img2_path = "data/temporary/test_img2.jpg"
    
    if not os.path.exists(img1_path):
        with open(img1_path, "wb") as f:
            f.write(requests.get(img1_url).content)
    if not os.path.exists(img2_path):
        with open(img2_path, "wb") as f:
            f.write(requests.get(img2_url).content)
            
    yield img1_path, img2_path

def test_face_detection(sample_images):
    img1_path, _ = sample_images
    engine = FaceEngine()
    result = engine.detect_face(img1_path)
    assert result["success"] is True
    assert result["faces_detected"] >= 1

def test_generate_embedding(sample_images):
    img1_path, _ = sample_images
    engine = FaceEngine()
    result = engine.generate_embedding(img1_path)
    assert result["success"] is True
    assert "embedding" in result
    assert result["dimension"] > 0

def test_verify_match(sample_images):
    img1_path, img2_path = sample_images
    engine = FaceEngine()
    # img1 and img2 are the same person in deepface test dataset
    result = engine.verify_match(img1_path, img2_path)
    assert result["success"] is True
    assert result["verified"] is True
