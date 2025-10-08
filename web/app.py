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
status_col = routerdb["interface_status"]
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
    data = {
        "ip": ip,
        "username": username,
        "password": password,
        "command_type": "show",
    }
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
    recent_status = list(
        status_col.find({"router_ip": input_ip}).sort("timestamp", -1).limit(1)
    )
    template = "router_detail.html"
    return render_template(template, ip=input_ip, status=recent_status)


# Update config for router
@sample.route("/update_config/<input_ip>", methods=["POST"])
def update_config(input_ip):
    ip = input_ip

    # Collect interfaces from the form
    interfaces = {}
    for key, value in request.form.items():
        if key.startswith("interfaces"):
            parts = key.replace("interfaces[", "").replace("]", "").split("[")
            idx = parts[0]
            field = parts[1]
            if idx not in interfaces:
                interfaces[idx] = {}
            interfaces[idx][field] = value.strip()

    router = routercol.find_one({"ip": input_ip})
    router_status = list(
        status_col.find({"router_ip": input_ip}).sort("timestamp", -1).limit(1)
    )

    if not router:
        return redirect(f"/router/{ip}")

    # Retrieve original status data (so we can compare old vs new)
    latest_entry = router_status[0].get("data", {}) if router_status else {}
    old_status_data = latest_entry.get("show ip interface brief", [])

    for idx, iface in interfaces.items():
        new_raw_ip = iface.get("ip", "")
        new_status = iface.get("status", "").lower()

        # Convert CIDR to IP + mask
        ip_only = ""
        subnet_mask = ""
        if "/" in new_raw_ip:
            ip_part, prefix = new_raw_ip.split("/", 1)
            ip_only = ip_part.strip()
            prefix = int(prefix.strip())
            mask_bits = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
            subnet_mask = ".".join(
                [
                    str((mask_bits >> 24) & 0xFF),
                    str((mask_bits >> 16) & 0xFF),
                    str((mask_bits >> 8) & 0xFF),
                    str(mask_bits & 0xFF),
                ]
            )
        else:
            ip_only = new_raw_ip

        # Find the matching old data row
        old_data = next(
            (o for o in old_status_data if o.get("INTERFACE") == iface.get("name")),
            None,
        )

        if old_data:
            old_ip = old_data.get("IP_ADDRESS", "").strip()
            old_status = old_data.get("STATUS", "").strip().lower()
        else:
            old_ip = ""
            old_status = ""

        # ✅ Skip if nothing has changed
        if ip_only == old_ip and new_status == old_status:
            continue

        # ✅ Translate status
        if new_status == "up":
            cli_status = "no shutdown"
        elif new_status == "down":
            cli_status = "shutdown"
        elif new_status == "administratively":
            cli_status = "shutdown"
        else:
            cli_status = new_status

        config = {
            "ENABLE_PASS": router.get("enable_pass", ""),
            "INTERFACE_NAME": iface.get("name"),
            "NEW_IP_ADDRESS": ip_only,
            "SUBNET_MASK": subnet_mask,
            "STATUS": cli_status,
        }

        new_router = {
            "ip": router["ip"],
            "username": router["username"],
            "password": router["password"],
            "command_type": "config",
            "details": config,
        }

        routercol.insert_one(new_router)

    return redirect(f"/router/{ip}")


if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=8080, threaded=False)
