# ============================================================
# app.py — punto di partenza dell'applicazione
# Questo è il file che Python esegue quando scrivi: python app.py
# ============================================================

# Flask è il framework web che usiamo: gestisce le richieste HTTP
# redirect  → manda il browser a un'altra pagina
# url_for   → genera l'URL di una route dal suo nome (evita di scrivere URL a mano)
from flask import Flask, redirect, url_for

# init_db è la funzione che crea le tabelle nel DB al primo avvio
from service.db import init_db

# ogni Blueprint è un gruppo di route definite in un file separato
from routes.aziende     import aziende_bp
from routes.referenti   import referenti_bp
from routes.candidature import candidature_bp
from routes.dashboard   import dashboard_bp


# Flask(__name__) crea l'applicazione.
# __name__ è il nome del modulo corrente: Flask lo usa per trovare
# la cartella templates/ e static/ in modo automatico.
app = Flask(__name__)

# secret_key è una password interna usata da Flask per firmare i cookie
# di sessione (necessaria per i messaggi flash).
# In produzione andrebbe una stringa lunga e casuale; in locale va bene così.
app.secret_key = 'careerflow-local'

# Crea le tabelle nel DB leggendo schema_db.sql.
# Usa CREATE TABLE IF NOT EXISTS e INSERT OR IGNORE, quindi
# se il DB esiste già non sovrascrive nulla.
init_db()

# register_blueprint "monta" i gruppi di route sull'app principale.
# Senza questa riga le route definite in quel file non sarebbero raggiungibili.
app.register_blueprint(aziende_bp)
app.register_blueprint(referenti_bp)
app.register_blueprint(candidature_bp)
app.register_blueprint(dashboard_bp)


# Questa è la route principale: quando l'utente va su http://127.0.0.1:5000/
# viene reindirizzato automaticamente alla dashboard.
# @app.route('/') significa "esegui questa funzione quando il browser chiede la pagina /"
@app.route('/')
def index():
    # url_for('dashboard.index') genera l'URL /dashboard/
    # senza doverlo scrivere a mano (e senza rischiare errori se l'URL cambia)
    return redirect(url_for('dashboard.index'))


# Questo blocco viene eseguito solo se avvii il file direttamente con:
#   python app.py
# Se invece usi "flask run", questo blocco viene ignorato.
# debug=True: ricarica automaticamente l'app quando salvi un file,
#             e mostra errori dettagliati nel browser.
if __name__ == '__main__':
    app.run(debug=True)