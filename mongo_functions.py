import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGO_CONNECTION = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
DATABASE = MongoClient(MONGO_CONNECTION)[MONGO_DB]
MONGO_USER_COLLECTION = os.getenv("MONGO_USER_COLLECTION")

user_collection = DATABASE[MONGO_USER_COLLECTION]


def add_patient_identifier(identifier: str, email: str) ->None:
    """
    update Mongo document with the corresponding EPIC identifier

    returns: None
    """
    # e.g., Patient/eaqTUQq5pakG8s476u4uh4Q3
    identifier = identifier.split("/")[-1]
    email = email.lower()
    user_collection.update_one({"email": email}, {"$set": {"epic_identifier": identifier}}, upsert=False)