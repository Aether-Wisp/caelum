import os

target_file = r'd:\1-compitition\waibao\caelum\src\caelum\server.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

import_pattern = "from flask import Flask, request, jsonify, render_template"
if "send_from_directory" not in content and "from flask import" in content:
    content = content.replace("from flask import Flask", "from flask import Flask, send_from_directory")

old_route = """@app.route('/', methods=['GET'])
def index():
    \"\"\"提供前端界面\"\"\"
    return app.send_static_file('index.html')"""

new_route = """import os

# Serve the main HTML file from the /HTML directory
@app.route('/', methods=['GET'])
def index():
    \"\"\"提供前端界面\"\"\"
    return send_from_directory('../../HTML', '01-caelum.html')

# Serve other HTML slice files (e.g. /HTML/01-test-tasks-content.html)
@app.route('/HTML/<path:filename>', methods=['GET'])
def serve_html(filename):
    return send_from_directory('../../HTML', filename)

# Keep the static path if needed, or point /src to be sure
@app.route('/src/caelum/static/<path:filename>', methods=['GET'])
def serve_caelum_static(filename):
    return send_from_directory('static', filename)"""

# Handle encoding differences exactly
if "@app.route('/', methods=['GET'])" in content and "index.html" in content:
    # Use split and join since characters might not map cleanly in terminal output
    lines = content.split('\n')
    new_lines = []
    skip = False
    replaced = False
    for line in lines:
        if "@app.route('/', methods=['GET'])" in line and not replaced:
            new_lines.extend(new_route.split('\n'))
            skip = True
            replaced = True
            continue
        if skip:
            if "def index" in line:
                continue
            if "index.html" in line:
                skip = False
                continue
        else:
            new_lines.append(line)
            
    if replaced:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print("Successfully updated routes in server.py!")
    else:
        print("Failed to find exact block.")
else:
    print("Could not locate route block in content.")
