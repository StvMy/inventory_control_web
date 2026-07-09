from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = "flask_admin"
    
    from .view import views  #import package view
    from .table import tables
    # ----- // CAN IMPORT MORE HERE // -------
    
    app.register_blueprint(views, url_prefix="/") #register the views function to blueprint with no prefix
    app.register_blueprint(tables, url_prefix="/data")
    # ----- // CAN ADD MORE BLUEPRINT HERE // -------
    
    return app