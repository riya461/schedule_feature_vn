
from flask import request, jsonify, render_template
from flask import Flask
from flask_cors import CORS
from event_extract import extract
import json

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        summary = request.form['text']
        print(summary)
        tasks = extract(summary)
        return render_template('index.html', results=tasks)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)



