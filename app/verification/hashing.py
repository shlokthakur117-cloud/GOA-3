import hashlib
import json

def generate_fingerprint(source_url: str, title: str, timestamp: int):
    """
    Generates a deterministic SHA-256 fingerprint for a post.
    Canonicalization: JSON serialize a sorted dictionary.
    """
    canonical_data = {
        "source": source_url.strip().lower(),
        "title": title.strip().lower(),
        "timestamp": timestamp
    }
    
    # We serialize with keys sorted to ensure deterministic output
    json_str = json.dumps(canonical_data, sort_keys=True, separators=(',', ':'))
    
    # Create SHA-256 hash
    fingerprint = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    return fingerprint, f"0x{fingerprint}"
