from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Ik how to do this part now</p>"