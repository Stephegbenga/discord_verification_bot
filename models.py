from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os

DB_URL=os.environ.get('db_url')

conn = MongoClient(DB_URL)
db = conn.get_database("Main")

Verification_codes = db.get_collection("verification_codes")
Settings = db.get_collection("setting")