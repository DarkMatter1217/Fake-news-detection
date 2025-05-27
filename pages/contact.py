import streamlit as st


def show_contact():
    """Display contact information"""

    st.markdown("## 📞 Contact Us")
    st.markdown(
        "Get in touch with our team for support, questions, or collaboration opportunities."
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 👨‍💻 Developer Information")

        # You can edit this section with your information
        st.markdown("""
        **Name:** Prabhjot Singh  
        **Email:** prabhjot96439@gmail.com  
        **Name:** Rushil Nijhawan  
        **Email:** RJ001@gmail.com 
        
        ---
        
        ### 🚀 About This Project
        
        This Fake News Detection System was developed to help users identify potentially false or misleading information using advanced AI technologies and real-time fact-checking against trusted global news sources.
        
        **Technologies Used:**
        - 🤖 RoBERTa Transformer Model for text analysis
        - 📰 NewsAPI for real-time article fetching
        - 🧠 Perplexity AI for detailed analysis
        - 🎯 Streamlit for interactive web interface
        - 🗄️ SQLAlchemy for database management
        
        **Features:**
        - Real-time fake news detection
        - Cross-referencing with 100+ trusted global sources
        - Confidence scoring and detailed reporting
        - User feedback system
        - Admin dashboard for monitoring
        
        ---
        
        ### 🤝 Support & Collaboration
        
        If you have questions, suggestions, or would like to collaborate on this project, please don't hesitate to reach out. We welcome feedback and contributions from the community.
        
        **For Technical Support:**
        - Report bugs or issues
        - Request new features
        - Get help with setup
        
        """)

    with col2:
        st.markdown("### 📊 Project Stats")

        # Project statistics
        st.info("""
        **📰 Sources:** 100+ Global  
        **🌍 Languages:** English  
        **⚡ Response Time:** <10 seconds  
        **🔄 Updates:** Real-time  
        """)

        st.markdown("### 🛠️ Quick Actions")

        if st.button("📧 Send Email", type="primary"):
            st.markdown("**Email:** prabhjot96439@gmail.com")

        if st.button("🐛 Report Bug"):
            st.markdown("Please use the Feedback page to report any bugs or issues.")

        if st.button("💡 Suggest Feature"):
            st.markdown(
                "We'd love to hear your feature suggestions! Use the Feedback page."
            )

        st.markdown("### 🔗 Useful Links")

        st.markdown("""
        - [🔧 API Reference](https://docs.perplexity.ai/api-reference/chat-completions)
        """)
