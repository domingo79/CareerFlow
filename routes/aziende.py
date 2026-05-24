from flask import Blueprint, render_template, request, redirect, url_for, flash
import service.aziende as svc

aziende_bp = Blueprint("aziende", __name__, url_prefix="/aziende")
DIMENSIONI = ["startup", "PMI", "corporate"]


# ==============================================================================
# LIST
# ==============================================================================

@aziende_bp.route("/")
def index():
    mostra_tutte = request.args.get("tutte", "0") == "1"
    aziende = svc.get_all(solo_attive=not mostra_tutte)
    return render_template(
        "aziende/index.html", aziende=aziende, mostra_tutte=mostra_tutte,)


# ==============================================================================
# CREATE
# ==============================================================================

@aziende_bp.route("/nuova", methods=["GET", "POST"])
def nuova():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Il nome dell'azienda è obbligatorio.", "errore")
            return render_template("aziende/form.html", azienda=None, dimensioni=DIMENSIONI)

        svc.create(
            nome=nome,
            linkedin=request.form.get("linkedin") or None,
            sito_web=request.form.get("sito_web") or None,
            username=request.form.get("username") or None,
            note_accesso=request.form.get("note_accesso") or None,
            citta=request.form.get("citta") or None,
            paese=request.form.get("paese") or None,
            dimensione_azienda=request.form.get("dimensione_azienda") or None,
            note=request.form.get("note") or None,
        )
        flash(f"Azienda «{nome}» aggiunta con successo.", "successo")
        return redirect(url_for("aziende.index"))

    return render_template("aziende/form.html", azienda=None, dimensioni=DIMENSIONI)


# ==============================================================================
# DETAIL
# ==============================================================================

@aziende_bp.route("/<int:azienda_id>")
def dettaglio(azienda_id: int):
    azienda = svc.get_by_id(azienda_id)
    if azienda is None:
        flash("Azienda non trovata.", "errore")
        return redirect(url_for("aziende.index"))
    return render_template("aziende/dettaglio.html", azienda=azienda)


# ==============================================================================
# EDIT
# ==============================================================================

@aziende_bp.route("/<int:azienda_id>/modifica", methods=["GET", "POST"])
def modifica(azienda_id: int):
    azienda = svc.get_by_id(azienda_id)
    if azienda is None:
        flash("Azienda non trovata.", "errore")
        return redirect(url_for("aziende.index"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Il nome dell'azienda è obbligatorio.", "errore")
            return render_template("aziende/form.html", azienda=azienda, dimensioni=DIMENSIONI)

        svc.update(
            azienda_id=azienda_id,
            nome=nome,
            linkedin=request.form.get("linkedin") or None,
            sito_web=request.form.get("sito_web") or None,
            username=request.form.get("username") or None,
            note_accesso=request.form.get("note_accesso") or None,
            citta=request.form.get("citta") or None,
            paese=request.form.get("paese") or None,
            dimensione_azienda=request.form.get("dimensione_azienda") or None,
            note=request.form.get("note") or None,
        )
        flash(f"Azienda «{nome}» aggiornata.", "successo")
        return redirect(url_for("aziende.dettaglio", azienda_id=azienda_id))

    return render_template("aziende/form.html", azienda=azienda, dimensioni=DIMENSIONI)


# ==============================================================================
# SOFT DELETE / RESTORE
# ==============================================================================

@aziende_bp.route("/<int:azienda_id>/disattiva", methods=["POST"])
def disattiva(azienda_id: int):
    svc.set_attiva(azienda_id, False)
    flash("Azienda disattivata.", "info")
    return redirect(url_for("aziende.index"))


@aziende_bp.route("/<int:azienda_id>/ripristina", methods=["POST"])
def ripristina(azienda_id: int):
    svc.set_attiva(azienda_id, True)
    flash("Azienda ripristinata.", "successo")
    return redirect(url_for("aziende.index"))
