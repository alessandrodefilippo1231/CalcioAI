import sqlite3


DATABASE = "database/calcioai.db"


# ============================================================
# CONNESSIONE DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE)


# ============================================================
# NORMALIZZAZIONE MERCATI
# ============================================================

def normalizza_mercato(mercato):

    if not mercato:
        return ""

    mercato = str(mercato).strip()
    m = mercato.lower()

    alias = {

        # OVER
        "over 1.5": "Over 1.5 Gol",
        "over 1.5 gol": "Over 1.5 Gol",

        "over 2.5": "Over 2.5 Gol",
        "over 2.5 gol": "Over 2.5 Gol",

        "over 3.5": "Over 3.5 Gol",
        "over 3.5 gol": "Over 3.5 Gol",

        # UNDER
        "under 1.5": "Under 1.5 Gol",
        "under 1.5 gol": "Under 1.5 Gol",

        "under 2.5": "Under 2.5 Gol",
        "under 2.5 gol": "Under 2.5 Gol",

        "under 3.5": "Under 3.5 Gol",
        "under 3.5 gol": "Under 3.5 Gol",

        # GOAL
        "goal": "Goal",
        "gol": "Goal",
        "gg": "Goal",
        "gol gol": "Goal",
        "golgol": "Goal",

        # NO GOAL
        "no goal": "No Goal",
        "no gol": "No Goal",
        "ng": "No Goal",

        # 1X2
        "1": "1",
        "x": "X",
        "2": "2",

        # DOPPIE CHANCE
        "1x": "1X",
        "x2": "X2",
        "12": "12",
    }

    return alias.get(m, mercato)


# ============================================================
# STATISTICHE PER MERCATO
# ============================================================

def statistiche_mercati():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                pronostico,
                COUNT(*),
                SUM(
                    CASE
                        WHEN esito = 'CORRETTO'
                        THEN 1
                        ELSE 0
                    END
                )
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
            GROUP BY pronostico
        """)

        rows = cursor.fetchall()

    finally:
        conn.close()

    risultati = {}

    for mercato, totale, corrette in rows:

        mercato = normalizza_mercato(mercato)

        if not mercato:
            continue

        if mercato not in risultati:

            risultati[mercato] = {
                "totale": 0,
                "corrette": 0,
                "precisione": 0
            }

        risultati[mercato]["totale"] += totale
        risultati[mercato]["corrette"] += corrette or 0

    for mercato, dati in risultati.items():

        totale = dati["totale"]
        corrette = dati["corrette"]

        if totale > 0:

            dati["precisione"] = round(
                (corrette / totale) * 100,
                1
            )

    return risultati


# ============================================================
# STATISTICHE AI SCORE
# ============================================================

def statistiche_ai_score():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                ai_score,
                esito
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
              AND ai_score IS NOT NULL
        """)

        rows = cursor.fetchall()

    finally:
        conn.close()

    fasce = {

        "0-59": {
            "totale": 0,
            "corrette": 0
        },

        "60-69": {
            "totale": 0,
            "corrette": 0
        },

        "70-79": {
            "totale": 0,
            "corrette": 0
        },

        "80-89": {
            "totale": 0,
            "corrette": 0
        },

        "90-100": {
            "totale": 0,
            "corrette": 0
        },
    }

    for ai_score, esito in rows:

        try:
            score = float(ai_score)
        except (TypeError, ValueError):
            continue

        if score < 60:
            fascia = "0-59"

        elif score < 70:
            fascia = "60-69"

        elif score < 80:
            fascia = "70-79"

        elif score < 90:
            fascia = "80-89"

        else:
            fascia = "90-100"

        fasce[fascia]["totale"] += 1

        if esito == "CORRETTO":
            fasce[fascia]["corrette"] += 1

    for fascia, dati in fasce.items():

        totale = dati["totale"]

        if totale > 0:

            dati["precisione"] = round(
                (dati["corrette"] / totale) * 100,
                1
            )

        else:

            dati["precisione"] = 0

    return fasce


# ============================================================
# STATISTICHE FIDUCIA
# ============================================================

