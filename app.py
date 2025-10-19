from flask import Flask, request
import requests

app = Flask(__name__)

@app.route("/")
def hello():
    return "It works. Your genealogy API is alive!"

@app.route("/tree", methods=["GET"])
def get_tree():
    person = request.args.get("person", "John Doe")
    return {"requested_person": person, "records": []}
