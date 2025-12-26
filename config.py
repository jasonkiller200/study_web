import os

# 取得目前檔案所在的資料夾絕對路徑
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """通用設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-you-should-change'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin1234'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NOTES_PER_PAGE = 9

    # Image Upload Settings
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_IMAGE_WIDTH = 800
    IMAGE_QUALITY = 85

class DevelopmentConfig(Config):
    """開發環境設定"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or         'sqlite:///' + os.path.join(basedir, 'instance', 'carbon_learning.db')

class TestingConfig(Config):
    """測試環境設定"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'

class ProductionConfig(Config):
    """生產環境設定"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///./instance/carbon_learning.db'

# 建立一個字典，方便根據環境名稱來選取設定
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
