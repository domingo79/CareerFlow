from flask import Flask
from service.db import init_db
from routes.aziende import aziende_bp
# from routes.contatti import contatti_bp
# from routes.candidature import candidature_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")

    with app.app_context():
        init_db()

    app.register_blueprint(aziende_bp)
    # app.register_blueprint(contatti_bp)
    # app.register_blueprint(candidature_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
