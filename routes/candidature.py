# ============================================================
# routes/candidature.py — tutte le pagine relative alle candidature
# È la sezione centrale dell'app: collega aziende, referenti e stati.
# ============================================================

from datetime import date   # per ottenere la data di oggi in Python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from service.db import apri_db


candidature_bp = Blueprint('candidature', __name__, url_prefix='/candidature')


# ── LISTA ──────────────────────────────────────────────────
@candidature_bp.route('/')
def lista():
    with apri_db() as db:
        # Questa query usa due JOIN perché la tabella candidature
        # ha solo gli ID (azienda_id, stato_candidatura_id) ma noi
        # vogliamo mostrare i nomi (nome_azienda, nome_stato, colore_stato).
        # JOIN collega le tabelle sulle colonne corrispondenti.
        candidature = db.execute('''
            SELECT c.*,
                   a.nome  AS nome_azienda,
                   sc.nome AS nome_stato,
                   sc.colore AS colore_stato
            FROM candidature c
            JOIN aziende a            ON c.azienda_id           = a.id
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1
            ORDER BY c.data_candidatura DESC
        ''').fetchall()
    return render_template('candidature/lista.html', candidature=candidature)


# ── NUOVA CANDIDATURA ──────────────────────────────────────
@candidature_bp.route('/nuova', methods=['GET', 'POST'])
def nuova():
    with apri_db() as db:
        # carichiamo tutte le liste necessarie per i menu <select> del form
        aziende   = db.execute(
            'SELECT id, nome FROM aziende WHERE attiva = 1 ORDER BY nome'
        ).fetchall()

        referenti = db.execute('''
            SELECT r.id, r.nome, r.cognome, r.azienda_id
            FROM referenti r
            WHERE r.attiva = 1
            ORDER BY r.nome
        ''').fetchall()
        # nota: passiamo azienda_id per ogni referente così il JavaScript
        # nel form può filtrare i referenti in base all'azienda scelta

        stati = db.execute(
            'SELECT * FROM stati_candidatura WHERE attiva = 1 ORDER BY ordine'
        ).fetchall()

        modalita = db.execute('SELECT * FROM modalita_lavoro ORDER BY id').fetchall()

        if request.method == 'POST':
            posizione  = request.form.get('posizione', '').strip()
            azienda_id = request.form.get('azienda_id')
            stato_id   = request.form.get('stato_candidatura_id')

            if not posizione or not azienda_id or not stato_id:
                flash('Posizione, azienda e stato sono obbligatori.', 'danger')
                return render_template('candidature/form.html',
                                       aziende=aziende, referenti=referenti,
                                       stati=stati, modalita=modalita,
                                       dati=request.form)

            # date.today().isoformat() restituisce la data di oggi come stringa
            # nel formato 'YYYY-MM-DD' (es. '2026-05-29').
            # Viene usata come fallback se l'utente non compila il campo data.
            # Non possiamo affidarci al DEFAULT CURRENT_DATE dello schema SQL
            # perché passare None esplicitamente sovrascrive il default.
            db.execute('''
                INSERT INTO candidature
                    (azienda_id, referente_id, posizione, stato_candidatura_id,
                     modalita_lavoro_id, versione_cv, data_candidatura,
                     data_colloquio, url_offerta, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                azienda_id,
                request.form.get('referente_id') or None,
                posizione,
                stato_id,
                request.form.get('modalita_lavoro_id') or None,
                request.form.get('versione_cv') or None,
                request.form.get('data_candidatura') or date.today().isoformat(),
                request.form.get('data_colloquio') or None,
                request.form.get('url_offerta') or None,
                request.form.get('note') or None,
            ))
            db.commit()
            flash(f'Candidatura per "{posizione}" aggiunta.', 'success')
            return redirect(url_for('candidature.lista'))

        return render_template('candidature/form.html',
                               aziende=aziende, referenti=referenti,
                               stati=stati, modalita=modalita, dati={})


# ── MODIFICA CANDIDATURA ───────────────────────────────────
@candidature_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
def modifica(id):
    with apri_db() as db:
        candidatura = db.execute(
            'SELECT * FROM candidature WHERE id = ? AND attiva = 1', (id,)
        ).fetchone()

        if candidatura is None:
            return redirect(url_for('candidature.lista'))

        # carichiamo di nuovo tutte le liste per i menu <select>
        aziende   = db.execute(
            'SELECT id, nome FROM aziende WHERE attiva = 1 ORDER BY nome'
        ).fetchall()
        referenti = db.execute('''
            SELECT r.id, r.nome, r.cognome, r.azienda_id
            FROM referenti r
            WHERE r.attiva = 1
            ORDER BY r.nome
        ''').fetchall()
        stati    = db.execute(
            'SELECT * FROM stati_candidatura WHERE attiva = 1 ORDER BY ordine'
        ).fetchall()
        modalita = db.execute('SELECT * FROM modalita_lavoro ORDER BY id').fetchall()

        if request.method == 'POST':
            posizione  = request.form.get('posizione', '').strip()
            azienda_id = request.form.get('azienda_id')
            stato_id   = request.form.get('stato_candidatura_id')

            if not posizione or not azienda_id or not stato_id:
                flash('Posizione, azienda e stato sono obbligatori.', 'danger')
                return render_template('candidature/form.html',
                                       aziende=aziende, referenti=referenti,
                                       stati=stati, modalita=modalita,
                                       dati=request.form, candidatura=candidatura)

            db.execute('''
                UPDATE candidature
                SET azienda_id=?, referente_id=?, posizione=?,
                    stato_candidatura_id=?, modalita_lavoro_id=?,
                    versione_cv=?, data_candidatura=?,
                    data_colloquio=?, url_offerta=?, note=?
                WHERE id=?
            ''', (
                azienda_id,
                request.form.get('referente_id') or None,
                posizione,
                stato_id,
                request.form.get('modalita_lavoro_id') or None,
                request.form.get('versione_cv') or None,
                request.form.get('data_candidatura') or date.today().isoformat(),
                request.form.get('data_colloquio') or None,
                request.form.get('url_offerta') or None,
                request.form.get('note') or None,
                id
            ))
            db.commit()
            flash(f'Candidatura "{posizione}" aggiornata.', 'success')
            return redirect(url_for('candidature.lista'))

        return render_template('candidature/form.html',
                               aziende=aziende, referenti=referenti,
                               stati=stati, modalita=modalita,
                               dati=candidatura, candidatura=candidatura)


# ── ELIMINA CANDIDATURA ────────────────────────────────────
@candidature_bp.route('/<int:id>/elimina', methods=['POST'])
def elimina(id):
    with apri_db() as db:
        candidatura = db.execute(
            'SELECT posizione FROM candidature WHERE id = ?', (id,)
        ).fetchone()
        if candidatura:
            # soft delete
            db.execute('UPDATE candidature SET attiva = 0 WHERE id = ?', (id,))
            db.commit()
            flash(f'Candidatura "{candidatura["posizione"]}" eliminata.', 'warning')
    return redirect(url_for('candidature.lista'))