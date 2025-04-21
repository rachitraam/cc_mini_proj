from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import redis
import validators
import shortuuid
import os
import logging

app = Flask(__name__)
CORS(app)

# Log all errors
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
    return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Configure Redis
redis_host = os.getenv('REDIS_HOST', 'redis')  # Use the service name as default
redis_password = os.getenv('REDIS_PASSWORD', None)
redis_client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True, password=redis_password)

base_url = os.getenv('BASE_URL', 'http://localhost')

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        long_url = data['url']
        # Validate URL
        if not validators.url(long_url):
            return jsonify({'error': 'Invalid URL'}), 400
        # Generate short URL
        short_id = shortuuid.uuid()[:8]
        # Store in Redis
        redis_client.set(short_id, long_url)
        print("\n\n\n\nshort_id:", short_id)
        # Create short URL
        short_url = f"{base_url}/api/{short_id}"
        return jsonify({
            'short_url': short_url,
            'long_url': long_url
        }), 201
    except Exception as e:
        app.logger.error(f"Error in shorten_url: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@app.route('/api/retrieve/<short_id>')
def get_url(short_id):
    try:
        long_url = redis_client.get(short_id)
        if long_url is None:
            return jsonify({'error': 'URL not found'}), 404

        return jsonify({
            'long_url': long_url
        }), 200
    except Exception as e:
        app.logger.error(f"Error in get_url: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/<short_id>')
def redirect_to_url(short_id):
    try:
        long_url = redis_client.get(short_id)
        if long_url is None:
            return jsonify({'error': 'URL not found'}), 404
        
        # Just return the long URL as JSON instead of trying to redirect

        return redirect(long_url)
        return jsonify({
            'long_url': long_url
        }), 200
    except Exception as e:
        app.logger.error(f"Error in redirect_to_url: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500






@app.route('/health')
def health_check():
    try:
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        app.logger.error(f"Error in health_check: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 