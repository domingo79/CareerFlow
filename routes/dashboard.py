# ============================================================
# routes/dashboard.py — pagina principale con le statistiche
# ============================================================

import json
from flask import Blueprint, render_template
from service.db import apri_db


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
def index():
    with apri_db() as db:

        # ── KPI ─────────────────────────────────────────────────────
        totale = db.execute(
            'SELECT COUNT(*) FROM candidature WHERE attiva = 1'
        ).fetchone()[0]

        # is_terminale=0: stati ancora "in gioco" (non rifiuto, non accettata)
        aperte = db.execute('''
            SELECT COUNT(*) FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1 AND sc.is_terminale = 0
        ''').fetchone()[0]

        # ordine >= 3: tutti gli stati dopo INVIATA e FOLLOW-UP, quindi ha risposto
        risposte = db.execute('''
            SELECT COUNT(*) FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1 AND sc.ordine >= 3
        ''').fetchone()[0]

        ghostati = db.execute('''
            SELECT COUNT(*) FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1 AND sc.nome = 'GHOST'
        ''').fetchone()[0]

        colloqui = db.execute('''
            SELECT COUNT(*) FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1 AND sc.nome IN ('COLLOQUIO', 'OFFERTA', 'ACCETTATA')
        ''').fetchone()[0]

        # ── Grafico a barre: una riga per stato, ordinata secondo il flusso
        per_stato = db.execute('''
            SELECT sc.nome, sc.colore, COUNT(*) AS n
            FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1
            GROUP BY sc.id
            ORDER BY sc.ordine
        ''').fetchall()

        # ── Grafico a ciambella: raggruppa per tipo (positivo/negativo/neutro)
        per_tipo = db.execute('''
            SELECT sc.tipo, COUNT(*) AS n
            FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1
            GROUP BY sc.tipo
        ''').fetchall()

        # ── Trend mensile: strftime estrae anno-mese dalla data (es. '2026-05')
        trend = db.execute('''
            SELECT strftime('%Y-%m', data_candidatura) AS mese, COUNT(*) AS n
            FROM candidature
            WHERE attiva = 1 AND data_candidatura IS NOT NULL
            GROUP BY mese
            ORDER BY mese ASC
            LIMIT 12
        ''').fetchall()

    # divisione sicura: evita ZeroDivisionError se ancora non ci sono candidature
    perc_risposta = round(risposte / totale * 100) if totale > 0 else 0
    perc_ghostati = round(ghostati / totale * 100) if totale > 0 else 0
    perc_colloqui = round(colloqui / totale * 100) if totale > 0 else 0

    # json.dumps() converte le liste Python in stringhe JSON leggibili da JavaScript
    barre_labels = json.dumps([r['nome'] for r in per_stato])
    barre_valori = json.dumps([r['n'] for r in per_stato])
    barre_colori = json.dumps([r['colore'] for r in per_stato])

    colori_tipo = {'positivo': '#a8d5a2',
                   'negativo': '#f8cecc', 'neutro': '#dae8fc'}
    torta_labels = json.dumps([r['tipo'] for r in per_tipo])
    torta_valori = json.dumps([r['n'] for r in per_tipo])
    # .get(tipo, '#ccc'): grigio di fallback se arriva un tipo non previsto
    torta_colori = json.dumps(
        [colori_tipo.get(r['tipo'], '#ccc') for r in per_tipo])

    trend_labels = json.dumps([r['mese'] for r in trend])
    trend_valori = json.dumps([r['n'] for r in trend])

    return render_template('dashboard.html',
                           totale=totale,
                           aperte=aperte,
                           perc_risposta=perc_risposta,
                           perc_ghostati=perc_ghostati,
                           perc_colloqui=perc_colloqui,
                           barre_labels=barre_labels,
                           barre_valori=barre_valori,
                           barre_colori=barre_colori,
                           torta_labels=torta_labels,
                           torta_valori=torta_valori,
                           torta_colori=torta_colori,
                           trend_labels=trend_labels,
                           trend_valori=trend_valori,
                           )
