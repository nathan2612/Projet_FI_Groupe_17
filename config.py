import os

#>>>import random, string, os
#>>>"".join([random.choice(string.printable) for _ in os.urandom(24) ] )
SECRET_KEY = "730c3469-5303-432e-ad06-d0de212a7d98"

basedir = os.path.abspath(os.path.dirname(__file__))
# Use DATABASE_URL environment variable when provided, otherwise connect to the
# requested MariaDB server. Default DB name is 'oumami' — change if needed.
SQLALCHEMY_DATABASE_URI = os.environ.get(
	'DATABASE_URL',
	'mysql+pymysql://joubert:joubert@servinfo-maria:3306/DBjoubert?charset=utf8mb4'
)

BOOTSTRAP_SERVE_LOCAL = True