def statistiche_fiducia():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                fiducia,
                esito
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
              AND fiducia IS NOT NULL
        """)

        rows = cursor.fetchall()

    finally:
        conn.close()

    fasce = {

        "0-59": {
            "totale": 0,
            "corrette": 0
        },

        "60-69": {
            "totale": 0,
            "corrette": 0
        },

        "70-79": {
            "totale": 0,
            "corrette": 0
        },

        "80-89": {
            "totale": 0,
            "corrette": 0
        },

        "90-100": {
            "totale": 0,
            "corrette": 0
        },
    }

    for fiducia, esito in rows:

        try:
            valore = float(fiducia)
        except (TypeError, ValueError):
            continue

        if valore < 60:
            fascia = "0-59"

        elif valore < 70:
            fascia = "60-69"

        elif valore < 80:
            fascia = "70-79"

        elif valore < 90:
            fascia = "80-89"

        else:
            fascia = "90-100"

        fasce[fascia]["totale"] += 1

        if esito == "CORRETTO":
            fasce[fascia]["corrette"] += 1

    for fascia, dati in fasce.items():

        totale = dati["totale"]

        if totale > 0:

            dati["precisione"] = round(
                (dati["corrette"] / totale) * 100,
                1
            )

        else:

            dati["precisione"] = 0

    return fasce


# ============================================================
# STATISTICHE RISCHIO
# ============================================================

def statistiche_rischio():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                rischio,
                COUNT(*),
                SUM(
                    CASE
                        WHEN esito = 'CORRETTO'
                        THEN 1
                        ELSE 0
                    END
                )
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
            GROUP BY rischio
        """)

        rows = cursor.fetchall()

    finally:
        conn.close()

    risultati = {}

    for rischio, totale, corrette in rows:

        rischio = rischio or "N/D"

        precisione = 0

        if totale > 0:

            precisione = round(
                ((corrette or 0) / totale) * 100,
                1
            )

        risultati[rischio] = {

            "totale": totale,

            "corrette":
                corrette or 0,

            "precisione":
                precisione
        }

    return risultati


# ============================================================
# PRECISIONE GENERALE
# ============================================================

def precisione_generale():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                COUNT(*),
                SUM(
                    CASE
                        WHEN esito = 'CORRETTO'
                        THEN 1
                        ELSE 0
                    END
                )
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
        """)

        totale, corrette = cursor.fetchone()

    finally:
        conn.close()

    totale = totale or 0
    corrette = corrette or 0

    if totale == 0:
        return 0

    return round(
        (corrette / totale) * 100,
        1
    )


# ============================================================
# MEDIA AI SCORE
# ============================================================

def media_ai_score():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT AVG(ai_score)
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
              AND ai_score IS NOT NULL
        """)

        risultato = cursor.fetchone()[0]

    finally:
        conn.close()

    if risultato is None:
        return 0

    return round(
        float(risultato),
        1
    )


# ============================================================
# MEDIA FIDUCIA
# ============================================================

