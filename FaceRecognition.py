# Import necessary libraries
from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import face_recognition
import numpy as np
import cv2
import logging
import uvicorn
import nest_asyncio
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor
import io
import subprocess
import time
from pathlib import Path 
from PIL import Image
from io import BytesIO
import shutil
from typing import List
import math 
script_directory = Path(os.path.dirname(__file__))
# Create an instance of FastAPI
app = FastAPI()

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)

# Function to save face encodings as NumPy arrays
def save_encoding_to_file_np(encoding, output_file_path):
    np.save(output_file_path, encoding)

def run_ngrok(ngrok_path, domain, local_port):
      subprocess.Popen([ngrok_path, 'http', '--domain=excited-hound-vastly.ngrok-free.app', 'localhost:8010'])
    
def load_encodings_from_folderForFamily(folder_path):
    encodings = {}
    for root, dirs, files in os.walk(folder_path):
        encodings[os.path.basename(root)] = [np.load(os.path.join(root, file)) for file in files if file.endswith(".npy")]
    return encodings    
# Function to load face encodings from NumPy arrays
def load_encodings_from_folder(folder_path):
    encodings = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".npy"):
                file_path = os.path.join(root, file_name)
                encodings[file_name[:-4]] = np.load(file_path)
    return encodings 

async def register_image(patient_id: str, family_member_id: str, images: List[UploadFile]):
    base_path = script_directory / "encodings" / f"Patient_{patient_id}" / f"FamilyMember_{family_member_id}"
    os.makedirs(base_path, exist_ok=True)
    
    for idx, image in enumerate(images):
        image_data = await image.read()
        face_image = face_recognition.load_image_file(BytesIO(image_data))
        encodings = face_recognition.face_encodings(face_image)
        if encodings:
            save_encoding_to_file_np(encodings[0], base_path / f"{family_member_id}_{idx}.npy")

    return f"Encodings for Family Member {family_member_id} registered successfully."
def extractid(name):
    # Split the string by ''
    parts = name.split('_')
    # Return the part after the underscore if it exists
    if len(parts) > 1:
        return parts[1]
    return None  # Return None or appropriate value if underscore is not present
def find_best_matchForFamily(unknown_encoding, known_encodings, distance_threshold=0.6, consensus_threshold=.8):
    logging.debug("Starting face match process.")
    candidates = {}

    for full_name, encodings_list in known_encodings.items():
        if not encodings_list:
            logging.debug(f"No encodings available for {full_name}")
            continue
        
        # Calculate distances and count how many are below the threshold
        distances = [np.linalg.norm(encoding - unknown_encoding) for encoding in encodings_list]
        matches = [distance <= distance_threshold for distance in distances]
        match_rate = sum(matches) / len(matches)
        logging.debug(f"{full_name} match rate: {match_rate * 100}% with distances: {distances}")

        # Only consider this person if the match rate exceeds the consensus threshold
        if match_rate >= consensus_threshold:
            candidates[full_name] = match_rate

    # Decide based on the highest match rate if any candidates meet the criteria
    if candidates:
        best_match = max(candidates, key=candidates.get)
        logging.debug(f"Best match based on consensus is {best_match} with match rate {candidates[best_match] * 100}%")
        return extractid(best_match)

    logging.debug("No matches found meeting the consensus threshold. Returning 'Unknown'.")
    return "Unknown"
    
# Function to find the nearest match for a face encoding among known encodings
def find_nearest_match(unknown_encoding, known_encodings, distance_threshold=0.6):
    best_match_name = "Unknown"
    best_distance = float('inf')

    for name, known_encoding in known_encodings.items():
         #Calculate the distance between the unknown encoding and the known encoding
        
        distance = np.linalg.norm(known_encoding - unknown_encoding)
        
        if distance < best_distance:
            best_distance = distance
            #Extract name from the filename
            name_parts = name.split("_")
            if len(name_parts) > 1:
                best_match_name = "_".join(name_parts[1:])
            else:
                best_match_name = name

    #If the best distance is within the threshold, consider it a match
    if best_distance <= distance_threshold:
        return best_match_name
    else:
        return "Unknown"
##################################################################################################################################################################
async def register_image(patient_id: str, family_member_id: str,idx : str, image: UploadFile):
    base_path = script_directory / "encodings" / f"Patient_{patient_id}" / f"FamilyMember_{family_member_id}" 
    os.makedirs(base_path, exist_ok=True)

    try:
        image_data = await image.read()
        image_pil = Image.open(BytesIO(image_data)).convert('RGB')
        image_cv2 = np.array(image_pil)[:, :, ::-1].copy()
        image_cv2 = cv2.detailEnhance(image_cv2, sigma_s=10, sigma_r=0.15)

        face_locations = face_recognition.face_locations(image_cv2, model="hog")
        logging.debug(f"The face location is {face_locations}")
        if len(face_locations) != 1:
            shutil.rmtree(base_path)
            raise HTTPException(status_code=400, detail="No face detected or more than one face in the uploaded image.")

        encodings = face_recognition.face_encodings(image_cv2)
        
        if encodings:
            logging.debug("getting into encoding file")
            save_encoding_to_file_np(encodings[0], base_path / f"{family_member_id}_{idx}.npy")
        else:
            raise HTTPException(status_code=400, detail="Unable to encode face.")

        return f"Encodings for Family Member {family_member_id} registered successfully."

    except HTTPException as e:
        shutil.rmtree(base_path)
        raise e
    except Exception as e:
        shutil.rmtree(base_path)
        logging.error(f"An error occurred while registering image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")
 #####################################################################################################################
