from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################

@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################

@app.route("/count")
def count():
    """Return the length of data"""
    if data is not None:
        return jsonify(length=len(data)), 200
    return jsonify(message="Internal server error"), 500

######################################################################
# GET ALL PICTURES
######################################################################

@app.route("/picture", methods=["GET"])
def get_pictures():
    # Return the list of pictures as JSON
    return jsonify(data)

######################################################################
# GET A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    # Search for the picture with the matching id in the data list
    for picture in data:
        if picture.get("id") == id:
            return jsonify(picture)
    # If not found, return a 404 error
    abort(404)

######################################################################
# CREATE A PICTURE
######################################################################

@app.route("/picture", methods=["POST"])
def create_picture():
    # Ensure the request contains JSON data
    if not request.json:
        abort(400, description="Request body must be JSON")
    
    new_picture = request.get_json()

    # Check if the picture already exists by id if provided.
    # If id is provided and already exists, return 302.
    if "id" in new_picture:
        existing = next((p for p in data if p.get("id") == new_picture["id"]), None)
        if existing is not None:
            return jsonify({"Message": f"picture with id {new_picture['id']} already present"}), 302
        new_id = new_picture["id"]
    else:
        # If no id provided, assign a new unique id
        new_id = max((item.get("id", 0) for item in data), default=0) + 1
        new_picture["id"] = new_id

    data.append(new_picture)
    response = jsonify(new_picture)
    response.status_code = 201
    response.headers["Location"] = url_for("get_picture_by_id", id=new_id)
    return response

######################################################################
# UPDATE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    # Ensure the request contains JSON data
    if not request.json:
        abort(400, description="Request body must be JSON")
    
    # Find the picture by id
    picture = next((p for p in data if p.get("id") == id), None)
    if picture is None:
        abort(404)
    
    update_data = request.get_json()
    # Update the picture fields except for the "id"
    for key, value in update_data.items():
        if key != "id":
            picture[key] = value
    
    return jsonify(picture), 200

######################################################################
# DELETE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    # Find the picture by id
    picture = next((p for p in data if p.get("id") == id), None)
    if picture is None:
        abort(404)
    data.remove(picture)
    # Return no content on successful deletion
    return "", 204