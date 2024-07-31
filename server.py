from flask import Flask, request, jsonify
import lexical
import sintacticals
import pprint
import os

app = Flask(__name__)

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def compile_code(file_path):
    input_text = read_file(file_path)
    ret = sintacticals.sintactical(input_text)
    return ret

@app.route('/compile', methods=['POST'])
def compile_endpoint():
    #print("Headers:", request.headers)
    #print("Form data:", request.form)
    #print("Files:", request.files)
    
    if 'file' not in request.files:
        print("No file part in the request")
        return jsonify({'error': 'No file provided'}), 500
    
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return jsonify({'error': 'No selected file'}), 500
    
    file_path = os.path.join('/tmp', file.filename)
    file.save(file_path)
    
    result = compile_code(file_path)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
