import os
import requests
from app.face.engine import FaceEngine

class ResultRanker:
    def __init__(self):
        self.face_engine = FaceEngine()

    def download_image(self, url: str, save_path: str):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
        except Exception:
            pass
        return False

    def rank_candidates(self, query_image_path: str, candidates: list):
        """
        Ranks candidates by comparing their thumbnail face to the query face.
        Optimized: Only processes the top 8 candidates. Removed threading to fix OpenCV thread-safety issues.
        """
        valid_candidates = []
        os.makedirs("data/temporary", exist_ok=True)
        
        # Only process the top 8 candidates to save time
        for idx, candidate in enumerate(candidates[:8]):
            thumbnail_url = candidate.get("thumbnail")
            if not thumbnail_url:
                continue
                
            temp_path = f"data/temporary/candidate_{idx}.jpg"
            if self.download_image(thumbnail_url, temp_path):
                # Verify match
                result = self.face_engine.verify_match(query_image_path, temp_path)
                
                if result.get("success") and result.get("verified"):
                    candidate["distance"] = result.get("distance")
                    valid_candidates.append(candidate)
                    
        # Sort by distance (ascending)
        valid_candidates.sort(key=lambda x: x.get("distance", 999))
        
        return valid_candidates
