import streamlit as st
from config.database import get_session, Feedback
from utils.auth import check_authentication
from datetime import datetime

def show_feedback_form(require_login=True):
    """Display feedback form with optional login requirement"""
    
    st.markdown("## 💬 Feedback Form")
    
    if require_login:
        st.markdown("We value your feedback! Please let us know about your experience.")
        # Get current user info
        is_authenticated, name, username = check_authentication()
        if not is_authenticated:
            st.error("Please login to submit feedback.")
            return
    else:
        st.markdown("We value your feedback! No login required - share your thoughts anonymously.")
        username = "Anonymous"
    
    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            feedback_type = st.selectbox(
                "Feedback Type:",
                options=['rating', 'suggestion', 'bug_report', 'feature_request', 'general'],
                format_func=lambda x: {
                    'rating': '⭐ Rating',
                    'suggestion': '💡 Suggestion',
                    'bug_report': '🐛 Bug Report',
                    'feature_request': '🚀 Feature Request',
                    'general': '💬 General Feedback'
                }.get(x, x)
            )
        
        with col2:
            if feedback_type == 'rating':
                rating = st.selectbox(
                    "Rating (1-5 stars):",
                    options=[1, 2, 3, 4, 5],
                    format_func=lambda x: "⭐" * x
                )
            else:
                rating = None
        
        # Enhanced feedback widget using Streamlit's built-in feedback
        st.markdown("### Quick Rating")
        quick_rating = st.feedback("thumbs")
        
        page = st.selectbox(
            "Which feature is this feedback about?",
            options=['general', 'fake_news_detector', 'current_news', 'admin_dashboard', 'website'],
            format_func=lambda x: {
                'fake_news_detector': '🔍 Fake News Detector',
                'current_news': '📰 Current News',
                'general': '🌐 General',
                'admin_dashboard': '📊 Admin Dashboard',
                'website': '🌐 Website'
            }.get(x, x)
        )
        
        message = st.text_area(
            "Your Feedback:",
            height=150,
            placeholder="Please share your thoughts, suggestions, or report any issues..."
        )
        
        # Additional feedback options
        if not require_login:
            email = st.text_input(
                "Email (Optional):",
                placeholder="your.email@example.com (for follow-up)"
            )
        
        submitted = st.form_submit_button("📤 Submit Feedback", type="primary")
        
        if submitted:
            if message.strip():
                # Combine ratings
                final_rating = rating if rating else (quick_rating + 1 if quick_rating is not None else None)
                
                success = save_feedback(
                    feedback_type, 
                    final_rating, 
                    message, 
                    page, 
                    username,
                    email if not require_login else None
                )
                
                if success:
                    st.success("✅ Thank you for your feedback! We appreciate your input.")
                    st.balloons()
                    
                    # Show follow-up message
                    if not require_login:
                        st.info("💡 Want to access more features? Try our User or Admin login options!")
                else:
                    st.error("❌ Failed to submit feedback. Please try again.")
            else:
                st.error("Please enter your feedback message.")

def save_feedback(feedback_type, rating, message, page, username, email=None):
    """Save feedback to database"""
    try:
        session = get_session()
        
        # Add email to message if provided
        if email:
            message = f"{message}\n\nContact Email: {email}"
        
        feedback = Feedback(
            username=username,
            feedback_type=feedback_type,
            rating=rating,
            message=message,
            page=page,
            created_at=datetime.utcnow()
        )
        
        session.add(feedback)
        session.commit()
        session.close()
        return True
        
    except Exception as e:
        st.error(f"Failed to save feedback: {str(e)}")
        return False

# For backward compatibility
def show_feedback():
    """Original feedback function for logged-in users"""
    show_feedback_form(require_login=True)
