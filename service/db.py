import sqlite3
import os
from contextlib import contextmanager  # gestore di contesto

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..',
                 'instance', 'hub_candidature.db')
)
SCHEMA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'schema_db.sql')
)


def get_db():
    """Apre e restituisce una connessione al database."""

    # timeout=10: se un'altra connessione sta scrivendo, aspetta fino a 10 secondi
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    # foreign_keys = ON: attiva i controlli sulle chiavi esterne.
    conn.execute("PRAGMA foreign_keys = ON")
    # Permette letture e scritture simultanee senza bloccarsi.
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


# @contextmanager serve per garantire che la connessione venga SEMPRE chiusa,
# anche se il codice dentro il 'with' solleva un'eccezione.
@contextmanager
def apri_db():
    """Apre la connessione e la chiude SEMPRE alla fine, anche in caso di errore."""
    conn = get_db()
    try:
        # 'yield conn' sospende questa funzione e consegna la connessione
        # al blocco 'with' nel codice chiamante.
        # In pratica "consegna conn a chi la usa, poi aspetta qui finché il blocco with non finisce, poi continua con finally".
        yield conn
    finally:
        conn.close()


def init_db():
    """ Se il DB esiste già, non sovrascrive nulla. """
    # crea la cartella instance/ se non esiste ancora
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with apri_db() as conn:
        with open(SCHEMA_PATH, encoding='utf-8') as f:
            conn.executescript(f.read())
