"""
Sample vulnerable application for testing CodeGuard AI.
This file contains intentional security vulnerabilities.
"""

import os
import subprocess
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Hardcoded secret (CWE-798)
SECRET_KEY = "my-super-secret-key-12345"
DATABASE_PASSWORD = "admin123"

# SQL Injection vulnerability (CWE-89)
@app.route('/user/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # VULNERABLE: Direct string interpolation
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return str(user)

# Command Injection vulnerability (CWE-78)
@app.route('/ping')
def ping_host():
    host = request.args.get('host', 'localhost')
    # VULNERABLE: Shell injection
    result = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return result.decode()

# XSS vulnerability (CWE-79)
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # VULNERABLE: XSS
    template = f"<h1>Search results for: {query}</h1>"
    return render_template_string(template)

# Weak cryptography (CWE-327)
import hashlib

def hash_password(password):
    # VULNERABLE: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()

# Insecure deserialization (CWE-502)
import pickle

def load_user_data(data):
    # VULNERABLE: Pickle can execute arbitrary code
    return pickle.loads(data)

# Path traversal (CWE-22)
@app.route('/file')
def read_file():
    filename = request.args.get('file', 'default.txt')
    # VULNERABLE: No path validation
    with open(filename, 'r') as f:
        return f.read()

# Insecure random (CWE-330)
import random

def generate_token():
    # VULNERABLE: Not cryptographically secure
    return random.randint(1000, 9999)

# Hardcoded credentials (CWE-798)
DB_USER = "admin"
DB_PASS = "password123"

# Missing authentication
@app.route('/admin')
def admin_panel():
    # VULNERABLE: No authentication check
    return "Admin panel - Welcome!"

# Insecure direct object reference (CWE-639)
@app.route('/api/user/<user_id>/data')
def get_user_data(user_id):
    # VULNERABLE: No authorization check
    data = {"user_id": user_id, "sensitive_data": "secret"}
    return data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

