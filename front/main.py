import cv2
import numpy as np
import io
import requests
import time
from PIL import Image, ImageDraw
import streamlit as st
import os


def save_image(image, file_path):
    with open(file_path, 'wb') as f:
        f.write(image.getvalue())

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

# Fonction pour traiter et annoter une image ou une vidéo
def annotate_media(media_file, api_url):
    temp_file_path = "./tmp/temp_media_file"
    annotated_video_path = "./tmp/annotated_video.mp4"
    
    # Sauvegarder le fichier téléchargé sur le disque
    with open(temp_file_path, "wb") as f:
        f.write(media_file.read())
    
    if media_file.type.startswith('video'):
        # Traitement de la vidéo
        video_capture = cv2.VideoCapture(temp_file_path)
        frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video_capture.get(cv2.CAP_PROP_FPS))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec pour la vidéo de sortie
        video_writer = cv2.VideoWriter(annotated_video_path, fourcc, fps, (frame_width, frame_height))

        while video_capture.isOpened():
            ret, frame = video_capture.read()

            if not ret:
                break

            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            image_bytes = io.BytesIO()
            pil_image.save(image_bytes, format='JPEG')
            image_bytes.seek(0)

            files = {'file': image_bytes}
            response = requests.post(api_url, files=files)

            if response.status_code == 200:
                detections = response.json()["detections"]
                pil_image_with_boxes = draw_boxes(pil_image, detections)
                annotated_frame = cv2.cvtColor(np.array(pil_image_with_boxes), cv2.COLOR_RGB2BGR)
                video_writer.write(annotated_frame)
            else:
                print("Erreur lors de la détection pour une frame.")

        video_capture.release()
        video_writer.release()

        # Lire la vidéo annotée en mémoire
        with open(annotated_video_path, "rb") as f:
            annotated_video_bytes = io.BytesIO(f.read())
        
        # Nettoyer les fichiers temporaires
        os.remove(temp_file_path)
        os.remove(annotated_video_path)

        return annotated_video_bytes

    elif media_file.type.startswith('image'):
        # Traitement de l'image
        pil_image = Image.open(temp_file_path)
        image_bytes = io.BytesIO()
        pil_image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        files = {'file': image_bytes}
        response = requests.post(api_url, files=files)

        if response.status_code == 200:
            detections = response.json()["detections"]
            pil_image_with_boxes = draw_boxes(pil_image, detections)
            annotated_image_bytes = io.BytesIO()
            pil_image_with_boxes.save(annotated_image_bytes, format='JPEG')
            annotated_image_bytes.seek(0)
            return annotated_image_bytes
        else:
            print("Erreur lors de la détection pour l'image.")
            return None


# Configuration de la page
st.set_page_config(
    page_title="WLIN MI (Sauve moi)",
    page_icon="🐄",
    layout="wide"
)

# Sidebar pour la navigation
st.sidebar.title("Menu de navigation")
section = st.sidebar.radio("Aller à", ["Accueil", "Exemples d'utilisation", "Uploader une image ou vidéo", "À propos"])

# Page d'accueil
if section == "Accueil":
    st.title("WLIN MI (Sauve moi)")
    st.markdown("## Détection intelligente de pathologies bovines 🐄")
    with st.spinner('Chargement de la solution...'):
        time.sleep(2)  # Simule un temps de chargement
    st.success("Chargement terminé !")
    
    st.markdown("""
    ### Bienvenue dans l'application WLIN MI (Sauve moi) 🚜
    L'élevage est un secteur crucial, et la santé de vos vaches est essentielle pour assurer une production de qualité. Avec **WLIN MI**, vous pouvez désormais :
    - **Uploader** des images ou vidéos de vos vaches malades.
    - **Obtenir instantanément un diagnostic** des pathologies potentielles grâce à un modèle de deep learning.
    - **Voir les zones touchées annotées** directement sur les images/vidéos.

    **Objectif** : Améliorer la détection précoce des maladies et optimiser la gestion des troupeaux.

    Laissez-nous vous montrer comment cela fonctionne ! 🧑‍🌾
    """)

    st.markdown("### Découvrez nos autres fonctionnalités dans la barre latérale à gauche !")

