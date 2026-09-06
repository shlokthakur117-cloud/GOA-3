import time
from app.face.engine import FaceEngine
from app.search.engine import SearchProvider
from app.search.ranker import ResultRanker
from app.verification.hashing import generate_fingerprint
from app.blockchain.client import BlockchainClient

class VerificationPipeline:
    def __init__(self):
        self.face_engine = FaceEngine()
        self.search_provider = SearchProvider()
        self.ranker = ResultRanker()
        self.blockchain = BlockchainClient()

    def run(self, image_path: str):
        print(f"[1/7] Loading input image: {image_path}")
        # Detect Face
        print("[2/7] Detecting face...")
        detect_res = self.face_engine.detect_face(image_path)
        if not detect_res.get("success") or detect_res.get("faces_detected") == 0:
            print("❌ Error: No face detected in the image.")
            if detect_res.get("error"):
                print(f"Details: {detect_res['error']}")
            return False
            
        print(f"✅ Face detected! (Count: {detect_res['faces_detected']})")
        
        # Searching
        print("[3/7] Searching web/social sources (Genuine Reverse Image Search)...")
        search_res = self.search_provider.search(image_path)
        if not search_res.get("success"):
            print(f"❌ Error during search: {search_res.get('error')}")
            return False
            
        candidates = search_res.get("candidates", [])
        print(f"✅ Found {len(candidates)} visual matches from SerpApi.")
        if len(candidates) == 0:
            print("❌ Error: No visual matches returned from Search Engine.")
            return False
        
        # Matching
        print("[4/7] Matching candidates against input face...")
        valid_candidates = self.ranker.rank_candidates(image_path, candidates)
        
        if not valid_candidates:
            print("❌ No matching social posts found with the same face.")
            return False
            
        best_match = valid_candidates[0]
        print(f"✅ Found best match!")
        print(f"   Source: {best_match['source_url']}")
        print(f"   Similarity Distance: {best_match.get('distance', 'N/A')}")
        
        # Fingerprint
        print("[5/7] Generating deterministic fingerprint...")
        timestamp = int(time.time())
        fingerprint, fingerprint_hex = generate_fingerprint(
            source_url=best_match['source_url'],
            title=best_match['title'],
            timestamp=timestamp
        )
        print(f"✅ Fingerprint generated: {fingerprint_hex}")
        
        # Blockchain write
        print("[6/7] Writing fingerprint to blockchain...")
        tx_res = self.blockchain.store_verification(
            fingerprint_hex=fingerprint_hex,
            source=best_match['source_url'],
            timestamp=timestamp
        )
        if not tx_res.get("success"):
            print("❌ Error writing to blockchain.")
            return False
            
        print(f"✅ Transaction successful! Hash: {tx_res.get('transaction_hash')}")
        
        # Re-verify
        print("[7/7] Re-verifying blockchain record...")
        verify_res = self.blockchain.get_verification(fingerprint_hex)
        
        if not verify_res.get("success"):
            print(f"❌ Error reading from blockchain: {verify_res.get('error')}")
            return False
            
        print(f"✅ Record found on chain!")
        print(f"   Stored Fingerprint: {verify_res['fingerprint']}")
        
        # Compare
        if verify_res['fingerprint'] == fingerprint_hex:
            print("\n🎉 VERIFICATION PASSED: Local Hash == On-Chain Hash 🎉")
            return True
        else:
            print("\n❌ VERIFICATION FAILED: Data tampered!")
            return False
