from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import string
import random
import json
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import base64
import qrcode
from io import BytesIO
import os
import urllib.parse
import signal
import sys

# Database setup
DATABASE_URL = "sqlite:///./url_shortener.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class URLMapping(Base):
    __tablename__ = "url_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True)
    original_url = Column(Text)
    type = Column(String)
    user_id = Column(String, nullable=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
class ProfileData(Base):
    __tablename__ = "profile_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    name = Column(String)
    title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    email = Column(String, nullable=True)
    contact_number = Column(String)
    address = Column(Text)
    bio = Column(Text, nullable=True)
    social_links = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Function to add missing columns to existing table
def add_missing_columns():
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('profile_data')]
    
    with engine.connect() as conn:
        if 'title' not in existing_columns:
            conn.execute('ALTER TABLE profile_data ADD COLUMN title VARCHAR')
        if 'company' not in existing_columns:
            conn.execute('ALTER TABLE profile_data ADD COLUMN company VARCHAR')
        if 'bio' not in existing_columns:
            conn.execute('ALTER TABLE profile_data ADD COLUMN bio TEXT')
        conn.commit()

# Create tables and migrate if needed
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    add_missing_columns()
except Exception as e:
    print(f"⚠️ Database error: {e}")

app = FastAPI(title="Digital Business Card - URL Shortener & QR Code Generator")

# Request models
class ShortenURLRequest(BaseModel):
    url: str
    custom_code: Optional[str] = None
    expires_in_days: int = 30

