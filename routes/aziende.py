from flask import Blueprint, render_template, request, redirect, url_for, flash
from service.db import apri_db

aziende_bp = Blueprint('aziende', __name__, url_prefix='/aziende')


@aziende_bp.route('/')
def lista():
    with apri_db() as db:
        aziende = db.execute('''
            SELECT a.*, d.nome AS dimensione
            FROM aziende a
            LEFT JOIN dimensione_azienda d ON a.dimensione_azienda_id = d.id
            WHERE a.attiva = 1
            ORDER BY a.nome
        ''').fetchall()
    return render_template('aziende/lista.html', aziende=aziende)


@aziende_bp.route('/nuova', methods=['GET', 'POST'])
def nuova():
    with apri_db() as db:
        dimensioni = db.execute('SELECT * FROM dimensione_azienda ORDER BY id').fetchall()

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            if not nome:
                flash('Il nome è obbligatorio.', 'danger')
                return render_template('aziende/form.html', dimensioni=dimensioni, dati=request.form)

            db.execute('''
                INSERT INTO aziende (nome, linkedin, sito_web, username, note_accesso, citta, paese, dimensione_azienda_id, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            ))
            db.commit()
            flash(f'Azienda "{nome}" aggiunta.', 'success')
            return redirect(url_for('aziende.lista'))

        return render_template('aziende/form.html', dimensioni=dimensioni, dati={})


@aziende_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
def modifica(id):
    with apri_db() as db:
        azienda = db.execute('SELECT * FROM aziende WHERE id = ? AND attiva = 1', (id,)).fetchone()
        if azienda is None:
            return redirect(url_for('aziende.lista'))

        dimensioni = db.execute('SELECT * FROM dimensione_azienda ORDER BY id').fetchall()

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            if not nome:
                flash('Il nome è obbligatorio.', 'danger')
                return render_template('aziende/form.html', dimensioni=dimensioni, dati=request.form, azienda=azienda)

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
                id
            ))
            db.commit()
            flash(f'Azienda "{nome}" aggiornata.', 'success')
            return redirect(url_for('aziende.lista'))

        return render_template('aziende/form.html', dimensioni=dimensioni, dati=azienda, azienda=azienda)


@aziende_bp.route('/<int:id>/elimina', methods=['POST'])
def elimina(id):
    with apri_db() as db:
        azienda = db.execute('SELECT nome FROM aziende WHERE id = ?', (id,)).fetchone()
        if azienda:
            db.execute('UPDATE aziende SET attiva = 0 WHERE id = ?', (id,))
            db.commit()
            flash(f'Azienda "{azienda["nome"]}" eliminata.', 'warning')
    return redirect(url_for('aziende.lista'))