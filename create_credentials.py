import streamlit_authenticator as stauth
import yaml

users = {
    'admin': {
        'email': 'admin@fakenews.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'password': 'admin123',
        'roles': ['admin']
    },
    'testuser': {
        'email': 'test@fakenews.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'test123',
        'roles': ['user']
    },
    'Prabhjot':{
        'email':'pj2001@gmail.com',
        'first_name': 'Prabhjot',
        'last_name': 'Singh',
        'password': 'prabhjot123',
        'roles': ['user','admin']
    },
    'P_admin':{
        'email': 'pj@gmail.com',
        'first_name': 'Prabhjot',
        'last_name': 'Singh',
        'password': 'prabhjot123',
        'roles': ['admin']
    }
    
}

config = {
    'cookie': {
        'expiry_days': 30,
        'key': 'fake_news_detector_auth_key',
        'name': 'fake_news_detector_auth_cookie'
    },
    'credentials': {
        'usernames': {}
    }
}

for username, user_data in users.items():
    config['credentials']['usernames'][username] = {
        'email': user_data['email'],
        'failed_login_attempts': 0,
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'logged_in': False,
        'password': user_data['password'],
        'roles': user_data['roles']
    }

# Hash the passwords  and saving 
stauth.Hasher.hash_passwords(config['credentials'])
with open('credentials.yml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)




