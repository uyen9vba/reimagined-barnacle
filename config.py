class Config:
    DEBUG = True


    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@localhost/ihws'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = 'secret-key-not-known-222-1'
    JWT_ERROR_MESSAGE_KEY = 'message'

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    UPLOADED_IMAGES_DEST = 'static/images'
