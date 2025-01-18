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


## Folder Structure
**A typical structure (once you run the app and start registering encodings) might look like this**:

   ```bash
face-recognition-server/
│
├─ main.py              # Main FastAPI application
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
## License 
نسخ
