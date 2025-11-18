#!/usr/bin/env python3
"""
Script test API transcribe audio với chuyển đổi format tự động
"""
import requests
import sys
import os
from pathlib import Path


def test_transcribe_api(audio_file: str, api_url: str = "http://localhost:8000"):
    """
    Test API transcribe với file âm thanh
    
    Args:
        audio_file: Đường dẫn đến file âm thanh
        api_url: URL của API server
    """
    # Kiểm tra file tồn tại
    if not os.path.exists(audio_file):
        print(f"❌ File không tồn tại: {audio_file}")
        return False
    
    file_path = Path(audio_file)
    file_size = file_path.stat().st_size / 1024  # KB
    
    print(f"📁 File: {file_path.name}")
    print(f"📊 Kích thước: {file_size:.2f} KB")
    print(f"🔧 Format: {file_path.suffix}")
    print(f"🌐 API: {api_url}/api/v1/voices/transcribe")
    print("-" * 60)
    
    # Gửi request
    endpoint = f"{api_url}/api/v1/voices/transcribe"
    
    try:
        print("⏳ Đang upload và xử lý...")
        
        with open(audio_file, "rb") as f:
            files = {"file": (file_path.name, f, "audio/*")}
            response = requests.post(endpoint, files=files, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ THÀNH CÔNG!")
            print("-" * 60)
            print(f"🎯 Transcription:")
            print(f"   {result.get('transcription', 'N/A')}")
            print(f"\n📝 Chi tiết:")
            print(f"   - Model: {result.get('model', 'N/A')}")
            print(f"   - Original file: {result.get('original_filename', 'N/A')}")
            print(f"   - Format: {result.get('file_format', 'N/A')}")
            print(f"   - Success: {result.get('success', False)}")
            print("-" * 60)
            return True
        else:
            print(f"\n❌ LỖI! Status code: {response.status_code}")
            try:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"   Chi tiết: {error_detail}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ LỖI: Request timeout! File có thể quá lớn hoặc server chậm.")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ LỗI: Không thể kết nối đến {api_url}")
        print("   Đảm bảo server đang chạy với: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        return False


def test_health_check(api_url: str = "http://localhost:8000"):
    """Test health check endpoint"""
    try:
        response = requests.get(f"{api_url}/api/v1/voices/health-check", timeout=5)
        if response.status_code == 200:
            print("✅ Server đang hoạt động!")
            return True
        else:
            print(f"⚠️  Server response code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server không phản hồi: {str(e)}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_api_transcribe.py <audio_file> [api_url]")
        print("\nVí dụ:")
        print("  python test_api_transcribe.py audio.mp3")
        print("  python test_api_transcribe.py audio.aac http://localhost:8000")
        print("\nFormat hỗ trợ: mp3, aac, m4a, mp2, ogg, flac, wav, wma, opus")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    print("=" * 60)
    print("  🎤 TEST API VOICE TRANSCRIPTION")
    print("=" * 60)
    print()
    
    # Test health check trước
    print("1️⃣  Kiểm tra server...")
    if not test_health_check(api_url):
        print("\n💡 Hãy khởi động server với:")
        print("   cd vicobi-ai")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    
    print("\n2️⃣  Test transcription API...")
    print()
    success = test_transcribe_api(audio_file, api_url)
    
    print()
    if success:
        print("🎉 Test hoàn tất thành công!")
        sys.exit(0)
    else:
        print("⚠️  Test thất bại!")
        sys.exit(1)


if __name__ == "__main__":
    main()
