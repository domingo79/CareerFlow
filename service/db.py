import sqlite3
import os
from contextlib import contextmanager

# os.path.abspath garantisce un percorso assoluto e fisso,
# indipendente da dove si avvia lo script
DB_PATH    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'hub_candidature.db'))
SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'schema_db.sql'))


def get_db():
    """Apre e restituisce una connessione al database."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def apri_db():
    """Apre la connessione e la chiude SEMPRE alla fine, anche se c'è un errore.

    Uso nelle route:
        with apri_db() as db:
            db.execute(...)
            return render_template(...)   <- db.close() viene chiamato in automatico
    """
    conn = get_db()
    try:
        yield conn       # qui viene eseguito il codice dentro il blocco 'with'
    finally:
        conn.close()     # questo viene eseguito SEMPRE, succeda quel che succeda


def init_db():
    """Crea le tabelle e inserisce i dati seed se non esistono già."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with apri_db() as conn:
        with open(SCHEMA_PATH, encoding='utf-8') as f:
            conn.executescript(f.read())
