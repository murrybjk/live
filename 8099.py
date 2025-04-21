from flask import Flask, request, render_template_string, redirect, url_for
import os
 
# Initialize the Flask application
app = Flask(__name__)
 
# Sets the starting directory to the current directory where the script is run
base_dir = os.getcwd()
 
@app.route('/')
@app.route('/browse/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def index(subpath=""):
    # Normalize the subpath to avoid double slashes
    current_path = os.path.join(base_dir, subpath)
    if not os.path.exists(current_path):
        return "Directory not found", 404
 
    files = os.listdir(current_path)
    file_info = []
 
    for file in files:
        full_path = os.path.join(current_path, file)
        file_info.append({
            "name": file,
            "is_dir": os.path.isdir(full_path),
            "path": os.path.join(subpath, file) if subpath else file
        })
 
    return render_template_string('''
        <h2>File Browser</h2>
        <ul>
            {% if subpath %}
                <li><a href="{{ url_for('index', subpath=subpath.rsplit('/', 1)[0]) }}">.. (Up one level)</a></li>
            {% endif %}
            {% for file in file_info %}
                <li>
                    {% if file.is_dir %}
                        <a href="{{ url_for('index', subpath=file.path) }}">{{ file.name }}</a>
                    {% else %}
                        <a href="{{ url_for('view_file', subpath=subpath if subpath else '', filename=file.name) }}">{{ file.name }}</a>
                    {% endif %}
                </li>
            {% endfor %}
        </ul>
        <a href="{{ url_for('create_file', subpath=subpath) }}">Create New File</a><br>
        <a href="{{ url_for('create_directory', subpath=subpath) }}">Create New Directory</a>
    ''', file_info=file_info, subpath=subpath)
 
@app.route('/view/', defaults={'subpath': '', 'filename': ''})
@app.route('/view/<path:subpath>/<filename>', methods=['GET', 'POST'])
@app.route('/view/<filename>', methods=['GET', 'POST'])
def view_file(subpath='', filename=''):
    # Normalize subpath to avoid leading slashes
    if not filename:
        return "File not specified", 400
 
    # Construct the file path properly
    filepath = os.path.join(base_dir, subpath.strip("/"), filename)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}", 404
 
    if request.method == 'POST':
        # Save the updated content
        content = request.form['content'].replace('\r\n', '\n')
        with open(filepath, 'w', newline='') as f:
            f.write(content)
        return redirect(url_for('index', subpath=subpath))
 
    # Read the file content
    with open(filepath, 'r') as f:
        content = f.read()
    return render_template_string('''
        <h2>Editing {{ filename }}</h2>
        <form method="post">
            <textarea name="content" rows="20" cols="80">{{ content }}</textarea><br>
            <input type="submit" value="Save">
        </form>
        <a href="{{ url_for('index', subpath=subpath) }}">Back to file list</a>
    ''', filename=filename, content=content, subpath=subpath)
 
@app.route('/create/', methods=['GET', 'POST'], defaults={'subpath': ''})
@app.route('/create/<path:subpath>', methods=['GET', 'POST'])
def create_file(subpath):
    # Normalize subpath (handles root directory and subdirectories)
    subpath = subpath.strip("/")
    if request.method == 'POST':
        # Create a new file
        filename = request.form['filename']
        if not filename:
            return "Filename cannot be empty", 400
 
        filepath = os.path.join(base_dir, subpath, filename)
        try:
            content = request.form['content'].replace('\r\n', '\n')
            with open(filepath, 'w', newline='') as f:
                f.write(content)
            return redirect(url_for('index', subpath=subpath))
        except Exception as e:
            return f"Error creating file: {str(e)}", 500
 
    return render_template_string('''
        <h2>Create New File</h2>
        <form method="post">
            Filename: <input type="text" name="filename"><br>
            <textarea name="content" rows="10" cols="50"></textarea><br>
            <input type="submit" value="Create">
        </form>
        <a href="{{ url_for('index', subpath=subpath) }}">Back to file list</a>
    ''', subpath=subpath)
 
@app.route('/create_directory/', methods=['GET', 'POST'], defaults={'subpath': ''})
@app.route('/create_directory/<path:subpath>', methods=['GET', 'POST'])
def create_directory(subpath):
    # Normalize subpath (handles root directory and subdirectories)
    subpath = subpath.strip("/")
    if request.method == 'POST':
        # Create a new directory
        dirname = request.form['dirname']
        if not dirname:
            return "Directory name cannot be empty", 400
 
        directory_path = os.path.join(base_dir, subpath, dirname)
        try:
            os.makedirs(directory_path, exist_ok=True)  # Create directory if it doesn't exist
            return redirect(url_for('index', subpath=subpath))
        except Exception as e:
            return f"Error creating directory: {str(e)}", 500
 
    return render_template_string('''
        <h2>Create New Directory</h2>
        <form method="post">
            Directory Name: <input type="text" name="dirname"><br>
            <input type="submit" value="Create Directory">
        </form>
        <a href="{{ url_for('index', subpath=subpath) }}">Back to file list</a>
    ''', subpath=subpath)
 
if __name__ == '__main__':
    # Run the Flask app on all network interfaces, making it accessible on other devices
    app.run(host='0.0.0.0', port=8099, debug=True)