def media_fiducia():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT AVG(fiducia)
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
              AND fiducia IS NOT NULL
        """)

        risultato = cursor.fetchone()[0]

    finally:
        conn.close()

    if risultato is None:
        return 0

    return round(
        float(risultato),
        1
    )


# ============================================================
# MIGLIOR MERCATO
# ============================================================

def miglior_mercato_ai():

    dati = statistiche_mercati()

    migliori = []

    for mercato, valori in dati.items():

        totale = valori.get(
            "totale",
            0
        )

        precisione = valori.get(
            "precisione",
            0
        )

        if totale >= 3:

            migliori.append(
                (
                    precisione,
                    totale,
                    mercato
                )
            )

    if not migliori:
        return None

    migliori.sort(
        key=lambda x: (
            x[0],
            x[1]
        ),
        reverse=True
    )

    precisione, totale, mercato = migliori[0]

    return {

        "mercato":
            mercato,

        "precisione":
            precisione,

        "totale":
            totale
    }


# ============================================================
# MERCATI AFFIDABILI
# ============================================================

def mercati_affidabili(minimo_pronostici=3):

    dati = statistiche_mercati()

    risultati = []

    for mercato, valori in dati.items():

        totale = valori.get(
            "totale",
            0
        )

        precisione = valori.get(
            "precisione",
            0
        )

        if totale >= minimo_pronostici:

            risultati.append({

                "mercato":
                    mercato,

                "totale":
                    totale,

                "corrette":
                    valori.get(
                        "corrette",
                        0
                    ),

                "precisione":
                    precisione
            })

    risultati.sort(
        key=lambda x: (
            x["precisione"],
            x["totale"]
        ),
        reverse=True
    )

    return risultati


# ============================================================
# LIVELLO AFFIDABILITÀ LEARNING
# ============================================================

def livello_affidabilita_learning(totale):

    if totale < 5:
        return "INIZIALE"

    if totale < 10:
        return "BASSA"

    if totale < 20:
        return "MEDIA"

    if totale < 50:
        return "BUONA"

    if totale < 100:
        return "ALTA"

    return "MOLTO ALTA"


# ============================================================
# PESO LEARNING
# ============================================================

def peso_learning(totale):

    if totale < 5:
        return 0.05

    if totale < 10:
        return 0.10

    if totale < 20:
        return 0.20

    if totale < 50:
        return 0.35

    if totale < 100:
        return 0.50

    return 0.65


# ============================================================
# FATTORI DI PESO PER FASCE
# ============================================================

def fattore_fascia(totale):

    """
    Evita che poche partite producano
    correzioni troppo forti.
    """

    if totale < 3:
        return 0.0

    if totale < 5:
        return 0.15

    if totale < 10:
        return 0.30

    if totale < 20:
        return 0.50

    if totale < 50:
        return 0.70

    return 1.0


# ============================================================
# CORREZIONE AI SCORE
# ============================================================

def correzione_ai_score(ai_score):

    try:

        score = float(
            ai_score
        )

    except (
        TypeError,
        ValueError
    ):

        return 0

    dati = statistiche_ai_score()

    if score < 60:
        fascia = "0-59"

    elif score < 70:
        fascia = "60-69"

    elif score < 80:
        fascia = "70-79"

    elif score < 90:
        fascia = "80-89"

    else:
        fascia = "90-100"

    storico = dati.get(
        fascia,
        {}
    )

    totale = storico.get(
        "totale",
        0
    )

    precisione = storico.get(
        "precisione",
        0
    )

    if totale < 3:

        print(
            "🧠 LEARNING SCORE |",
            fascia,
            "| Dati insufficienti:",
            totale
        )

        return 0

    differenza = (
        precisione - 50
    )

    fattore = fattore_fascia(
        totale
    )

    correzione = (
        differenza
        * 0.10
        * fattore
    )

    correzione = max(
        -5,
        min(
            5,
            correzione
        )
    )

    print(
        "🧠 LEARNING SCORE |",
        fascia,
        "| Storico:",
        totale,
        "| Precisione:",
        precisione,
        "| Correzione:",
        round(
            correzione,
            2
        )
    )

    return round(
        correzione,
        2
    )


# ============================================================
# CORREZIONE FIDUCIA
# ============================================================

def correzione_fiducia(fiducia):

    try:

        valore = float(
            fiducia
        )

    except (
        TypeError,
        ValueError
    ):

        return 0

    dati = statistiche_fiducia()

    if valore < 60:
        fascia = "0-59"

    elif valore < 70:
        fascia = "60-69"

    elif valore < 80:
        fascia = "70-79"

    elif valore < 90:
        fascia = "80-89"

    else:
        fascia = "90-100"

    storico = dati.get(
        fascia,
        {}
    )

    totale = storico.get(
        "totale",
        0
    )

    precisione = storico.get(
        "precisione",
        0
    )

    if totale < 3:

        print(
            "🧠 LEARNING FIDUCIA |",
            fascia,
            "| Dati insufficienti:",
            totale
        )

        return 0

    differenza = (
        precisione - 50
    )

    fattore = fattore_fascia(
        totale
    )

    correzione = (
        differenza
        * 0.08
        * fattore
    )

    correzione = max(
        -4,
        min(
            4,
            correzione
        )
    )

    print(
        "🧠 LEARNING FIDUCIA |",
        fascia,
        "| Storico:",
        totale,
        "| Precisione:",
        precisione,
        "| Correzione:",
        round(
            correzione,
            2
        )
    )

    return round(
        correzione,
        2
    )


# ============================================================
# VALUE INDEX
# ============================================================

def fascia_value_index(value_index):

    try:

        valore = float(
            value_index
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    if valore < 60:
        return "0-59"

    if valore < 70:
        return "60-69"

    if valore < 80:
        return "70-79"

    if valore < 90:
        return "80-89"

    return "90-100"


# ============================================================
# STATISTICHE VALUE INDEX
# ============================================================

def statistiche_value_index():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                ai_score,
                fiducia,
                esito
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
              AND ai_score IS NOT NULL
              AND fiducia IS NOT NULL
        """)

        rows = cursor.fetchall()

    finally:
        conn.close()

    fasce = {

        "0-59": {
            "totale": 0,
            "corrette": 0,
            "precisione": 0
        },

        "60-69": {
            "totale": 0,
            "corrette": 0,
            "precisione": 0
        },

        "70-79": {
            "totale": 0,
            "corrette": 0,
            "precisione": 0
        },

        "80-89": {
            "totale": 0,
            "corrette": 0,
            "precisione": 0
        },

        "90-100": {
            "totale": 0,
            "corrette": 0,
            "precisione": 0
        },
    }

    # ========================================================
    # PROXY VALUE INDEX
    # ========================================================
    #
    # Il database attuale non contiene una colonna
    # value_index.
    #
    # Usiamo quindi:
    #
    # AI Score 60%
    # Fiducia 40%
    #
    # Solo per l'apprendimento storico.
    #
    # ========================================================

    for ai_score, fiducia, esito in rows:

        try:

            score = float(
                ai_score
            )

            conf = float(
                fiducia
            )

        except (
            TypeError,
            ValueError
        ):

            continue

        value_index = (
            score * 0.60
            +
            conf * 0.40
        )

        fascia = fascia_value_index(
            value_index
        )

        if fascia is None:
            continue

        fasce[fascia]["totale"] += 1

        if esito == "CORRETTO":

            fasce[fascia]["corrette"] += 1

    # ========================================================
    # PRECISIONE
    # ========================================================

    for fascia, dati in fasce.items():

        totale = dati["totale"]

        if totale > 0:

            dati["precisione"] = round(
                (
                    dati["corrette"]
                    /
                    totale
                )
                * 100,
                1
            )

        else:

            dati["precisione"] = 0

    return fasce


