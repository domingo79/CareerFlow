import datetime
import sqlite3


class Azienda:
    def __init__(self, nome, sito_web=None, note=None, id_azienda=None):
        self.id = id_azienda
        self.nome = nome
        self.sito_web = sito_web
        self.note = note


class Credenziali:
    def __init__(self, id_azienda, username, password):
        self.id_azienda = id_azienda
        self.username = username
        self.password = password


class Candidatura:
    def __init__(self, id_azienda, posizione, cv_usato, piattaforma="LinkedIn", id_cand=None):
        self.id = id_cand
        self.id_azienda = id_azienda
        self.posizione = posizione
        self.cv_usato = cv_usato
        self.piattaforma = piattaforma
        self.stato = "Inviata"
        self.data_invio = datetime.date.today()
        self.ultimo_aggiornamento = datetime.date.today()


class DatabaseManager:
    def __init__(self, db_name="careerflow.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.crea_struttura()

    def crea_struttura(self):
        cursor = self.conn.cursor()
        # Tabella Aziende
        cursor.execute('''CREATE TABLE IF NOT EXISTS aziende (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            sito_web TEXT
        )''')

        # Tabella Credenziali (Legata all'azienda)
        cursor.execute('''CREATE TABLE IF NOT EXISTS credenziali (
            azienda_id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            FOREIGN KEY(azienda_id) REFERENCES aziende(id)
        )''')

        # Tabella Candidature
        cursor.execute('''CREATE TABLE IF NOT EXISTS candidature (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            azienda_id INTEGER,
            posizione TEXT,
            data_invio DATE,
            stato TEXT,
            cv_usato TEXT,
            piattaforma TEXT,
            ultimo_aggiornamento DATE,
            FOREIGN KEY(azienda_id) REFERENCES aziende(id)
        )''')
        self.conn.commit()

    def aggiungi_candidatura_completa(self, azienda_nome, posizione, cv, piattaforma, user=None, pwd=None):
        """Metodo 'intelligente' che gestisce tutto il flusso"""
        cursor = self.conn.cursor()

        # 1. Controlla o inserisce l'azienda
        cursor.execute(
            "INSERT OR IGNORE INTO aziende (nome) VALUES (?)", (azienda_nome,))
        cursor.execute("SELECT id FROM aziende WHERE nome = ?",
                       (azienda_nome,))
        az_id = cursor.fetchone()[0]

        # 2. Se ci sono credenziali, le salva
        if user and pwd:
            cursor.execute(
                "INSERT OR REPLACE INTO credenziali VALUES (?, ?, ?)", (az_id, user, pwd))

        # 3. Crea la candidatura
        cursor.execute('''INSERT INTO candidature
            (azienda_id, posizione, data_invio, stato, cv_usato, piattaforma, ultimo_aggiornamento)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (az_id, posizione, datetime.date.today(), "Inviata", cv, piattaforma, datetime.date.today()))

        self.conn.commit()
