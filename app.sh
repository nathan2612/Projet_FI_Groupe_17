cd Projet_FI_Groupe_17/
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
export FLASK_APP=monApp
export FLASK_ENV=development
flask loaddb monApp/data/data.yml
flask run