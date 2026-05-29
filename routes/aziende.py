# ============================================================
# routes/aziende.py — tutte le pagine relative alle aziende
# Operazioni disponibili: lista, nuova, modifica, elimina
# ============================================================

# Blueprint, render_template, request, redirect, url_for, flash
# sono strumenti di Flask importati uno per uno:
#   Blueprint        → raggruppa route dello stesso argomento in un file separato
#   render_template  → legge un file HTML dalla cartella templates/ e lo restituisce
#   request          → contiene i dati della richiesta HTTP (form, parametri URL, ecc.)
#   redirect         → dice al browser di andare a un'altra pagina
#   url_for          → genera l'URL di una route dal suo nome (es. 'aziende.lista' → '/aziende/')
#   flash            → aggiunge un messaggio temporaneo (successo/errore) visibile una sola volta
from flask import Blueprint, render_template, request, redirect, url_for, flash

from service.db import apri_db   # il nostro gestore di connessione al DB


# Blueprint('aziende', ..., url_prefix='/aziende') significa:
# - il nome di questo gruppo di route è 'aziende'
# - tutte le route definite qui inizieranno con /aziende/
aziende_bp = Blueprint('aziende', __name__, url_prefix='/aziende')


# ── LISTA ──────────────────────────────────────────────────
# URL: GET /aziende/
@aziende_bp.route('/')
def lista():
    with apri_db() as db:
        # SELECT con LEFT JOIN: prendiamo tutte le colonne di 'aziende' (a.*)
        # più il nome della dimensione dall'altra tabella (d.nome AS dimensione).
        # LEFT JOIN significa: includi l'azienda anche se non ha una dimensione associata.
        # WHERE a.attiva = 1: mostra solo le aziende non eliminate (soft delete).
        aziende = db.execute('''
            SELECT a.*, d.nome AS dimensione
            FROM aziende a
            LEFT JOIN dimensione_azienda d ON a.dimensione_azienda_id = d.id
            WHERE a.attiva = 1
            ORDER BY a.nome
        ''').fetchall()
        # fetchall() restituisce una lista con tutte le righe trovate.
        # Se non ci sono risultati, restituisce una lista vuota [].

    # render_template cerca il file in templates/aziende/lista.html
    # e passa la variabile 'aziende' al template HTML
    return render_template('aziende/lista.html', aziende=aziende)


