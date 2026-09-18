import sqlite3

DATABASE = "database/calcioai.db"

def _leggi_storico(mercato=None, min_ai_score=0):

```
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

query = """
    SELECT
        id,
        data,
        data_partita,
        campionato,
        casa,
        trasferta,
        pronostico,
        fiducia,
        ai_score,
        esito,
        risultato
    FROM storico
    WHERE esito IN ('CORRETTO', 'ERRATO')
    AND ai_score >= ?
"""

parametri = [min_ai_score]

if mercato:
    query += " AND pronostico = ?"
    parametri.append(mercato)

query += """
    ORDER BY
        CASE
            WHEN data_partita IS NULL
            OR data_partita = ''
            THEN data
            ELSE data_partita
        END ASC,
        id ASC
"""

try:
    cursor.execute(query, parametri)
    dati = cursor.fetchall()

except sqlite3.OperationalError:

    query = """
        SELECT
            id,
            data,
            data_partita,
            campionato,
            casa,
            trasferta,
            pronostico,
            fiducia,
            ai_score,
            esito,
            risultato
        FROM storico
        WHERE esito IN ('CORRETTO', 'ERRATO')
        AND ai_score >= ?
    """

    parametri = [min_ai_score]

    if mercato:
        query += " AND pronostico = ?"
        parametri.append(mercato)

    query += " ORDER BY id ASC"

    cursor.execute(query, parametri)
    dati = cursor.fetchall()

conn.close()

risultati = []

for riga in dati:

    risultati.append({
        "id": riga[0],
        "data": riga[1],
        "data_partita": riga[2],
        "campionato": riga[3],
        "casa": riga[4],
        "trasferta": riga[5],
        "pronostico": riga[6],
        "fiducia": riga[7] or 0,
        "ai_score": riga[8] or 0,
        "esito": riga[9],
        "risultato": riga[10]
    })

return risultati
```

def _calcola_strisce(dati):

```
max_corrette = 0
max_errate = 0

corrette_attuali = 0
errate_attuali = 0

for partita in dati:

    if partita["esito"] == "CORRETTO":

        corrette_attuali += 1
        errate_attuali = 0

    elif partita["esito"] == "ERRATO":

        errate_attuali += 1
        corrette_attuali = 0

    max_corrette = max(
        max_corrette,
        corrette_attuali
    )

    max_errate = max(
        max_errate,
        errate_attuali
    )

return max_corrette, max_errate
```

def simula_raddoppio(
dati,
puntata_base=1.0,
quota=2.0,
max_raddoppi=5
):

```
if not dati:

    return {
        "partite": 0,
        "profitto": 0.0,
        "puntate_totali": 0.0,
        "massima_puntata": 0.0,
        "massima_perdita_cumulata": 0.0,
        "raddoppi_utilizzati": 0,
        "serie_massima_affrontata": 0,
        "stop_perdita": 0
    }

profitto = 0.0
puntate_totali = 0.0
massima_puntata = 0.0

perdita_cumulata = 0.0
massima_perdita_cumulata = 0.0

livello = 0

raddoppi_utilizzati = 0
serie_massima_affrontata = 0
stop_perdita = 0

for partita in dati:

    puntata = puntata_base * (2 ** livello)

    puntate_totali += puntata

    massima_puntata = max(
        massima_puntata,
        puntata
    )

    serie_massima_affrontata = max(
        serie_massima_affrontata,
        livello
    )

    if partita["esito"] == "CORRETTO":

        profitto_giocata = (
            puntata * (quota - 1)
        )

        profitto += profitto_giocata

        perdita_cumulata = 0.0

        livello = 0

    elif partita["esito"] == "ERRATO":

        profitto -= puntata

        perdita_cumulata += puntata

        massima_perdita_cumulata = max(
            massima_perdita_cumulata,
            perdita_cumulata
        )

        if livello < max_raddoppi:

            livello += 1
            raddoppi_utilizzati += 1

        else:

            livello = 0
            stop_perdita += 1

return {
    "partite": len(dati),
    "profitto": round(profitto, 2),
    "puntate_totali": round(puntate_totali, 2),
    "massima_puntata": round(massima_puntata, 2),
    "massima_perdita_cumulata": round(
        massima_perdita_cumulata,
        2
    ),
    "raddoppi_utilizzati": raddoppi_utilizzati,
    "serie_massima_affrontata": serie_massima_affrontata,
    "stop_perdita": stop_perdita
}
```

def analizza_mercato(
mercato,
puntata_base=1.0,
quota=2.0,
max_raddoppi=5,
min_ai_score=0
):

