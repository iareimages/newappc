import face_recognition
import numpy as np
import os
import json

ENCODINGS_FILE = "face_encodings.json" 

def get_image_paths(folder_path):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    if not os.path.isdir(folder_path):
        print("Invalid folder path!")
        return []
    
    image_paths = [
        os.path.join(folder_path, file).replace("\\", "//")
        for file in os.listdir(folder_path)
        if os.path.splitext(file)[1].lower() in image_extensions
    ]
    
    return image_paths


def get_face_encoding(image_path):
    """Extracts face encoding from an image."""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) == 0:
        print(f"Error: No face detected in {image_path}")
        return None
    return encodings[0].tolist() 

def save_encodings_to_file(encodings_list, file_path=ENCODINGS_FILE):
    """Saves face encodings along with image names to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(encodings_list, file)

def load_encodings_from_file(file_path=ENCODINGS_FILE):
    """Loads face encodings and associated image names from a JSON file."""
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        print(f"Warning: {file_path} not found or is empty.")
        return []
    with open(file_path, "r") as file:
        return json.load(file)

def compare_faces(image_path):
    stored_encodings = load_encodings_from_file()

    if not stored_encodings:
        print("No stored encodings found. Please add images first.")
        return

    img_encoding = get_face_encoding(image_path)
    if img_encoding is None:
        print("Error: No face found in the provided image.")
        return

    known_encodings = [np.array(entry["encoding"]) for entry in stored_encodings]
    image_names = [entry["name"] for entry in stored_encodings]

    face_distances = face_recognition.face_distance(known_encodings, np.array(img_encoding))

    matches = list(zip(image_names, face_distances))
    matches.sort(key=lambda x: x[1])

    top_matches = matches[:20]

    if top_matches:
        print("Top 20 Matches:")
        for name, distance in top_matches:
            print(f"{name} - Similarity Score: {100 - (distance * 100):.2f}%")
    else:
        print("No match found.")

def add_encoding(image_path):
    """Adds a new face encoding to the database."""
    stored_encodings = load_encodings_from_file()

    img_encoding = get_face_encoding(image_path)
    if img_encoding is not None:
        stored_encodings.append({"name": os.path.basename(image_path), "encoding": img_encoding})
        save_encodings_to_file(stored_encodings)
        print(f"Added encoding for {os.path.basename(image_path)}")

if __name__ == "__main__":
    # folder_path = input("Enter the folder path: ")
    # images = get_image_paths(folder_path)
    # count = 0
    # if images:
    #     print("Images found:")
    #     for img in images:
    #         count+=1
    #         print(count,end=" ")
    #         add_encoding(img)
    # else:
    #     print("No images found in the given folder.")
    # print("total images are ",count)
    compare_faces("C:\\Users\\dkuma\\Downloads\\WhatsApp Image 2025-02-14 at 10.52.14 PM.jpeg")