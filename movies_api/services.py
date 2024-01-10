from typing import Optional
from database import Database

def get_db() -> Optional[Database]:
    return Database()