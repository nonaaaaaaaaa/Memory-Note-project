from __init__ import *


# ----------------------------------------------------------------
# Api users, Memories
# ----------------------------------------------------------------

users_bp = Blueprint('user', __name__)
memories_bp = Blueprint('memory', __name__)


@users_bp.route('/users', methods=['GET'])
@users_bp.route('/users/', methods=['GET'])
@users_bp.route('/users/<int:user_id>', methods=['GET'])
@users_bp.route('/users/<int:user_id>/', methods=['GET'])
def get_users(user_id=None):
    """get all users data"""
    if user_id != None:
        user = users_module.get_user_by_id(user_id)
        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404
    return jsonify(users_module.load_user_data())


@users_bp.route('/current-user', methods=['GET'])
@users_bp.route('/current-user/', methods=['GET'])
@users_bp.route('/profile', methods=['GET', 'PUT'])
@users_bp.route('/profile/', methods=['GET', 'PUT'])
def get_profile():
    if request.method == 'GET':
        return jsonify(users_module.current_user), 200
    elif request.method == 'PUT':
        data = request.get_json()
        fields = ["fullname", "username", "email", "image"]
        for field in fields:
            if data.get(field) is not None and data[field] != "":
                users_module.current_user[field] = data[field]
        password = data.get("password")
        if password:
            users_module.current_user["password"] = users_module.hash_password(password)
            users_module.current_user["confirmemail"] = password
        current_user = users_module.update_user()
        return jsonify(current_user), 200


@users_bp.route('/users/like/<int:memory_id>', methods=['POST'])
def add_or_minus_like(memory_id):
    """Add or minus like"""
    try:
        if memory_id in users_module.current_user['memories']['liked']:
            message = memories_module.add_or_minus_like_function(memory_id, 'F')
        else:
            message = memories_module.add_or_minus_like_function(memory_id, 'T')
        users_module.add_memory_id_to_user_data(memory_id, 'liked')
        return jsonify({'message': message})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@memories_bp.route('/memories', methods=['GET'])
@memories_bp.route('/memories/', methods=['GET'])
@memories_bp.route('/memories/<int:memory_id>', methods=['GET'])
@memories_bp.route('/memories/<int:memory_id>/', methods=['GET'])
def get_memories(memory_id=None):
    """get all memories data"""
    if memory_id != None:
        memory = memories_module.get_memories_by_id(memory_id)
        if memory:
            return jsonify(memory)
        else:
            return jsonify({"error": "memory not found"}), 404
    return jsonify(memories_module.load_memories_data())


@memories_bp.route('/get-memories', methods=['GET'])
def get_user_memories():
    """Get memories"""
    memories = memories_module.get_all_memories(users_module.current_user['id'])
    memories_sorted = sorted(
        memories,
        key=lambda x: datetime.strptime(x['timestamp'], '%a %b %d %H:%M:%S %Y'),
        reverse=True
    )
    return jsonify(memories_sorted)

# ----------------------------------------------------------------
# Image Routes
# ----------------------------------------------------------------

app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/upload-images', methods=['POST'])
def upload_images():
    if 'images' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('images')
    image_paths = []

    for file in files:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        image_url = os.path.join('/static/uploads/', filename)
        image_paths.append(image_url)

    return jsonify({'imagePaths': image_paths})


# ----------------------------------------------------------------
# Main Routes
# ----------------------------------------------------------------


@app.route('/', methods=['GET', 'POST', 'DELETE'])
@app.route('/home/', methods=['GET', 'POST', 'DELETE'])
@load_user
def home_page():
    """Home"""
    if is_authentication() is False:
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('home.html', image=users_module.current_user['image'])
    elif request.method == 'POST':
        data = request.get_json()
        new_memory_data = {
            "id": len(memories_module.memories) + 1,
            "user_id": users_module.current_user['id'],
            "title": data['title'] if data['title'] else datetime.now().strftime("%a %H:%M:%S %d:%m:%Y"),
            "timestamp": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
            "image": data['image'],
            "description": data['content'],
            "share": data['share'],
            "type": data['status'],
            "calendar": data['calendar'],
            "likes": 0,
            "likelist": [],
            "file": [],
            "comments": [
                {
                    "comment_id": "",
                    "user_id": 0,
                    "comment": "",
                    "timestamp": ""
                }
            ]
        }
        users_module.add_memory_id_to_user_data(
            new_memory_data['id'], new_memory_data['type'].lower()
        )
        memories_module.save_memories_data(new_memory_data)
        return jsonify({'message': 'True'})
    elif request.method == 'DELETE':
        return jsonify({'message': 'Home Page - DELETE'})
    else:
        return jsonify({'error': 'Method not allowed'}), 405


@app.route('/search', methods=['GET'])
@load_user
def search_page():
    """Home"""
    if request.method == 'GET':
        query = request.args.get('query')
        if query:
            memories = memories_module.search_memories_data(query)
            users = users_module.search_about_users(query)
            return render_template('search.html', memories=memories, users=users)
        return render_template('search.html')
    else:
        return jsonify({'error': 'Method not allowed'}), 405


@app.route('/login/', methods=['GET', 'POST'])
@load_user
def login():
    """login page"""
    if is_authentication():
        return redirect(url_for('home_page'))
    if request.method == 'GET':
        return render_template('login.html')
    try:
        data = request.get_json()
        user_data = users_module.check_user_if_exists(data['username'], data['password'])
        if user_data:
            users_module.current_user = user_data
            session['session_id'] = user_data['session_id']
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'message': 'email not found'}), 401
    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/register/', methods=['GET', 'POST'])
@load_user
def register():
    """register"""
    if is_authentication():
        return redirect(url_for('home_page'))
    if request.method == 'GET':
        return render_template('register.html')
    try:
        data = request.get_json()
        new_user_data = {
            "id": len(users_module.load_user_data()) + 1,
            "fullname": data['fullname'],
            "username": data['username'],
            "email": data['email'],
            "dob": data['dob'],
            "timecreated": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
            "password": users_module.hash_password(data['password']),
            "confirmpass": data['confirmpass'],
            "description": "",
            "session_id": str(uuid4()),
            "image": "",
            "following": [],
            "followingcount": [],
            "followers": [],
            "followerscount": [],
            "memories": {
                "public": [],
                "liked": [],
                "draft": [],
                "private": []
            },
            "my_comments": []
        }
        users_module.save_user_data(new_user_data)
        users_module.current_user = new_user_data
        session['session_id'] = new_user_data['session_id']
        return jsonify({'message': 'Register successful'})
    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/logout')
@load_user
def  logout():
    """logout"""
    users_module.current_user = {}
    session.clear()
    return redirect(url_for('login'))


# @app.errorhandler(Exception)
# def error(e):
#     """error handler"""
#     error_code = 500
#     error_message = "Internal Server Error"
#     if hasattr(e, 'code'):
#         error_code = e.code
#         error_message = e.name
#     return render_template('error.html', error_code=error_code, error_message=error_message), error_code


# Register blueprints after defining all routes
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(memories_bp, url_prefix='/api')


if __name__ == "__main__":
    # print(name(name='ali'))
    # print(dir())
    # print(__name__)
    # session['session_id'] = '0000'
    app.run(host="127.0.0.1", port=5000, debug=True)
    # print(datetime.now())
    # print(datetime.now().strftime("%H:%M:%S %a %d:%m:%Y"))
    # for i in dir():
    # for i in locals():
    # for i in globals():
    # for i in vars(object):
        # print(i)