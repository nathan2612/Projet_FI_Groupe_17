import os

SECRET_KEY = "730c3469-5303-432e-ad06-d0de212a7d98"

SQLALCHEMY_DATABASE_URI = os.environ.get(
	'DATABASE_URL',
	'mysql+pymysql://louis:louis@localhost:3306/oumami?charset=utf8mb4')
