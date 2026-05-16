import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "hub_candidature.db"
STATI_VALIDI = ("inviata", "ricevuta", "pending", "rifiutata, sollecito")
TIPI_CANDIDATURA = ("semplice", "portale")

# Flusso(Con Risposta):
# Al momento dell'invio del CV, la candidatura assume lo stato Inviata.
# Se l'azienda risponde con una conferma di ricezione, lo stato avanza a Ricevuta.
# Trascorsi 2 giorni lavorativi in questo stato, la candidatura passa automaticamente
# a Pending. Se non si registrano ulteriori aggiornamenti dopo altri 8 giorni lavorativi,
# il sistema segnala la necessità di inviare un Sollecito.

# Flusso(Senza Risposta):
# Se la candidatura rimane nello stato Inviata e non si riceve alcun riscontro
# o conferma automatica entro 3 giornni lavorativi, la pratica viene spostata
# nello stato collecito e verrà valorizzato un campo di controllo per tenere
# traccia del fatto che quell'azienda non ha sistemi di tracciamento automatico
# e in fase di sollecito useremo un tono leggermente diverso, dato che non
# abbiamo la certezza matematica che abbiano ricevuto il nostro cv

# ----------------------------------------------
# SCHEMA SQL
# ----------------------------------------------

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS aziende (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nome     TEXT    NOT NULL,
    sito_web TEXT,
    username TEXT,
    password TEXT,
    note     TEXT
);

CREATE TABLE IF NOT EXISTS contatti (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    id_azienda    INTEGER NOT NULL REFERENCES aziende(id),
    nome          TEXT,
    ruolo         TEXT,
    linkedin_url  TEXT,
    email         TEXT,
    note          TEXT
);

