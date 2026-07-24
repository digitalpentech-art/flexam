import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'test-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Celery & Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY = {
        'broker_url': REDIS_URL,
        'result_backend': REDIS_URL,
        'task_ignore_result': False,
    }
    
    # Caching
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = REDIS_URL
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/flexam_dev'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/flexam_test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        if not cls.SQLALCHEMY_DATABASE_URI:
             raise ValueError("No DATABASE_URL set for production")
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
