import os
import requests
from dotenv import load_dotenv

load_dotenv()

class SearchProvider:
    def __init__(self):
        self.api_key = os.getenv("SEARCH_API_KEY")

    def _upload_image_temporarily(self, image_path: str) -> str:
        """
        Uploads the image to a temporary anonymous file host (freeimage.host)
        to get a public URL for the reverse image search engine.
        """
        try:
            with open(image_path, "rb") as f:
                data_payload = {'key': '6d207e02198a847aa98d0a2a901485a5', 'action': 'upload'}
                response = requests.post("https://freeimage.host/api/1/upload", data=data_payload, files={"source": f}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data['image']['url']
            else:
                raise Exception(f"Failed to upload image. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"Temporary image hosting failed: {e}")

    def search(self, image_path: str):
        """
        Performs a genuine reverse image search using SerpApi (Google Lens).
        """
        if not self.api_key or self.api_key == "your_serpapi_key_here":
            return {"success": False, "error": "SEARCH_API_KEY is not configured."}

        try:
            # 1. Get a public URL for the local image
            public_url = self._upload_image_temporarily(image_path)
            
            # 2. Perform SerpApi Google Lens Search
            params = {
                "engine": "google_lens",
                "url": public_url,
                "api_key": self.api_key
            }
            
            search_response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            if search_response.status_code != 200:
                return {"success": False, "error": f"SerpApi returned {search_response.status_code}"}
                
            data = search_response.json()
            
            # 3. Extract Visual Matches (the candidates)
            visual_matches = data.get("visual_matches", [])
            candidates = []
            
            for match in visual_matches:
                candidates.append({
                    "title": match.get("title", ""),
                    "source_domain": match.get("source", ""),
                    "source_url": match.get("link", ""),
                    "thumbnail": match.get("thumbnail", ""),
                    "original_image": match.get("thumbnail", "") # Lens mostly provides thumbnails
                })
                
            return {
                "success": True,
                "search_method": "SerpApi Google Lens",
                "candidates_found": len(candidates),
                "candidates": candidates
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
