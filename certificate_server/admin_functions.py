import os
import pandas as pd
import joblib
import logging
from flask import jsonify, send_file

CACHE_FILE = 'data_cache.joblib'
EXCEL_FILE = 'file.xlsx'
CACHE_CONFIG_FILE = 'cache_config.joblib'
DOWNLOAD_LOG_FILE = 'certificate_downloads.xlsx'
GENERATED_FILES_DIR = 'generated_files'

def get_cache_status():
    if os.path.exists(CACHE_CONFIG_FILE):
        return joblib.load(CACHE_CONFIG_FILE)
    return True  # Default to caching enabled

def set_cache_status(status):
    joblib.dump(status, CACHE_CONFIG_FILE)

def load_data():
    if get_cache_status() and os.path.exists(CACHE_FILE) and os.path.getmtime(CACHE_FILE) > os.path.getmtime(EXCEL_FILE):
        logging.info("Loading data from cache")
        df = joblib.load(CACHE_FILE)
    else:
        logging.info("Loading data from Excel and creating cache")
        df = pd.read_excel(EXCEL_FILE)
        if get_cache_status():
            joblib.dump(df, CACHE_FILE)
    return df

def refresh_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        if get_cache_status():
            joblib.dump(df, CACHE_FILE)
        return jsonify({"message": "Data refreshed successfully"}), 200
    except Exception as e:
        logging.error(f"Error refreshing data: {str(e)}")
        return jsonify({"error": "Failed to refresh data"}), 500

def toggle_caching():
    current_status = get_cache_status()
    new_status = not current_status
    set_cache_status(new_status)
    return jsonify({"message": f"Caching {'enabled' if new_status else 'disabled'}"}), 200

def get_download_stats():
    if os.path.exists(DOWNLOAD_LOG_FILE):
        df = pd.read_excel(DOWNLOAD_LOG_FILE, parse_dates=['Timestamp'])
        total_downloads = len(df)
        unique_students = df['Student ID'].nunique()
        recent_downloads = len(df[df['Timestamp'] > pd.Timestamp.now() - pd.Timedelta(days=7)])
        return {
            "total_downloads": total_downloads,
            "unique_students": unique_students,
            "recent_downloads": recent_downloads
        }
    else:
        return {
            "total_downloads": 0,
            "unique_students": 0,
            "recent_downloads": 0
        }

def get_log_file_path():
    return os.path.abspath(DOWNLOAD_LOG_FILE)

def get_generated_files_stats():
    stats = {
        'file_count': 0,
        'total_size': 0,
        'files': []
    }
    
    for filename in os.listdir(GENERATED_FILES_DIR):
        file_path = os.path.join(GENERATED_FILES_DIR, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            stats['file_count'] += 1
            stats['total_size'] += file_size
            stats['files'].append({
                'name': filename,
                'size': file_size
            })
    
    stats['total_size_formatted'] = format_size(stats['total_size'])
    for file in stats['files']:
        file['size_formatted'] = format_size(file['size'])
    
    return stats

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"