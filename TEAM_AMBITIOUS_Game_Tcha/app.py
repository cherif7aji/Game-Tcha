from flask import Flask, request, render_template, jsonify
import cv2
import numpy as np
import math
import time

app = Flask(__name__)

# Chemin de l'image utilisée pour le CAPTCHA
IMAGE_PATH = "static/tree_with_fruits.png"
IMAGE = cv2.imread(IMAGE_PATH)

if IMAGE is None:
    raise FileNotFoundError(f"Impossible de lire l'image à l'emplacement : {IMAGE_PATH}")


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


FRUIT_POSITIONS = detect_apples(IMAGE)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/validate-captcha', methods=['POST'])
def validate_captcha():
    """
    Valide les cercles dessinés par l'utilisateur en fonction des positions des fruits détectés.
    """
    data = request.get_json()
    circles = data.get('circles', [])
    start_time = data.get('startTime')
    end_time = data.get('endTime')

    # Calcul de la durée
    duration = (end_time - start_time) / 1000

    # Vérification de la durée
    if duration < 0.5:
        return jsonify({'message': 'Action suspecte : trop rapide, probablement un robot.'})

    matched_circles = 0
    unmatched_fruits = len(FRUIT_POSITIONS)
    extra_circles = 0
    perfectly_matched = 0
    
    # validation des cercles dessinés
    for circle in circles:
        matched = False
        for fruit in FRUIT_POSITIONS:
            # Calcul de la distance entre le centre du cercle et celui du fruit
            distance = math.sqrt((circle['x'] - fruit['x']) ** 2 + (circle['y'] - fruit['y']) ** 2)

            # Vérifier si le cercle entoure approximativement le fruit
            if distance < fruit['radius'] * 1.5:  # Tolérance réaliste pour les utilisateurs
                matched = True
                matched_circles += 1
                unmatched_fruits -= 1

                # Vérifier si le tracé est trop parfait (distance très petite et rayon identique)
                if distance < fruit['radius'] * 0.3 and abs(circle['radius'] - fruit['radius']) <= fruit['radius'] * 0.2:
                    perfectly_matched += 1
                break
        if not matched:
            extra_circles += 1

    # Détection d'un comportement suspect si trop de cercles parfaits
    if perfectly_matched >= len(FRUIT_POSITIONS) * 0.8:
        return jsonify({'message': 'Action suspecte : dessin trop parfait, probablement un robot.'})

    # Validation basée sur le temps et les correspondances
    if matched_circles >= len(FRUIT_POSITIONS) * 0.8 and 0.5 <= duration <= 120:
        return jsonify({'message': 'Validation réussie : Humain détecté.'})

    # Échec de la validation
    output_image = IMAGE.copy()
    for fruit in FRUIT_POSITIONS:
        cv2.circle(output_image, (fruit['x'], fruit['y']), fruit['radius'], (0, 255, 0), 3)
        cv2.putText(output_image, "Pomme", (fruit['x'] - 10, fruit['y'] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    output_path = "static/corrected_tree_with_fruits.png"
    cv2.imwrite(output_path, output_image)

    return jsonify({'message': 'Validation échouée : probablement un robot', 'corrected_image': output_path})


if __name__ == '__main__':
    app.run(debug=True)

