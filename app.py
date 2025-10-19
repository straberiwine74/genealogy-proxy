from flask import Flask, redirect, request
import requests, os
from urllib.parse import urlencode

app = Flask(__name__)

# Replace with your real FamilySearch client ID once approved
CLIENT_ID = "YOUR_CLIENT_ID_HERE"
REDIRECT_URI = "https://genealogy-proxy.onrender.com/callback"
BASE_AUTH_URL = "https://ident.familysearch.org/cis-web/oauth2/v3/authorization"
TOKEN_URL = "https://ident.familysearch.org/cis-web/oauth2/v3/token"
API_BASE = "https://api.familysearch.org"

# Step 1: send user to FamilySearch login
@app.route("/authorize")
def authorize():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "profile tree",
    }
    return redirect(f"{BASE_AUTH_URL}?{urlencode(params)}")

# Step 2: handle callback and exchange code for token
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }

    response = requests.post(TOKEN_URL, data=data)
    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return f"Error: {token_data}", 400

    return f"Access token acquired successfully: {access_token[:20]}..."

# Step 3: fetch user’s family tree (once you have token)
@app.route("/tree", methods=["GET"])
def get_tree():
    token = request.args.get("token")
    person = request.args.get("person", "me")

    if not token:
        return {"error": "Missing access token"}, 400

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    url = f"{API_BASE}/platform/tree/persons/{person}"

    response = requests.get(url, headers=headers)
    return response.json()

@app.route("/")
def hello():
    return "OAuth-ready genealogy API is alive!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
