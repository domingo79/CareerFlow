import sqlite3
from pathlib import Path

# ==============================================================================
# Percordo al db nella root del progetto
# ==============================================================================
ROOT_DIR = Path(__file__).parent.parent  # da service/ risale alla root
instance_dir = ROOT_DIR / "instance"
schema_path = ROOT_DIR / "schema_db.sql"
db_path = instance_dir / "hub_candidature.db"


def get_connection() -> sqlite3.Connection:
    """
    Restituisce una connessione al database con row_factory impostata e controllo
    delle chiavi esterne.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """
    Inizializza il db seguendo lo schema SQL e il seed dei dati di  lookup
    """
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    with get_connection() as conn:
        conn.executescript(schema_sql)
        _seed_tables(conn)
        conn.commit()

# ==============================================================================
# Seed per le tabelle stati_candidatura e modalita_lavoro
# ==============================================================================


def _seed_tables(conn: sqlite3.Connection) -> None:
    """Popola le tabelle di lookup se sono vuote."""

    # Stati candidatura
    count = conn.execute(
        "SELECT COUNT(*) FROM stati_candidatura").fetchone()[0]
    if count == 0:
        stati = [
            ("Inviata",     "#3B82F6", 1, 1),   # blu
            ("Confermata",  "#8B5CF6", 2, 1),   # viola
            ("Colloquio",   "#F59E0B", 3, 1),   # giallo
            ("Proposta",    "#10B981", 4, 1),   # verde
            ("Rifiutata",   "#EF4444", 5, 1),   # rosso
            ("Ritirata",    "#818489", 6, 1),   # grigio
        ]
        conn.executemany(
            "INSERT INTO stati_candidatura(nome,colore, ordine,attiva) VALUES(?,?,?,?)",
            stati
        )

    # Modalita Lavoro
    count = conn.execute("SELECT COUNT(*) FROM modalita_lavoro").fetchone()[0]
    if count == 0:
        modalita = [
            ("In presenza",),
            ("Ibrido",),
            ("Da remoto",),
        ]
        conn.executemany(
            "INSERT INTO modalita_lavoro (nome) VALUES (?)",
            modalita
        )
