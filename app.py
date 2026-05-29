from flask import Flask, redirect, url_for
from service.db import init_db
from routes.aziende import aziende_bp
from routes.referenti import referenti_bp
from routes.candidature import candidature_bp
from routes.dashboard import dashboard_bp

# crea l'applicazione Flask
app = Flask(__name__)

# chiave segreta necessaria per i messaggi flash (notifiche)
app.secret_key = 'careerflow-local'

# crea le tabelle nel DB al primo avvio (se esistono già non fa nulla)
init_db()

# registra le route di ogni sezione
app.register_blueprint(aziende_bp)
app.register_blueprint(referenti_bp)
app.register_blueprint(candidature_bp)
app.register_blueprint(dashboard_bp)


# route principale: apre la dashboard
@app.route('/')
def index():
    return redirect(url_for('dashboard.index'))


if __name__ == '__main__':
    app.run(debug=True)
