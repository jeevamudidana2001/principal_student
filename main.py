from datetime import datetime
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime
import requests  # ✅ Required for Google Sheets integration

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

FILE_NAME = "students.json"

# Load or create
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as f:
        students = json.load(f)
else:
    students = []

@app.get("/")
def home():
    return {"message": "Welcome to the Principal-Student App 🚀"}

@app.post("/register")
async def register_student(name: str = Form(...), roll: str = Form(...)):
    with open("students.json", "r") as file:
        students = json.load(file)

    # Check for duplicate roll numbers
    for student in students:
        if student["roll"] == roll:
            return {"error": "Student with this roll number already exists."}

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append new student with timestamp
    students.append({
        "name": name,
        "roll": roll,
        "timestamp": timestamp
    })

    with open("students.json", "w") as file:
        json.dump(students, file, indent=2)

    return {"message": "Student registered successfully."}


    with open(FILE_NAME, "w") as f:
        json.dump(students, f, indent=4)

    # ✅ Send data to Google Sheets
    try:
        requests.post(
            "https://script.google.com/macros/s/AKfycbxevMkfR04q_6UWqcV5-7RkVEDF433ruvO_VZTFJky1Xyxuqk1a7WDJ_kNLwKT0n734/exec",
            json=student
        )
    except Exception as e:
        print("⚠️ Google Sheets update failed:", e)

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

# ✅ Admin login route
@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "admin123":
        return {"success": True}
    else:
        return {"success": False, "error": "Invalid credentials"}
