import os

from pymongo import MongoClient
mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("DB_NAME")


def get_router_info():
#print(mongo_uri, db_name)
    client = MongoClient(mongo_uri)
    routerdb = client[db_name]
    routers = routerdb["routers"]

    router_data = routers.find()
    for data in router_data:
        print(data)
    return router_data


if __name__ == '__main__':
    get_router_info()