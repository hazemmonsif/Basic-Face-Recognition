# Face Recognition Server

A **FastAPI**-based face recognition server that provides endpoints to register patients, register family members for a patient, authenticate a patient, and recognize faces in uploaded images. This project uses [face_recognition](https://github.com/ageitgey/face_recognition), [OpenCV](https://opencv.org/), and [FastAPI](https://fastapi.tiangolo.com/) under the hood.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Endpoints](#api-endpoints)
   - [Register a Patient](#register-a-patient)
   - [Register a Family Member Image](#register-a-family-member-image)
   - [Recognize Faces for a Patient](#recognize-faces-for-a-patient)
   - [Patient Login (Authentication)](#patient-login-authentication)
6. [Folder Structure](#folder-structure)
7. [License](#license)
8. [Contributing](#contributing)
9. [Contact](#contact)

---

## Features

- **Patient Registration**: Register a patient's face encoding from a single image.
- **Family Member Registration**: Register multiple face encodings for a patient's family member.
- **Face Recognition**: Given an image, detect and identify faces that belong to registered family members.
- **Patient Login**: Authenticate a patient by matching their face to stored encodings.
- **Ngrok Integration**: Automatically tunnels the local server over HTTPS using [Ngrok](https://ngrok.com/) (optional, can be disabled or removed if not needed).
- **Logging**: Useful debug logs for troubleshooting.

---

## Prerequisites

1. **Python 3.7+** installed.
2. **pip** or **conda** for installing dependencies.
3. **Ngrok** (optional). If you want to expose your API publicly, place the Ngrok executable path as in the code (`C:\Program Files\Ngrok\ngrok.exe` or another path on your system).

---

## Installation

1. **Clone or download this repository**:
   ```bash
   git clone https://github.com/your-username/face-recognition-server.git
   cd face-recognition-server

Install dependencies. For instance:

bash
نسخ
pip install -r requirements.txt
Or manually install the main libraries:

bash
نسخ
pip install fastapi uvicorn numpy opencv-python face_recognition pillow nest_asyncio
(Optional) Set up your Ngrok:

Download and install Ngrok.
Update ngrok_path in the code if your Ngrok path is different.
Set your custom domain (if you have one) or remove that line if you're only using the default ngrok subdomain or running locally.
Usage
Run the server:

bash
نسخ
python main.py
By default, it will:

Attempt to run Ngrok on port 8010.
Launch the FastAPI server at 127.0.0.1:8010.
If Ngrok is configured, you can also use the public Ngrok URL to access the API.
Test the API:

Go to http://127.0.0.1:8010/docs (or your Ngrok URL with /docs) to see the interactive Swagger UI.
Use tools like cURL, Postman, or Insomnia to send requests to the endpoints.
API Endpoints
Below are the primary endpoints along with example usage:

1. Register a Patient
Endpoint: POST /register_patient
Query Parameters:
patient_id (string)
Form Data:
image (UploadFile)
Description: Registers a single face encoding for a new patient.
Example (using cURL):

bash
نسخ
curl -X POST "http://127.0.0.1:8010/register_patient?patient_id=12345" \
     -F "image=@/path/to/patient_photo.jpg"
Response:
json
نسخ
{
  "status": "Encoding saved successfully",
  "path": "path/to/Patient_12345/12345.npy"
}
2. Register a Family Member Image
Endpoint: POST /register_image
Query Parameters:
patient_id (string)
family_member_id (string)
idx (string) — used to differentiate multiple images for the same family member.
Form Data:
image (UploadFile)
Description: Registers encodings for a patient's family member. You may call this endpoint multiple times with different images for better accuracy.
Example (using cURL):

bash
نسخ
curl -X POST "http://127.0.0.1:8010/register_image?patient_id=12345&family_member_id=abc123&idx=0" \
     -F "image=@/path/to/family_member_photo.jpg"
Response:
json
نسخ
{
  "status": "Success",
  "message": "Encodings for Family Member abc123 registered successfully."
}
3. Recognize Faces for a Patient
Endpoint: POST /recognize_faces
Query Parameters:
patient_id (string)
Form Data:
image (UploadFile)
Description: Given an image, attempts to recognize any registered family member’s face(s) that belong to the specified patient.
Example (using cURL):

bash
نسخ
curl -X POST "http://127.0.0.1:8010/recognize_faces?patient_id=12345" \
     -F "image=@/path/to/group_photo.jpg"
Response:
json
نسخ
{
  "recognition_results": [
    {
      "face_location": [top, right, bottom, left],
      "identified_name": "abc123"   // Or "Unknown"
    }
  ]
}
4. Patient Login (Authentication)
Endpoint: POST /login_patient
Form Data:
image (UploadFile)
Description: Attempts to match an uploaded face to the already registered patients.
Example (using cURL):

bash
نسخ
curl -X POST "http://127.0.0.1:8010/login_patient" \
     -F "image=@/path/to/patient_photo.jpg"
Response:
json
نسخ
{
  "status": "Authenticated",
  "patient_id": "12345"
}
or
json
نسخ
{
  "status": "Authentication Failed"
}
Folder Structure
A typical structure (once you run the app and start registering encodings) might look like this:

graphql
نسخ
face-recognition-server/
│
├─ main.py              # Main FastAPI application (the file shown in the snippet)
├─ requirements.txt     # Required dependencies
├─ encodings/           # Folder automatically created for family members
│  └─ Patient_12345/
│     └─ FamilyMember_abc123/
│        ├─ abc123_0.npy
│        ├─ abc123_1.npy
│        ...
│
└─ patients_encoding/   # Folder automatically created for patient encodings
   └─ Patient_12345/
      └─ 12345.npy
encodings/: Stores face encodings for each patient’s family members.
patients_encoding/: Stores each patient’s own face encodings.
License
This project is open-source. You may use it freely for personal or commercial purposes.
See LICENSE for more details.

Contributing
Fork the repository.
Create a new branch with your feature or fix:
bash
نسخ
git checkout -b feature/awesome-feature
Commit your changes and push your branch:
bash
نسخ
git push origin feature/awesome-feature
Create a Pull Request on the main repository.