# ── NUOVA AZIENDA ──────────────────────────────────────────
# URL: GET /aziende/nuova  → mostra il form vuoto
# URL: POST /aziende/nuova → riceve i dati del form e salva
# methods=['GET', 'POST'] dice a Flask che questa route accetta entrambi i metodi HTTP
@aziende_bp.route('/nuova', methods=['GET', 'POST'])
def nuova():
    with apri_db() as db:
        # carichiamo le dimensioni azienda per riempire il menu <select> nel form
        dimensioni = db.execute('SELECT * FROM dimensione_azienda ORDER BY id').fetchall()

        # request.method dice che tipo di richiesta è arrivata:
        # - 'GET'  → l'utente ha cliccato il link "Nuova azienda"
        # - 'POST' → l'utente ha compilato il form e premuto "Salva"
        if request.method == 'POST':

            # request.form è un dizionario con i valori del form HTML.
            # .get('nome', '') restituisce il valore del campo 'nome',
            # oppure '' se il campo non esiste (evita KeyError).
            # .strip() rimuove spazi all'inizio e alla fine.
            nome = request.form.get('nome', '').strip()

            # validazione: il nome è obbligatorio
            if not nome:
                # flash aggiunge un messaggio che apparirà nella pagina successiva.
                # 'danger' è la categoria Bootstrap (rosso = errore).
                flash('Il nome è obbligatorio.', 'danger')
                # torniamo al form con i dati già inseriti (dati=request.form)
                # così l'utente non deve riscrivere tutto
                return render_template('aziende/form.html', dimensioni=dimensioni, dati=request.form)

            # INSERT INTO salva una nuova riga nel DB.
            # I '?' sono segnaposto: SQLite li sostituisce con i valori nella tupla.
            # Usare i segnaposto invece di concatenare stringhe evita la SQL injection.
            db.execute('''
                INSERT INTO aziende
                    (nome, linkedin, sito_web, username, note_accesso, citta, paese, dimensione_azienda_id, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nome,
                # 'or None': se il campo è una stringa vuota '', salviamo NULL nel DB
                # (più corretto di salvare una stringa vuota)
                request.form.get('linkedin') or None,
                request.form.get('sito_web') or None,
                request.form.get('username') or None,
                request.form.get('note_accesso') or None,
                request.form.get('citta') or None,
                request.form.get('paese') or None,
                request.form.get('dimensione_azienda_id') or None,
                request.form.get('note') or None,
            ))
            # db.commit() rende permanenti le modifiche nel file .db.
            # Senza commit le modifiche esistono solo in memoria e vanno perse.
            db.commit()

            # flash con 'success' → messaggio verde di conferma
            flash(f'Azienda "{nome}" aggiunta.', 'success')

            # redirect manda il browser alla lista delle aziende
            return redirect(url_for('aziende.lista'))

        # se la richiesta è GET, mostriamo semplicemente il form vuoto (dati={})
        return render_template('aziende/form.html', dimensioni=dimensioni, dati={})


# ── MODIFICA AZIENDA ───────────────────────────────────────
# URL: GET /aziende/42/modifica  → form precompilato con i dati dell'azienda 42
# URL: POST /aziende/42/modifica → salva le modifiche
# <int:id> è un parametro dinamico nell'URL: Flask lo estrae e lo passa alla funzione
@aziende_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
def modifica(id):
    with apri_db() as db:
        # fetchone() restituisce una sola riga (o None se non trovata).
        # Cerchiamo l'azienda con quell'id, solo se è attiva (non eliminata).
        azienda = db.execute(
            'SELECT * FROM aziende WHERE id = ? AND attiva = 1', (id,)
        ).fetchone()

        # se l'azienda non esiste (o è stata eliminata), torniamo alla lista
        if azienda is None:
            return redirect(url_for('aziende.lista'))

        dimensioni = db.execute('SELECT * FROM dimensione_azienda ORDER BY id').fetchall()

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            if not nome:
                flash('Il nome è obbligatorio.', 'danger')
                return render_template('aziende/form.html',
                                       dimensioni=dimensioni,
                                       dati=request.form,
                                       azienda=azienda)

            # UPDATE modifica una riga esistente nel DB.
            # SET elenca i campi da aggiornare.
            # WHERE id=? garantisce di modificare solo quella riga specifica.
            db.execute('''
                UPDATE aziende
                SET nome=?, linkedin=?, sito_web=?, username=?, note_accesso=?,
                    citta=?, paese=?, dimensione_azienda_id=?, note=?
                WHERE id=?
            ''', (
                nome,
                request.form.get('linkedin') or None,
                request.form.get('sito_web') or None,
                request.form.get('username') or None,
                request.form.get('note_accesso') or None,
                request.form.get('citta') or None,
                request.form.get('paese') or None,
                request.form.get('dimensione_azienda_id') or None,
                request.form.get('note') or None,
                id   # ultimo valore: corrisponde al ? in WHERE id=?
            ))
            db.commit()
            flash(f'Azienda "{nome}" aggiornata.', 'success')
            return redirect(url_for('aziende.lista'))

        # GET: passiamo i dati dell'azienda al form per precompilarlo.
        # 'dati=azienda' → i campi del form mostrano i valori attuali
        # 'azienda=azienda' → il template lo usa per cambiare il titolo ("Modifica" vs "Nuova")
        return render_template('aziende/form.html',
                               dimensioni=dimensioni,
                               dati=azienda,
                               azienda=azienda)


# ── ELIMINA AZIENDA ────────────────────────────────────────
# URL: POST /aziende/42/elimina
# Solo POST (non GET) perché eliminare è un'azione distruttiva:
# non vogliamo che basti visitare un URL per eliminare dati.
@aziende_bp.route('/<int:id>/elimina', methods=['POST'])
def elimina(id):
    with apri_db() as db:
        azienda = db.execute('SELECT nome FROM aziende WHERE id = ?', (id,)).fetchone()
        if azienda:
            # SOFT DELETE: non cancelliamo la riga dal DB (DELETE sarebbe irreversibile),
            # ma impostiamo attiva=0. Le query che mostrano i dati filtrano con WHERE attiva=1,
            # quindi l'azienda sparisce dall'interfaccia ma resta nel DB per sicurezza.
            db.execute('UPDATE aziende SET attiva = 0 WHERE id = ?', (id,))
            db.commit()
            # 'warning' → messaggio giallo
            flash(f'Azienda "{azienda["nome"]}" eliminata.', 'warning')

    return redirect(url_for('aziende.lista'))