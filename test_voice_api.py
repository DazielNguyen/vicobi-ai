#!/usr/bin/env python3
"""
Test Voice Processing API - Upload audio → Get structured JSON
"""
import requests
import sys
from pathlib import Path


def test_voice_processing(audio_file: str, api_url: str = "http://localhost:8000"):
    """Test /process-audio endpoint"""
    
    if not Path(audio_file).exists():
        print(f"❌ File không tồn tại: {audio_file}")
        return False
    
    endpoint = f"{api_url}/api/v1/voices/process-audio"
    
    print("=" * 70)
    print("  🎤 TEST VOICE PROCESSING API")
    print("=" * 70)
    print(f"📁 File: {audio_file}")
    print(f"🌐 Endpoint: {endpoint}")
    print("-" * 70)
    
    try:
        print("⏳ Uploading và xử lý...")
        
        with open(audio_file, "rb") as f:
            files = {"file": (Path(audio_file).name, f, "audio/*")}
            response = requests.post(endpoint, files=files, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ THÀNH CÔNG!")
            print("=" * 70)
            print(f"🆔 Voice ID: {result['voice_id']}")
            print(f"💰 Money Type: {result['money_type']}")
            print(f"🕐 Time: {result['utc_time']}")
            
            print(f"\n📊 TỔNG KẾT:")
            print(f"   Thu nhập:  {result['total_amount']['incomes']:>15,.0f} VND")
            print(f"   Chi tiêu:  {result['total_amount']['expenses']:>15,.0f} VND")
            print(f"   Chênh lệch: {(result['total_amount']['incomes'] - result['total_amount']['expenses']):>14,.0f} VND")
            
            # Incomes
            incomes = result['transactions']['incomes']
            if incomes:
                print(f"\n💵 THU NHẬP ({len(incomes)} giao dịch):")
                for i, t in enumerate(incomes, 1):
                    print(f"   {i}. {t['description'][:50]}")
                    print(f"      → {t['amount']:,.0f} VND ({t['amount_string']})")
            
            # Expenses
            expenses = result['transactions']['expenses']
            if expenses:
                print(f"\n💸 CHI TIÊU ({len(expenses)} giao dịch):")
                for i, t in enumerate(expenses, 1):
                    print(f"   {i}. {t['description'][:50]}")
                    print(f"      → {t['amount']:,.0f} VND ({t['amount_string']})")
            
            print("=" * 70)
            print("✨ Data đã được lưu vào MongoDB!")
            return True
        else:
            print(f"\n❌ LỖI! Status: {response.status_code}")
            try:
                error = response.json()
                print(f"Chi tiết: {error.get('detail', 'Unknown error')}")
            except:
                print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timeout! File quá lớn hoặc server chậm.")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Không thể kết nối đến {api_url}")
        print("   Kiểm tra server: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        return False


def test_health_check(api_url: str = "http://localhost:8000"):
    """Test health check"""
    try:
        response = requests.get(f"{api_url}/api/v1/voices/health-check", timeout=5)
        if response.status_code == 200:
            print("✅ Server online!")
            return True
        return False
    except:
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_voice_api.py <audio_file> [api_url]")
        print("\nVí dụ:")
        print("  python test_voice_api.py audio.mp3")
        print("  python test_voice_api.py recording.m4a http://localhost:8000")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    # Check server
    print("Checking server...")
    if not test_health_check(api_url):
        print("❌ Server không phản hồi!")
        print("\n💡 Khởi động server:")
        print("   cd vicobi-ai")
        print("   source .venv/bin/activate")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    
    print()
    
    # Test processing
    success = test_voice_processing(audio_file, api_url)
    sys.exit(0 if success else 1)