```
dati = _leggi_storico(
    mercato=mercato,
    min_ai_score=min_ai_score
)

totale = len(dati)

corrette = sum(
    1
    for partita in dati
    if partita["esito"] == "CORRETTO"
)

errate = sum(
    1
    for partita in dati
    if partita["esito"] == "ERRATO"
)

precisione = (
    round(
        corrette / totale * 100,
        2
    )
    if totale
    else 0
)

max_corrette, max_errate = _calcola_strisce(
    dati
)

simulazione = simula_raddoppio(
    dati,
    puntata_base=puntata_base,
    quota=quota,
    max_raddoppi=max_raddoppi
)

return {
    "mercato": mercato,
    "totale": totale,
    "corrette": corrette,
    "errate": errate,
    "precisione": precisione,
    "massima_serie_corrette": max_corrette,
    "massima_serie_errate": max_errate,
    "simulazione": simulazione
}
```

def analizza_tutto(
puntata_base=1.0,
quota=2.0,
max_raddoppi=5,
min_ai_score=0
):

```
dati = _leggi_storico(
    min_ai_score=min_ai_score
)

if not dati:

    return {
        "totale": 0,
        "corrette": 0,
        "errate": 0,
        "precisione": 0,
        "massima_serie_corrette": 0,
        "massima_serie_errate": 0,
        "simulazione": simula_raddoppio(
            [],
            puntata_base=puntata_base,
            quota=quota,
            max_raddoppi=max_raddoppi
        ),
        "mercati": {}
    }

corrette = sum(
    1
    for partita in dati
    if partita["esito"] == "CORRETTO"
)

errate = sum(
    1
    for partita in dati
    if partita["esito"] == "ERRATO"
)

totale = len(dati)

precisione = round(
    corrette / totale * 100,
    2
)

max_corrette, max_errate = _calcola_strisce(
    dati
)

mercati = sorted(
    set(
        partita["pronostico"]
        for partita in dati
        if partita["pronostico"]
    )
)

risultati_mercati = {}

for mercato in mercati:

    risultati_mercati[mercato] = analizza_mercato(
        mercato,
        puntata_base=puntata_base,
        quota=quota,
        max_raddoppi=max_raddoppi,
        min_ai_score=min_ai_score
    )

return {
    "totale": totale,
    "corrette": corrette,
    "errate": errate,
    "precisione": precisione,
    "massima_serie_corrette": max_corrette,
    "massima_serie_errate": max_errate,
    "simulazione": simula_raddoppio(
        dati,
        puntata_base=puntata_base,
        quota=quota,
        max_raddoppi=max_raddoppi
    ),
    "mercati": risultati_mercati
}
```

def stampa_report(
puntata_base=1.0,
quota=2.0,
max_raddoppi=5,
min_ai_score=0
):

```
report = analizza_tutto(
    puntata_base=puntata_base,
    quota=quota,
    max_raddoppi=max_raddoppi,
    min_ai_score=min_ai_score
)

print()
print("🔥 CALCIOAI - BACKTEST RADDOPPIO")
print("=" * 45)

if report["totale"] == 0:

    print(
        "⏳ Nessun pronostico chiuso disponibile."
    )

    print("=" * 45)

    return report

print(
    f"📊 Partite analizzate: "
    f"{report['totale']}"
)

print(
    f"✅ Corrette: "
    f"{report['corrette']}"
)

print(
    f"❌ Errate: "
    f"{report['errate']}"
)

print(
    f"🎯 Precisione reale: "
    f"{report['precisione']}%"
)

print(
    f"📈 Massima serie corretta: "
    f"{report['massima_serie_corrette']}"
)

print(
    f"📉 Massima serie errata: "
    f"{report['massima_serie_errate']}"
)

simulazione = report["simulazione"]

print()
print("💰 SIMULAZIONE RADDOPPIO")

print(
    f"💵 Puntata base: "
    f"€{puntata_base:.2f}"
)

print(
    f"🎲 Quota simulata: "
    f"{quota:.2f}"
)

print(
    f"🔢 Massimo raddoppi: "
    f"{max_raddoppi}"
)

print(
    f"📈 Massima puntata raggiunta: "
    f"€{simulazione['massima_puntata']:.2f}"
)

print(
    f"📉 Massima perdita cumulata: "
    f"€{simulazione['massima_perdita_cumulata']:.2f}"
)

print(
    f"💎 Profitto/perdita simulato: "
    f"€{simulazione['profitto']:.2f}"
)

print()
print("🏆 ANALISI PER MERCATO")

for mercato, dati_mercato in report["mercati"].items():

    sim = dati_mercato["simulazione"]

    print()
    print(f"⚽ {mercato}")

    print(
        f"   Partite: "
        f"{dati_mercato['totale']}"
    )

    print(
        f"   Precisione: "
        f"{dati_mercato['precisione']}%"
    )

    print(
        f"   Max serie ERRATE: "
        f"{dati_mercato['massima_serie_errate']}"
    )

    print(
        f"   Max puntata: "
        f"€{sim['massima_puntata']:.2f}"
    )

    print(
        f"   Risultato simulato: "
        f"€{sim['profitto']:.2f}"
    )

print()
print("=" * 45)

return report
```

if **name** == "**main**":
stampa_report()
