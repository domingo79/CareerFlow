# Abstract: "Spiegazione semplice del progetto" (cosa fa la app, non come lo fa)

**"CareeFlow"** è un'applicazione che aiuta a tenere sotto controllo tutte le candidature di lavoro inviate.

Una volta registrato l'invio del CV, si può aggiornare lo stato in ogni fase: feedback ricevuto, colloquio fissato, colloquio svolto, assunzione, scarto o "ghostato" (quando l'azienda non risponde più).

L'app mostra subito una panoramica chiara con il numero di candidature in ogni stato, per capire a colpo d'occhio quanti colloqui sono stati ottenuti, quante candidature sono ancora in attesa e quante sono finite nel nulla.

Inoltre avremo una dashboard con grafici a barre e a torta per visualizzare subito la distribuzione degli stati. Metriche come il tasso di risposta e la percentuale di ghostati aiuteranno a capire l'efficacia della propria ricerca.

# requirements: (lista di moduli esterni di python che avete intenzione di usarem,se ne avete idea)

* `flask` – per creare un'interfaccia web accessibile da browser
* `sqlite3` – database leggero
* `matplotlib` – per generare grafici
* `datetime`, `os`, – librerie built-in per utility varie

# API: (API pubbliche che avete intenzione di usare per il progetto, se ne avete idea)

Nessuna API esterna necessaria. L'app funziona completamente in locale e offline, salvando i dati direttamente sul dispositivo dell'utente.

eventuali implementazioni in corso d'opera

    (Opzionale) Se esiste una email cheker - Per rilevare automaticamente risposte ricevute e suggerire di aggiornare lo stato.

    (Opzionale) Se esiste un calendario - Per aggiungere promemoria o colloqui.


## NOTE


Blueprint        → raggruppa route dello stesso argomento in un file separato

render_template  → legge un file HTML dalla cartella templates/ e lo restituisce

request          → contiene i dati della richiesta HTTP (form, parametri URL, ecc.)

redirect         → dice al browser di andare a un'altra pagina

url_for          → genera l'URL di una route dal suo nome (es. 'aziende.lista' → '/aziende/')

flash            → aggiunge un messaggio temporaneo (successo/errore) visibile una sola volta
