import streamlit as st
from models.news_classifier import get_classifier
from models.confidence_analyzer import ConfidenceAnalyzer
from services.news_api_service import get_news_service
from services.perplexity_service import get_perplexity_service
from config.database import get_session, NewsAnalysis
from utils.auth import check_authentication
from utils.animations import show_spyglass_loader, show_typing_animation
import time

def show_fake_news_detector():
    """Main fake news detection interface with maximum readability"""
    
    # Enhanced readability CSS with white backgrounds and dark text
    st.markdown("""
    <style>
        /* Force white background for all content */
        .main .block-container {
            max-width: 100% !important;
            padding: 2rem !important;
            background: white !important;
            border-radius: 20px !important;
            margin: 2rem auto !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important;
            border: 3px solid #e2e8f0 !important;
        }
        
        /* Override Streamlit's default background */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        
        /* High contrast title */
        .main-title {
            font-size: 4rem !important;
            font-weight: 900 !important;
            color: #1a202c !important;
            line-height: 1.1 !important;
            margin: 0 0 2rem 0 !important;
            text-align: center !important;
            background: white !important;
            padding: 3rem !important;
            border-radius: 20px !important;
            box-shadow: 0 15px 35px rgba(0,0,0,0.12) !important;
            border: 3px solid #667eea !important;
        }
        
        /* High contrast subtitle */
        .subtitle {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #2d3748 !important;
            text-align: center !important;
            margin-bottom: 3rem !important;
            line-height: 1.6 !important;
            background: white !important;
            padding: 2rem !important;
            border-radius: 15px !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1) !important;
            border: 2px solid #e2e8f0 !important;
        }
        
        /* High contrast description */
        .description {
            font-size: 1.3rem !important;
            line-height: 1.8 !important;
            color: #1e293b !important;
            margin-bottom: 3rem !important;
            text-align: center !important;
            max-width: 900px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            background: white !important;
            padding: 2.5rem !important;
            border-radius: 15px !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1) !important;
            border: 2px solid #e2e8f0 !important;
            font-weight: 500 !important;
        }
        
        /* Enhanced text area */
        .stTextArea > div > div > textarea {
            border-radius: 16px !important;
            border: 3px solid #667eea !important;
            padding: 2rem !important;
            font-size: 1.2rem !important;
            line-height: 1.7 !important;
            font-family: inherit !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1) !important;
            resize: vertical !important;
            background: white !important;
            color: #1e293b !important;
            font-weight: 500 !important;
            min-height: 200px !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: #764ba2 !important;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2) !important;
            outline: none !important;
        }
        
        .stTextArea label {
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
            margin-bottom: 1rem !important;
            background: white !important;
            padding: 1rem 1.5rem !important;
            border-radius: 10px !important;
            border: 2px solid #e2e8f0 !important;
        }
        
        /* Process steps with enhanced readability */
        .analysis-steps-horizontal, .analysis-results-section {
            background: white !important;
            border: 4px solid #667eea !important;
            border-radius: 20px !important;
            padding: 3rem !important;
            margin: 3rem 0 !important;
            box-shadow: 0 15px 35px rgba(0,0,0,0.12) !important;
        }
        
        .analysis-steps-horizontal h3, .analysis-results-section h3 {
            color: #1e293b !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
            margin-bottom: 2.5rem !important;
            text-align: center !important;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
            padding: 1.5rem !important;
            border-radius: 15px !important;
            border: 2px solid #e2e8f0 !important;
        }
        
        .step-container, .results-container {
            display: flex !important;
            justify-content: space-between !important;
            align-items: flex-start !important;
            gap: 2rem !important;
            flex-wrap: wrap !important;
        }
        
        .step-item, .result-item {
            flex: 1 !important;
            min-width: 220px !important;
            text-align: center !important;
            padding: 2rem !important;
            background: white !important;
            border-radius: 15px !important;
            border: 3px solid #e2e8f0 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
        }
        
        .step-item:hover, .result-item:hover {
            transform: translateY(-6px) !important;
            box-shadow: 0 15px 30px rgba(102, 126, 234, 0.2) !important;
            border-color: #667eea !important;
        }
        
        .step-number, .result-icon {
            width: 3.5rem !important;
            height: 3.5rem !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 900 !important;
            font-size: 1.4rem !important;
            margin: 0 auto 1.5rem auto !important;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4) !important;
        }
        
        .step-title, .result-title {
            font-size: 1.2rem !important;
            font-weight: 800 !important;
            color: #1e293b !important;
            margin-bottom: 0.8rem !important;
        }
        
        .step-description, .result-description {
            font-size: 1rem !important;
            color: #4a5568 !important;
            line-height: 1.5 !important;
            font-weight: 600 !important;
        }
        
        /* Enhanced dropdown section */
        .dropdown-section {
            background: white !important;
            padding: 3rem !important;
            border-radius: 20px !important;
            box-shadow: 0 15px 35px rgba(0,0,0,0.12) !important;
            border: 3px solid #e2e8f0 !important;
            margin: 3rem 0 !important;
        }
        
        .dropdown-title {
            color: #1e293b !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
            margin-bottom: 2rem !important;
            text-align: center !important;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
            padding: 1.5rem !important;
            border-radius: 15px !important;
            border: 2px solid #e2e8f0 !important;
        }
        
        /* Enhanced selectbox with better readability */
        .stSelectbox > div > div > select {
            border-radius: 16px !important;
            border: 3px solid #667eea !important;
            padding: 1.5rem !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            background: white !important;
            color: #1e293b !important;
            min-height: 70px !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1) !important;
        }
        
        .stSelectbox > div > div > select:focus {
            border-color: #764ba2 !important;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2) !important;
            outline: none !important;
        }
        
        .stSelectbox label {
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
            margin-bottom: 1rem !important;
        }
        
        /* Enhanced button with maximum visibility */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 1.8rem 3rem !important;
            font-weight: 800 !important;
            font-size: 1.3rem !important;
            width: 100% !important;
            margin-top: 2rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4) !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 18px 40px rgba(102, 126, 234, 0.5) !important;
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        }
        
        /* Force all text to be dark and readable */
        p, div, span, h1, h2, h3, h4, h5, h6, li, label {
            color: #1e293b !important;
        }
        
        .stMarkdown p {
            color: #1e293b !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
        }
        
        /* Section titles with enhanced visibility */
        .section-title {
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            color: #1e293b !important;
            margin: 4rem 0 3rem 0 !important;
            text-align: center !important;
            position: relative !important;
            background: white !important;
            padding: 2.5rem !important;
            border-radius: 20px !important;
            box-shadow: 0 15px 35px rgba(0,0,0,0.12) !important;
            border: 3px solid #e2e8f0 !important;
        }
        
        .section-title::after {
            content: '' !important;
            position: absolute !important;
            bottom: -10px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100px !important;
            height: 6px !important;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
            border-radius: 3px !important;
        }
        
        /* Article cards with enhanced readability */
        .article-card {
            background: white !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 20px !important;
            padding: 2.5rem !important;
            margin: 2rem 0 !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
        }
        
        .article-card:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important;
            border-color: #667eea !important;
        }
        
        .article-number {
            font-size: 1.2rem !important;
            font-weight: 800 !important;
            color: #667eea !important;
            margin-bottom: 1rem !important;
        }
        
        .article-title {
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
            line-height: 1.4 !important;
            margin-bottom: 1rem !important;
        }
        
        .article-description {
            font-size: 1.1rem !important;
            color: #4a5568 !important;
            line-height: 1.6 !important;
            margin-bottom: 1rem !important;
            font-weight: 500 !important;
        }
        
        .credibility-score {
            background: white !important;
            border: 3px solid #667eea !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            text-align: center !important;
            min-width: 180px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
        }
        
        .credibility-score:hover {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-color: #764ba2 !important;
            transform: scale(1.05) !important;
        }
        
        .score-label {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #4a5568 !important;
            margin-bottom: 1rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }
        
        .score-value {
            font-size: 2.5rem !important;
            font-weight: 900 !important;
            color: #667eea !important;
            margin: 1rem 0 !important;
            line-height: 1 !important;
        }
        
        .score-date {
            font-size: 0.9rem !important;
            color: #64748b !important;
            margin-top: 1rem !important;
            font-weight: 600 !important;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2.5rem !important;
            }
            
            .subtitle {
                font-size: 1.2rem !important;
            }
            
            .description {
                font-size: 1.1rem !important;
            }
            
            .step-container, .results-container {
                flex-direction: column !important;
            }
            
            .step-item, .result-item {
                min-width: 100% !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced page header with maximum contrast
    st.markdown("""
    <div class="main-title">🔍 Fake News Detection Portal</div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="subtitle">
        Advanced AI-powered truth verification with real-time fact-checking against 100+ trusted global sources
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced description with maximum readability
    st.markdown("""
    <div class="description">
        Enter a news article or headline below to analyze its credibility using our sophisticated AI system. 
        Our platform combines multiple advanced technologies including RoBERTa transformers, real-time news correlation, 
        and expert AI verification to provide you with comprehensive credibility analysis.
    </div>
    """, unsafe_allow_html=True)
    
    # Full-width input section with enhanced readability
    user_input = st.text_area(
        "📝 Enter news content to analyze:",
        height=200,
        placeholder="Paste your news article, headline, or claim here for comprehensive analysis...",
        key="news_input",
        help="Enter any news content, from headlines to full articles. Our AI will analyze it for credibility."
    )
    
    # Analysis process steps with enhanced readability
    st.markdown("""
    <div class="analysis-steps-horizontal">
        <h3>🔍 Analysis Process</h3>
        <div class="step-container">
            <div class="step-item">
                <div class="step-number">1</div>
                <div class="step-title">🤖 AI Analysis</div>
                <div class="step-description">RoBERTa transformer model prediction</div>
            </div>
            <div class="step-item">
                <div class="step-number">2</div>
                <div class="step-title">📰 Fact Checking</div>
                <div class="step-description">Cross-reference with 1000+ articles</div>
            </div>
            <div class="step-item">
                <div class="step-number">3</div>
                <div class="step-title">📊 Confidence Scoring</div>
                <div class="step-description">Calculate credibility metrics</div>
            </div>
            <div class="step-item">
                <div class="step-number">4</div>
                <div class="step-title">🧠 Expert Verification</div>
                <div class="step-description">Perplexity AI analysis</div>
            </div>
            <div class="step-item">
                <div class="step-number">5</div>
                <div class="step-title">📝 Detailed Report</div>
                <div class="step-description">Comprehensive findings</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced dropdown section with maximum readability
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 3, 1], gap="large")
    
    with col2:
        st.markdown("""
        <div class="dropdown-section">
            <div class="dropdown-title">
                Choose Your Analysis Type
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        analysis_option = st.selectbox(
            "Select Analysis Method:",
            options=[
                "Select Analysis Type",
                "🔍 Quick News Analysis", 
                "📝 Detailed Analysis Report"
            ],
            index=0,
            key="analysis_dropdown",
            help="Choose between quick analysis for immediate results or detailed report for comprehensive insights"
        )
        
        if st.button("🚀 Start Analysis", type="primary", key="execute_analysis", use_container_width=True):
            if not user_input or not isinstance(user_input, str) or not user_input.strip():
                st.error("⚠️ Please enter some text to analyze.")
            elif analysis_option == "Select Analysis Type":
                st.error("⚠️ Please select an analysis type from the dropdown.")
            else:
                execute_analysis(user_input.strip(), analysis_option)

def execute_analysis(input_text, analysis_type):
    """Execute the selected analysis type"""
    
    if analysis_type == "🔍 Quick News Analysis":
        analyze_news_with_enhanced_animation(input_text)
    elif analysis_type == "📝 Detailed Analysis Report":
        generate_detailed_report_with_animation(input_text)

def analyze_news_with_enhanced_animation(input_text):
    """Perform complete news analysis with enhanced animations and better UX"""
    
    if not input_text or not isinstance(input_text, str):
        st.error("❌ Invalid input text provided")
        return
    
    input_text = input_text.strip() if input_text else ""
    if not input_text:
        st.error("❌ Please enter some text to analyze")
        return
    
    loader_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    try:
        # Enhanced progress tracking with better descriptions
        steps = [
            ("🤖 Initializing AI neural networks...", 10),
            ("🤖 Running RoBERTa transformer analysis...", 25),
            ("📰 Scanning global news databases...", 40),
            ("📰 Cross-referencing with trusted sources...", 55),
            ("📊 Calculating credibility scores...", 70),
            ("📊 Analyzing source reliability...", 80),
            ("🧠 Consulting expert AI systems...", 90),
            ("✅ Compiling final analysis...", 100)
        ]
        
        # Step 1: RoBERTa Analysis
        loader_placeholder = show_spyglass_loader(steps[0][0])
        with progress_placeholder:
            progress_bar = st.progress(0)
        time.sleep(1.5)
        
        loader_placeholder.empty()
        loader_placeholder = show_spyglass_loader(steps[1][0])
        progress_bar.progress(steps[1][1])
        time.sleep(2)
        
        classifier = get_classifier()
        roberta_prediction, roberta_confidence = classifier.predict(input_text)
        
        if roberta_prediction is None:
            loader_placeholder.empty()
            progress_placeholder.empty()
            st.error("❌ Failed to analyze text with AI model.")
            return
        
        # Step 2: Fetch related articles
        loader_placeholder.empty()
        loader_placeholder = show_spyglass_loader(steps[2][0])
        progress_bar.progress(steps[2][1])
        time.sleep(1.5)
        
        loader_placeholder.empty()
        loader_placeholder = show_spyglass_loader(steps[3][0])
        progress_bar.progress(steps[3][1])
        time.sleep(2)
        
        news_service = get_news_service()
        articles = news_service.fetch_related_articles(input_text, max_articles=1000)
        
        # Step 3: Confidence analysis
        loader_placeholder.empty()
        loader_placeholder = show_spyglass_loader(steps[4][0])
        progress_bar.progress(steps[4][1])
        time.sleep(1.5)
        
        loader_placeholder.empty()
        loader_placeholder = show_spyglass_loader(steps[5][0])
        progress_bar.progress(steps[5][1])
        time.sleep(1.5)
        
        analyzer = ConfidenceAnalyzer()
        newsapi_confidence, top_articles = analyzer.analyze_articles(articles, input_text)
        final_prediction, combined_confidence = analyzer.get_final_prediction(newsapi_confidence)
        
        # Step 4: Perplexity prediction
        loader_placeholder.empty()
        loader_placeholder = show_spyglass_loader(steps[6][0])
        progress_bar.progress(steps[6][1])
        time.sleep(2)
        
        perplexity_service = get_perplexity_service()
        perplexity_prediction, perplexity_explanation = perplexity_service.predict_news_credibility(input_text)
        
        # Final step
        loader_placeholder.empty()
        loader_placeholder = show_spyglass_loader(steps[7][0])
        progress_bar.progress(steps[7][1])
        time.sleep(1)
        
        loader_placeholder.empty()
        progress_placeholder.empty()
        
        # Enhanced success animation with white background
        success_placeholder = st.empty()
        success_placeholder.markdown("""
        <div style="text-align: center; padding: 4rem; background: white; 
                    border-radius: 20px; margin: 3rem 0; border: 4px solid #10b981;
                    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.2);">
            <div style="font-size: 5rem; animation: bounce 1s ease-in-out; margin-bottom: 2rem;">✅</div>
            <div style="font-size: 2rem; color: #059669; font-weight: 800; margin-bottom: 1rem;">Analysis Complete!</div>
            <div style="font-size: 1.3rem; color: #047857; font-weight: 600;">Your news content has been thoroughly analyzed</div>
        </div>
        <style>
        @keyframes bounce {
            0%, 20%, 60%, 100% { transform: translateY(0); }
            40% { transform: translateY(-20px); }
            80% { transform: translateY(-10px); }
        }
        </style>
        """, unsafe_allow_html=True)
        time.sleep(3)
        success_placeholder.empty()
        
        # Display enhanced results with same styling as analysis process
        display_perfectly_aligned_results(
            input_text, roberta_prediction, roberta_confidence,
            newsapi_confidence, final_prediction, combined_confidence,
            len(articles), top_articles, perplexity_prediction, perplexity_explanation
        )
        
        save_analysis_to_db(
            input_text, roberta_prediction, roberta_confidence,
            newsapi_confidence, final_prediction, perplexity_prediction
        )
        
    except Exception as e:
        loader_placeholder.empty()
        progress_placeholder.empty()
        st.error(f"❌ An error occurred during analysis: {str(e)}")

def generate_detailed_report_with_animation(input_text):
    """Generate detailed report with enhanced animation and better UX"""
    
    if not input_text or not isinstance(input_text, str):
        st.error("❌ Invalid input text provided")
        return
    
    input_text = input_text.strip() if input_text else ""
    if not input_text:
        st.error("❌ Please enter some text to analyze")
        return
    
    loader_placeholder = show_spyglass_loader("📝 Preparing comprehensive analysis...")
    time.sleep(1.5)
    
    loader_placeholder.empty()
    loader_placeholder = show_spyglass_loader("📝 Generating detailed insights...")
    time.sleep(2)
    
    loader_placeholder.empty()
    loader_placeholder = show_spyglass_loader("📝 Formatting expert report...")
    time.sleep(1.5)
    
    try:
        perplexity_service = get_perplexity_service()
        classifier = get_classifier()
        roberta_prediction, roberta_confidence = classifier.predict(input_text)
        
        news_service = get_news_service()
        articles = news_service.fetch_related_articles(input_text, max_articles=100)
        
        analyzer = ConfidenceAnalyzer()
        newsapi_confidence, top_articles = analyzer.analyze_articles(articles, input_text)
        final_prediction, _ = analyzer.get_final_prediction(newsapi_confidence)
        
        detailed_report = perplexity_service.generate_detailed_report(
            input_text, roberta_prediction, roberta_confidence,
            newsapi_confidence, final_prediction, top_articles
        )
        
        loader_placeholder.empty()
        
        st.markdown('<div class="section-title">📝 Detailed Analysis Report</div>', unsafe_allow_html=True)
        with st.expander("🔍 View Full AI-Generated Expert Report", expanded=True):
            st.markdown(f"""
            <div style="background: white; padding: 3rem; border-radius: 16px; border: 3px solid #e2e8f0;
                        color: #1e293b; font-size: 1.2rem; line-height: 1.8; font-weight: 500;">
                {detailed_report}
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        loader_placeholder.empty()
        st.error(f"❌ Error generating report: {str(e)}")

def display_perfectly_aligned_results(input_text, roberta_prediction, roberta_confidence,
                                     newsapi_confidence, final_prediction, combined_confidence,
                                     articles_count, top_articles, perplexity_prediction, perplexity_explanation):
    """Display analysis results with SAME styling as analysis process"""
    
    # Analysis results section with SAME styling as process section
    st.markdown("""
    <div class="analysis-results-section">
        <h3>📊 Analysis Results</h3>
        <div class="results-container">
            <div class="result-item">
                <div class="result-icon">🤖</div>
                <div class="result-title">RoBERTa AI</div>
                <div class="result-description">
                    <strong>{}</strong><br>
                    Confidence: <strong>{:.1%}</strong>
                </div>
            </div>
            <div class="result-item">
                <div class="result-icon">📰</div>
                <div class="result-title">News Analysis</div>
                <div class="result-description">
                    <strong>{}</strong><br>
                    Confidence: <strong>{:.1%}</strong>
                </div>
            </div>
            <div class="result-item">
                <div class="result-icon">🧠</div>
                <div class="result-title">Perplexity AI</div>
                <div class="result-description">
                    <strong>{}</strong><br>
                    AI Verification
                </div>
            </div>
            <div class="result-item">
                <div class="result-icon">📈</div>
                <div class="result-title">Overall Stats</div>
                <div class="result-description">
                    Articles: <strong>{}</strong><br>
                    Trusted Sources: <strong>{}</strong>
                </div>
            </div>
        </div>
    </div>
    """.format(
        roberta_prediction.title() if roberta_prediction else 'Uncertain',
        roberta_confidence,
        final_prediction if final_prediction != "Likely False" else "Likely False",
        combined_confidence,
        perplexity_prediction if perplexity_prediction not in ["Unknown", "Not Available"] else "Not Available",
        articles_count,
        len([a for a in top_articles[:10] if a.get('score', 0) > 0.7])
    ), unsafe_allow_html=True)
    
    # Enhanced article cards section
    st.markdown('<div class="section-title">📰 Top 20 Most Relevant Articles from Trusted Sources</div>', unsafe_allow_html=True)
    
    if top_articles:
        for i, article in enumerate(top_articles[:20], 1):
            if not article or not isinstance(article, dict):
                continue
            
            with st.container():
                col1, col2 = st.columns([5, 1], gap="medium")
                
                with col1:
                    score = article.get('score', 0)
                    credibility_icon = "🟢" if score > 0.7 else "🟡" if score > 0.5 else "🔴"
                    source = article.get('source', 'Unknown')
                    title = article.get('title', 'No title')
                    url = article.get('url', '')
                    description = article.get('description', '')
                    
                    st.markdown(f"""
                    <div class="article-card">
                        <div class="article-number">{i}. {credibility_icon} {source}</div>
                        <div class="article-title">
                            {"<a href='" + url + "' target='_blank' style='color: #1e293b; text-decoration: none;'>" + title + "</a>" if url else title}
                        </div>
                        <div class="article-description">
                            {description[:200] + "..." if description else "No description available"}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="credibility-score">
                        <div class="score-label">Credibility</div>
                        <div class="score-value">{score:.2f}</div>
                        <div class="score-date">
                            📅 {article.get('published_at', '')[:10] if article.get('published_at') else 'Unknown'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if i < 20:
                    st.markdown('<hr style="margin: 2rem 0; border: 2px solid #e2e8f0;">', unsafe_allow_html=True)
    
    # Enhanced Perplexity explanation section
    if perplexity_explanation and perplexity_explanation not in ["Perplexity API key not configured", "Not Available"]:
        st.markdown('<div class="section-title">🧠 Expert AI Analysis</div>', unsafe_allow_html=True)
        with st.expander("🔍 View Detailed Perplexity AI Explanation", expanded=False):
            st.markdown(f"""
            <div style="background: white; padding: 3rem; border-radius: 16px; border: 3px solid #e2e8f0; 
                        font-size: 1.2rem; line-height: 1.8; color: #1e293b; font-weight: 500;">
                {perplexity_explanation}
            </div>
            """, unsafe_allow_html=True)

def save_analysis_to_db(input_text, roberta_prediction, roberta_confidence,
                       newsapi_confidence, final_prediction, perplexity_prediction):
    """Save analysis results to database with enhanced error handling"""
    try:
        session = get_session()
        
        is_authenticated, name, username = check_authentication()
        user_id = None
        
        analysis = NewsAnalysis(
            user_id=user_id,
            input_text=input_text,
            roberta_prediction=roberta_prediction or "unknown",
            roberta_confidence=roberta_confidence or 0.0,
            newsapi_confidence=newsapi_confidence or 0.0,
            final_prediction=final_prediction or "unknown",
            perplexity_prediction=perplexity_prediction or "unknown"
        )
        
        session.add(analysis)
        session.commit()
        session.close()
        
        st.success("✅ Analysis results saved successfully!")
        
    except Exception as e:
        st.warning(f"⚠️ Could not save analysis to database: {str(e)}")
