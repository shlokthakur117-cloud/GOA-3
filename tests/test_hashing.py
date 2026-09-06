from app.verification.hashing import generate_fingerprint

def test_generate_fingerprint_deterministic():
    f1, hex1 = generate_fingerprint("http://test.com", "Test Title", 12345)
    f2, hex2 = generate_fingerprint("http://test.com", "Test Title", 12345)
    
    # Must be deterministic
    assert f1 == f2
    assert hex1 == hex2
    assert hex1.startswith("0x")

def test_generate_fingerprint_tamper():
    f1, hex1 = generate_fingerprint("http://test.com", "Test Title", 12345)
    
    # Tampered data
    f2, hex2 = generate_fingerprint("http://test.com", "Tampered Title", 12345)
    
    # Must change if data changes
    assert f1 != f2
    assert hex1 != hex2
