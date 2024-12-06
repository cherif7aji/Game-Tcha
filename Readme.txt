#etapes à suivre pour tourner l'applicaation
cd game_tcha
# Sur Linux ou macOS
python3 -m venv venv
source venv/bin/activate

# Sur Windows
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt


# pour tester l'application en mode robot ça suffit d'exécuter les scripts python test1.py et test2.py
