import cv2
import numpy as np
import time
import random
import requests
from PIL import Image, ImageDraw

# URL de votre application Flask
url = "http://127.0.0.1:5000/validate-captcha"

# Fonction de détection des pommes rouges
def detect_apples(image):
    """
    Détecte les pommes rouges dans une image donnée.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red_1 = np.array([0, 150, 150])
    upper_red_1 = np.array([10, 255, 255])
    lower_red_2 = np.array([160, 150, 150])
    upper_red_2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
    mask = cv2.bitwise_or(mask1, mask2)

    blurred_mask = cv2.GaussianBlur(mask, (5, 5), 0)
    kernel = np.ones((5, 5), np.uint8)
    closed_mask = cv2.morphologyEx(blurred_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    fruit_positions = []
    for contour in contours:
        if cv2.contourArea(contour) > 500:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            fruit_positions.append({'x': int(x), 'y': int(y), 'radius': int(radius)})

    return fruit_positions

# Charger l'image téléchargée
image_path = 'static/tree_with_fruits.png'  # L'image téléchargée
image = cv2.imread(image_path)

# Enregistrer le temps de début de l'exécution
start_time = time.time()

# Détecter les pommes sur l'image
apple_positions = detect_apples(image)

# Convertir l'image OpenCV en image Pillow pour affichage
image_pil = Image.open(image_path)

# Dessiner des cercles sur les pommes détectées
def draw_circles_on_apples(image_pil, apple_positions):
    draw = ImageDraw.Draw(image_pil)

    # Dessiner chaque cercle sur les pommes
    for apple in apple_positions:
        x, y, radius = apple['x'], apple['y'], apple['radius']
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="black", width=2)

    return image_pil

# Dessiner les cercles
modified_image = draw_circles_on_apples(image_pil, apple_positions)

# Afficher l'image modifiée
modified_image.show()

# Simuler le comportement humain ou robotique
def simulate_behavior(apple_positions):
    # Temps de début
    start_time = int(time.time() * 1000)

    # Envoi des données des pommes détectées
    data = {
        "circles": apple_positions,
        "startTime": start_time,
        "endTime": int(time.time() * 1000)
    }

    print(f"Test robotique: {len(apple_positions)} cercles générés avec un délai.")

    # Envoyer une requête POST à l'application Flask
    response = requests.post(url, json=data)

    # Résultat de la validation
    if response.status_code == 200:
        print("Réponse de l'application:", response.json())
    else:
        print("Erreur lors de l'envoi de la requête:", response.status_code, response.text)

# Lancer la simulation
simulate_behavior(apple_positions)

# Enregistrer le temps de fin de l'exécution
end_time = time.time()

# Calculer la durée d'exécution
execution_duration = end_time - start_time

# Afficher la durée d'exécution
print(f"Durée d'exécution du programme: {execution_duration:.2f} secondes.")

