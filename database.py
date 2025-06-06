from pymongo import MongoClient
from pymongo.database import Database
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.cursor import Cursor

from datetime import datetime

from typing import Dict

URI: str = ""

with open("mongodbURI.txt", "r") as f:
    URI = f.read()
    
class DatabaseManager:
    """
    Structure:
        - wedding id
            - fname
            - lname
            - phone num
            - email
            - wedding date
    """

    def __init__(self) -> None:
        self.db_client = MongoClient(URI, server_api=ServerApi('1'))
        self.db = self.db_client["plaching"]
        self.weddings = self.db["weddings"]

    def get_wedding(self, phone: int) -> Dict | None:
        return self.weddings.find_one({"phone": phone}) 

    def add_wedding(self, fname: str, lname: str, phone: int, email: str, date: datetime) -> None:
        post = {
            "fname": fname,
            "lname": lname,
            "phone": phone,
            "email": email,
            "date": date
        }

        self.weddings.insert_one(post)