async def recognize_faces_in_image(patient_id: str, image: UploadFile):
    try:
        logging.debug("Loading patient directory")
        patient_directory = script_directory / "encodings" / f"Patient_{patient_id}"
        logging.debug(f"Patient directory: {patient_directory}")
        
        known_encodings = load_encodings_from_folderForFamily(patient_directory)
        logging.debug("Loaded known encodings")

        image_data = await image.read()
        image_pil = Image.open(BytesIO(image_data)).convert('RGB')
        image_cv2 = np.array(image_pil)[:, :, ::-1].copy()
        image_cv2 = cv2.detailEnhance(image_cv2, sigma_s=10, sigma_r=0.15)
        face_locations = face_recognition.face_locations(image_cv2,model="hog")
        face_encodings = face_recognition.face_encodings(image_cv2, face_locations)
        
        results = []
        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            best_match_name = find_best_matchForFamily(face_encoding, known_encodings)
            cv2.rectangle(image_cv2, (left, top), (right, bottom), (0, 255, 0) if best_match_name != "Unknown" else (0, 0, 255), 2)
            cv2.putText(image_cv2, best_match_name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            results.append({"face_location": (top, right, bottom, left), "identified_name": best_match_name})
        
        return {"recognition_results": results}
    except Exception as e:
        logging.error(f"Error during face recognition: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Define the base directory for patient encodings
base_directory = Path(f"{script_directory}\patients_encoding")

# Ensure the base directory exists
os.makedirs(base_directory, exist_ok=True)
# Function to register a patient's face encoding
@app.post("/register_patient")
async def register_patient(patient_id: str, image: UploadFile):
    try:
        # Create directory for the patient if it does not exist
        patient_directory = base_directory / f"Patient_{patient_id}"
        os.makedirs(patient_directory, exist_ok=True)

        # Read the uploaded image
        image_data = await image.read()
        unknown_image = face_recognition.load_image_file(io.BytesIO(image_data))
        unknown_encodings = face_recognition.face_encodings(unknown_image)

        if len(unknown_encodings) == 0:
            raise HTTPException(status_code=400, detail="No face detected in the uploaded image")

        # Save the face encoding
        unknown_encoding = unknown_encodings[0]
        encoding_file_path = patient_directory / f"{patient_id}.npy"
        save_encoding_to_file_np(unknown_encoding, encoding_file_path)

        return {"status": "Encoding saved successfully", "path": str(encoding_file_path)}
    except Exception as e:
        logging.error(f"Error during face registration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to register an image and return the file location
@app.post("/register_image")
async def register_images_endpoint(patient_id: str, family_member_id: str,idx : str, image:UploadFile = File(...)):
    try:
        response = await register_image(patient_id, family_member_id,idx, image )
        return {"status": "Success", "message": response}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "Error", "message": str(e)}

@app.post("/recognize_faces")
async def recognize_faces_endpoint(patient_id: str, image: UploadFile = File(...)):
    return await recognize_faces_in_image(patient_id, image)

def load_encoding_from_file(file_path):
    return np.load(file_path, allow_pickle=True)

def load_all_encodings(directory):
    known_encodings = {}
    # Iterate over each subfolder in the base directory
    for patient_folder in directory.iterdir():
        if patient_folder.is_dir():  # Ensure it's a directory
            for encoding_file in patient_folder.glob('*.npy'):  # Assuming one encoding file per patient folder
                patient_id = patient_folder.name  # Folder name as patient ID
                known_encodings[patient_id] = load_encoding_from_file(encoding_file)
    return known_encodings


@app.post("/login_patient")
async def login(image: UploadFile):
    try:
        image_data = await image.read()
        unknown_image = face_recognition.load_image_file(io.BytesIO(image_data))
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        if not unknown_encodings:
            return {"status": "No face detected"}

        unknown_encoding = unknown_encodings[0]
        matched_patient = find_nearest_match(unknown_encoding,load_encodings_from_folder(base_directory) )
        if matched_patient != "Unknown":
            return {"status": "Authenticated", "patient_id": matched_patient}
        else:
            return {"status": "Authentication Failed"}
    except Exception as e:
        logging.error(f"Error during login attempt: {e}")
        return {"status": "Error", "message": str(e)}


# Run the FastAPI application using uvicorn server
if __name__ == "__main__":
    ngrok_path = r"C:\Program Files\Ngrok\ngrok.exe"
    domain = "excited-hound-vastly.ngrok-free.app"
    local_port = 8010
    run_ngrok(ngrok_path, domain, local_port)
    nest_asyncio.apply()
    uvicorn.run(app, host="127.0.0.1", port=8010)
    