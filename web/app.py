# Add to this file for the sample app lab
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from pymongo import MongoClient
from bson import ObjectId
import os

sample = Flask(__name__)

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("DB_NAME")
client = MongoClient(mongo_uri)
routerdb = client[db_name]
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
        routercol.insert_one(
            {"ip": ip, "username": username, "password": password}
        )
    return redirect("/")


@sample.route("/delete", methods=["POST"])
def delete_comment():
    try:
        idx = request.form.get("idx")
        myquery = {"_id": ObjectId(idx)}
        routercol.delete_one(myquery)
    except Exception:
        pass
    return redirect("/")


@sample.route("/router/<input_ip>")
def router_detail(input_ip):
    # ดึง 3 รายการล่าสุดของ interface status สำหรับ router ที่เลือก
    status_col = routerdb["interface_status"]
    # INTERVAL 60 วินาที: สมมติว่ามี field 'timestamp' เป็น datetime
    recent_status = list(
        status_col.find({"router_ip": input_ip}).sort("timestamp", -1).limit(3)
    )
    # print(recent_status)
    return render_template(
        "router_detail.html", ip=input_ip, status=recent_status
    )


if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=8080, threaded=False)
