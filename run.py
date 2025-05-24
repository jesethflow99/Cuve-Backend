from app import create_app
from dotenv import load_dotenv
load_dotenv()
from flask import jsonify
from init_db import create_superuser
from flask_migrate import upgrade

app = create_app()

#endpoint test
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Test endpoint"}), 200


if __name__ == '__main__':
    with app.app_context():
        upgrade() 
        create_superuser()
    app.run(host='0.0.0.0', port=5000, debug=True)