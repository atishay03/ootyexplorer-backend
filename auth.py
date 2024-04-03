import csv
from pydantic import BaseModel
import os

# Pydantic model for user data
class User(BaseModel):
    email: str
    password: str

# Path to the CSV file where user credentials are stored
users_file = 'users.csv'

def user_exists(email: str) -> bool:
    with open(users_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        return any(row[0] == email for row in reader)

def register_user(email: str, password: str):
    with open(users_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email, password])

def authenticate_user(email: str, password: str) -> bool:
    with open(users_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        return any(row[0] == email and row[1] == password for row in reader)

# Ensure the users file exists
if not os.path.exists(users_file):
    open(users_file, 'w').close()
