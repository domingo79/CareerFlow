import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "hub_candidature.db"

# Valori ammessi per lo stato
STATI_VALIDI = ("inviata", "ricevuta", "pending", "sollecito", "rifiutata")
TIPI_CANDIDATURA = ("semplice", "portale")

# ----------------------------------------------
# SCHEMA SQL
# ----------------------------------------------

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS aziende (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nome     TEXT    NOT NULL,
    citta    TEXT,
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
    nessun_feedback      INTEGER DEFAULT 0,
    data_invio           TEXT,
    data_ultima_modifica TEXT,
    note                 TEXT
);
"""

# ----------------------------------------------
# FUNZIONI HELPER
# ----------------------------------------------


def _conn() -> sqlite3.Connection:
    """Apre una connessione con foreign keys attive e row_factory."""
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    con.row_factory = sqlite3.Row
    return con


def _oggi() -> str:
    """Restituisce la data odierna in formato ISO (YYYY-MM-DD)."""
    return date.today().isoformat()


def _giorni_lavorativi(data_iso: str) -> int:
    """
    Calcola i giorni lavorativi trascorsi da data_iso a oggi.
    Esclude sabato (5) e domenica (6).
    """
    try:
        data_target = date.fromisoformat(data_iso)
    except (ValueError, TypeError):
        return 0

    oggi = date.today()
    if data_target == oggi:
        return 0

    # Iteriamo dal giorno successivo a oggi verso data_target
    passo = 1 if data_target > oggi else -1
    giorni = 0
    corrente = oggi

    while corrente != data_target:
        corrente += timedelta(days=passo)
        if corrente.weekday() < 5:   # 0–4 = lun–ven
            giorni += passo

    return giorni


# ----------------------------------------------
# Inizializzazione DB
# ----------------------------------------------


def init_db() -> None:
    """Crea le tabelle se non esistono già."""
    with _conn() as con:
        con.executescript(SCHEMA)


# ==============================================================================
# AZIENDE
# ==============================================================================

class AziendeManager:

    @staticmethod
    def create(
        nome: str,
        citta: str = "",
        sito_web: str = "",
        username: str = "",
        password: str = "",
        note: str = "",
    ) -> int:
        """Inserisce una nuova azienda e restituisce il suo id."""
        with _conn() as con:
            cur = con.execute(
                "INSERT INTO aziende (nome, citta, sito_web, username, password, note) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (nome, citta, sito_web, username, password, note),
            )
            return cur.lastrowid

    @staticmethod
    def read_all() -> list[sqlite3.Row]:
        """Restituisce tutte le aziende ordinate per nome."""
        with _conn() as con:
            return con.execute(
                "SELECT * FROM aziende ORDER BY nome"
            ).fetchall()

    @staticmethod
    def read_by_id(id_azienda: int) -> sqlite3.Row | None:
        """Restituisce una singola azienda per id, o None se non esiste."""
        with _conn() as con:
            return con.execute(
                "SELECT * FROM aziende WHERE id = ?", (id_azienda,)
            ).fetchone()

    @staticmethod
    def update(
        id_azienda: int,
        nome: str,
        citta: str = "",
        sito_web: str = "",
        username: str = "",
        password: str = "",
        note: str = "",
    ) -> None:
        """Aggiorna i dati di un'azienda esistente."""
        with _conn() as con:
            con.execute(
                "UPDATE aziende SET nome=?, citta=?, sito_web=?, username=?, password=?, note=? "
                "WHERE id=?",
                (nome, citta, sito_web, username, password, note, id_azienda),
            )


# ==============================================================================
# CONTATTI
# ==============================================================================