# Section des exemples d'utilisation
elif section == "Exemples d'utilisation":
    st.header("Exemples d'utilisation")
    st.markdown("### Voici quelques exemples d'images de vaches avec des pathologies identifiées 🐄")

    # Liste des images et descriptions
    images = [
        "https://www.lacompagniedesanimaux.com/media/amasty/blog/cache/A/v/800/410/Avril_2021_-_cetose_vache_laitiere.jpg",
        "https://www.difagri.fr/wp-content/uploads/2023/07/vaches-ferme-moderne-mangent-ensilage-table-alimentation-1200x800.jpg",
        "https://www.inrae.fr/sites/default/files/styles/actu/public/jpg/Vache%20montbelliarde%20laitiere.jpg?itok=YX6RXBoH"
    ]

    captions = [
        "Cétose chez une vache laitière : Cette maladie métabolique survient souvent lors des périodes de production de lait.",
        "Alimentation dans une ferme moderne : Les bonnes pratiques alimentaires aident à prévenir plusieurs pathologies.",
        "Vache Montbéliarde en pleine santé : Un bon état général est essentiel pour maximiser la production laitière."
    ]

    # Utilisation d'une animation simple avec le sélecteur d'images
    index = st.slider("Choisissez une image à voir", min_value=0, max_value=len(images)-1, step=1)
    st.image(images[index], caption=captions[index], use_column_width=True)

    # Simulation d'une analyse d'image
    st.markdown(f"**Analyse de l'image {index + 1}...**")
    with st.spinner('Analyse en cours...'):
        time.sleep(3)  # Simulation du processus d'analyse
    st.success(f"Analyse terminée pour l'image {index + 1} ! Pathologie détectée : {captions[index].split(':')[0]}")

# Section pour uploader une image ou une vidéo
elif section == "Uploader une image ou vidéo":
    st.header("Uploader une image ou une vidéo")
    st.markdown("""
    ### Téléchargez une image ou vidéo de votre vache malade et laissez notre modèle faire le diagnostic. 📷
    """)

    uploaded_media = st.file_uploader("Téléchargez une image ou une vidéo", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])

    if uploaded_media is not None:
        api_url = "http://127.0.0.1:8000/detect"  # URL de votre API

        if uploaded_media.type.startswith('video'):
            st.video(uploaded_media)  # Afficher la vidéo uploadée
            with st.spinner("Annotation de la vidéo en cours..."):
                annotated_video_file = annotate_media(uploaded_media, api_url)
                st.video(annotated_video_file.read())  # Afficher la vidéo annotée
                st.download_button(
                    label="Télécharger la vidéo annotée",
                    data=annotated_video_file,
                    file_name="annotated_video.mp4",
                    mime="video/mp4"
                )
        elif uploaded_media.type.startswith('image'):
            #st.image(uploaded_media)  # Afficher l'image uploadée
            with st.spinner("Annotation de l'image en cours..."):
                annotated_image_bytes = annotate_media(uploaded_media, api_url)
                if annotated_image_bytes:
                    st.image(annotated_image_bytes)
                    st.download_button(
                        label="Télécharger l'image annotée",
                        data=annotated_image_bytes,
                        file_name="annotated_image.jpg",
                        mime="image/jpeg"
                    )
    

# Section "À propos"
elif section == "À propos":
    st.header("À propos de WLIN MI (Sauve moi)")
    st.markdown("""
    ### L'application WLIN MI (Sauve moi) est une solution intelligente de détection de pathologies bovines basée sur l'intelligence artificielle.
    
    Elle a été conçue pour aider les éleveurs à mieux gérer la santé de leurs troupeaux et à détecter rapidement les maladies avant qu'elles ne deviennent critiques. 

    **Principales fonctionnalités** :
    - Détection automatique des pathologies à partir d'images et de vidéos.
    - Annotations automatiques des parties affectées.
    - Interface intuitive et facile à utiliser.

    **Technologies utilisées** :
    - Modèles de deep learning avancés pour la détection d'images (basés sur YOLOv8).
    - Interface interactive développée avec Streamlit.
    
    Développé par une équipe passionnée d'experts en IA et en élevage. 🌍
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("**© 2024 WLIN MI | Tous droits réservés**")
