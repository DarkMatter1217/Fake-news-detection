import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, desc, asc
from config.database import get_database_engine, User, Feedback, NewsAnalysis
from datetime import datetime, timedelta
import pandas as pd

class DatabaseManager:
    def __init__(self):
        self.engine = get_database_engine()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()
    
    # User management methods
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            return self.session.query(User).filter(User.username == username).first()
        except Exception as e:
            st.error(f"Error getting user: {e}")
            return None
    
    def get_all_users(self):
        """Get all users"""
        try:
            return self.session.query(User).all()
        except Exception as e:
            st.error(f"Error getting users: {e}")
            return []
    
    def create_user(self, username, email, password_hash, role='user'):
        """Create new user"""
        try:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role
            )
            self.session.add(user)
            self.session.commit()
            return True, "User created successfully"
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating user: {e}"
    
    def update_user_login(self, username):
        """Update user's last login time"""
        try:
            user = self.get_user_by_username(username)
            if user:
                user.last_login = datetime.utcnow()
                self.session.commit()
        except Exception as e:
            st.error(f"Error updating login time: {e}")
    
    def deactivate_user(self, username):
        """Deactivate user account"""
        try:
            user = self.get_user_by_username(username)
            if user:
                user.is_active = False
                self.session.commit()
                return True, "User deactivated"
            return False, "User not found"
        except Exception as e:
            self.session.rollback()
            return False, f"Error deactivating user: {e}"
    
    # Feedback management methods
    def save_feedback(self, username, feedback_type, rating, message, page):
        """Save user feedback"""
        try:
            feedback = Feedback(
                username=username,
                feedback_type=feedback_type,
                rating=rating,
                message=message,
                page=page,
                created_at=datetime.utcnow()
            )
            
            self.session.add(feedback)
            self.session.commit()
            return True, "Feedback saved successfully"
            
        except Exception as e:
            self.session.rollback()
            return False, f"Error saving feedback: {e}"
    
    def get_all_feedback(self, limit=None):
        """Get all feedback"""
        try:
            query = self.session.query(Feedback).order_by(desc(Feedback.created_at))
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            st.error(f"Error getting feedback: {e}")
            return []
    
    def get_feedback_by_type(self, feedback_type):
        """Get feedback by type"""
        try:
            return self.session.query(Feedback).filter(
                Feedback.feedback_type == feedback_type
            ).order_by(desc(Feedback.created_at)).all()
        except Exception as e:
            st.error(f"Error getting feedback by type: {e}")
            return []
    
    def mark_feedback_resolved(self, feedback_id):
        """Mark feedback as resolved"""
        try:
            feedback = self.session.query(Feedback).filter(Feedback.id == feedback_id).first()
            if feedback:
                feedback.is_resolved = True
                self.session.commit()
                return True, "Feedback marked as resolved"
            return False, "Feedback not found"
        except Exception as e:
            self.session.rollback()
            return False, f"Error marking feedback as resolved: {e}"
    
    # News analysis methods
    def save_news_analysis(self, user_id, input_text, roberta_prediction, roberta_confidence,
                          newsapi_confidence, final_prediction, perplexity_prediction=None,
                          perplexity_report=None, articles_analyzed=0, trusted_sources_count=0):
        """Save news analysis results"""
        try:
            analysis = NewsAnalysis(
                user_id=user_id,
                input_text=input_text,
                roberta_prediction=roberta_prediction,
                roberta_confidence=roberta_confidence,
                newsapi_confidence=newsapi_confidence,
                final_prediction=final_prediction,
                perplexity_prediction=perplexity_prediction,
                perplexity_report=perplexity_report,
                articles_analyzed=articles_analyzed,
                trusted_sources_count=trusted_sources_count,
                created_at=datetime.utcnow()
            )
            
            self.session.add(analysis)
            self.session.commit()
            return True, "Analysis saved successfully"
            
        except Exception as e:
            self.session.rollback()
            return False, f"Error saving analysis: {e}"
    
    def get_all_analyses(self, limit=None):
        """Get all news analyses"""
        try:
            query = self.session.query(NewsAnalysis).order_by(desc(NewsAnalysis.created_at))
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            st.error(f"Error getting analyses: {e}")
            return []
    
    def get_analyses_by_user(self, user_id, limit=None):
        """Get analyses by user"""
        try:
            query = self.session.query(NewsAnalysis).filter(
                NewsAnalysis.user_id == user_id
            ).order_by(desc(NewsAnalysis.created_at))
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            st.error(f"Error getting user analyses: {e}")
            return []
    
    # Analytics methods
    def get_user_stats(self):
        """Get user statistics"""
        try:
            total_users = self.session.query(User).count()
            active_users = self.session.query(User).filter(User.is_active == True).count()
            admin_users = self.session.query(User).filter(User.role == 'admin').count()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'admin_users': admin_users,
                'inactive_users': total_users - active_users
            }
        except Exception as e:
            st.error(f"Error getting user stats: {e}")
            return {}
    
    def get_feedback_stats(self):
        """Get feedback statistics"""
        try:
            total_feedback = self.session.query(Feedback).count()
            resolved_feedback = self.session.query(Feedback).filter(Feedback.is_resolved == True).count()
            
            # Feedback by type
            feedback_by_type = self.session.query(
                Feedback.feedback_type,
                func.count(Feedback.id)
            ).group_by(Feedback.feedback_type).all()
            
            # Average rating
            avg_rating = self.session.query(func.avg(Feedback.rating)).filter(
                Feedback.rating.isnot(None)
            ).scalar()
            
            return {
                'total_feedback': total_feedback,
                'resolved_feedback': resolved_feedback,
                'pending_feedback': total_feedback - resolved_feedback,
                'feedback_by_type': dict(feedback_by_type),
                'average_rating': round(avg_rating, 2) if avg_rating else 0
            }
        except Exception as e:
            st.error(f"Error getting feedback stats: {e}")
            return {}
    
    def get_analysis_stats(self):
        """Get analysis statistics"""
        try:
            total_analyses = self.session.query(NewsAnalysis).count()
            
            # Predictions distribution
            predictions = self.session.query(
                NewsAnalysis.final_prediction,
                func.count(NewsAnalysis.id)
            ).group_by(NewsAnalysis.final_prediction).all()
            
            # Average confidence
            avg_roberta_confidence = self.session.query(func.avg(NewsAnalysis.roberta_confidence)).scalar()
            avg_newsapi_confidence = self.session.query(func.avg(NewsAnalysis.newsapi_confidence)).scalar()
            
            # Recent analyses (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_analyses = self.session.query(NewsAnalysis).filter(
                NewsAnalysis.created_at >= week_ago
            ).count()
            
            return {
                'total_analyses': total_analyses,
                'predictions_distribution': dict(predictions),
                'avg_roberta_confidence': round(avg_roberta_confidence, 3) if avg_roberta_confidence else 0,
                'avg_newsapi_confidence': round(avg_newsapi_confidence, 3) if avg_newsapi_confidence else 0,
                'recent_analyses': recent_analyses
            }
        except Exception as e:
            st.error(f"Error getting analysis stats: {e}")
            return {}
    
    def get_daily_usage_data(self, days=30):
        """Get daily usage data for charts"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Daily analyses
            daily_analyses = self.session.query(
                func.date(NewsAnalysis.created_at).label('date'),
                func.count(NewsAnalysis.id).label('count')
            ).filter(
                NewsAnalysis.created_at >= start_date
            ).group_by(func.date(NewsAnalysis.created_at)).all()
            
            # Daily feedback
            daily_feedback = self.session.query(
                func.date(Feedback.created_at).label('date'),
                func.count(Feedback.id).label('count')
            ).filter(
                Feedback.created_at >= start_date
            ).group_by(func.date(Feedback.created_at)).all()
            
            return {
                'daily_analyses': [(str(date), count) for date, count in daily_analyses],
                'daily_feedback': [(str(date), count) for date, count in daily_feedback]
            }
        except Exception as e:
            st.error(f"Error getting daily usage data: {e}")
            return {'daily_analyses': [], 'daily_feedback': []}

# Utility functions
def get_db_manager():
    """Get database manager instance"""
    return DatabaseManager()

def cleanup_old_data(days=90):
    """Clean up old data (older than specified days)"""
    try:
        db = get_db_manager()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old analyses
        old_analyses = db.session.query(NewsAnalysis).filter(
            NewsAnalysis.created_at < cutoff_date
        ).delete()
        
        # Delete old resolved feedback
        old_feedback = db.session.query(Feedback).filter(
            Feedback.created_at < cutoff_date,
            Feedback.is_resolved == True
        ).delete()
        
        db.session.commit()
        db.close()
        
        return True, f"Cleaned up {old_analyses} analyses and {old_feedback} feedback entries"
        
    except Exception as e:
        return False, f"Error cleaning up data: {e}"

def export_data_to_csv(table_name, file_path):
    """Export table data to CSV"""
    try:
        db = get_db_manager()
        
        if table_name == 'users':
            data = db.session.query(User).all()
            df = pd.DataFrame([{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role,
                'created_at': u.created_at,
                'last_login': u.last_login,
                'is_active': u.is_active
            } for u in data])
            
        elif table_name == 'feedback':
            data = db.session.query(Feedback).all()
            df = pd.DataFrame([{
                'id': f.id,
                'username': f.username,
                'feedback_type': f.feedback_type,
                'rating': f.rating,
                'message': f.message,
                'page': f.page,
                'created_at': f.created_at,
                'is_resolved': f.is_resolved
            } for f in data])
            
        elif table_name == 'analyses':
            data = db.session.query(NewsAnalysis).all()
            df = pd.DataFrame([{
                'id': a.id,
                'user_id': a.user_id,
                'input_text': a.input_text[:100] + '...' if len(a.input_text) > 100 else a.input_text,
                'roberta_prediction': a.roberta_prediction,
                'roberta_confidence': a.roberta_confidence,
                'newsapi_confidence': a.newsapi_confidence,
                'final_prediction': a.final_prediction,
                'perplexity_prediction': a.perplexity_prediction,
                'articles_analyzed': a.articles_analyzed,
                'trusted_sources_count': a.trusted_sources_count,
                'created_at': a.created_at
            } for a in data])
        else:
            return False, "Invalid table name"
        
        df.to_csv(file_path, index=False)
        db.close()
        
        return True, f"Data exported to {file_path}"
        
    except Exception as e:
        return False, f"Error exporting data: {e}"
