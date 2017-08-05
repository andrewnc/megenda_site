class Config(object):
	""" Common Configurations"""
	pass


class DevelopmentConfig(object):
	DEBUG = True
	SQLALCHEMY_ECHO = False

class ProductionConfig(object):
	DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}