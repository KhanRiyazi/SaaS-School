import streamlit as st
import requests
import json
import base64
import traceback
from datetime import datetime
import re
import webbrowser

# Page configuration
st.set_page_config(
    page_title="Professional Digital Business Card & URL Shortener",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .stTextArea > div > div > textarea {
        border-radius: 10px;
    }
    .success-message {
        padding: 10px;
        border-radius: 10px;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .info-message {
        padding: 10px;
        border-radius: 10px;
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'qr_generated' not in st.session_state:
    st.session_state.qr_generated = False
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'current_qr_data' not in st.session_state:
    st.session_state.current_qr_data = None
if 'card_data' not in st.session_state:
    st.session_state.card_data = None
if 'generated_short_url' not in st.session_state:
    st.session_state.generated_short_url = None

# API endpoint - Update this with your deployed backend URL
API_URL = "http://localhost:8000"

# Professional Card Preview CSS
PROFESSIONAL_CARD_PREVIEW = """
<style>
.pro-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 25px;
    border-radius: 20px;
    color: white;
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    transition: transform 0.3s ease;
}
.pro-card:hover {
    transform: translateY(-5px);
}
.pro-header {
    text-align: center;
    margin-bottom: 20px;
}
.pro-avatar {
    width: 80px;
    height: 80px;
    background: white;
    border-radius: 50%;
    margin: 0 auto 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
.pro-name {
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 5px;
}
.pro-title {
    font-size: 14px;
    opacity: 0.9;
    margin-bottom: 10px;
}
.pro-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
}
.pro-info {
    margin-top: 15px;
    border-top: 1px solid rgba(255,255,255,0.2);
    padding-top: 15px;
}
.pro-info-row {
    display: flex;
    margin-bottom: 10px;
    font-size: 13px;
}
.pro-info-label {
    width: 80px;
    opacity: 0.8;
}
.pro-info-value {
    flex: 1;
    font-weight: 500;
}
</style>
"""

# Title
st.title("💼 Professional Digital Business Card System")
st.markdown("Create stunning digital business cards and smart URL shortener for professionals")

# Create tabs
tab1, tab2, tab3 = st.tabs(["✨ Business Card Generator", "🔗 URL Shortener", "📊 Analytics"])

# Tab 1: Professional Business Card Generator
with tab1:
    st.header("Create Your Professional Digital Business Card")
    st.markdown("Generate a stunning digital business card with QR code for easy sharing")
    
    with st.form("business_card_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Personal Information")
            full_name = st.text_input("Full Name *", placeholder="John Doe")
            job_title = st.text_input("Job Title *", placeholder="Software Engineer")
            company_name = st.text_input("Company Name *", placeholder="ABC Technologies")
            email = st.text_input("Email Address", placeholder="john@example.com")
            phone = st.text_input("Phone Number *", placeholder="+91 9876543210")
            address = st.text_area("Address *", placeholder="Enter your complete address")
            bio = st.text_area("Short Bio", placeholder="Tell people about yourself...", height=80)
            
        with col2:
            st.subheader("🌐 Social Media Links")
            st.caption("Add your professional social profiles")
            
            instagram = st.text_input("Instagram", placeholder="https://instagram.com/username")
            linkedin = st.text_input("LinkedIn", placeholder="https://linkedin.com/in/username")
            github = st.text_input("GitHub", placeholder="https://github.com/username")
            twitter = st.text_input("Twitter/X", placeholder="https://twitter.com/username")
            facebook = st.text_input("Facebook", placeholder="https://facebook.com/username")
            website = st.text_input("Personal Website", placeholder="https://yourwebsite.com")
            
            st.markdown("---")
            st.subheader("⚙️ Card Settings")
            card_type = st.selectbox("Card Type", ["Professional", "Student", "Teacher", "Freelancer"])
            expires_days = st.slider("Business Card Expiry (days)", 7, 365, 90)
        
        submitted = st.form_submit_button("✨ Generate Professional Business Card", type="primary", use_container_width=True)
        
        if submitted:
            if not full_name or not phone or not company_name:
                st.error("❌ Please fill in all required fields (*)")
            else:
                # Prepare social links
                social_links = []
                if instagram and instagram.strip():
                    social_links.append({"platform": "instagram", "url": instagram.strip()})
                if linkedin and linkedin.strip():
                    social_links.append({"platform": "linkedin", "url": linkedin.strip()})
                if github and github.strip():
                    social_links.append({"platform": "github", "url": github.strip()})
                if twitter and twitter.strip():
                    social_links.append({"platform": "twitter", "url": twitter.strip()})
                if facebook and facebook.strip():
                    social_links.append({"platform": "facebook", "url": facebook.strip()})
                if website and website.strip():
                    social_links.append({"platform": "website", "url": website.strip()})
                
                # Prepare bio
                bio_text = f"{card_type} | {bio}" if bio else card_type
                
                request_data = {
                    "name": full_name,
                    "title": job_title,
                    "company": company_name,
                    "email": email if email else None,
                    "contact_number": phone,
                    "address": address,
                    "bio": bio_text,
                    "social_links": social_links,
                    "expires_in_days": expires_days
                }
                
                with st.spinner("🎨 Creating your professional business card..."):
                    try:
                        response = requests.post(f"{API_URL}/api/generate-qr", json=request_data, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            st.session_state.qr_generated = True
                            st.session_state.form_submitted = True
                            st.session_state.current_qr_data = data
                            st.session_state.card_data = {
                                "full_name": full_name,
                                "job_title": job_title,
                                "company_name": company_name,
                                "email": email,
                                "phone": phone,
                                "address": address,
                                "bio": bio_text,
                                "card_type": card_type,
                                "social_links": social_links
                            }
                            
                            st.success("✅ Professional business card generated successfully!")
                            st.rerun()
                        else:
                            error_msg = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ Failed to generate business card: {error_msg}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error(f"❌ Cannot connect to backend server at {API_URL}")
                        st.info("💡 Please start the backend with: python main.py")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # Display Business Card
    if st.session_state.form_submitted and st.session_state.qr_generated and st.session_state.current_qr_data:
        st.divider()
        st.subheader("✨ Your Professional Digital Business Card")
        
        try:
            card_data = st.session_state.card_data
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**📱 QR Code - Scan to Connect**")
                # Display QR code from base64 directly
                if 'qr_code' in st.session_state.current_qr_data:
                    st.image(f"data:image/png;base64,{st.session_state.current_qr_data['qr_code']}", 
                            caption="Share this QR code", width=220)
                    
                    # Download button for QR code
                    import base64
                    qr_bytes = base64.b64decode(st.session_state.current_qr_data['qr_code'])
                    st.download_button(
                        label="💾 Download QR Code",
                        data=qr_bytes,
                        file_name=f"business_card_{st.session_state.current_qr_data.get('short_code', 'card')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                # Profile URL
                if 'profile_url' in st.session_state.current_qr_data:
                    profile_url = f"{API_URL}{st.session_state.current_qr_data['profile_url']}"
                    st.markdown("**🔗 Business Card Link**")
                    st.code(profile_url, language="text")
                    
                    col1a, col1b = st.columns(2)
                    with col1a:
                        if st.button("🌐 View Card", use_container_width=True):
                            webbrowser.open(profile_url)
                    with col1b:
                        if st.button("📋 Copy Link", use_container_width=True):
                            st.write(f'<script>navigator.clipboard.writeText("{profile_url}")</script>', unsafe_allow_html=True)
                            st.success("✅ Copied!")
            
            with col2:
                st.markdown(PROFESSIONAL_CARD_PREVIEW, unsafe_allow_html=True)
                
                # Professional Card Preview
                social_icons = " ".join([f"🔗" for _ in card_data['social_links'][:3]])
                
                st.markdown(f"""
                <div class="pro-card">
                    <div class="pro-header">
                        <div class="pro-avatar">👨‍💼</div>
                        <div class="pro-name">{card_data['full_name']}</div>
                        <div class="pro-title">{card_data['job_title']}</div>
                        <div class="pro-badge">{card_data['card_type']} Card</div>
                    </div>
                    <div class="pro-info">
                        <div class="pro-info-row">
                            <div class="pro-info-label">🏢 Company:</div>
                            <div class="pro-info-value">{card_data['company_name']}</div>
                        </div>
                        <div class="pro-info-row">
                            <div class="pro-info-label">📧 Email:</div>
                            <div class="pro-info-value">{card_data['email'] if card_data['email'] else 'Not provided'}</div>
                        </div>
                        <div class="pro-info-row">
                            <div class="pro-info-label">📞 Phone:</div>
                            <div class="pro-info-value">{card_data['phone']}</div>
                        </div>
                        <div class="pro-info-row">
                            <div class="pro-info-label">📍 Location:</div>
                            <div class="pro-info-value">{card_data['address']}</div>
                        </div>
                        {f'<div class="pro-info-row"><div class="pro-info-label">🌐 Social:</div><div class="pro-info-value">{social_icons} {len(card_data["social_links"])} profiles</div></div>' if card_data['social_links'] else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption("💡 Share this card by scanning the QR code or sharing the link")
                
        except Exception as e:
            st.error(f"❌ Error displaying business card: {str(e)}")

# Tab 2: URL Shortener (simplified)
with tab2:
    st.header("🔗 Smart URL Shortener")
    st.markdown("Create short, memorable links for any destination")
    
    with st.form("url_form"):
        original_url = st.text_input("Enter Long URL *", placeholder="https://example.com/very/long/url/path")
        custom_code = st.text_input("Custom Short Code (Optional)", placeholder="my-custom-link", max_chars=20)
        url_expires_days = st.slider("Link Expiry (days)", 1, 365, 30)
        
        submitted_url = st.form_submit_button("🔗 Create Short Link", type="primary", use_container_width=True)
        
        if submitted_url:
            if not original_url:
                st.error("❌ Please enter a URL")
            else:
                request_data = {"url": original_url, "expires_in_days": url_expires_days}
                if custom_code:
                    custom_code = re.sub(r'[^a-zA-Z0-9_-]', '', custom_code)
                    request_data["custom_code"] = custom_code
                
                with st.spinner("Creating short link..."):
                    try:
                        response = requests.post(f"{API_URL}/api/shorten-url", json=request_data, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            short_url = f"{API_URL}{data['short_url']}"
                            st.session_state.generated_short_url = short_url
                            
                            st.success("✅ Short link created successfully!")
                            st.markdown("### 📋 Your Short Link")
                            st.code(short_url, language="text")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🔗 Open Link", use_container_width=True):
                                    webbrowser.open(short_url)
                            with col2:
                                if st.button("📋 Copy Link", use_container_width=True):
                                    st.success(f"✅ Copied: {short_url}")
                        else:
                            st.error("❌ Failed to create short link")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Tab 3: Analytics (simplified)
with tab3:
    st.header("📊 Link Analytics & Tracking")
    
    stats_code = st.text_input("Enter Short Code", placeholder="e.g., abc123")
    
    if st.button("📊 Get Analytics", type="primary", use_container_width=True):
        if stats_code:
            with st.spinner("Fetching analytics..."):
                try:
                    response = requests.get(f"{API_URL}/api/stats/{stats_code}", timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ Analytics for '{stats_code}'")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📌 Type", data.get('type', 'N/A').upper())
                        with col2:
                            st.metric("👆 Total Clicks", data.get('clicks', 0))
                        with col3:
                            if 'expires_at' in data:
                                st.metric("⏰ Expires", data['expires_at'].split('T')[0])
                        
                        if data.get('original_url'):
                            st.markdown("**🔗 Original Destination:**")
                            st.code(data['original_url'], language="text")
                    else:
                        st.error("❌ Short code not found")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a short code")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/qr-code.png", width=80)
    st.header("💼 Professional Features")
    
    # Server status check
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Not Connected")
        st.info("💡 Run: python main.py")
    
    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit & FastAPI")