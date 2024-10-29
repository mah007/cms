import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://mahmoud:password@localhost:5432/blog_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

