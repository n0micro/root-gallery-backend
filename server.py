from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()
PORT = int(os.getenv('SERVER_PORT', 3000))  # Використовуємо порт 3000

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Дозволяє запити з інших джерел (якщо потрібно)

UPLOAD_FOLDER = 'static/images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Завантаження або ініціалізація robots.json
ROBOTS_FILE = 'robots.json'
if not os.path.exists(ROBOTS_FILE):
    with open(ROBOTS_FILE, 'w') as f:
        json.dump([], f, indent=2)

@app.route('/add_robot', methods=['POST'])
def add_robot():
    author = request.form.get('author')
    name = request.form.get('name')
    description = request.form.get('description')
    images = request.files.getlist('images')

    if not name or not description or not images or not author:
        return jsonify({'error': 'Missing fields'}), 400

    image_paths = []
    for image in images:
        if image and image.mimetype.startswith('image/'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filename)
            image_paths.append(f'/static/images/{image.filename}')
        else:
            return jsonify({'error': 'Invalid file format'}), 400

    with open(ROBOTS_FILE, 'r+') as f:
        robots = json.load(f)
        robots.append({'author': author, 'name': name, 'images': image_paths, 'description': description})
        f.seek(0)
        json.dump(robots, f, indent=2)
        f.truncate()

    return jsonify({'message': 'Робота додано', 'robots': robots}), 200

@app.route('/update_robot/<int:index>', methods=['PUT'])
def update_robot(index):
    data = request.form
    new_name = data.get('name')
    new_description = data.get('description')
    new_author = data.get('author')
    images = request.files.getlist('images')

    with open(ROBOTS_FILE, 'r+') as f:
        robots = json.load(f)
        if index < 0 or index >= len(robots):
            return jsonify({'error': 'Invalid index'}), 404

        robot = robots[index]
        if new_name:
            robot['name'] = new_name
        if new_description:
            robot['description'] = new_description
        if new_author:
            robot['author'] = new_author
        if images:
            image_paths = robot.get('images', [])
            for image in images:
                if image and image.mimetype.startswith('image/'):
                    filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                    image.save(filename)
                    image_paths.append(f'/static/images/{image.filename}')
            robot['images'] = image_paths

        robots[index] = robot
        f.seek(0)
        json.dump(robots, f, indent=2)
        f.truncate()

    return jsonify({'message': 'Робота оновлено', 'robots': robots}), 200

@app.route('/delete_robot/<int:index>', methods=['DELETE'])
def delete_robot(index):
    with open(ROBOTS_FILE, 'r+') as f:
        robots = json.load(f)
        if index < 0 or index >= len(robots):
            return jsonify({'error': 'Invalid index'}), 404

        robots.pop(index)
        f.seek(0)
        json.dump(robots, f, indent=2)
        f.truncate()

    return jsonify({'message': 'Робота видалено', 'robots': robots}), 200

@app.route('/robots', methods=['GET'])
def get_robots():
    with open(ROBOTS_FILE, 'r') as f:
        robots = json.load(f)
    return jsonify(robots)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path == '' and os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

port = int(os.getenv("PORT", 3000))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)