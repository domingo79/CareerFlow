# redirect  → manda il browser a un'altra pagina
# url_for   → genera l'URL di una route dal suo nome (evita di scrivere URL a mano)
from flask import Flask, redirect, url_for

# init_db è la funzione che crea le tabelle nel DB al primo avvio
from service.db import init_db

# ogni Blueprint è un gruppo di route definite in un file separato
from routes.aziende import aziende_bp
from routes.referenti import referenti_bp
from routes.candidature import candidature_bp
from routes.dashboard import dashboard_bp


app = Flask(__name__)

# secret_key è una password interna usata da Flask per firmare i cookie
# di sessione (necessaria per i messaggi flash).
app.secret_key = 'careerflow-local'

# Crea le tabelle nel DB leggendo schema_db.sql.
init_db()

# register_blueprint "monta" i gruppi di route sull'app principale.
# Senza questa riga le route definite in quel file non sarebbero raggiungibili.
app.register_blueprint(aziende_bp)
app.register_blueprint(referenti_bp)
app.register_blueprint(candidature_bp)
app.register_blueprint(dashboard_bp)


@app.route('/')
def index():
    # url_for('dashboard.index') genera l'URL /dashboard/
    # senza doverlo scrivere a mano (e senza rischiare errori se l'URL cambia)
    return redirect(url_for('dashboard.index'))


if __name__ == '__main__':
    app.run(debug=True)
