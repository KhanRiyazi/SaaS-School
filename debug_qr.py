import requests
import base64
from PIL import Image
import io
import sys

API_URL = "http://localhost:8000"

def test_qr_generation():
    print("Testing QR Code Generation...")
    
    test_data = {
        "name": "Test User",
        "contact_number": "+1234567890",
        "address": "123 Test Street",
        "social_links": [],
        "expires_in_days": 30
    }
    
    try:
        response = requests.post(f"{API_URL}/api/generate-qr", json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ QR Code generated successfully!")
            print(f"Short Code: {data['short_code']}")
            print(f"QR Code data length: {len(data['qr_code'])} characters")
            
            # Try to decode and save
            try:
                qr_data = base64.b64decode(data['qr_code'])
                print(f"Decoded data length: {len(qr_data)} bytes")
                
                qr_image = Image.open(io.BytesIO(qr_data))
                print(f"Image size: {qr_image.size}")
                print(f"Image mode: {qr_image.mode}")
                
                # Save the image
                qr_image.save("test_qr_output.png")
                print("✅ QR Code saved as 'test_qr_output.png'")
                
                return True
            except Exception as e:
                print(f"❌ Error decoding/saving QR code: {str(e)}")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_qr_generation()
    sys.exit(0 if success else 1)