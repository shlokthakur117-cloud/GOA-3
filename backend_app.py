import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from app.face.engine import FaceEngine
from app.search.engine import SearchProvider
from app.search.ranker import ResultRanker
from app.verification.hashing import generate_fingerprint

app = Flask(__name__)
# Allow requests from our local HTML file
CORS(app)

face_engine = FaceEngine()
search_provider = SearchProvider()
ranker = ResultRanker()

os.makedirs("data/temporary", exist_ok=True)

@app.route('/api/process', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image provided"}), 400
            
        file = request.files['image']
        filepath = os.path.join("data/temporary", secure_filename(file.filename))
        file.save(filepath)
        
        print(f"Processing image: {filepath}")
        
        # 1. Detect
        detect_res = face_engine.detect_face(filepath)
        if not detect_res.get("success") or detect_res.get("faces_detected") == 0:
            return jsonify({"success": False, "error": "No face detected in the image."})
            
        # 2. Search
        search_res = search_provider.search(filepath)
        if not search_res.get("success"):
            return jsonify({"success": False, "error": search_res.get("error")})
            
        # 3. Match
        candidates = search_res.get("candidates", [])
        valid_candidates = ranker.rank_candidates(filepath, candidates)
        
        if not valid_candidates:
            return jsonify({"success": False, "error": "No matching posts found with the same face."})
            
        best_match = valid_candidates[0]
        
        # 4. Fingerprint
        timestamp = int(time.time())
        fingerprint, fingerprint_hex = generate_fingerprint(
            source_url=best_match['source_url'],
            title=best_match['title'],
            timestamp=timestamp
        )
        
        return jsonify({
            "success": True,
            "source": best_match['source_url'],
            "timestamp": timestamp,
            "fingerprint": fingerprint_hex,
            "distance": best_match.get('distance')
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("Starting AI Backend on http://localhost:5000")
    app.run(port=5000)