class QRCodeRequest(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    contact_number: str
    address: str
    bio: Optional[str] = None
    social_links: List[dict] = []
    expires_in_days: int = 30

def generate_short_code(length=6):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_user_id():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

# Professional Digital Business Card Template
PROFESSIONAL_CARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="description" content="Digital Business Card - {name}">
    <title>{name} | Professional Digital Business Card</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }}
        
        /* Animated background */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="rgba(255,255,255,0.05)" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,154.7C960,171,1056,181,1152,165.3C1248,149,1344,107,1392,85.3L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') repeat-x bottom;
            background-size: 1440px 100px;
            opacity: 0.3;
            pointer-events: none;
        }}
        
        .business-card {{
            max-width: 480px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 40px;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            z-index: 1;
        }}
        
        .business-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 35px 60px -15px rgba(0, 0, 0, 0.3);
        }}
        
        /* Header Section */
        .card-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px 35px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .card-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1%, transparent 1%);
            background-size: 30px 30px;
            animation: shimmer 30s linear infinite;
        }}
        
        @keyframes shimmer {{
            from {{ transform: translate(0, 0); }}
            to {{ transform: translate(50px, 50px); }}
        }}
        
        .avatar-wrapper {{
            position: relative;
            display: inline-block;
            margin-bottom: 20px;
        }}
        
        .avatar {{
            width: 110px;
            height: 110px;
            background: linear-gradient(135deg, #fff, #f8f9fa);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 55px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
            transition: transform 0.3s ease;
            border: 4px solid rgba(255,255,255,0.3);
        }}
        
        .avatar:hover {{
            transform: scale(1.05);
        }}
        
        .status-badge {{
            position: absolute;
            bottom: 5px;
            right: 5px;
            width: 20px;
            height: 20px;
            background: #4ade80;
            border-radius: 50%;
            border: 3px solid white;
            z-index: 2;
        }}
        
        .name {{
            font-size: 28px;
            font-weight: 800;
            color: white;
            margin-bottom: 8px;
            position: relative;
            z-index: 1;
            letter-spacing: -0.5px;
        }}
        
        .title {{
            font-size: 16px;
            color: rgba(255,255,255,0.95);
            margin-bottom: 5px;
            position: relative;
            z-index: 1;
            font-weight: 500;
        }}
        
        .company {{
            font-size: 14px;
            color: rgba(255,255,255,0.85);
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }}
        
        .badge-container {{
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 15px;
            position: relative;
            z-index: 1;
        }}
        
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 11px;
            font-weight: 600;
            color: white;
            letter-spacing: 0.3px;
        }}
        
        /* Main Content */
        .card-main {{
            padding: 30px;
        }}
        
        .section-title {{
            font-size: 13px;
            font-weight: 700;
            color: #667eea;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .info-grid {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 30px;
        }}
        
        .info-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 14px 18px;
            background: #f8f9fa;
            border-radius: 16px;
            transition: all 0.3s ease;
            cursor: pointer;
            border: 1px solid transparent;
        }}
        
        .info-item:hover {{
            background: #e9ecef;
            transform: translateX(5px);
            border-color: #667eea;
        }}
        
        .info-icon {{
            width: 40px;
            height: 40px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: #667eea;
            transition: transform 0.3s ease;
        }}
        
        .info-item:hover .info-icon {{
            transform: scale(1.05);
        }}
        
        .info-content {{
            flex: 1;
        }}
        
        .info-label {{
            font-size: 10px;
            font-weight: 600;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 4px;
        }}
        
        .info-value {{
            font-size: 15px;
            font-weight: 600;
            color: #212529;
            word-break: break-word;
        }}
        
        .info-value a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        /* Social Links */
        .social-section {{
            margin-bottom: 30px;
        }}
        
        .social-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        
        .social-btn {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 16px;
            border-radius: 14px;
            text-decoration: none;
            color: white;
            font-weight: 600;
            font-size: 13px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .social-btn::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.5s, height 0.5s;
        }}
        
        .social-btn:hover::before {{
            width: 300px;
            height: 300px;
        }}
        
        .social-btn span {{
            position: relative;
            z-index: 1;
        }}
        
        .social-btn i {{
            font-size: 18px;
            position: relative;
            z-index: 1;
        }}
        
        .social-btn:hover {{
            transform: translateY(-2px);
            filter: brightness(1.05);
        }}
        
        .btn-facebook {{ background: #1877f2; }}
        .btn-instagram {{ background: linear-gradient(45deg, #f09433, #d62976, #962fbf); }}
        .btn-twitter {{ background: #1da1f2; }}
        .btn-linkedin {{ background: #0077b5; }}
        .btn-whatsapp {{ background: #25d366; }}
        .btn-telegram {{ background: #0088cc; }}
        .btn-github {{ background: #181717; }}
        .btn-website {{ background: #6c757d; }}
        
        /* Action Buttons */
        .action-buttons {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .action-btn {{
            padding: 15px;
            border: none;
            border-radius: 16px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
        }}
        
        .action-btn-primary {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .action-btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }}
        
        .action-btn-secondary {{
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }}
        
        .action-btn-secondary:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }}
        
        /* Footer */
        .card-footer {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px 30px;
            text-align: center;
            border-top: 1px solid rgba(0,0,0,0.05);
        }}
        
        .expiry-info {{
            font-size: 11px;
            color: #6c757d;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        
        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 12px;
        }}
        
        .footer-links a {{
            color: #667eea;
            text-decoration: none;
            font-size: 12px;
            font-weight: 500;
            transition: opacity 0.3s;
        }}
        
        .footer-links a:hover {{
            opacity: 0.7;
        }}
        
        .copyright {{
            font-size: 10px;
            color: #adb5bd;
        }}
        
        /* QR Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        
        .modal-content {{
            background: white;
            border-radius: 30px;
            padding: 30px;
            text-align: center;
            max-width: 90%;
        }}
        
        /* Responsive */
        @media (max-width: 480px) {{
            body {{
                padding: 12px;
            }}
            
            .card-header {{
                padding: 30px 20px 25px;
            }}
            
            .card-main {{
                padding: 20px;
            }}
            
            .card-footer {{
                padding: 15px 20px;
            }}
            
            .avatar {{
                width: 90px;
                height: 90px;
                font-size: 45px;
            }}
            
            .name {{
                font-size: 24px;
            }}
            
            .social-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .loading {{
            animation: pulse 1.5s ease-in-out infinite;
        }}
    </style>
</head>
<body>
    <div class="business-card">
        <!-- Header -->
        <div class="card-header">
            <div class="avatar-wrapper">
                <div class="avatar">{avatar_icon}</div>
                <div class="status-badge"></div>
            </div>
            <div class="name">{name}</div>
            {title_html}
            {company_html}
            <div class="badge-container">
                <div class="badge"><i class="fas fa-id-card"></i> Digital Card</div>
                <div class="badge"><i class="fas fa-shield-alt"></i> Verified</div>
                <div class="badge"><i class="fas fa-qrcode"></i> Scan to Connect</div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="card-main">
            <div class="section-title">
                <i class="fas fa-address-card"></i>
                <span>Contact Information</span>
            </div>
            <div class="info-grid">
                {email_html}
                <div class="info-item" onclick="window.location.href='tel:{phone}'">
                    <div class="info-icon"><i class="fas fa-phone-alt"></i></div>
                    <div class="info-content">
                        <div class="info-label">Phone</div>
                        <div class="info-value">{phone}</div>
                    </div>
                    <i class="fas fa-chevron-right" style="color: #cbd5e1;"></i>
                </div>
                <div class="info-item" onclick="window.open('https://maps.google.com/?q={address_encoded}', '_blank')">
                    <div class="info-icon"><i class="fas fa-map-marker-alt"></i></div>
                    <div class="info-content">
                        <div class="info-label">Address</div>
                        <div class="info-value">{address}</div>
                    </div>
                    <i class="fas fa-external-link-alt" style="color: #cbd5e1; font-size: 12px;"></i>
                </div>
            </div>
            
            <div class="social-section">
                <div class="section-title">
                    <i class="fas fa-share-alt"></i>
                    <span>Connect With Me</span>
                </div>
                <div class="social-grid">
                    {social_buttons}
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="action-btn action-btn-primary" onclick="saveContact()">
                    <i class="fas fa-save"></i> Save to Contacts
                </button>
                <button class="action-btn action-btn-secondary" onclick="shareCard()">
                    <i class="fas fa-share-alt"></i> Share Business Card
                </button>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="card-footer">
            <div class="expiry-info">
                <i class="far fa-clock"></i>
                <span>Valid until {expires_date}</span>
            </div>
            <div class="footer-links">
                <a href="#" onclick="showQR()"><i class="fas fa-qrcode"></i> View QR Code</a>
                <a href="#" onclick="reportIssue()"><i class="fas fa-flag"></i> Report Issue</a>
            </div>
            <div class="copyright">
                <i class="far fa-copyright"></i> 2024 Digital Business Card | All rights reserved
            </div>
        </div>
    </div>
    
    <!-- QR Modal -->
    <div id="qrModal" class="modal" onclick="closeModal()">
        <div class="modal-content" onclick="event.stopPropagation()">
            <i class="fas fa-qrcode" style="font-size: 48px; color: #667eea; margin-bottom: 15px;"></i>
            <img id="qrImage" class="modal-img" style="max-width: 100%; border-radius: 20px;" alt="QR Code">
            <button class="action-btn action-btn-primary" style="margin-top: 20px;" onclick="closeModal()">Close</button>
        </div>
    </div>
    
    <script>
        const qrCodeData = "{qr_code_data}";
        
        function saveContact() {{
            const vCard = `BEGIN:VCARD
VERSION:3.0
FN:{name}
{title_vcard}{company_vcard}{email_vcard}TEL;TYPE=CELL:{phone}
ADR;TYPE=WORK:{address}
URL:{profile_url}
REV:{timestamp}
END:VCARD`;
            
            const blob = new Blob([vCard], {{type: 'text/vcard'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{name_clean}.vcf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            // Show success notification
            showNotification('✅ Contact saved successfully!');
        }}
        
        function shareCard() {{
            if (navigator.share) {{
                navigator.share({{
                    title: '{name} - Digital Business Card',
                    text: 'Check out my professional digital business card!',
                    url: window.location.href
                }}).catch(() => {{
                    copyToClipboard();
                }});
            }} else {{
                copyToClipboard();
            }}
        }}
        
        function copyToClipboard() {{
            navigator.clipboard.writeText(window.location.href).then(() => {{
                showNotification('✅ Link copied to clipboard!');
            }});
        }}
        
        function showQR() {{
            const modal = document.getElementById('qrModal');
            const qrImage = document.getElementById('qrImage');
            if (qrCodeData) {{
                qrImage.src = 'data:image/png;base64,' + qrCodeData;
            }}
            modal.style.display = 'flex';
        }}
        
        function closeModal() {{
            document.getElementById('qrModal').style.display = 'none';
        }}
        
        function reportIssue() {{
            showNotification('📧 For support, please contact your provider.');
        }}
        
        function showNotification(message) {{
            // Simple alert for now - can be enhanced with custom toast
            alert(message);
        }}
        
        // Add smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth' }});
                }}
            }});
        }});
    </script>
</body>
</html>
"""

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Professional Digital Business Card API", 
        "status": "active",
        "version": "4.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/shorten-url")
async def shorten_url(request: ShortenURLRequest):
    db = SessionLocal()
    
    try:
        short_code = request.custom_code if request.custom_code else generate_short_code()
        
        if request.custom_code:
            existing = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
            if existing:
                raise HTTPException(status_code=400, detail="Custom code already taken")
        
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
        
        url_mapping = URLMapping(
            short_code=short_code,
            original_url=request.url,
            type="url",
            clicks=0,
            expires_at=expires_at
        )
        db.add(url_mapping)
        db.commit()
        
        return {
            "short_code": short_code,
            "short_url": f"/{short_code}",
            "original_url": request.url,
            "expires_at": expires_at.isoformat(),
            "clicks": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/generate-qr")
async def generate_qr(request: QRCodeRequest):
    db = SessionLocal()
    
    try:
        user_id = generate_user_id()
        short_code = generate_short_code()
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
        
        profile = ProfileData(
            user_id=user_id,
            name=request.name,
            title=request.title,
            company=request.company,
            email=request.email,
            contact_number=request.contact_number,
            address=request.address,
            bio=request.bio,
            social_links=json.dumps(request.social_links)
        )
        db.add(profile)
        
        base_url = "http://localhost:8000"
        profile_url = f"{base_url}/{short_code}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(profile_url)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="#667eea", back_color="white")
        
        buffered = BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        url_mapping = URLMapping(
            short_code=short_code,
            original_url=f"/api/profile/{short_code}",
            type="profile",
            user_id=user_id,
            clicks=0,
            expires_at=expires_at
        )
        db.add(url_mapping)
        db.commit()
        
        return {
            "user_id": user_id,
            "short_code": short_code,
            "profile_url": f"/{short_code}",
            "qr_code": qr_base64,
            "expires_at": expires_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/profile/{short_code}", response_class=HTMLResponse)
async def get_profile_page(short_code: str):
    db = SessionLocal()
    
    try:
        url_mapping = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
        
        if not url_mapping:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        if url_mapping.expires_at < datetime.utcnow():
            raise HTTPException(status_code=404, detail="Profile has expired")
        
        url_mapping.clicks += 1
        db.commit()
        
        profile = db.query(ProfileData).filter(ProfileData.user_id == url_mapping.user_id).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile data not found")
        
        social_links = json.loads(profile.social_links) if profile.social_links else []
        
        # Generate QR code for modal
        base_url = "http://localhost:8000"
        profile_url = f"{base_url}/{short_code}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(profile_url)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="#667eea", back_color="white")
        
        buffered = BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        social_buttons_html = ""
        platform_config = {
            "facebook": ("fab fa-facebook-f", "Facebook", "btn-facebook"),
            "instagram": ("fab fa-instagram", "Instagram", "btn-instagram"),
            "twitter": ("fab fa-twitter", "Twitter", "btn-twitter"),
            "linkedin": ("fab fa-linkedin-in", "LinkedIn", "btn-linkedin"),
            "whatsapp": ("fab fa-whatsapp", "WhatsApp", "btn-whatsapp"),
            "telegram": ("fab fa-telegram-plane", "Telegram", "btn-telegram"),
            "github": ("fab fa-github", "GitHub", "btn-github"),
            "website": ("fas fa-globe", "Website", "btn-website")
        }
        
        for link in social_links:
            platform = link.get('platform', '').lower()
            url = link.get('url', '')
            if url and platform in platform_config:
                icon, name, btn_class = platform_config[platform]
                social_buttons_html += f'''
                <a href="{url}" class="social-btn {btn_class}" target="_blank" rel="noopener noreferrer">
                    <i class="{icon}"></i>
                    <span>{name}</span>
                </a>
                '''
        
        if not social_buttons_html:
            social_buttons_html = '<p style="color: #6c757d; text-align: center; grid-column: 1/-1;">No social links added</p>'
        
        title_html = f'<div class="title">{profile.title}</div>' if profile.title else ''
        company_html = f'<div class="company">{profile.company}</div>' if profile.company else ''
        
        title_vcard = f"TITLE:{profile.title}\n" if profile.title else ""
        company_vcard = f"ORG:{profile.company}\n" if profile.company else ""
        
        email_html = ""
        email_vcard = ""
        if profile.email:
            email_html = f'''
            <div class="info-item" onclick="window.location.href='mailto:{profile.email}'">
                <div class="info-icon"><i class="fas fa-envelope"></i></div>
                <div class="info-content">
                    <div class="info-label">Email</div>
                    <div class="info-value">{profile.email}</div>
                </div>
                <i class="fas fa-chevron-right" style="color: #cbd5e1;"></i>
            </div>
            '''
            email_vcard = f"EMAIL:{profile.email}\n"
        
        address_encoded = urllib.parse.quote(profile.address)
        
        # Determine avatar icon based on gender/name
        avatar_icon = "👤"
        name_lower = profile.name.lower()
        if any(gender in name_lower for gender in ['mr.', 'mr ', 'mohammad', 'ahmed', 'ali', 'rizwan']):
            avatar_icon = "👨‍💼"
        elif any(gender in name_lower for gender in ['ms.', 'mrs.', 'miss', 'fatima', 'ayesha']):
            avatar_icon = "👩‍💼"
        else:
            avatar_icon = "👤"
        
        html_content = PROFESSIONAL_CARD_TEMPLATE.format(
            name=profile.name,
            avatar_icon=avatar_icon,
            title_html=title_html,
            company_html=company_html,
            title_vcard=title_vcard,
            company_vcard=company_vcard,
            email_html=email_html,
            email_vcard=email_vcard,
            phone=profile.contact_number,
            address=profile.address,
            address_encoded=address_encoded,
            social_buttons=social_buttons_html,
            expires_date=url_mapping.expires_at.strftime("%B %d, %Y"),
            qr_code_data=qr_base64,
            name_clean=profile.name.replace(' ', '_'),
            profile_url=profile_url,
            timestamp=datetime.utcnow().strftime("%Y%m%d%H%M%S")
        )
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    db = SessionLocal()
    
    try:
        url_mapping = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
        
        if not url_mapping:
            raise HTTPException(status_code=404, detail="URL not found")
        
        if url_mapping.expires_at < datetime.utcnow():
            raise HTTPException(status_code=404, detail="URL has expired")
        
        url_mapping.clicks += 1
        db.commit()
        
        if url_mapping.type == "profile":
            db.close()
            return await get_profile_page(short_code)
        
        return RedirectResponse(url=url_mapping.original_url)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            db.close()
        except:
            pass

@app.get("/api/stats/{short_code}")
async def get_stats(short_code: str):
    db = SessionLocal()
    
    try:
        url_mapping = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
        
        if not url_mapping:
            raise HTTPException(status_code=404, detail="Short code not found")
        
        return {
            "short_code": short_code,
            "type": url_mapping.type,
            "clicks": url_mapping.clicks,
            "created_at": url_mapping.created_at.isoformat(),
            "expires_at": url_mapping.expires_at.isoformat(),
            "original_url": url_mapping.original_url if url_mapping.type == "url" else "Profile page"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=False,
        log_level="info"
    )