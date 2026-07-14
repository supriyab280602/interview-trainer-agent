import streamlit as st
import requests
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Optional


# Set page configurations
st.set_page_config(
    page_title="IBM watsonx AI - Interview Trainer Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"
if "interview_session" not in st.session_state:
    st.session_state.interview_session = None
if "profile_configured" not in st.session_state:
    st.session_state.profile_configured = False
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "last_eval" not in st.session_state:
    st.session_state.last_eval = None

# Custom CSS injection for premium SaaS UI
st.markdown("""
<style>
    /* Hide Default Streamlit Style but keep header toggle container */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 99990 !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    /* Style collapsed sidebar toggle to be prominent and clickable on all Streamlit versions */
    [data-testid="collapsedControl"],
    [data-testid="baseButton-header"],
    header button[aria-label="Expand sidebar"],
    header button[title="Expand sidebar"] {
        position: fixed !important;
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        background-color: #1a1a2e !important;
        border: 1px solid rgba(69, 137, 255, 0.4) !important;
        border-radius: 8px !important;
        z-index: 99999 !important;
        top: 15px !important;
        left: 15px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="baseButton-header"] svg,
    header button[aria-label="Expand sidebar"] svg,
    header button[title="Expand sidebar"] svg {
        fill: #78A9FF !important;
        color: #78A9FF !important;
    }

    /* Hide collapse button on desktop to prevent accidental collapse */
    @media (min-width: 992px) {
        button[data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebar"] button[aria-label="Collapse sidebar"],
        [data-testid="stSidebar"] button[title="Collapse sidebar"] {
            display: none !important;
        }
    }
    
    /* Font style */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Premium Cards styling */
    .saas-card {
        background-color: #FFFFFF;
        border: 1px solid #DDE1E6;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: box-shadow 0.25s ease, transform 0.25s ease;
        color: #161616 !important;
    }
    .saas-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.09);
        transform: translateY(-2px);
    }
    .saas-card-title {
        color: #161616;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F62FE;
    }
    
    /* Chat Bubbles */
    .chat-bubble-ai {
        background-color: #FCFCFC;
        border: 1px solid #DDE1E6;
        border-left: 4px solid #0F62FE;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #161616;
    }
    .chat-bubble-user {
        background-color: #E8F0FE;
        border: 1px solid #DDE1E6;
        border-left: 4px solid #4589FF;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #161616;
    }
    
    /* Glass panel effect */
    .glass-banner {
        background: linear-gradient(135deg, #0F62FE 0%, #4589FF 100%);
        color: #FFFFFF;
        padding: 40px;
        border-radius: 14px;
        margin-bottom: 30px;
        box-shadow: 0 6px 20px rgba(15, 98, 254, 0.15);
    }
    
    /* ============================================
       ANTI-BLINK / ANTI-DIM: Prevent Streamlit
       from greying out the page during reruns.
       ============================================ */

    /* 1. Kill the full-screen translucent overlay Streamlit paints while rerunning */
    div[data-testid="stAppViewContainer"]::before,
    div[data-testid="stAppViewContainer"]::after,
    div[data-testid="stApp"]::before,
    div[data-testid="stApp"]::after {
        display: none !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* 2. Force every Streamlit container to stay fully opaque at all times */
    div[data-testid="stAppViewContainer"],
    div[data-testid="stApp"],
    div[data-testid="stAppViewBlockContainer"],
    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"],
    div[data-testid="stSidebar"],
    div[data-testid="stSidebarContent"],
    div[data-testid="stMainBlockContainer"],
    section[data-testid="stSidebar"],
    .main .block-container,
    .element-container,
    .stMarkdown,
    .stButton,
    .stTextInput,
    .stSelectbox,
    .stTextArea,
    .stTabs,
    .stTab,
    .stForm,
    .stDownloadButton,
    .stFileUploader,
    .stExpander,
    .stProgress,
    .stAlert,
    .stSpinner {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }

    /* 3. Neutralise the "stale element" styling Streamlit applies to
          old widgets while new ones are being hydrated */
    [data-stale="true"],
    .stale-element,
    [class*="stale"] {
        opacity: 1 !important;
        filter: none !important;
        pointer-events: auto !important;
    }

    /* 4. Hide the running-man / connection-status indicators that
          flash in the top-right corner during reruns */
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* 5. Prevent any blanket CSS transitions on the root app
          (Streamlit sometimes injects transition: opacity …) */
    .stApp, #root {
        transition: none !important;
    }

    /* ============================================
       SMOOTH CONTENT TRANSITIONS
       ============================================ */

    /* Gentle fade-in for content blocks so new renders feel smooth */
    @keyframes smoothFadeIn {
        from { opacity: 0.85; transform: translateY(4px); }
        to   { opacity: 1;    transform: translateY(0);   }
    }
    .main .block-container {
        animation: smoothFadeIn 0.2s ease-out;
    }

    /* Polished button interactions */
    .stButton > button {
        transition: background-color 0.2s ease,
                    box-shadow 0.2s ease,
                    transform 0.1s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(15, 98, 254, 0.18);
    }
    .stButton > button:active {
        transform: translateY(0px) scale(0.98);
        box-shadow: 0 1px 4px rgba(15, 98, 254, 0.12);
    }

    /* Sidebar nav buttons get matching transitions */
    section[data-testid="stSidebar"] .stButton > button {
        transition: background-color 0.2s ease,
                    transform 0.1s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateX(3px);
    }

    /* Smooth tab switching */
    .stTabs [data-baseweb="tab-panel"] {
        animation: smoothFadeIn 0.2s ease-out;
    }

    /* Expander open/close feel */
    .stExpander details[open] > div {
        animation: smoothFadeIn 0.25s ease-out;
    }

    /* ============================================
       INTERVIEW QUESTION & EVALUATION CARDS
       ============================================ */

    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0);    }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 8px rgba(15, 98, 254, 0.15); }
        50%      { box-shadow: 0 0 20px rgba(15, 98, 254, 0.30); }
    }

    /* Question card */
    .q-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid rgba(69, 137, 255, 0.3);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        animation: slideInUp 0.4s cubic-bezier(0.22, 1, 0.36, 1);
        position: relative;
        overflow: hidden;
    }
    .q-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0F62FE, #4589FF, #78A9FF, #4589FF, #0F62FE);
        background-size: 200% 100%;
        animation: shimmer 3s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%   { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .q-card .q-badge {
        display: inline-block;
        background: rgba(15, 98, 254, 0.2);
        color: #78A9FF;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 14px;
    }
    .q-card .q-text {
        color: #FFFFFF;
        font-size: 1.15rem;
        line-height: 1.7;
        font-weight: 400;
    }

    /* Evaluation result card */
    .eval-card {
        background: linear-gradient(135deg, #0a1628 0%, #111d33 100%);
        border: 1px solid rgba(36, 161, 72, 0.3);
        border-radius: 16px;
        padding: 28px 32px;
        margin: 20px 0;
        animation: slideInUp 0.45s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .eval-card .eval-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
    }
    .eval-card .score-ring {
        width: 64px; height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        font-weight: 800;
        color: #FFFFFF;
        flex-shrink: 0;
        animation: pulseGlow 2s ease-in-out infinite;
    }
    .eval-card .eval-section {
        margin-bottom: 14px;
    }
    .eval-card .eval-label {
        color: #78A9FF;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }
    .eval-card .eval-text {
        color: #C6D0DC;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Progress bar styling */
    .interview-progress {
        background: rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 24px;
        border: 1px solid rgba(69, 137, 255, 0.15);
    }
    .interview-progress .prog-label {
        color: #A0AEC0;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    .interview-progress .prog-bar {
        background: rgba(255,255,255,0.08);
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
    }
    .interview-progress .prog-fill {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, #0F62FE, #4589FF);
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)


# Connection Health check
@st.cache_data(ttl=30)
def check_backend_health() -> bool:
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False

backend_online = check_backend_health()

if not backend_online:
    st.warning("⚠️ FastAPI Backend Server is offline. Please launch the backend by running `uvicorn main:app --reload` to sync Cloud services and trigger live Granite AI actions. Showing local simulator for viewing navigation.")

# Request wrapper to inject Session-ID headers
def backend_request(method: str, path: str, json_data: dict = None, files: dict = None) -> Optional[requests.Response]:
    headers = {}
    if st.session_state.session_id:
        headers["X-Session-ID"] = st.session_state.session_id
        
    try:
        url = f"{BACKEND_URL}{path}"
        if method == "GET":
            return requests.get(url, headers=headers, timeout=30.0)
        elif method == "POST":
            # AI operations (question generation, evaluation) can take 90+ seconds
            # on large models like llama-3-3-70b-instruct, especially on cold start
            post_timeout = 180.0
            if files:
                return requests.post(url, headers=headers, files=files, timeout=post_timeout)
            return requests.post(url, headers=headers, json=json_data, timeout=post_timeout)
        elif method == "PUT":
            return requests.put(url, headers=headers, json=json_data, timeout=60.0)
        elif method == "DELETE":
            return requests.delete(url, headers=headers, timeout=30.0)
    except Exception as e:
        st.error(f"Network error contacting backend: {str(e)}")
        return None
    return None

# ==========================================
# AUTHENTICATION SCREEN
# ==========================================
def render_welcome_screen():
    st.markdown("""
        <div style='text-align: center; padding: 40px 0;'>
            <h1 style='color: #0F62FE; font-size: 3rem; font-weight: 800;'>IBM watsonx AI</h1>
            <p style='color: #6F6F6F; font-size: 1.3rem; font-weight: 400;'>Next-Gen AI Interview Trainer Agent</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        tab_login, tab_register = st.tabs(["🔒 Sign In", "📝 Create Account"])
        
        with tab_login:
            st.subheader("Login to your Account")
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_pw")
            
            if st.button("Sign In", type="primary", use_container_width=True):
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        if not backend_online:
                            # Mock authentication for developer preview
                            st.session_state.logged_in = True
                            st.session_state.session_id = "mock_session_id"
                            st.session_state.user_name = "Jane Doe"
                            st.session_state.user_email = email
                            st.session_state.profile_configured = True
                            st.rerun()
                        else:
                            res = backend_request("POST", "/api/login", json_data={"email": email, "password": password})
                            if res and res.status_code == 200:
                                data = res.json()
                                st.session_state.logged_in = True
                                st.session_state.session_id = data["session_id"]
                                st.session_state.user_name = data["full_name"]
                                st.session_state.user_email = data["email"]
                                if data.get("active_profile"):
                                    st.session_state.profile_configured = True
                                st.success("Logged in successfully!")
                                st.rerun()
                            else:
                                err = res.json().get("detail") if res else "Credentials error."
                                st.error(f"Authentication failed: {err}")
                                
        with tab_register:
            st.subheader("Create a New Account")
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email Address", key="reg_email")
            reg_pw = st.text_input("Password (min 6 chars)", type="password", key="reg_pw")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Register Account", type="primary", use_container_width=True):
                if not reg_name or not reg_email or not reg_pw or not reg_confirm:
                    st.error("Please fill in all fields.")
                elif reg_pw != reg_confirm:
                    st.error("Passwords do not match.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating profile record..."):
                        if not backend_online:
                            st.success("Account created successfully (Simulated mode). Sign in using Login tab.")
                        else:
                            res = backend_request("POST", "/api/signup", json_data={
                                "full_name": reg_name,
                                "email": reg_email,
                                "password": reg_pw,
                                "confirm_password": reg_confirm
                            })
                            if res and res.status_code == 200:
                                st.success("Registration complete! You can now log in.")
                            else:
                                err = res.json().get("detail") if res else "Signup conflict."
                                st.error(f"Sign up failed: {err}")

# ==========================================
# DASHBOARD PAGE
# ==========================================
def render_dashboard():
    # Load Dashboard profile/statistics
    user_name = st.session_state.user_name
    
    st.markdown(f"""
        <div class="glass-banner">
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700;">Welcome Back, {user_name}!</h1>
            <p style="margin: 5px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Configure your career profile, track evaluation progress, or start an AI-guided mock interview session.</p>
        </div>
    """, unsafe_allow_html=True)

    if not backend_online:
        # No fake stats — require backend for real data
        st.error("⚠️ The FastAPI backend is offline. Start it with `uvicorn main:app --reload` to load your real interview data, scores, and analytics.")
        st.info("💡 All questions, evaluations, and scores are powered by IBM watsonx.ai — no mock data is used.")
        return

    # Call backend for dashboard stats
    db_res = backend_request("GET", "/api/dashboard")
    if db_res and db_res.status_code == 200:
        dash_data = db_res.json()
        stats = dash_data["stats"]
        profile_details = dash_data["profile_details"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="saas-card"><div class="saas-card-title">Average Score</div><div class="metric-value">{stats['average_score']}/10</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="saas-card"><div class="saas-card-title">Best Score</div><div class="metric-value">{stats['highest_score']}/10</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="saas-card"><div class="saas-card-title">Total Sessions</div><div class="metric-value">{stats['total_interviews']}</div></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="saas-card"><div class="saas-card-title">Completion Rate</div><div class="metric-value">{stats['completion_rate']}%</div></div>""", unsafe_allow_html=True)
        
        # Display Career Profile Setup Card
        st.subheader("Target Job Profile")
        if not profile_details:
            st.info("You haven't configured a career target profile yet. Click below to specify your target role and experience level.")
            if st.button("Set Up Interview Profile", type="primary"):
                st.session_state.active_page = "Profile Setup"
                st.rerun()
        else:
            col_p1, col_p2 = st.columns([2, 1])
            with col_p1:
                st.markdown(f"""
                    <div class="saas-card">
                        <div class="saas-card-title">Active Profile Focus: <b>{dash_data['active_profile']}</b></div>
                        <p style="margin: 0;"><b>Target Role:</b> {profile_details['target_role']}</p>
                        <p style="margin: 4px 0 0 0;"><b>Experience Track:</b> {profile_details['experience_level']}</p>
                        <p style="margin: 4px 0 0 0;"><b>Resume Attached:</b> {'Yes' if profile_details.get('resume_id') else 'No (Highly Recommended)'}</p>
                    </div>
                """, unsafe_allow_html=True)
            with col_p2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Modify Profile Setup", use_container_width=True):
                    st.session_state.active_page = "Profile Setup"
                    st.rerun()
                if st.button("Go to Resume Center", use_container_width=True):
                    st.session_state.active_page = "Resume Center"
                    st.rerun()
                if st.button("Start Practicing Now", type="primary", use_container_width=True):
                    st.session_state.active_page = "Interview Session"
                    st.rerun()
                    
            # Recent Progress
            st.subheader("Recent Sessions Activity")
            trend = dash_data["recent_progress"]
            if not trend:
                st.write("No interview sessions found in history. Start a new session to record progress.")
            else:
                for idx, t in enumerate(reversed(trend)):
                    st.markdown(f"""
                        <div style="background-color: #F8F9FA; padding: 12px 20px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #DDE1E6;">
                            <b>{t['role']}</b> ({t['type']} Interview) — Score: <b>{t['score']}/10</b> on {t['date']}
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.error("Failed to load dashboard data. Please create a career profile first.")
        if st.button("Set Up Interview Profile", type="primary"):
            st.session_state.active_page = "Profile Setup"
            st.rerun()

# ==========================================
# INTERVIEW PROFILE SETUP
# ==========================================
def render_profile_setup():
    st.subheader("Career & Interview Target Settings")
    st.write("This profile context is retrieved before generating questions and evaluating responses, allowing custom-tailored simulation.")
    
    # Check if profile already exists to prepopulate
    prof_name = ""
    target_role = ""
    exp_level = "Fresher"
    
    if backend_online:
        prof_res = backend_request("GET", "/api/profile")
        if prof_res and prof_res.status_code == 200:
            user_data = prof_res.json()
            active_p = user_data.get("active_profile_name")
            if active_p and "profiles" in user_data:
                p_details = user_data["profiles"][active_p]
                prof_name = active_p
                target_role = p_details.get("target_role", "")
                exp_level = p_details.get("experience_level", "Fresher")

    with st.form("profile_form"):
        p_name = st.text_input("Career Profile Configuration Name", value=prof_name if prof_name else "Standard Profile", placeholder="e.g. Backend Dev Profile")
        p_role = st.selectbox("Target Job Role Focus", 
                              options=["Software Engineer", "Backend Developer", "Frontend Developer", "AI Engineer", "ML Engineer", "Cloud Engineer", "Data Analyst", "Cyber Security", "Custom Role"],
                              index=0)
        custom_role = st.text_input("Specify Custom Role (If chosen above)", value=target_role if p_role == "Custom Role" else "")
        p_exp = st.selectbox("Experience Level", 
                             options=["Fresher", "1-3 Years", "3-5 Years", "5+ Years"],
                             index=0)
        
        submit = st.form_submit_button("Save Profile Settings", type="primary")
        if submit:
            final_role = custom_role if p_role == "Custom Role" else p_role
            if not p_name or not final_role:
                st.error("Please enter a profile name and job role.")
            else:
                with st.spinner("Configuring..."):
                    if not backend_online:
                        st.session_state.profile_configured = True
                        st.session_state.active_page = "Dashboard"
                        st.success("Simulated profile settings saved!")
                        st.rerun()
                    else:
                        res = backend_request("PUT", "/api/profile", json_data={
                            "profile_name": p_name,
                            "experience_level": p_exp,
                            "target_role": final_role
                        })
                        if res and res.status_code == 200:
                            st.session_state.profile_configured = True
                            st.success("Target profile configured successfully!")
                            st.session_state.active_page = "Dashboard"
                            st.rerun()
                        else:
                            st.error("Failed to update profile settings.")

# ==========================================
# RESUME CENTER
# ==========================================
def render_resume_center():
    st.subheader("Resume Management & Extraction")
    st.write("Upload your resume in PDF format. The system automatically extracts skills, achievements, education, and past projects using Granite AI reasoning. Extracted topics will guide the interview pipeline.")

    if not backend_online:
        st.info("Local simulator mode active. Resume upload requires FastAPI backend running.")
        return

    # Check if a resume is already uploaded for active profile
    resume_doc = None
    res = backend_request("GET", "/api/resume")
    if res and res.status_code == 200:
        resume_doc = res.json()
        
    if resume_doc:
        st.success(f"📄 Active Resume Uploaded: {resume_doc['resume_name']} (Analyzed on: {resume_doc['upload_date'][:10]})")
        
        # Display parsed details
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Extracted Candidate Name:** {resume_doc.get('candidate_name', 'Unknown')}")
            st.markdown("**Skills Matrix:**")
            st.write(", ".join(resume_doc.get("skills", [])))
            st.markdown("**Programming Languages:**")
            st.write(", ".join(resume_doc.get("programming_languages", [])))
            st.markdown("**Frameworks:**")
            st.write(", ".join(resume_doc.get("frameworks", [])))
        with col2:
            st.markdown("**Technologies & Tools:**")
            st.write(", ".join(resume_doc.get("technologies", []) + resume_doc.get("tools", [])))
            st.markdown("**Soft Skills:**")
            st.write(", ".join(resume_doc.get("soft_skills", [])))
            
        with st.expander("Show Parsed Experience & Projects"):
            st.write("**Work Experience:**")
            st.write(resume_doc.get("work_experience", []))
            st.write("**Projects:**")
            st.write(resume_doc.get("projects", []))
            st.write("**Education:**")
            st.write(resume_doc.get("education", []))
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Delete Resume", type="secondary"):
            with st.spinner("Deleting file..."):
                del_res = backend_request("DELETE", "/api/resume")
                if del_res and del_res.status_code == 200:
                    st.success("Resume deleted.")
                    st.rerun()
                else:
                    st.error("Failed to delete resume.")
    else:
        st.info("No resume uploaded yet for the active career profile.")
        uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
        if uploaded_file is not None:
            if st.button("Analyze & Save Resume", type="primary"):
                with st.spinner("Analyzing resume content with IBM Granite... This may take up to 30 seconds."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    up_res = backend_request("POST", "/api/resume/upload", files=files)
                    if up_res and up_res.status_code == 200:
                        st.success("Resume processed and analyzed successfully!")
                        st.rerun()
                    else:
                        err = up_res.json().get("detail") if up_res else "Incompatible size/format."
                        st.error(f"Failed to process resume: {err}")

# ==========================================
# INTERVIEW SIMULATOR (CHAT INTERFACE)
# ==========================================
def render_interview_session():
    st.subheader("Mock Interview Session")
    
    if not backend_online:
        st.error("FastAPI Backend is offline. Starting mock interviews is disabled.")
        return

    # Check active profile
    prof_res = backend_request("GET", "/api/profile")
    if not prof_res or prof_res.status_code != 200:
        st.warning("Please configure your career profile before starting an interview.")
        return
        
    user_profile = prof_res.json()
    active_profile = user_profile.get("active_profile_name")
    if not active_profile:
        st.warning("No active career profile configured. Set up your profile first.")
        return

    # Initialize evaluation display state
    if "show_eval" not in st.session_state:
        st.session_state.show_eval = False

    # If interview is not started yet, show configuration page
    if not st.session_state.interview_session:
        st.markdown(f"**Interview Profile Context:** {active_profile} ({user_profile['profiles'][active_profile]['target_role']})")
        
        col1, col2 = st.columns(2)
        with col1:
            i_type = st.selectbox("Interview Mode Focus", options=["Technical", "HR", "Behavioral", "Mixed"])
            i_diff = st.selectbox("Difficulty Setting", options=["Easy", "Medium", "Hard", "Adaptive"])
        with col2:
            i_len = st.selectbox("Total Question Count", options=[5, 10, 15], index=0)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Initiate Interview Session", type="primary", use_container_width=True):
            with st.spinner("🔄 IBM watsonx.ai is generating your first interview question... This may take up to 2 minutes on the first call."):
                start_res = backend_request("POST", "/api/interview/start", json_data={
                    "profile_name": active_profile,
                    "interview_type": i_type,
                    "difficulty": i_diff,
                    "length": i_len
                })
                if start_res and start_res.status_code == 200:
                    st.session_state.interview_session = start_res.json()
                    st.session_state.current_question_index = 0
                    st.session_state.last_eval = None
                    st.session_state.show_eval = False
                    st.rerun()
                else:
                    err_msg = "Failed to start interview."
                    if start_res is not None:
                        try:
                            err_msg = start_res.json().get("detail", f"Server error (HTTP {start_res.status_code})")
                        except Exception:
                            err_msg = f"Server error (HTTP {start_res.status_code})"
                    st.error(f"❌ {err_msg}")
        return

    # Load active interview session details
    session = st.session_state.interview_session
    interview_id = session["_id"]
    questions = session["questions"]
    answers = session["answers"]
    evaluations = session.get("evaluations", [])
    length = session.get("length", 5)
    status = session["status"]

    # Calculate current state
    q_index = len(answers)  # Next unanswered question index

    # Custom progress bar
    progress_pct = min(q_index / length * 100, 100)
    st.markdown(f"""
        <div class="interview-progress">
            <div class="prog-label">Question {min(q_index + 1, length)} of {length}  •  {q_index} answered</div>
            <div class="prog-bar"><div class="prog-fill" style="width: {progress_pct}%;"></div></div>
        </div>
    """, unsafe_allow_html=True)

    # If all questions answered but status is not COMPLETED in DB, end it
    if q_index >= length and status == "IN_PROGRESS":
        with st.spinner("Finishing interview. Granite is aggregating scores and creating summary..."):
            end_res = backend_request("POST", f"/api/interview/end?interview_id={interview_id}")
            if end_res and end_res.status_code == 200:
                st.session_state.interview_session = end_res.json()
                st.session_state.show_eval = False
                st.rerun()
            else:
                st.error("Failed to compile final interview summary.")
                return

    # Check status — show final summary
    if status == "COMPLETED" or q_index >= length:
        st.success("🎉 Interview Concluded Successfully!")
        summary = session.get("summary", {})
        
        if summary:
            st.markdown(f"""
                <div class="glass-banner">
                    <h2 style="margin: 0; font-size: 1.8rem;">Final Performance Rating: {round(session.get('overall_score', 0.0), 2)} / 10</h2>
                    <p style="margin: 5px 0 0 0; font-size: 1.1rem;">Readiness Assessment: <b>{summary.get('readiness_level', 'N/A')}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Dimensions Scores Breakdown:**")
                scores = summary.get("scores", {})
                st.write(f"- Technical Score: **{scores.get('technical_score', 0.0)} / 10**")
                st.write(f"- HR / Core Score: **{scores.get('hr_score', 0.0)} / 10**")
                st.write(f"- STAR Method Alignment: **{scores.get('behavioural_score', 0.0)} / 10**")
                st.write(f"- Communication Rating: **{scores.get('communication_score', 0.0)} / 10**")
                st.write(f"- Delivery Confidence: **{scores.get('confidence_score', 0.0)} / 10**")
            with col2:
                st.markdown("**Core Strength Analysis:**")
                st.write(summary.get("strength_analysis"))
                st.markdown("**Areas to Improve:**")
                st.write(summary.get("weakness_analysis"))
                
            st.markdown("### 📋 Recommended Study & Practice Plan")
            st.write(summary.get("recommended_study_plan"))
            
            st.markdown("<br>", unsafe_allow_html=True)
            report_res = backend_request("GET", f"/api/interview/{interview_id}/report")
            if report_res and report_res.status_code == 200:
                st.download_button(
                    label="📥 Download PDF Performance Report",
                    data=report_res.content,
                    file_name=f"interview_report_{interview_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("Loading summary details...")
            
        if st.button("Back to Dashboard", type="primary", use_container_width=True):
            st.session_state.interview_session = None
            st.session_state.active_page = "Dashboard"
            st.session_state.show_eval = False
            st.rerun()
        return

    # ── PHASE 1: Show evaluation of the last answer + "Next Question" button ──
    if st.session_state.show_eval and st.session_state.last_eval:
        ev = st.session_state.last_eval
        score_val = ev.get('overall_score', 0)
        # Color the score ring based on score
        if score_val >= 8:
            ring_bg = "linear-gradient(135deg, #24A148, #42be65)"
        elif score_val >= 5:
            ring_bg = "linear-gradient(135deg, #F1C21B, #f7d96e)"
        else:
            ring_bg = "linear-gradient(135deg, #DA1E28, #fa4d56)"

        # Show which question was just answered
        prev_q_num = q_index  # q_index is already incremented (len of answers)
        prev_question = questions[prev_q_num - 1] if prev_q_num > 0 else ""

        st.markdown(f"""
            <div class="q-card" style="opacity: 0.7; border-color: rgba(69,137,255,0.15);">
                <div class="q-badge">Question {prev_q_num} — Answered ✓</div>
                <div class="q-text" style="font-size: 1rem;">{prev_question}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="eval-card">
                <div class="eval-header">
                    <div class="score-ring" style="background: {ring_bg};">{score_val}</div>
                    <div>
                        <div style="color: #FFFFFF; font-size: 1.15rem; font-weight: 600;">Evaluation Result</div>
                        <div style="color: #78A9FF; font-size: 0.85rem;">Score {score_val} / 10</div>
                    </div>
                </div>
                <div class="eval-section">
                    <div class="eval-label">💪 Strengths</div>
                    <div class="eval-text">{ev.get('strengths', 'N/A')}</div>
                </div>
                <div class="eval-section">
                    <div class="eval-label">🎯 Improvement Tips</div>
                    <div class="eval-text">{ev.get('improvement_tips', 'N/A')}</div>
                </div>
                <div class="eval-section">
                    <div class="eval-label">📝 Model Answer</div>
                    <div class="eval-text">{ev.get('ideal_model_answer', 'N/A')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Show "Next Question" or "Finish Interview" button
        if q_index >= length:
            if st.button("🏁 Finish Interview & Get Summary", type="primary", use_container_width=True):
                st.session_state.show_eval = False
                st.rerun()
        else:
            if st.button(f"➡️ Next Question ({q_index + 1} of {length})", type="primary", use_container_width=True):
                st.session_state.show_eval = False
                st.session_state.last_eval = None
                st.rerun()
        return

    # ── PHASE 2: Display current question card + answer input ──
    if q_index >= len(questions):
        st.warning("Waiting for next question to be generated...")
        return

    curr_question = questions[q_index]
    st.markdown(f"""
        <div class="q-card">
            <div class="q-badge">Question {q_index + 1} of {length}  •  {session.get('interview_type', '')}  •  {session.get('difficulty', '')}</div>
            <div class="q-text">{curr_question}</div>
        </div>
    """, unsafe_allow_html=True)

    # Show collapsible history of previous evaluations
    if len(evaluations) > 0:
        with st.expander(f"📊 Previous Evaluations ({len(evaluations)} answered)", expanded=False):
            for idx, ev in enumerate(evaluations):
                score_v = ev.get('overall_score', 0) if isinstance(ev, dict) else getattr(ev, 'overall_score', 0)
                st.markdown(f"**Q{idx+1}** — Score: **{score_v}/10**")

    # Collect user answer
    user_ans = st.text_area("Your Response", placeholder="Speak your thoughts clearly... Use the STAR method to describe experiences.", height=140, key=f"answer_input_{q_index}")
    
    if st.button("Submit Answer", type="primary", use_container_width=True):
        if not user_ans or len(user_ans.strip()) < 5:
            st.error("Please enter a structured answer before submitting.")
        else:
            with st.spinner("Granite is evaluating your response and formulating the next question..."):
                ans_res = backend_request("POST", "/api/interview/answer", json_data={
                    "interview_id": interview_id,
                    "question_index": q_index,
                    "answer": user_ans
                })
                if ans_res and ans_res.status_code == 200:
                    result = ans_res.json()
                    st.session_state.last_eval = result["evaluation"]

                    # Directly update session state from the answer response
                    # instead of re-fetching the entire history
                    session["answers"].append(user_ans)
                    session["evaluations"].append(result["evaluation"])
                    if result.get("next_question"):
                        session["questions"].append(result["next_question"])
                    if result.get("status"):
                        session["status"] = result["status"]
                    if result.get("overall_score") is not None:
                        session["overall_score"] = result["overall_score"]
                    st.session_state.interview_session = session

                    # Show the evaluation card before advancing
                    st.session_state.show_eval = True
                    st.rerun()
                else:
                    err_msg = "Submission error — backend unreachable."
                    if ans_res is not None:
                        try:
                            err_msg = ans_res.json().get("detail", f"Server error (HTTP {ans_res.status_code})")
                        except Exception:
                            err_msg = f"Server error (HTTP {ans_res.status_code})"
                    st.error(f"❌ {err_msg}")

# ==========================================
# INTERVIEW HISTORY
# ==========================================
def render_history():
    st.subheader("Historical Sessions & Reports")
    
    if not backend_online:
        st.error("FastAPI Backend is offline. Viewing history is disabled.")
        return

    hist_res = backend_request("GET", "/api/interview/history")
    if hist_res and hist_res.status_code == 200:
        history = hist_res.json()
        if not history:
            st.info("No past interview sessions found.")
            return
            
        for session in history:
            date = session.get("started_time", "")[:10]
            status = session.get("status")
            score = round(session.get("overall_score", 0.0), 2) if session.get("overall_score") else "N/A"
            
            st.markdown(f"""
                <div class="saas-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span style="font-size: 1.2rem; font-weight: 600; color: #161616;">{session['role']}</span> — 
                            <span style="color: #6F6F6F;">{session['interview_type']} Interview</span>
                        </div>
                        <span style="background-color: {'#24A148' if status == 'COMPLETED' else '#F1C21B'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">{status}</span>
                    </div>
                    <p style="margin: 6px 0;">Date Attempted: {date}  |  Difficulty: {session['difficulty']}</p>
                    <p style="font-size: 1.1rem; font-weight: 600; color: #0F62FE;">Overall Score: {score}/10</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Show options to view and download report
            if status == "COMPLETED":
                col_btn1, col_btn2 = st.columns([1, 4])
                with col_btn1:
                    # Download button
                    report_res = backend_request("GET", f"/api/interview/{session['_id']}/report")
                    if report_res and report_res.status_code == 200:
                        st.download_button(
                            label="📥 Download PDF",
                            data=report_res.content,
                            file_name=f"interview_report_{session['_id']}.pdf",
                            mime="application/pdf",
                            key=f"dl_{session['_id']}"
                        )
                with col_btn2:
                    if st.button("🔍 View Performance Details", key=f"view_{session['_id']}"):
                        st.session_state.interview_session = session
                        st.session_state.active_page = "Interview Session"
                        st.rerun()

# ==========================================
# ANALYTICS CENTER
# ==========================================
def render_analytics():
    st.subheader("Performance Analytics Center")
    
    if not backend_online:
        st.error("FastAPI Backend is offline. Analytics processing is disabled.")
        return

    anal_res = backend_request("GET", "/api/analytics")
    if anal_res and anal_res.status_code == 200:
        data = anal_res.json()
        
        if data["total_interviews"] == 0:
            st.info("Insufficient data to generate analytics. Complete at least one interview session first.")
            return

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="saas-card"><div class="saas-card-title">Aggregated Rating</div><div class="metric-value">{data['average_score']}/10</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="saas-card"><div class="saas-card-title">Highest Score</div><div class="metric-value">{data['highest_score']}/10</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="saas-card"><div class="saas-card-title">Questions Graded</div><div class="metric-value">{data['questions_attempted']}</div></div>""", unsafe_allow_html=True)

        # Plotly Charts
        st.markdown("### 📈 Chronological Score Progress")
        trend = data["progress_trend"]
        if trend:
            df = pd.DataFrame(trend)
            fig = px.line(df, x="date", y="score", hover_data=["role", "type"], markers=True, labels={"date": "Session Date", "score": "Inference Score"})
            fig.update_layout(
                yaxis_range=[1, 10], 
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=True, gridcolor="#DDE1E6"),
                yaxis=dict(showgrid=True, gridcolor="#DDE1E6")
            )
            st.plotly_chart(fig, use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("### 🔍 Frequently Missed Topics / Concepts")
            missed = data.get("missed_topics", [])
            if not missed:
                st.write("Excellent! No recurring missed concepts identified.")
            else:
                for idx, item in enumerate(missed):
                    st.write(f"{idx+1}. 🚨 **{item}**")
        with col_r:
            st.markdown("### 💡 Recommended Study Focus Areas")
            weak = data.get("weakest_skills", [])
            if not weak:
                st.write("Keep practicing to identify skill clusters.")
            else:
                for idx, item in enumerate(weak):
                    st.write(f"{idx+1}. 📚 **{item}**")
    else:
        st.error("Failed to fetch analytics metrics.")

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='color: #0F62FE; font-weight: 800; margin-bottom: 20px;'>IBM watsonx AI</h2>", unsafe_allow_html=True)
        
        # User credentials block
        st.markdown(f"**Logged in as:** {st.session_state.user_name}")
        st.markdown(f"Email: `{st.session_state.user_email}`")
        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
        
        # Navigation Options
        pages = ["Dashboard", "Interview Session", "Resume Center", "Interview History", "Analytics Center", "Profile Setup"]
        icons = ["📊", "🤖", "📄", "🕒", "📈", "⚙️"]
        
        for idx, page in enumerate(pages):
            is_active = st.session_state.active_page == page
            btn_style = "primary" if is_active else "secondary"
            if st.button(f"{icons[idx]} {page}", key=f"nav_{page}", use_container_width=True, type=btn_style):
                st.session_state.active_page = page
                st.rerun()
                
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout Account", use_container_width=True, type="secondary"):
            # Call backend logout
            if backend_online:
                backend_request("POST", "/api/logout")
            st.session_state.logged_in = False
            st.session_state.session_id = None
            st.session_state.user_name = None
            st.session_state.user_email = None
            st.session_state.interview_session = None
            st.session_state.profile_configured = False
            st.rerun()

# ==========================================
# MAIN APPLICATION ROUTER
# ==========================================
def main():
    if not st.session_state.logged_in:
        render_welcome_screen()
    else:
        render_sidebar()
        
        # Routing logic
        page = st.session_state.active_page
        if page == "Dashboard":
            render_dashboard()
        elif page == "Profile Setup":
            render_profile_setup()
        elif page == "Resume Center":
            render_resume_center()
        elif page == "Interview Session":
            render_interview_session()
        elif page == "Interview History":
            render_history()
        elif page == "Analytics Center":
            render_analytics()

if __name__ == "__main__":
    main()
