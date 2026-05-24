CREATE TABLE IF NOT EXISTS aziende (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome                TEXT NOT NULL,
    linkedin            TEXT,
    sito_web            TEXT,
    username            TEXT,
    note_accesso        TEXT,
    citta               TEXT,
    paese               TEXT,
    dimensione_azienda  TEXT, -- startup | PMI | corporate
    note                TEXT,
    data_creazione      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modifica       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attiva INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
);

CREATE TABLE IF NOT EXISTS contatti (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    azienda_id      INTEGER NOT NULL,
    nome            TEXT NOT NULL,
    cognome         TEXT,
    email           TEXT UNIQUE,
    telefono        TEXT,
    ruolo           TEXT,
    linkedin        TEXT,
    note            TEXT,
    data_creazione  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modifica   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attiva          INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1)), -- puo cambiare azienda
    FOREIGN KEY (azienda_id) REFERENCES aziende(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS stati_candidatura (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    colore TEXT,
    ordine INTEGER UNIQUE,
    attiva INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS modalita_lavoro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS candidature (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    azienda_id              INTEGER NOT NULL,
    contatto_id             INTEGER, -- possiamo candidarci senza HR noto
    posizione               TEXT NOT NULL,
    stato_candidatura_id    INTEGER NOT NULL, 
    modalita_lavoro_id      INTEGER, 
    versione_cv             TEXT,
    data_candidatura        DATE,
    data_colloquio          DATE,
    feedback                TEXT,
    url_offerta             TEXT,
    note                    TEXT,
    data_creazione          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modifica           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attiva                  INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1)),

    FOREIGN KEY (stato_candidatura_id) REFERENCES stati_candidatura(id),
    FOREIGN KEY (modalita_lavoro_id) REFERENCES modalita_lavoro(id),
    FOREIGN KEY (azienda_id) REFERENCES aziende(id) ON DELETE RESTRICT,
    FOREIGN KEY (contatto_id) REFERENCES contatti(id) ON DELETE SET NULL -- può andare via dall'azienda
);


-- =================================================================
-- ===     Trigger per aggiornare le date di modifica            ===
-- =================================================================
CREATE TRIGGER IF NOT EXISTS trg_aziende_data_modifica
AFTER UPDATE ON aziende
FOR EACH ROW
WHEN OLD.data_modifica = NEW.data_modifica
BEGIN
    UPDATE aziende
    SET data_modifica = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_contatti_data_modifica
AFTER UPDATE ON contatti
FOR EACH ROW
WHEN OLD.data_modifica = NEW.data_modifica
BEGIN
    UPDATE contatti
    SET data_modifica = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_candidature_data_modifica
AFTER UPDATE ON candidature
FOR EACH ROW
WHEN OLD.data_modifica = NEW.data_modifica
BEGIN
    UPDATE candidature
    SET data_modifica = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;