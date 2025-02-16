import streamlit as st
import face_recognition
import numpy as np
import json
import os
from PIL import Image

ENCODINGS_FILE = "face_encodings.json"

def load_encodings_from_file(file_path=ENCODINGS_FILE):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        return []
    with open(file_path, "r") as file:
        return json.load(file)

def get_face_encoding(image):
    image_array = np.array(image)
    encodings = face_recognition.face_encodings(image_array)
    return encodings[0].tolist() if encodings else None

def compare_faces(uploaded_image):
    stored_encodings = load_encodings_from_file()
    if not stored_encodings:
        return "No stored encodings found. Please add images first.", []

    img_encoding = get_face_encoding(uploaded_image)
    if img_encoding is None:
        return "Error: No face found in the uploaded image.", []

    known_encodings = [np.array(entry["encoding"]) for entry in stored_encodings]
    image_names = [os.path.splitext(entry["name"])[0] for entry in stored_encodings]
    
    face_distances = face_recognition.face_distance(known_encodings, np.array(img_encoding))
    matches = sorted(zip(image_names, face_distances), key=lambda x: x[1])[:20]

    results = [{"name": name, "url": f"https://iare-data.s3.ap-south-1.amazonaws.com/uploads/STUDENTS/{name}/{name}.jpg"} for name, _ in matches]
    return None, results

st.title("Face Recognition Comparison")
st.write("Upload an image or capture from the camera to compare with stored faces.")

option = st.radio("Choose an option:", ["Upload Image", "Open Camera"])

image = None

if option == "Upload Image":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

elif option == "Open Camera":
    captured_image = st.camera_input("Capture an image")
    if captured_image is not None:
        image = Image.open(captured_image)

if image:
    scale_percent = 50  
    new_size = (int(image.width * scale_percent / 100), int(image.height * scale_percent / 100))
    resized_image = image.resize(new_size)
    
    st.image(resized_image, caption="Uploaded Image", use_container_width=False)
    st.write("Processing image...")
    
    error, results = compare_faces(image)

    if error:
        st.error(error)
    else:
        st.success("Top 20 Matches:")
        cols = st.columns(5)

        for idx, result in enumerate(results):
            name, url = result["name"], result["url"]
            with cols[idx % 5]:
                link = f'<a href="?selected={name}"><img src="{url}" width="100"><br><b>{name}</b></a>'
                st.markdown(link, unsafe_allow_html=True)

if "selected" in st.query_params:
    selected_name = st.query_params["selected"]
    st.toast(f"Hi, {selected_name}")
