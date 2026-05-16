# CareerFlow — Specifiche Tecniche

## Schema DB

### `aziende`

| Colonna  | Tipo       | Note                |
| -------- | ---------- | ------------------- |
| id       | INTEGER PK | autoincrement       |
| nome     | TEXT       | obbligatorio        |
| sito_web | TEXT       |                     |
| username | TEXT       | credenziali portale |
| password | TEXT       | credenziali portale |
| note     | TEXT       |                     |

### `contatti`

| Colonna      | Tipo       | Note          |
| ------------ | ---------- | ------------- |
| id           | INTEGER PK | autoincrement |
| id_azienda   | INTEGER FK | → aziende.id |
| nome         | TEXT       |               |
| ruolo        | TEXT       |               |
| linkedin_url | TEXT       |               |
| email        | TEXT       |               |
| note         | TEXT       |               |

### `candidature`

| Colonna              | Tipo       | Note                      |
| -------------------- | ---------- | ------------------------- |
| id                   | INTEGER PK | autoincrement             |
| id_azienda           | INTEGER FK | → aziende.id             |
| id_contatto          | INTEGER FK | → contatti.id (nullable) |
| posizione            | TEXT       |                           |
| tipo_candidatura     | TEXT       | `semplice`/`portale`  |
| versione_curriculum  | TEXT       |                           |
| stato                | TEXT       | default `inviata`       |
| nessun_feedback      | INTEGER    | default `0`(bool)       |
| data_invio           | TEXT       | ISO date                  |
| data_ultima_modifica | TEXT       | ISO date                  |
| note                 | TEXT       |                           |

---

## Flusso stati

```
inviata  (3 gg lav, nessuna risposta) ──► sollecito   [nessun_feedback = 1]
inviata  (risposta manuale) ────────────► ricevuta
ricevuta (2 gg lav)  ───────────────────► pending
pending  (8 gg lav)  ───────────────────► sollecito
```

---

## Moduli `database/`

### `constants.py`

* `DB_PATH` — percorso assoluto del file SQLite
* `STATI_VALIDI` — tuple degli stati ammessi
* `TIPI_CANDIDATURA` — tuple dei tipi ammessi

### `connection.py`

* `_conn()` — apre connessione con `row_factory` e foreign keys ON
* `_oggi()` — restituisce data odierna ISO
* `_giorni_lavorativi(data_iso)` — conta giorni lavorativi da una data a oggi
* `init_db()` — crea le tabelle se non esistono
* `SCHEMA` — stringa SQL con `CREATE TABLE IF NOT EXISTS`

### `aziende.py` — `AziendeManager`

* `create(...)` → int
* `read_all()` → list[Row]
* `read_by_id(id)` → Row | None
* `update(id, ...)` → None

### `contatti.py` — `ContattiManager`

* `create(...)` → int
* `read_all()` → list[Row]
* `read_by_id(id)` → Row | None
* `read_by_azienda(id_azienda)` → list[Row]
* `update(id, ...)` → None

### `candidature.py` — `CandidatureManager`

* `create(...)` → int
* `read_all()` → list[Row]
* `read_by_id(id)` → Row | None
* `update(id, ...)` → None
* `update_stato(id, nuovo_stato)` → None
* `_aggiorna_stati_batch(ids, stato)` → int *(privato)*
* `_set_nessun_feedback_batch(ids)` → None *(privato)*
* `_filtra_per_transizione(stato, soglia)` → list[Row] *(privato)*
* `avanza_ricevuta_a_pending(soglia=2)` → int
* `avanza_pending_a_sollecito(soglia=8)` → int
* `avanza_inviata_a_sollecito(soglia=3)` → int
* `avanza_stati()` → dict[str, int] ← **orchestratore, chiamare all'avvio**

---

## Note rapide

* `avanza_stati()` va chiamato una volta all'avvio di ogni pagina Streamlit (o solo sulla dashboard)
* Nessun metodo `delete` per nessuna tabella — i dati sono storici
* `nessun_feedback` è salvato come `INTEGER` (0/1), non come stringa
* Le date sono stringhe ISO `YYYY-MM-DD` — nessun tipo `DATE` nativo SQLite
