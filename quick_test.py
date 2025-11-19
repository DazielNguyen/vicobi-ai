#!/usr/bin/env python3
"""
Quick test script để kiểm tra API transcribe endpoint
"""
import requests
import sys


def test_health_check(api_url="http://localhost:8000"):
    """Test health check endpoint"""
    print("1️⃣  Testing health check...")
    try:
        response = requests.get(f"{api_url}/api/v1/voices/health-check", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is healthy!")
            return True
        else:
            print(f"   ⚠️  Server returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_endpoints(api_url="http://localhost:8000"):
    """List available endpoints"""
    print("\n2️⃣  Available endpoints:")
    print(f"   POST {api_url}/api/v1/voices/transcribe")
    print(f"   GET  {api_url}/api/v1/voices/health-check")
    print(f"   POST {api_url}/api/v1/voices/process")
    print(f"   POST {api_url}/api/whisper/transcribe")


def main():
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("=" * 70)
    print("  🎤 VOICE API QUICK TEST")
    print("=" * 70)
    print(f"\nAPI URL: {api_url}\n")
    
    if not test_health_check(api_url):
        print("\n❌ Server is not running!")
        print("\n💡 Start server with:")
        print("   cd vicobi-ai")
        print("   source .venv/bin/activate")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    
    test_endpoints(api_url)
    
    print("\n3️⃣  Ready to test transcription!")
    print("\n📝 Usage examples:")
    print("   # Using curl")
    print(f'   curl -X POST "{api_url}/api/v1/voices/transcribe" \\')
    print('     -F "file=@audio.mp3"')
    print("\n   # Using test script")
    print("   python test_api_transcribe.py audio.mp3")
    
    print("\n✨ Server is ready!")
    print("=" * 70)


if __name__ == "__main__":
    main()
