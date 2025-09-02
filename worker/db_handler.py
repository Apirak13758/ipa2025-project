# ==================================================================

# File: db_handler.py
# Description: A module for saving data to MongoDB.

from pymongo import MongoClient
from datetime import datetime
import os

# --- การตั้งค่า MongoDB ---
MONGO_HOST = os.environ.get("MONGO_URI")
MONGO_DB = os.environ.get("DB_NAME")
MONGO_COLLECTION = "interface_status"


def save_to_mongo(data, ip):
    """
    Saves the parsed data to a MongoDB collection with a timestamp.

    Arguments:
        data (list): A list of dictionaries 
        containing the parsed interface data.
    """
    try:
        client = MongoClient(MONGO_HOST)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        data_with_timestamp = {
            "router_ip": ip,
            "timestamp": datetime.now(),
            "interfaces": data,
        }

        result = collection.insert_one(data_with_timestamp)
        print(f"✅ ข้อมูลถูกบันทึกใน MongoDB แล้ว: {result.inserted_id}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึกข้อมูลใน MongoDB: {e}")
