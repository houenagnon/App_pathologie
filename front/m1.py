import streamlit as st
import time
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
import io

# Initialisation du client d'inférence
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="5Sv4RL4KtzgRCh1lWKJw"
)

def save_image(image, file_path):
    with open(file_path, 'wb') as f:
        f.write(image.getvalue())

# Fonction pour dessiner les bounding boxes sur l'image
def draw_boxes(image, predictions):
    draw = ImageDraw.Draw(image)
    
    for prediction in predictions:
        # Calcul des coordonnées de la boîte
        x_center = prediction['x']
        y_center = prediction['y']
        width = prediction['width']
        height = prediction['height']
        
        # Coordonnées des coins  de la boîte
        x_min = x_center - width / 2
        y_min = y_center - height / 2
        x_max = x_center + width / 2
        y_max = y_center + height / 2
        
        # Dessiner le rectangle (bounding box)
        draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=3)
        
        # Ajouter le texte de la classe détectée avec la confiance
        label = f"{prediction['class']} ({prediction['confidence']:.2f})"
        draw.text((x_min, y_min - 10), label, fill="red")
    
    return image

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

    # Upload du fichier (support pour images uniquement dans cet exemple)
    uploaded_file = st.file_uploader("Uploader une image ou vidéo", type=["jpg", "jpeg", "png", "mp4"])

    if uploaded_file is not None:
        # Vérification si le fichier uploadé est une image
        if uploaded_file.type.startswith("image/"):
            img = Image.open(uploaded_file)
            #st.image(img, caption="Image uploadée", use_column_width=True)
            st.markdown("Analyse en cours...")

            # Conversion de l'image en bytes pour l'API
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            save_path = 'temp_image.jpg'

            # Sauvegarder l'image en local
            save_image(img_bytes, save_path)
            
            with st.spinner('Analyse de votre fichier...'):
                # Envoi de l'image au modèle d'inférence via l'API
                result = CLIENT.infer(save_path, model_id="cattle-diseases-ezkwx/1")
                time.sleep(3)  # Temps simulé pour l'inférence
            
            img_with_boxes = draw_boxes(img, result['predictions'])
            st.image(img_with_boxes, caption="Detection", use_column_width=True)
            st.success("Pathologie détectée : " + str(result))
            

        else:
            st.error("Le format vidéo n'est pas encore supporté. Veuillez uploader une image.")

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
