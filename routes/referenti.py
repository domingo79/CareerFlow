from flask import Blueprint, render_template, request, redirect, url_for, flash
from service.db import apri_db

referenti_bp = Blueprint('referenti', __name__, url_prefix='/referenti')


@referenti_bp.route('/')
def lista():
    with apri_db() as db:
        referenti = db.execute('''
            SELECT r.*, a.nome AS nome_azienda
            FROM referenti r
            JOIN aziende a ON r.azienda_id = a.id
            WHERE r.attiva = 1
            ORDER BY a.nome, r.nome
        ''').fetchall()
    return render_template('referenti/lista.html', referenti=referenti)


@referenti_bp.route('/nuovo', methods=['GET', 'POST'])
def nuovo():
    with apri_db() as db:
        aziende = db.execute('SELECT id, nome FROM aziende WHERE attiva = 1 ORDER BY nome').fetchall()

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            azienda_id = request.form.get('azienda_id')

            if not nome or not azienda_id:
                flash('Nome e azienda sono obbligatori.', 'danger')
                return render_template('referenti/form.html', aziende=aziende, dati=request.form)

            db.execute('''
                INSERT INTO referenti (azienda_id, nome, cognome, email, telefono, ruolo, linkedin, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                azienda_id,
                nome,
                request.form.get('cognome') or None,
                request.form.get('email') or None,
                request.form.get('telefono') or None,
                request.form.get('ruolo') or None,
                request.form.get('linkedin') or None,
                request.form.get('note') or None,
            ))
            db.commit()
            flash(f'Referente "{nome}" aggiunto.', 'success')
            return redirect(url_for('referenti.lista'))

        return render_template('referenti/form.html', aziende=aziende, dati={})


@referenti_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
def modifica(id):
    with apri_db() as db:
        referente = db.execute('SELECT * FROM referenti WHERE id = ? AND attiva = 1', (id,)).fetchone()
        if referente is None:
            return redirect(url_for('referenti.lista'))

        aziende = db.execute('SELECT id, nome FROM aziende WHERE attiva = 1 ORDER BY nome').fetchall()

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            azienda_id = request.form.get('azienda_id')

            if not nome or not azienda_id:
                flash('Nome e azienda sono obbligatori.', 'danger')
                return render_template('referenti/form.html', aziende=aziende, dati=request.form, referente=referente)

            db.execute('''
                UPDATE referenti
                SET azienda_id=?, nome=?, cognome=?, email=?, telefono=?, ruolo=?, linkedin=?, note=?
                WHERE id=?
            ''', (
                azienda_id,
                nome,
                request.form.get('cognome') or None,
                request.form.get('email') or None,
                request.form.get('telefono') or None,
                request.form.get('ruolo') or None,
                request.form.get('linkedin') or None,
                request.form.get('note') or None,
                id
            ))
            db.commit()
            flash(f'Referente "{nome}" aggiornato.', 'success')
            return redirect(url_for('referenti.lista'))

        return render_template('referenti/form.html', aziende=aziende, dati=referente, referente=referente)


@referenti_bp.route('/<int:id>/elimina', methods=['POST'])
def elimina(id):
    with apri_db() as db:
        referente = db.execute('SELECT nome FROM referenti WHERE id = ?', (id,)).fetchone()
        if referente:
            db.execute('UPDATE referenti SET attiva = 0 WHERE id = ?', (id,))
            db.commit()
            flash(f'Referente "{referente["nome"]}" eliminato.', 'warning')
    return redirect(url_for('referenti.lista'))