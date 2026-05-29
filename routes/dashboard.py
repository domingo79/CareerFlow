# ============================================================
# routes/dashboard.py — pagina principale con le statistiche
# Calcola tutti i numeri e li passa al template HTML.
# Il template usa Chart.js (JavaScript) per disegnare i grafici.
# ============================================================

import json   # per convertire liste Python in formato JSON leggibile da JavaScript
from flask import Blueprint, render_template
from service.db import apri_db


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
def index():
    with apri_db() as db:

        # ── KPI (Key Performance Indicators) ──────────────────────
        # COUNT(*) conta il numero di righe che soddisfano la condizione.
        # fetchone()[0] prende la prima (e unica) riga, poi il primo valore.

        # numero totale di candidature inserite (non eliminate)
        totale = db.execute(
            'SELECT COUNT(*) FROM candidature WHERE attiva = 1'
        ).fetchone()[0]

        # candidature ancora "in gioco": lo stato non è terminale
        # (is_terminale=0 → INVIATA, IN ATTESA, COLLOQUIO, ecc.)
        aperte = db.execute('''
            SELECT COUNT(*) FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1 AND sc.is_terminale = 0
        ''').fetchone()[0]

        # candidature che hanno ricevuto almeno una risposta:
        # ordine >= 3 significa stati dopo INVIATA e FOLLOW-UP
        risposte = db.execute('''
            SELECT COUNT(*) FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1 AND sc.ordine >= 3
        ''').fetchone()[0]

        # candidature finite in GHOST (azienda sparita senza rispondere)
        ghostati = db.execute('''
            SELECT COUNT(*) FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1 AND sc.nome = 'GHOST'
        ''').fetchone()[0]

        # candidature che sono arrivate almeno al colloquio
        colloqui = db.execute('''
            SELECT COUNT(*) FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1 AND sc.nome IN ('COLLOQUIO', 'OFFERTA', 'ACCETTATA')
        ''').fetchone()[0]

        # ── Dati per il grafico a barre (candidature per stato) ───
        # GROUP BY raggruppa le righe per stato e conta quante ce ne sono.
        # ORDER BY sc.ordine ordina gli stati nell'ordine logico del flusso.
        per_stato = db.execute('''
            SELECT sc.nome, sc.colore, COUNT(*) AS n
            FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1
            GROUP BY sc.id
            ORDER BY sc.ordine
        ''').fetchall()

        # ── Dati per il grafico a torta (positivo/negativo/neutro) ─
        per_tipo = db.execute('''
            SELECT sc.tipo, COUNT(*) AS n
            FROM candidature c
            JOIN stati_candidatura sc ON c.stato_candidatura_id = sc.id
            WHERE c.attiva = 1
            GROUP BY sc.tipo
        ''').fetchall()

        # ── Dati per il grafico trend mensile ─────────────────────
        # strftime('%Y-%m', data_candidatura) estrae anno e mese dalla data
        # es. '2026-03', '2026-04', '2026-05'
        trend = db.execute('''
            SELECT strftime('%Y-%m', data_candidatura) AS mese, COUNT(*) AS n
            FROM candidature
            WHERE attiva = 1 AND data_candidatura IS NOT NULL
            GROUP BY mese
            ORDER BY mese ASC
            LIMIT 12
        ''').fetchall()

    # ── Calcolo percentuali ─────────────────────────────────────
    # 'if totale > 0 else 0' evita la divisione per zero (ZeroDivisionError)
    # quando non ci sono ancora candidature
    perc_risposta = round(risposte / totale * 100) if totale > 0 else 0
    perc_ghostati = round(ghostati / totale * 100) if totale > 0 else 0
    perc_colloqui = round(colloqui / totale * 100) if totale > 0 else 0

    # ── Preparazione dati per Chart.js ──────────────────────────
    # Chart.js è una libreria JavaScript che disegna i grafici nel browser.
    # Python non può parlare direttamente con JavaScript, quindi convertiamo
    # le liste Python in stringhe JSON con json.dumps().
    # Il template HTML poi usa queste stringhe come variabili JavaScript.
    #
    # List comprehension [r['nome'] for r in per_stato] è un modo compatto
    # per creare una lista estraendo un valore da ogni riga del risultato SQL.
    # Equivale a:
    #   lista = []
    #   for r in per_stato:
    #       lista.append(r['nome'])

    barre_labels = json.dumps([r['nome']   for r in per_stato])  # nomi degli stati
    barre_valori = json.dumps([r['n']      for r in per_stato])  # conteggi
    barre_colori = json.dumps([r['colore'] for r in per_stato])  # colori hex dal DB

    # colori fissi per i 3 tipi (positivo/negativo/neutro)
    colori_tipo  = {'positivo': '#a8d5a2', 'negativo': '#f8cecc', 'neutro': '#dae8fc'}
    torta_labels = json.dumps([r['tipo'] for r in per_tipo])
    torta_valori = json.dumps([r['n']    for r in per_tipo])
    # .get(chiave, '#ccc') restituisce '#ccc' se il tipo non è nel dizionario
    torta_colori = json.dumps([colori_tipo.get(r['tipo'], '#ccc') for r in per_tipo])

    trend_labels = json.dumps([r['mese'] for r in trend])
    trend_valori = json.dumps([r['n']    for r in trend])

    # render_template passa tutte le variabili al file HTML.
    # Ogni nome a sinistra dell'= è il nome con cui si accede nel template.
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