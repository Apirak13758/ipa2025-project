# ==================================================================

# File: db_handler.py
# Description: A module for saving data to MongoDB.

from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId

# --- การตั้งค่า MongoDB ---
MONGO_HOST = os.environ.get("MONGO_URI")
MONGO_DB = os.environ.get("DB_NAME")
MONGO_COLLECTION_SAVETO = "interface_status"
MONGO_COLLECTION_DELETEFROM = "routers"


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
        collection = db[MONGO_COLLECTION_SAVETO]

        data_with_timestamp = {
            "router_ip": ip,
            "timestamp": datetime.now(),
            "data": data,
        }

        result = collection.insert_one(data_with_timestamp)
        print(f"ข้อมูลถูกบันทึกใน MongoDB แล้ว: {result.inserted_id}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกข้อมูลใน MongoDB: {e}")


def delete_by_id(id_str):
    """
    Delete a document from the given MongoDB collection by its _id.

    Args:
        collection: The pymongo collection object.
        id_str: The string representation of the ObjectId.
    """
    try:
        client = MongoClient(MONGO_HOST)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION_DELETEFROM]

        result = collection.delete_one({"_id": ObjectId(id_str)})
        if result.deleted_count:
            print(f"Deleted document with _id: {id_str}")
        else:
            print(f"No document found with _id: {id_str}")
    except Exception as e:
        print(f"Error deleting document: {e}")

def main():
    # ตัวอย่างการใช้งาน
    delete_by_id("68dba0830b245b3d4537567e")
