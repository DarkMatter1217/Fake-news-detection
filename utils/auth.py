import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import os

# Global config variable to ensure consistency
_config = None

def load_auth_config():
    """Load authentication configuration from credentials.yml"""
    global _config
    
    if _config is not None:
        return _config
    
    config_path = './credentials.yml'
    
    try:
        with open(config_path) as file:
            _config = yaml.load(file, Loader=SafeLoader)
        
        # DISABLE COOKIES by setting expiry to 0
        _config['cookie']['expiry_days'] = 0
        _config['cookie']['key'] = 'disabled_key'
        _config['cookie']['name'] = 'disabled_cookie'
        
        return _config
    except FileNotFoundError:
        st.error("credentials.yml file not found")
        return None

def setup_authenticator():
    """Setup authenticator with disabled cookies"""
    config = load_auth_config()
    
    if config is None:
        return None, None
    
    try:
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
        return authenticator, config
    except Exception as e:
        st.error(f"Error setting up authenticator: {e}")
        return None, config

def check_authentication():
    """Check authentication status"""
    if st.session_state.get('authentication_status') is True:
        return True, st.session_state.get('name'), st.session_state.get('username')
    return False, None, None

def is_admin():
    """Check if current user is admin"""
    if not st.session_state.get('authentication_status'):
        return False
    
    try:
        config = load_auth_config()
        if config is None:
            return False
            
        username = st.session_state.get('username')
        
        if username and username in config['credentials']['usernames']:
            user_roles = config['credentials']['usernames'][username].get('roles', [])
            return 'admin' in user_roles
        else:
            return False
            
    except Exception as e:
        return False

def logout_user():
    """Clear all session data"""
    global _config
    _config = None  # Clear cached config
    
    auth_keys = [
        'authentication_status', 'name', 'username', 'logout',
        'user_login_form', 'admin_login_form', 'app_started'
    ]
    
    for key in auth_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    return True
