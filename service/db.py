# ============================================================
# service/db.py — gestione della connessione al database
# Questo file è l'unico punto dove si parla con SQLite.
# Tutti gli altri file importano da qui.
# ============================================================

import sqlite3                          # libreria standard Python per SQLite
import os                               # per costruire percorsi di file
from contextlib import contextmanager   # per creare il "gestore di contesto" apri_db


# os.path.abspath converte un percorso relativo in assoluto.
# __file__ è il percorso di questo file (service/db.py).
# os.path.dirname(__file__) → cartella "service/"
# '..' → saliamo di un livello → cartella principale del progetto
# Risultato finale: C:\...\CareerFlow\instance\hub_candidature.db
DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'instance', 'hub_candidature.db')
)

# Stesso ragionamento per lo schema SQL
SCHEMA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'schema_db.sql')
)


def get_db():
    """Apre e restituisce una connessione al database SQLite."""

    # sqlite3.connect apre (o crea) il file .db sul disco.
    # timeout=10: se un'altra connessione sta scrivendo, aspetta fino a 10 secondi
    # invece di fallire subito con "database is locked".
    conn = sqlite3.connect(DB_PATH, timeout=10)

    # row_factory = sqlite3.Row cambia come vengono restituiti i risultati delle query.
    # Senza: ogni riga è una tupla → riga[0], riga[1], ...
    # Con:   ogni riga è un oggetto → riga['nome'], riga['citta'], ...  (molto più leggibile)
    conn.row_factory = sqlite3.Row

    # PRAGMA sono istruzioni di configurazione di SQLite (non query standard SQL).
    # foreign_keys = ON: attiva i controlli sulle chiavi esterne.
    # Di default SQLite le ignora completamente (per compatibilità storica).
    conn.execute("PRAGMA foreign_keys = ON")

    # journal_mode = WAL (Write-Ahead Logging): modalità di scrittura più moderna.
    # Permette letture e scritture simultanee senza bloccarsi.
    # Risolve il classico errore "database is locked" durante il debug.
    conn.execute("PRAGMA journal_mode = WAL")

    return conn


# @contextmanager trasforma questa funzione in un "gestore di contesto",
# cioè qualcosa che si usa con la parola chiave 'with'.
# Serve per garantire che la connessione venga SEMPRE chiusa,
# anche se il codice dentro il 'with' solleva un'eccezione.
@contextmanager
def apri_db():
    """Apre la connessione e la chiude SEMPRE alla fine, anche in caso di errore.

    Utilizzo nelle route:
        with apri_db() as db:
            risultati = db.execute('SELECT ...').fetchall()
            return render_template(...)
        # qui db.close() viene chiamato in automatico
    """
    conn = get_db()
    try:
        # 'yield conn' sospende questa funzione e consegna la connessione
        # al blocco 'with' nel codice chiamante.
        # Tutto il codice dentro 'with apri_db() as db:' viene eseguito qui.
        yield conn
    finally:
        # 'finally' viene eseguito SEMPRE:
        # sia se il codice è andato bene, sia se ha sollevato un errore.
        # Questo è il motivo per cui usiamo apri_db() invece di get_db() direttamente.
        conn.close()


def init_db():
    """Crea le tabelle e inserisce i dati seed al primo avvio.

    Legge ed esegue il file schema_db.sql che contiene tutti i
    CREATE TABLE IF NOT EXISTS e INSERT OR IGNORE.
    Se il DB esiste già, non sovrascrive nulla.
    """
    # crea la cartella instance/ se non esiste ancora
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with apri_db() as conn:
        # apre lo schema SQL come file di testo e lo esegue tutto in una volta.
        # executescript esegue più istruzioni SQL separate da ";"
        with open(SCHEMA_PATH, encoding='utf-8') as f:
            conn.executescript(f.read())