# ============================================================
# CORREZIONE VALUE INDEX
# ============================================================

def correzione_value_index(value_index):

    fascia = fascia_value_index(
        value_index
    )

    if fascia is None:
        return 0

    dati = statistiche_value_index()

    storico = dati.get(
        fascia,
        {}
    )

    totale = storico.get(
        "totale",
        0
    )

    precisione = storico.get(
        "precisione",
        0
    )

    # ========================================================
    # DATI INSUFFICIENTI
    # ========================================================

    if totale < 3:

        print(
            "🧠 LEARNING VALUE |",
            fascia,
            "| Dati insufficienti:",
            totale
        )

        return 0

    differenza = (
        precisione - 50
    )

    fattore = fattore_fascia(
        totale
    )

    correzione = (
        differenza
        * 0.08
        * fattore
    )

    correzione = max(
        -4,
        min(
            4,
            correzione
        )
    )

    print(
        "🧠 LEARNING VALUE |",
        fascia,
        "| Storico:",
        totale,
        "| Precisione:",
        precisione,
        "| Correzione:",
        round(
            correzione,
            2
        )
    )

    return round(
        correzione,
        2
    )


# ============================================================
# FATTORE MERCATO
# ============================================================

def fattore_mercato(mercato):

    mercato = normalizza_mercato(
        mercato
    )

    dati = statistiche_mercati()

    storico = dati.get(
        mercato
    )

    if not storico:
        return 0

    totale = storico.get(
        "totale",
        0
    )

    if totale < 3:
        return 0

    if totale < 5:
        return 0.25

    if totale < 10:
        return 0.50

    if totale < 20:
        return 0.75

    return 1.0


# ============================================================
# CORREZIONE LEARNING MERCATO
# ============================================================

def correzione_learning_mercato(mercato):

    mercato = normalizza_mercato(
        mercato
    )

    dati = statistiche_mercati()

    storico = dati.get(
        mercato
    )

    if not storico:
        return 0

    totale = storico.get(
        "totale",
        0
    )

    precisione = storico.get(
        "precisione",
        0
    )

    if totale < 3:
        return 0

    differenza = (
        precisione - 50
    )

    fattore = fattore_mercato(
        mercato
    )

    correzione = (
        differenza
        * fattore
        * 0.25
    )

    correzione = max(
        -10,
        min(
            10,
            correzione
        )
    )

    return round(
        correzione,
        2
    )


# ============================================================
# CONSIGLIO AI
# ============================================================

def consiglio_ai():

    generale = precisione_generale()

    mercati = mercati_affidabili()

    if generale == 0:

        return (
            "📚 Storico ancora insufficiente."
        )

    if generale >= 70:

        livello = "🔥 OTTIMO"

    elif generale >= 60:

        livello = "✅ BUONO"

    elif generale >= 50:

        livello = "⚠️ MEDIO"

    else:

        livello = "🔴 DA MIGLIORARE"

    messaggio = (
        f"{livello}\n"
        f"Precisione generale: {generale}%"
    )

    if mercati:

        migliori = mercati[:3]

        messaggio += (
            "\n\n📊 Mercati più affidabili:"
        )

        for mercato in migliori:

            messaggio += (
                f"\n• {mercato['mercato']}: "
                f"{mercato['precisione']}% "
                f"({mercato['totale']} pronostici)"
            )

    return messaggio


# ============================================================
# RIEPILOGO APPRENDIMENTO
# ============================================================

def riepilogo_apprendimento():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT COUNT(*)
            FROM storico
            WHERE esito IN ('CORRETTO', 'ERRATO')
        """)

        totale = (
            cursor.fetchone()[0]
            or 0
        )

    finally:
        conn.close()

    peso = peso_learning(
        totale
    )

    livello = livello_affidabilita_learning(
        totale
    )

    return {

        "pronostici_verificati":
            totale,

        "peso_learning":
            round(
                peso * 100
            ),

        "livello":
            livello,

        "precisione_generale":
            precisione_generale(),

        "media_ai_score":
            media_ai_score(),

        "media_fiducia":
            media_fiducia(),

        "mercati":
            statistiche_mercati(),

        "ai_score":
            statistiche_ai_score(),

        "fiducia":
            statistiche_fiducia(),

        "value_index":
            statistiche_value_index()
    }