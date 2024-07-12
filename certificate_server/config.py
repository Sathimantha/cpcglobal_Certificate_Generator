# config.py
# Replace these after installing the program in the server environment
ADMIN_PASSWORD = 'password' # replace password at prod
SECRET_KEY = 'session_key'

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "password",  # replace password at prod
    "port": 3306,
    "database": "students1"
}