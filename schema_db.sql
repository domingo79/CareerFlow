CREATE TABLE IF NOT EXISTS aziende (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome                    TEXT NOT NULL,
    linkedin                TEXT,
    sito_web                TEXT,
    username                TEXT,
    note_accesso            TEXT,
    citta                   TEXT,
    paese                   TEXT,
    dimensione_azienda_id   INTEGER, 
    note                    TEXT,
    data_creazione          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modifica           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attiva                  INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1)),

    FOREIGN KEY (dimensione_azienda_id) REFERENCES dimensione_azienda(id)
);

CREATE TABLE IF NOT EXISTS referenti (
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
    attiva          INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1)),

    FOREIGN KEY (azienda_id) REFERENCES aziende(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS stati_candidatura (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT NOT NULL UNIQUE,
    colore          TEXT,
    ordine          INTEGER UNIQUE,
    tipo            TEXT NOT NULL DEFAULT 'neutro' CHECK(tipo IN ('positivo', 'negativo', 'neutro')),
    is_terminale    INTEGER NOT NULL DEFAULT 0 CHECK(is_terminale IN (0,1)),
    attiva          INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
);

CREATE TABLE IF NOT EXISTS modalita_lavoro (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome    TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dimensione_azienda (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome    TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS candidature (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    azienda_id              INTEGER NOT NULL,
    referente_id            INTEGER,
    posizione               TEXT NOT NULL,
    stato_candidatura_id    INTEGER NOT NULL,
    modalita_lavoro_id      INTEGER,
    versione_cv             TEXT,
    data_candidatura        DATE,
    data_risposta           DATE,
    data_colloquio          DATE,
    feedback                TEXT,
    url_offerta             TEXT,
    note                    TEXT,
    data_creazione          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modifica           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attiva                  INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1)),

    FOREIGN KEY (stato_candidatura_id) REFERENCES stati_candidatura(id),
    FOREIGN KEY (modalita_lavoro_id)   REFERENCES modalita_lavoro(id),
    FOREIGN KEY (azienda_id)           REFERENCES aziende(id) ON DELETE RESTRICT,
    FOREIGN KEY (referente_id)         REFERENCES referenti(id) ON DELETE SET NULL
);


-- ======================================================================
-- ===  Seed: dimensione_azienda  stati_candidatura  modalita_lavoro  ===
-- ======================================================================

INSERT OR IGNORE INTO dimensione_azienda (nome) VALUES
    ('Startup'),
    ('PMI'),
    ('Corporate');

INSERT OR IGNORE INTO stati_candidatura (nome, colore, ordine, tipo, is_terminale) VALUES
    ('INVIATA',              '#d5e8d4', 1,  'neutro',   0),
    ('FOLLOW-UP',            '#d5e8d4', 2,  'neutro',   0),
    ('RICEVUTA',             '#d5e8d4', 3,  'neutro',   0),
    ('IN VALUTAZIONE',       '#d5e8d4', 4,  'neutro',   0),
    ('SOLLECITO',            '#d5e8d4', 5,  'neutro',   0),
    ('IN ATTESA',            '#d5e8d4', 6,  'neutro',   0),
    ('COLLOQUIO',            '#d5e8d4', 7,  'positivo', 0),
    ('OFFERTA',              '#fff2cc', 8,  'positivo', 0),
    ('ACCETTATA',            '#d5e8d4', 9,  'positivo', 1),
    ('DECLINATA',            '#f5f5f5', 10, 'neutro',   1),
    ('RIFIUTATO CV',         '#f8cecc', 11, 'negativo', 1),
    ('RIFIUTATO COLLOQUIO',  '#f8cecc', 12, 'negativo', 1),
    ('GHOST',                '#f8cecc', 13, 'negativo', 1);

INSERT OR IGNORE INTO modalita_lavoro (nome) VALUES
    ('In sede'),
    ('Ibrido'),
    ('Remoto');

-- =================================================================
-- ===     Trigger per aggiornare le date di modifica            ===
-- =================================================================

CREATE TRIGGER IF NOT EXISTS trg_aziende_data_modifica
AFTER UPDATE ON aziende
FOR EACH ROW
BEGIN
    UPDATE aziende SET data_modifica = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_referenti_data_modifica
AFTER UPDATE ON referenti
FOR EACH ROW
BEGIN
    UPDATE referenti SET data_modifica = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_candidature_data_modifica
AFTER UPDATE ON candidature
FOR EACH ROW
BEGIN
    UPDATE candidature SET data_modifica = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;