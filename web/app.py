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
    return render_template("index.html")


@sample.route("/routers")
def routers():
    data = [x for x in routercol.find()]
    return render_template("routers.html", routers=data)


@sample.route("/add", methods=["POST"])
def add_router():
    ip = request.form.get("ip")
    username = request.form.get("username")
    password = request.form.get("password")
    data = {"ip": ip, "username": username, "password": password, "command_type": "show"}
    if ip and username and password:
        routercol.insert_one(data)
    return redirect("/routers")


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
    status_col = routerdb["interface_status"]
    recent_status = list(
        status_col.find({"router_ip": input_ip}).sort("timestamp", -1).limit(1)
    )
    template = "router_detail.html"
    return render_template(template, ip=input_ip, status=recent_status)

# Update config for router
@sample.route("/update_config/<input_ip>", methods=["POST"])
def update_config(input_ip):
    interface_name = request.form.get("interface_name")
    new_ip_address = request.form.get("new_ip_address")
    subnet_mask = request.form.get("subnet_mask")
    ip = request.form.get("ip")
    # Find router document
    router = routercol.find_one({"ip": ip})
    if router:
        # Build config update
        config = {
            "ENABLE_PASS": router.get("enable_pass", ""),
            "INTERFACE_NAME": interface_name,
            "NEW_IP_ADDRESS": new_ip_address,
            "SUBNET_MASK": subnet_mask
        }
        routercol.update_one(
            {"_id": router["_id"]},
            {"$set": {"command_type": "config", "details": config}}
        )
    return redirect(f"/router/{ip}")


if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=8080, threaded=False)
