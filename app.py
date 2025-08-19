# Add to this file for the sample app lab
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from pymongo import MongoClient
from bson import ObjectId
sample = Flask(__name__)
client = MongoClient("mongodb://mongo:27017/")
routerdb = client["routers"]
routercol = routerdb["routers"]
data = []
@sample.route("/")
def main():
    data = [x for x in routercol.find()]
    return render_template("index.html", data=data)

@sample.route("/add", methods=["POST"])
def add_router():
    ip = request.form.get("ip")
    username = request.form.get("username")
    password = request.form.get("password")

    if ip and username and password:
        routercol.insert_one({ "ip": ip, "username": username , "password": password})
    return redirect("/")

@sample.route("/delete", methods=["POST"])
def delete_comment():
    try:
        idx = request.form.get("idx")
        myquery = {'_id': ObjectId(idx)}
        routercol.delete_one(myquery)
    except Exception:
        pass
    return redirect("/")

if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=8080, threaded=False)