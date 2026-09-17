import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 🔑 Teri API Key
VALID_KEY = "DEMO"

# Original API details
ORIGINAL_API_URL = "http://uersxinfo.in/api"
ORIGINAL_KEY = "newd64"

# 🔥 API Expiry Date (31 December 2026)
API_EXPIRY = "2026-09-19"

def is_expired():
    try:
        expiry = datetime.strptime(API_EXPIRY, "%Y-%m-%d")
        return datetime.utcnow() > expiry
    except:
        return False

@app.route('/')
def home():
    return jsonify({
        "status": True,
        "message": "Vehicle to Owner API is working! (X-TRACE Edition)",
        "developer": "@x_TRACEOWNER",
        "credit": "@x_TRACEOWNER",
        "expires_on": API_EXPIRY,
        "status": "Active" if not is_expired() else "Expired",
        "endpoints": {
            "info": "/api?key=YOUR_KEY&type=veh_numm&term=VEHICLE_NUMBER"
        },
        "example": "/api?key=DEMO&type=veh_numm&term=UP16EY3536"
    })

@app.route('/api')
def vehicle_info():
    if is_expired():
        return jsonify({
            "status": False,
            "error": f"API expired on {API_EXPIRY}!",
            "developer": "@x_TRACEOWNER",
            "credit": "@x_TRACEOWNER",
            "expires_on": API_EXPIRY
        }), 401
    
    key = request.args.get('key')
    term = request.args.get('term')
    query_type = request.args.get('type', 'veh_numm')
    
    if not key:
        return jsonify({"status": False, "error": "Missing API Key!", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 400
        
    if key != VALID_KEY:
        return jsonify({"status": False, "error": "Invalid API Key!", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 401
    
    if not term:
        return jsonify({"status": False, "error": "Missing 'term' parameter!", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 400
    
    term = term.strip().upper()
    
    params = {
        'key': ORIGINAL_KEY,
        'type': query_type,
        'term': term
    }
    
    try:
        response = requests.get(ORIGINAL_API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict):
            # 🔥 Check if data exists
            mobile_number = None
            vehicle_number = None
            
            if 'data' in data and isinstance(data['data'], dict):
                if 'data' in data['data'] and isinstance(data['data']['data'], dict):
                    mobile_number = data['data']['data'].get('mobile_number')
                    vehicle_number = data['data']['data'].get('vehicle_number')
                elif 'mobileNumber' in data:
                    mobile_number = data.get('mobileNumber')
                    vehicle_number = data.get('vehicleNumber')
            
            if not mobile_number or mobile_number == "":
                return jsonify({
                    "status": False,
                    "message": "No data found",
                    "developer": "@x_TRACEOWNER",
                    "credit": "@x_TRACEOWNER"
                }), 404
            
            # 🔥 Exact format — jaise tune dikhaya
            response_data = {
                "credit": "@x_TRACEOWNER",
                "data": {
                    "data": {
                        "mobile_number": mobile_number,
                        "vehicle_number": vehicle_number or term
                    }
                },
                "developer": "@x_TRACEOWNER",
                "mobileDetected": True,
                "mobileNumber": mobile_number,
                "status": "success",
                "success": True,
                "vehicleNumber": vehicle_number or term,
                "api_expires_on": API_EXPIRY
            }
            
            return jsonify(response_data)
        
        return jsonify({
            "status": False,
            "message": "No data found",
            "developer": "@x_TRACEOWNER",
            "credit": "@x_TRACEOWNER"
        }), 404
        
    except Exception as e:
        return jsonify({
            "status": False,
            "message": "No data found",
            "developer": "@x_TRACEOWNER",
            "credit": "@x_TRACEOWNER"
        }), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": False,
        "message": "No data found",
        "developer": "@x_TRACEOWNER",
        "credit": "@x_TRACEOWNER"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": False,
        "message": "No data found",
        "developer": "@x_TRACEOWNER",
        "credit": "@x_TRACEOWNER"
    }), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))