import streamlit as st
from PIL import Image, ImageDraw
import requests
import io

# Fonction pour dessiner les boîtes englobantes
def draw_boxes(image, detections):
    draw = ImageDraw.Draw(image)
    
    for detection in detections:
        bbox = detection["bbox"][0]  # Coordonnées des boîtes englobantes
        class_name = detection["class_name"]  # Nom de la classe détectée
        confidence = detection["confidence"][0]  # Confiance de la détection

        # Dessiner un rectangle autour de l'objet détecté
        draw.rectangle(bbox, outline="red", width=3)

        # Ajouter le texte (nom de la classe + score de confiance)
        draw.text((bbox[0], bbox[1]), f"{class_name} ({confidence:.2f})", fill="yellow")

    return image

# Simuler l'appel de l'API et obtenir l'image avec les détections
def get_detections_and_image():
    # URL de votre API FastAPI
    api_url = "http://127.0.0.1:8000/detect"
    
    # Charger une image depuis un fichier local
    uploaded_file = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # Convertir l'image en bytes pour l'envoyer à l'API
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
        
        # Envoyer l'image à l'API
        files = {'file': image_bytes}
        response = requests.post(api_url, files=files)

        if response.status_code == 200:
            detections = response.json()["detections"]
            st.write("Détections reçues:", detections)

            # Dessiner les boîtes sur l'image
            image_with_boxes = draw_boxes(image, detections)
            
            # Afficher l'image annotée dans Streamlit
            st.image(image_with_boxes, caption="Image annotée avec les détections", use_column_width=True)
        else:
            st.error("Erreur lors de la détection.")

# Interface Streamlit
st.title("Détection de pathologies animales avec YOLO")

get_detections_and_image()
