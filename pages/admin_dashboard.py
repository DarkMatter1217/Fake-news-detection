import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from config.database import get_session, NewsAnalysis, Feedback
from sqlalchemy import func, desc
import random

def show_admin_dashboard():
    """Show simplified admin dashboard with blue/orange color scheme"""
    
    st.markdown("## 📊 Admin Dashboard")
    st.markdown("Real-time fake news detection system analytics")
    
    # Custom CSS for metric cards with new colors
    st.markdown("""
    <style>
        /* Custom metric styling */
        [data-testid="metric-container"] {
            background-color: white;
            border: 1px solid #e1e5e9;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        /* Blue for positive/increase indicators */
        .metric-increase {
            color: #0066cc !important;
        }
        
        /* Orange for neutral indicators */
        .metric-neutral {
            color: #ff8c00 !important;
        }
        
        /* Purple for special indicators */
        .metric-special {
            color: #8a3ffc !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Get real data from database
    session = get_session()
    
    try:
        # Real metrics from your database
        total_analyses = session.query(NewsAnalysis).count()
        total_feedback = session.query(Feedback).count()
        
        # Get unique users count
        total_users = session.query(NewsAnalysis.user_id).distinct().count() if total_analyses > 0 else 0
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_analyses = session.query(NewsAnalysis).filter(
            NewsAnalysis.created_at >= week_ago
        ).count()
        
        # Average confidence from real data
        avg_confidence_result = session.query(func.avg(NewsAnalysis.roberta_confidence)).scalar()
        avg_confidence = (avg_confidence_result * 100) if avg_confidence_result else 0
        
    except Exception as e:
        st.error(f"Database error: {e}")
        # Fallback values
        total_analyses = 0
        total_feedback = 0
        total_users = 0
        recent_analyses = 0
        avg_confidence = 0
    
    # Essential Metrics Cards with new color scheme
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Users",
            value=total_users,
            delta="Active users",
            delta_color="normal"  # This will use blue instead of green
        )
    
    with col2:
        st.metric(
            label="📊 Total Analyses",
            value=total_analyses,
            delta=f"+{recent_analyses} this week",
            delta_color="normal"  # This will use blue instead of green
        )
    
    with col3:
        st.metric(
            label="💬 Total Feedback",
            value=total_feedback,
            delta="User responses",
            delta_color="normal"  # This will use blue instead of green
        )
    
    with col4:
        st.metric(
            label="🔍 Avg Confidence",
            value=f"{avg_confidence:.1f}%",
            delta="Model certainty",
            delta_color="normal"  # This will use blue instead of green
        )
    
    st.markdown("---")
    
    # Essential Charts Section with new color scheme
    col1, col2 = st.columns(2)
    
    with col1:
        # Detection Results with blue/orange color scheme
        st.markdown("### 🔍 Detection Results")
        
        try:
            prediction_stats = session.query(
                NewsAnalysis.final_prediction,
                func.count(NewsAnalysis.id).label('count')
            ).group_by(NewsAnalysis.final_prediction).all()
            
            if prediction_stats:
                labels = [stat[0] for stat in prediction_stats]
                values = [stat[1] for stat in prediction_stats]
                
                fig_pie = px.pie(
                    values=values,
                    names=labels,
                    title="News Credibility Analysis Results",
                    color_discrete_map={
                        'True': '#0066cc',      # Blue instead of green
                        'False': '#ff6b6b',     # Red
                        'Likely False': '#ff8c00',  # Orange
                        'unknown': '#6b7280'    # Gray
                    }
                )
                fig_pie.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No analysis data available yet. Start analyzing news to see results!")
        except Exception as e:
            st.error(f"Error loading prediction stats: {e}")
    
    with col2:
        # Daily Analysis Trend with blue line
        st.markdown("### 📈 Daily Analysis Activity")
        
        try:
            # Get daily analysis counts for last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            daily_stats = session.query(
                func.date(NewsAnalysis.created_at).label('date'),
                func.count(NewsAnalysis.id).label('count')
            ).filter(
                NewsAnalysis.created_at >= thirty_days_ago
            ).group_by(
                func.date(NewsAnalysis.created_at)
            ).order_by('date').all()
            
            if daily_stats:
                dates = [stat[0] for stat in daily_stats]
                counts = [stat[1] for stat in daily_stats]
                
                df_trend = pd.DataFrame({
                    'Date': dates,
                    'Analyses': counts
                })
                
                fig_line = px.line(
                    df_trend,
                    x='Date',
                    y='Analyses',
                    title='Daily Fake News Analyses',
                    markers=True
                )
                fig_line.update_layout(height=400)
                fig_line.update_traces(line_color='#0066cc')  # Blue instead of green/red
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No daily analysis data available yet.")
        except Exception as e:
            st.error(f"Error loading daily stats: {e}")
    
    st.markdown("---")
    
    # Recent Analyses
    st.markdown("### 📝 Recent Analyses")
    
    try:
        recent_analyses_data = session.query(NewsAnalysis).order_by(
            desc(NewsAnalysis.created_at)
        ).limit(10).all()
        
        if recent_analyses_data:
            for analysis in recent_analyses_data:
                with st.expander(f"Analysis - {analysis.created_at.strftime('%Y-%m-%d %H:%M')}"):
                    st.write(f"**Input:** {analysis.input_text[:100]}...")
                    st.write(f"**RoBERTa Prediction:** {analysis.roberta_prediction}")
                    st.write(f"**Final Result:** {analysis.final_prediction}")
                    st.write(f"**Confidence:** {analysis.roberta_confidence:.1%}")
        else:
            st.info("No analyses performed yet. Start using the fake news detector!")
    except Exception as e:
        st.error(f"Error loading recent analyses: {e}")
    
    session.close()