class ContattiManager:

    @staticmethod
    def create(
        id_azienda: int,
        nome: str = "",
        ruolo: str = "",
        linkedin_url: str = "",
        email: str = "",
        note: str = "",
    ) -> int:
        """Inserisce un nuovo contatto e restituisce il suo id."""
        with _conn() as con:
            cur = con.execute(
                "INSERT INTO contatti (id_azienda, nome, ruolo, linkedin_url, email, note) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (id_azienda, nome, ruolo, linkedin_url, email, note),
            )
            return cur.lastrowid

    @staticmethod
    def read_all() -> list[sqlite3.Row]:
        """Restituisce tutti i contatti con il nome dell'azienda associata."""
        with _conn() as con:
            return con.execute(
                "SELECT c.*, a.nome AS nome_azienda "
                "FROM contatti c JOIN aziende a ON c.id_azienda = a.id "
                "ORDER BY c.nome"
            ).fetchall()

    @staticmethod
    def read_by_id(id_contatto: int) -> sqlite3.Row | None:
        """Restituisce un singolo contatto per id."""
        with _conn() as con:
            return con.execute(
                "SELECT * FROM contatti WHERE id = ?", (id_contatto,)
            ).fetchone()

    @staticmethod
    def read_by_azienda(id_azienda: int) -> list[sqlite3.Row]:
        """Restituisce tutti i contatti di una specifica azienda."""
        with _conn() as con:
            return con.execute(
                "SELECT * FROM contatti WHERE id_azienda = ? ORDER BY nome",
                (id_azienda,),
            ).fetchall()

    @staticmethod
    def update(
        id_contatto: int,
        nome: str = "",
        ruolo: str = "",
        linkedin_url: str = "",
        email: str = "",
        note: str = "",
    ) -> None:
        """Aggiorna i dati di un contatto esistente."""
        with _conn() as con:
            con.execute(
                "UPDATE contatti SET nome=?, ruolo=?, linkedin_url=?, email=?, note=? "
                "WHERE id=?",
                (nome, ruolo, linkedin_url, email, note, id_contatto),
            )


# ==============================================================================
# CANDIDATURE
# ==============================================================================

