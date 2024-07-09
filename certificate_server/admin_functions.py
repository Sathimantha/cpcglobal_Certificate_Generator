import os
import pandas as pd
import joblib
import logging
from flask import jsonify

CACHE_FILE = 'data_cache.joblib'
EXCEL_FILE = 'file.xlsx'
CACHE_CONFIG_FILE = 'cache_config.joblib'
DOWNLOAD_LOG_FILE = 'certificate_downloads.xlsx'

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