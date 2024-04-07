from flask import Flask
from flask_talisman import Talisman
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_security import Security, SQLAlchemyUserDatastore
from .database import db
from .themes import themes
from .applications import apps
from .home import home
from .models.security import Role, User


def create_app(env="development"):

    app = Flask(__name__)
    app.config.from_object(f"app.config.{env.capitalize()}Config")

    # Third party
    # Talisman(app=app)
    db.init_app(app=app)
    Migrate(app=app, db=db)
    DebugToolbarExtension(app=app)

    # Flask security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    # Blueprints
    app.register_blueprint(themes, url_prefix="/themes")
    app.register_blueprint(apps, url_prefix="/apps")
    app.register_blueprint(home, url_prefix="/")

    return app