class CandidatureManager:
    """
    Gestisce il CRUD delle candidature e le transizioni di stato automatiche.
    """

    @staticmethod
    def create(
        id_azienda: int,
        posizione: str,
        tipo_candidatura: str,
        versione_curriculum: str = "",
        stato: str = "inviata",
        nessun_feedback: bool = False,
        data_invio: str = "",
        id_contatto: int | None = None,
        note: str = "",
    ) -> int:
        """Inserisce una nuova candidatura e restituisce il suo id."""
        if tipo_candidatura not in TIPI_CANDIDATURA:
            raise ValueError(
                f"tipo_candidatura non valido: {tipo_candidatura!r}")
        if stato not in STATI_VALIDI:
            raise ValueError(f"stato non valido: {stato!r}")

        oggi = _oggi()
        with _conn() as con:
            cur = con.execute(
                "INSERT INTO candidature "
                "(id_azienda, id_contatto, posizione, tipo_candidatura, "
                " versione_curriculum, stato, nessun_feedback, "
                " data_invio, data_ultima_modifica, note) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    id_azienda, id_contatto, posizione, tipo_candidatura,
                    versione_curriculum, stato, int(nessun_feedback),
                    data_invio or oggi, oggi, note,
                ),
            )
            return cur.lastrowid

    @staticmethod
    def read_all() -> list[sqlite3.Row]:
        """Restituisce tutte le candidature con nome azienda e contatto."""
        with _conn() as con:
            return con.execute(
                """
                SELECT c.*,
                       a.nome  AS nome_azienda,
                       co.nome AS nome_contatto,
                       co.linkedin_url
                FROM   candidature c
                JOIN   aziende  a  ON c.id_azienda  = a.id
                LEFT JOIN contatti co ON c.id_contatto = co.id
                ORDER  BY c.data_invio DESC
                """
            ).fetchall()

    @staticmethod
    def read_by_id(id_cand: int) -> sqlite3.Row | None:
        """Restituisce una singola candidatura per id."""
        with _conn() as con:
            return con.execute(
                """
                SELECT c.*,
                       a.nome  AS nome_azienda,
                       co.nome AS nome_contatto,
                       co.linkedin_url
                FROM   candidature c
                JOIN   aziende  a  ON c.id_azienda  = a.id
                LEFT JOIN contatti co ON c.id_contatto = co.id
                WHERE  c.id = ?
                """,
                (id_cand,),
            ).fetchone()

    @staticmethod
    def update(
        id_cand: int,
        posizione: str,
        tipo_candidatura: str,
        versione_curriculum: str,
        stato: str,
        nessun_feedback: bool,
        data_invio: str,
        id_contatto: int | None,
        note: str,
    ) -> None:
        """Aggiorna tutti i campi di una candidatura esistente."""
        if tipo_candidatura not in TIPI_CANDIDATURA:
            raise ValueError(
                f"tipo_candidatura non valido: {tipo_candidatura!r}")
        if stato not in STATI_VALIDI:
            raise ValueError(f"stato non valido: {stato!r}")

        with _conn() as con:
            con.execute(
                "UPDATE candidature "
                "SET posizione=?, tipo_candidatura=?, versione_curriculum=?, "
                "    stato=?, nessun_feedback=?, data_invio=?, "
                "    id_contatto=?, note=?, data_ultima_modifica=? "
                "WHERE id=?",
                (
                    posizione, tipo_candidatura, versione_curriculum,
                    stato, int(nessun_feedback), data_invio,
                    id_contatto, note, _oggi(), id_cand,
                ),
            )

    # ------------------------------------------------------------------
    # GESTIONE STATI
    # ------------------------------------------------------------------

    @staticmethod
    def update_stato(id_cand: int, nuovo_stato: str) -> None:
        """
        Cambia lo stato di una singola candidatura e aggiorna data_ultima_modifica.
        """
        if nuovo_stato not in STATI_VALIDI:
            raise ValueError(f"stato non valido: {nuovo_stato!r}")

        with _conn() as con:
            con.execute(
                "UPDATE candidature SET stato=?, data_ultima_modifica=? WHERE id=?",
                (nuovo_stato, _oggi(), id_cand),
            )

    @staticmethod
    def _aggiorna_stati_batch(ids: list[int], nuovo_stato: str) -> int:
        """
        Aggiorna lo stato di una lista di candidature e restituisce il numero di righe aggiornate.
        """
        if not ids:
            return 0
        if nuovo_stato not in STATI_VALIDI:
            raise ValueError(f"stato non valido: {nuovo_stato!r}")

        oggi = _oggi()
        with _conn() as con:
            placeholders = ",".join("?" * len(ids))
            cur = con.execute(
                f"UPDATE candidature SET stato=?, data_ultima_modifica=? "
                f"WHERE id IN ({placeholders})",
                [nuovo_stato, oggi, *ids],
            )
            return cur.rowcount

    @staticmethod
    def _set_nessun_feedback_batch(ids: list[int]) -> None:
        """
        Imposta nessun_feedback=1 per una lista di candidature.
        Usato quando passiamo da 'inviata' → 'sollecito' senza aver ricevuto risposta.
        """
        if not ids:
            return
        with _conn() as con:
            placeholders = ",".join("?" * len(ids))
            con.execute(
                f"UPDATE candidature SET nessun_feedback=1 WHERE id IN ({placeholders})",
                ids,
            )

    # ------------------------------------------------------------------
    # GESTIONE STATI — FILTRI
    # ------------------------------------------------------------------

    @staticmethod
    def _filtra_per_transizione(stato: str, soglia_giorni: int) -> list[sqlite3.Row]:
        """
        Restituisce le candidature che si trovano in `stato`
        e hanno data_ultima_modifica >= soglia_giorni lavorativi fa.
        """
        tutte = CandidatureManager.read_all()
        return [
            r for r in tutte
            if r["stato"] == stato
            and _giorni_lavorativi(r["data_ultima_modifica"]) >= soglia_giorni
        ]

    # ------------------------------------------------------------------
    # GESTIONE STATI — SPECIFICI
    # ------------------------------------------------------------------

    @staticmethod
    def avanza_ricevuta_a_pending(soglia_giorni: int = 2) -> int:
        """
        Transizione: ricevuta → pending
        Candidature con stato 'ricevuta' ferme da almeno `soglia_giorni`
        giorni lavorativi vengono spostate a 'pending'.
        Restituisce il numero di candidature aggiornate.
        """
        da_aggiornare = CandidatureManager._filtra_per_transizione(
            stato="ricevuta",
            soglia_giorni=soglia_giorni,
        )
        ids = [r["id"] for r in da_aggiornare]
        return CandidatureManager._aggiorna_stati_batch(ids, "pending")

    @staticmethod
    def avanza_pending_a_sollecito(soglia_giorni: int = 8) -> int:
        """
        Transizione: pending → sollecito
        Candidature con stato 'pending' ferme da almeno `soglia_giorni`
        giorni lavorativi vengono spostate a 'sollecito'.
        Restituisce il numero di candidature aggiornate.
        """
        da_aggiornare = CandidatureManager._filtra_per_transizione(
            stato="pending",
            soglia_giorni=soglia_giorni,
        )
        ids = [r["id"] for r in da_aggiornare]
        return CandidatureManager._aggiorna_stati_batch(ids, "sollecito")

    @staticmethod
    def avanza_inviata_a_sollecito(soglia_giorni: int = 3) -> int:
        """
        Transizione: inviata → sollecito (flusso senza risposta)
        Candidature rimaste in stato 'inviata' per almeno `soglia_giorni`
        giorni lavorativi senza feedback vengono:
          1. contrassegnate con nessun_feedback=1
          2. spostate in stato 'sollecito'
        Il flag nessun_feedback serve per adottare un tono diverso nel
        messaggio di sollecito, dato che non abbiamo certezza che il CV
        sia stato ricevuto.
        Restituisce il numero di candidature aggiornate.
        """
        da_aggiornare = CandidatureManager._filtra_per_transizione(
            stato="inviata",
            soglia_giorni=soglia_giorni,
        )
        ids = [r["id"] for r in da_aggiornare]

        # Prima marchiamo il flag, poi cambiamo lo stato
        CandidatureManager._set_nessun_feedback_batch(ids)
        return CandidatureManager._aggiorna_stati_batch(ids, "sollecito")

    # ------------------------------------------------------------------
    # ORCHESTRATORE — unico punto da chiamare da Streamlit / scheduler
    # ------------------------------------------------------------------

    @staticmethod
    def avanza_stati() -> dict[str, int]:
        """
        Esegue tutte le transizioni automatiche in sequenza.

        Restituisce un dizionario con il numero di candidature aggiornate
        per ogni transizione.

        Esempio di ritorno:
            {
                "ricevuta_a_pending"   :   2,
                "pending_a_sollecito"  :   1,
                "inviata_a_sollecito"  :   3,
            }
        """
        return {
            "ricevuta_a_pending":  CandidatureManager.avanza_ricevuta_a_pending(),
            "pending_a_sollecito": CandidatureManager.avanza_pending_a_sollecito(),
            "inviata_a_sollecito": CandidatureManager.avanza_inviata_a_sollecito(),
        }


# Inizializza DB
init_db()


# azienda = AziendeManager.create('VASS', 'Roma')

# contatto = ContattiManager.create(
#     azienda, 'Oriol Grasa Sánchez', 'Hiring Manager')

# candidatura = CandidatureManager.create(azienda, 'Junior Salesforce Administrator & Developer ',
#                                         'semplice', 'CV_DomenicoSanto_eng_ita_2026', id_contatto=contatto)

# print(f"ID dell\'azienza inserita è: {azienda}")
# print(f"ID dell'ultima candidatura è: {candidatura}")

# CandidatureManager.update_stato(7, 'ricevuta')