CREATE TABLE IF NOT EXISTS candidature (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_azienda           INTEGER NOT NULL REFERENCES aziende(id),
    id_contatto          INTEGER REFERENCES contatti(id),
    posizione            TEXT,
    tipo_candidatura     TEXT,
    versione_curriculum  TEXT,
    stato                TEXT    DEFAULT 'inviata',
    nessun_feedback      TEXT    DEFAULT False,
    data_invio           TEXT,
    data_ultima_modifica TEXT,
    note                 TEXT
);
"""

# ----------------------------------------------
# FUNZIONI HELPER
# ----------------------------------------------


def _conn():
    """Apre una connessione con foreign keys attive e row_factory"""
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    con.row_factory = sqlite3.Row
    return con


def _oggi() -> str:
    return date.today().isoformat()

# TODO Creare una funzione che mi calcola i giorni lavorativi escludendo sabato e domenica


def _giorni_lavorativi(data_iso: str) -> int:
    """Calcola i giorni lavorativi trascorsi da data_iso a oggi (esclude sab/dom)."""
    try:
        data_target = date.fromisoformat(data_iso)
    except (ValueError, TypeError):
        return 0
    oggi = date.today()

    if data_target == oggi:
        return 0

    # determiniamo la direzione (futuro o passato)
    passo = 1 if data_target >= oggi else -1
    giorni_lavorativi = 0
    data_corrente = oggi

    # Iteriamo giorno per giorno fino a raggiungere la data target
    while data_corrente != data_target:
        data_corrente += timedelta(days=passo)

        # weekday() restituisce 0 per Lunedì ... 5 per Sabato, 6 per Domenica
        if data_corrente.weekday() < 5:
            giorni_lavorativi += passo

    return giorni_lavorativi


# ----------------------------------------------
# Inizializzazione DB
# ----------------------------------------------


def init_db() -> None:
    """Crea le tabelle se non esistono."""
    with _conn() as con:
        con.executescript(SCHEMA)


# ----------------------------------------------
# AZIENDE
# ----------------------------------------------
class AziendeManager:

    @staticmethod
    def create(nome: str,  sito_web: str = "", username: str = "", password: str = "", note: str = "") -> int:
        with _conn() as con:
            cur = con.execute(
                "INSERT INTO aziende (nome, sito_web, username, password, note) "
                "VALUES (?, ?, ?, ?, ?)",
                (nome, sito_web, username, password, note),
            )
            return cur.lastrowid

    @staticmethod
    def real_all() -> list[sqlite3.Row]:
        with _conn() as con:
            return con.execute("SELECT * FROM aziende ORDER BY nome").fetchall()

    @staticmethod
    def real_by_id(id_azienda: int) -> sqlite3.Row | None:
        with _conn() as con:
            return con.execute(
                "SELECT * FROM aziende WHERE id = ?", (id_azienda,)
            ).fetchone()

    @staticmethod
    def update(id_azienda: int, nome: str, sito_web: str = "", username: str = "", password: str = "", note: str = "") -> None:
        with _conn() as con:
            con.execute(
                "UPDATE aziende SET nome=?, sito_web=?, username=?, password=?, note=? "
                "WHERE id=?",
                (nome, sito_web, username, password, note, id_azienda),
            )

# ----------------------------------------------
# CONTATTI
# ----------------------------------------------


class ContattiManager:

    @staticmethod
    def create(id_azienda: int, nome: str = "", ruolo: str = "",
               linkedin_url: str = "", email: str = "", note: str = "") -> int:
        with _conn() as con:
            cur = con.execute(
                "INSERT INTO contatti (id_azienda, nome, ruolo, linkedin_url, email, note) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (id_azienda, nome, ruolo, linkedin_url, email, note),
            )
            return cur.lastrowid

    @staticmethod
    def read_by_azienda(id_azienda: int) -> list[sqlite3.Row]:
        with _conn() as con:
            return con.execute(
                "SELECT * FROM contatti WHERE id_azienda = ? ORDER BY nome",
                (id_azienda,),
            ).fetchall()

    @staticmethod
    def read_by_id(id_contatto: int) -> sqlite3.Row | None:
        with _conn() as con:
            return con.execute(
                "SELECT * FROM contatti WHERE id = ?", (id_contatto,)
            ).fetchone()

    @staticmethod
    def read_all() -> list[sqlite3.Row]:
        with _conn() as con:
            return con.execute(
                "SELECT c.*, a.nome AS nome_azienda "
                "FROM contatti c JOIN aziende a ON c.id_azienda = a.id "
                "ORDER BY c.nome"
            ).fetchall()

    @staticmethod
    def update(id_contatto: int, nome: str = "", ruolo: str = "",
               linkedin_url: str = "", email: str = "", note: str = "") -> None:
        with _conn() as con:
            con.execute(
                "UPDATE contatti SET nome=?, ruolo=?, linkedin_url=?, email=?, note=? "
                "WHERE id=?",
                (nome, ruolo, linkedin_url, email, note, id_contatto),
            )


# ----------------------------------------------
# CANDIDATUREManager
# ----------------------------------------------
class CandicatureManager:

    @staticmethod
    def create(id_azienda: int, posizione: str, tipo_candidatura: str,
               versione_curriculum: str = "", stato: str = "inviata", nessun_feedback: bool = False,
               data_invio: str = "", id_contatto: int | None = None,
               note: str = "") -> int:
        # controllo il tipo di candidatura e stati altrimento sollevo eccezione
        if tipo_candidatura not in TIPI_CANDIDATURA:
            raise ValueError(
                f"Tipo di candidatura non valida: {tipo_candidatura}")
        if stato not in STATI_VALIDI:
            raise ValueError(f"stato non valido: {stato}")
        oggi = _oggi()
        with _conn() as con:
            cur = con.execute(
                "INSERT INTO candidature "
                "(id_azienda, id_contatto, posizione, tipo_candidatura, "
                " versione_curriculum, stato, nessun_feedback, data_invio, data_ultima_modifica, note) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (id_azienda, id_contatto, posizione, tipo_candidatura,
                 versione_curriculum, stato, nessun_feedback, data_invio or oggi, oggi, note),
            )
            return cur.lastrowid

    @staticmethod
    def read_all() -> list[sqlite3.Row]:
        with _conn() as con:
            return con.execute(
                """
                SELECT c.*,
                       a.nome  AS nome_azienda,
                       co.nome AS nome_contatto,
                       co.linkedin_url
                FROM   candidature c
                JOIN   aziende a  ON c.id_azienda  = a.id
                LEFT JOIN contatti co ON c.id_contatto = co.id
                ORDER  BY c.data_invio DESC
                """
            ).fetchall()

    @staticmethod
    def read_by_id(id_cand: int) -> sqlite3.Row | None:
        with _conn() as con:
            return con.execute(
                """
                SELECT c.*,
                       a.nome  AS nome_azienda,
                       co.nome AS nome_contatto,
                       co.linkedin_url
                FROM   candidature c
                JOIN   aziende a  ON c.id_azienda  = a.id
                LEFT JOIN contatti co ON c.id_contatto = co.id
                WHERE  c.id = ?
                """,
                (id_cand,),
            ).fetchone()

    @staticmethod
    def update(id_cand: int, posizione: str, tipo_candidatura: str,
               versione_curriculum: str, stato: str, nessun_feedback: bool, data_invio: str,
               id_contatto: int | None, note: str) -> None:
        if tipo_candidatura not in TIPI_CANDIDATURA:
            raise ValueError(
                f"tipo_candidatura non valido: {tipo_candidatura}")
        if stato not in STATI_VALIDI:
            raise ValueError(f"stato non valido: {stato}")
        with _conn() as con:
            con.execute(
                "UPDATE candidature SET posizione=?, tipo_candidatura=?, "
                "versione_curriculum=?, stato=?, nessun_feedback=?, data_invio=?, "
                "id_contatto=?, note=?, data_ultima_modifica=? WHERE id=?",
                (posizione, tipo_candidatura, versione_curriculum, stato, nessun_feedback,
                 data_invio, id_contatto, note, _oggi(), id_cand),
            )

    # Cambio stato
    @staticmethod
    def update_stato(id_cand: int, nuovo_stato: str) -> None:
        if nuovo_stato not in STATI_VALIDI:
            raise ValueError(f"stato non valido: {nuovo_stato}")
        with _conn() as con:
            con.execute(
                "UPDATE candidature SET stato=?, data_ultima_modifica=? WHERE id=?",
                (nuovo_stato, _oggi(), id_cand),
            )

    # TODO creare un metodo per cambiare lo stato da ricevuta a pending dopo 2 giorni lavorativi
    # TODO creare un metodo per sollecitare tutte le candidature con lo stato pending
