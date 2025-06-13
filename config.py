class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://sjzeriiat:Aa123*845257@localhost/license_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # 调试时开启，生产环境关闭
