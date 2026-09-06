import argparse
import sys
from app.pipeline import VerificationPipeline

def main():
    parser = argparse.ArgumentParser(description="Face Identification & Blockchain Verification")
    parser.add_argument("--image", required=True, help="Path to the input face image")
    
    args = parser.parse_args()
    
    try:
        pipeline = VerificationPipeline()
        success = pipeline.run(args.image)
        
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
