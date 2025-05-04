import os
from dotenv import load_dotenv

load_dotenv() 

CLIENT_ID       = os.getenv("CLIENT_ID")
CLIENT_SECRET   = os.getenv("CLIENT_SECRET")
REDIRECT_URI    = os.getenv("REDIRECT_URI")
QBO_SANDBOX_BASE= os.getenv("QBO_SANDBOX_BASE")
DB_PATH        = os.getenv("DB_PATH")