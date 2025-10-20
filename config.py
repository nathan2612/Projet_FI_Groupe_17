import os

#>>>import random, string, os
#>>>"".join([random.choice(string.printable) for _ in os.urandom(24) ] )
SECRET_KEY = "730c3469-5303-432e-ad06-d0de212a7d98"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'monApp.db')

BOOTSTRAP_SERVE_LOCAL = True