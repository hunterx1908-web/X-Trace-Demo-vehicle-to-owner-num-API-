import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 🔑 Teri API Key
VALID_KEY = "DEMO"

# 🔥 Original API details — Environment Variable se lo (code mein mat dikha)
ORIGINAL_API_URL = os.environ.get('ORIGINAL_API_URL', 'http://uersxinfo.in/api')
ORIGINAL_KEY = os.environ.get('ORIGINAL_KEY', 'newd64')

# 🔥 API Expiry Date (19 September 2026)
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
        response = requests.get(ORIGINAL_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict):
            # Remove unwanted fields
            data.pop('developer', None)
            data.pop('key_details', None)
            data.pop('status_code', None)
            data.pop('http_status', None)
            
            if 'data' in data and isinstance(data['data'], dict):
                data['data'].pop('response_time_seconds', None)
                data['data'].pop('limitsInfo', None)
                data['data'].pop('success', None)
                data['data'].pop('cached', None)
                data['data'].pop('response_time', None)
            
            if not data.get('mobileNumber') or data.get('mobileNumber') == "":
                return jsonify({"status": False, "message": "No data found", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 404
            
            # 🔥 Clean response
            response_data = {
                "status": "success",
                "vehicleNumber": data.get('vehicleNumber', term),
                "mobileNumber": data.get('mobileNumber', ''),
                "mobileDetected": data.get('mobileDetected', True),
                "data": {
                    "data": {
                        "vehicle_number": data.get('vehicleNumber', term),
                        "mobile_number": data.get('mobileNumber', '')
                    }
                },
                "success": True,
                "developer": "@x_TRACEOWNER",
                "credit": "@x_TRACEOWNER",
                "api_expires_on": API_EXPIRY
            }
            
            return jsonify(response_data)
        
        return jsonify({"status": False, "message": "No data found", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 404
        
    except requests.exceptions.Timeout:
        return jsonify({"status": False, "message": "Request timeout. Please try again later.", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 504
        
    except requests.exceptions.ConnectionError:
        return jsonify({"status": False, "message": "No data found", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 404
        
    except requests.exceptions.RequestException:
        return jsonify({"status": False, "message": "No data found", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 404
        
    except Exception:
        return jsonify({"status": False, "message": "No data found", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 404

@app.route('/api/<path:path>')
def catch_all(path):
    return jsonify({"status": False, "message": "No data found", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": False, "message": "No data found", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": False, "message": "No data found", "developer": "@x_TRACEOWNER", "credit": "@x_TRACEOWNER"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))