from flask import Flask
from flask_talisman import Talisman
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from .database import db
from .themes import themes
from .models.security import Role, User


def create_app(env="development"):

    app = Flask(__name__)
    app.config.from_object(f"app.settings.{env.capitalize()}Settings")

    # Third party
    Talisman(app=app)
    db.init_app(app=app)
    Migrate(app=app, db=db)

    # Flask security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    # Blueprints
    app.register_blueprint(themes, url_prefix="/themes")

    return app
