from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from datetime import datetime

app = FastAPI()

# Enable frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# File to store student data
FILE_NAME = "students.json"

# Load existing data or start fresh
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as f:
        students = json.load(f)
else:
    students = []

@app.get("/")
def home():
    return {"message": "Welcome to the Principal-Student App 🚀"}

@app.post("/register")
def register(name: str = Form(...), roll: str = Form(...)):
    for student in students:
        if student["roll"] == roll:
            return {"error": f"Student with roll number {roll} already exists."}

    student = {
        "name": name,
        "roll": roll,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    students.append(student)

    with open(FILE_NAME, "w") as f:
        json.dump(students, f, indent=4)

    return {"message": f"{name} registered successfully!", "total": len(students)}

@app.get("/students")
def get_students():
    return students

@app.delete("/delete/{roll}")
def delete_student(roll: str):
    global students
    original_count = len(students)
    students = [s for s in students if s["roll"] != roll]

    if len(students) < original_count:
        with open(FILE_NAME, "w") as f:
            json.dump(students, f, indent=4)
        return {"message": f"Student with roll number {roll} deleted successfully."}
    else:
        return {"error": f"No student found with roll number {roll}."}

@app.put("/update")
def update_student(
    old_roll: str = Form(...),
    new_name: str = Form(...),
    new_roll: str = Form(...)
):
    found = False
    for student in students:
        if student["roll"] == old_roll:
            student["name"] = new_name
            student["roll"] = new_roll
            found = True
            break

    if found:
        with open(FILE_NAME, "w") as f:
            json.dump(students, f, indent=4)
        return {"message": f"Student with roll {old_roll} updated successfully."}
    else:
        return {"error": f"No student found with roll number {old_roll}."}

# Admin login section
class LoginData(BaseModel):
    username: str
    password: str

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.post("/login")
def login(data: LoginData):
    if data.username == ADMIN_USERNAME and data.password == ADMIN_PASSWORD:
        return {"success": True, "message": "Login successful"}
    else:
        return {"success": False, "error": "Invalid username or password"}


