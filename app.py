from flask import Flask, redirect, request
import requests, os
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID", "YOUR_CLIENT_ID_HERE")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # this is where we'll keep your token
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

    # save token to .env file
    with open(".env", "r") as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for line in lines:
        if line.startswith("ACCESS_TOKEN="):
            new_lines.append(f"ACCESS_TOKEN={access_token}\n")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"ACCESS_TOKEN={access_token}\n")

    with open(".env", "w") as f:
        f.writelines(new_lines)

    return "Access token saved successfully!"

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

@app.route("/upload_gedcom", methods=["POST"])
def upload_gedcom():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    if not file.filename.endswith(".ged"):
        return {"error": "File must be a GEDCOM (.ged) file"}, 400

    # Save file locally
    filepath = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)

    return {"message": f"File {file.filename} uploaded successfully", "path": filepath}

@app.route("/")
def hello():
    return "OAuth-ready genealogy API is alive!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
