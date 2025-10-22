import os

SECRET_KEY = "730c3469-5303-432e-ad06-d0de212a7d98"

SQLALCHEMY_DATABASE_URI = os.environ.get(
	'DATABASE_URL',
	'mysql+pymysql://maillet:maillet@servinfo-maria:3306/DBmaillet?charset=utf8mb4'
)

BOOTSTRAP_SERVE_LOCAL = True