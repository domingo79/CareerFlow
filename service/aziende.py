import sqlite3
from service.db import get_connection

# ==============================================================================
# READ
# ==============================================================================


def get_all(solo_attive: bool = True) -> list:
    """Restituisce tutte le aziende `attive` ordinate per nome"""
    query = "SELECT * FROM aziende"
    if solo_attive:
        query += " WHERE attiva = 1"
    query += " ORDER BY nome COLLATE NOCASE"
    with get_connection() as conn:
        return conn.execute(query).fetchall()


def get_by_id(azienda_id: int) -> sqlite3.Row | None:
    """Restituisce una singola azienda per id."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM aziende WHERE id = ?", (azienda_id,)
        ).fetchone()

# ==============================================================================
# CREATE
# ==============================================================================


def create(
    nome: str,
    linkedin: str = None,
    sito_web: str = None,
    username: str = None,
    note_accesso: str = None,
    citta: str = None,
    paese: str = None,
    dimensione_azienda: str = None,
    note: str = None
) -> int:
    """ Crea una nuova aziensa e restituisce l'ID """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO aziende(nome, linkedin, sito_web, username, note_accesso,
                citta, paese, dimensione_azienda, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, linkedin, sito_web, username, note_accesso,
                  citta, paese, dimensione_azienda, note),
        )
        conn.commit()
        return cursor.lastrowid

# ==============================================================================
# UPDATE
# ==============================================================================


def update(
    azienda_id: int,
    nome: str,
    linkedin: str = None,
    sito_web: str = None,
    username: str = None,
    note_accesso: str = None,
    citta: str = None,
    paese: str = None,
    dimensione_azienda: str = None,
    note: str = None,
) -> bool:
    """Aggiorna un'azienda. Restituisce True se la riga esiste."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE aziende SET
                nome = ?, linkedin = ?, sito_web = ?,
                username = ?, note_accesso = ?,
                citta = ?, paese = ?, dimensione_azienda = ?, note = ?
            WHERE id = ?
            """,
            (nome, linkedin, sito_web, username, note_accesso,
             citta, paese, dimensione_azienda, note, azienda_id),
        )
        conn.commit()
        return cursor.rowcount > 0


# ==============================================================================
# SOFT DELETE / RESTORE
# ==============================================================================

def set_attiva(azienda_id: int, attiva: bool) -> bool:
    """Soft-delete (attiva=False) o ripristino (attiva=True)."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE aziende SET attiva = ? WHERE id = ?",
            (1 if attiva else 0, azienda_id),
        )
        conn.commit()
        return cursor.rowcount > 0
