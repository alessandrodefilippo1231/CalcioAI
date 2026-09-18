import sqlite3
from datetime import datetime


DATABASE = "database/calcioai.db"


# ============================================================
# CONNESSIONE DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE)


# ============================================================
# CREAZIONE DATABASE
# ============================================================

def crea_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS storico (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fixture_id INTEGER,

            data TEXT,

            data_partita TEXT,

            campionato TEXT,

            casa TEXT,

            trasferta TEXT,

            pronostico TEXT,

            fiducia REAL,

            ai_score REAL,

            rischio TEXT,

            risultato TEXT,

            esito TEXT
        )
    """)

    conn.commit()
    conn.close()

    print("💾 DATABASE STORICO PRONTO")


# ============================================================
# ESTRAI DATI PARTITA
# ============================================================

def estrai_dati_partita(partita):

    # ========================================================
    # FORMATO API-FOOTBALL COMPLETO
    # ========================================================

    fixture = partita.get(
        "fixture"
    )

    teams = partita.get(
        "teams"
    )

    league = partita.get(
        "league"
    )

    if fixture:

        fixture_id = fixture.get(
            "id"
        )

        data_partita = fixture.get(
            "date"
        )

        if teams:

            casa = teams.get(
                "home",
                {}
            ).get(
                "name",
                "Casa"
            )

            trasferta = teams.get(
                "away",
                {}
            ).get(
                "name",
                "Trasferta"
            )

        else:

            casa = partita.get(
                "casa",
                "Casa"
            )

            trasferta = partita.get(
                "trasferta",
                "Trasferta"
            )

        if league:

            campionato = league.get(
                "name",
                ""
            )

        else:

            campionato = partita.get(
                "lega",
                ""
            )

        return {
            "fixture_id": fixture_id,
            "data_partita": data_partita,
            "campionato": campionato,
            "casa": casa,
            "trasferta": trasferta
        }

    # ========================================================
    # FORMATO FLATTENED USATO DA PARTITE_OGGI
    # ========================================================

    fixture_id = partita.get(
        "id"
    )

    data_partita = (
        partita.get("data")
        or
        partita.get("date")
        or
        partita.get("fixture_date")
    )

    campionato = (
        partita.get("lega")
        or
        partita.get("campionato")
        or
        ""
    )

    casa = partita.get(
        "casa",
        "Casa"
    )

    trasferta = partita.get(
        "trasferta",
        "Trasferta"
    )

    return {
        "fixture_id": fixture_id,
        "data_partita": data_partita,
        "campionato": campionato,
        "casa": casa,
        "trasferta": trasferta
    }


# ============================================================
# SALVA PRONOSTICO
# ============================================================

def salva_pronostico(
    partita,
    analisi,
    forza=False
):

    dati = estrai_dati_partita(
        partita
    )

    fixture_id = dati[
        "fixture_id"
    ]

    data_partita = dati[
        "data_partita"
    ]

    campionato = dati[
        "campionato"
    ]

    casa = dati[
        "casa"
    ]

    trasferta = dati[
        "trasferta"
    ]

    pronostico = analisi.get(
        "pronostico",
        "Nessun pronostico"
    )

    fiducia = analisi.get(
        "fiducia",
        0
    )

    ai_score = analisi.get(
        "ai_score",
        0
    )

    rischio = analisi.get(
        "rischio",
        "N/D"
    )

    # ========================================================
    # CONTROLLO PRONOSTICO
    # ========================================================

    if (
        not pronostico
        or pronostico == "Nessun pronostico"
        or pronostico == "Dati insufficienti"
    ):

        print(
            f"⚠️ PRONOSTICO NON SALVATO: "
            f"{casa} - {trasferta}"
        )

        return False

    # ========================================================
    # CONTROLLO ID
    # ========================================================

    if not fixture_id:

        print(
            f"❌ IMPOSSIBILE SALVARE: "
            f"fixture_id mancante | "
            f"{casa} - {trasferta}"
        )

        return False

    # ========================================================
    # DATABASE
    # ========================================================

    conn = get_connection()
    cursor = conn.cursor()

    # ========================================================
    # CONTROLLO DUPLICATO
    # ========================================================

    cursor.execute(
        """
        SELECT id
        FROM storico
        WHERE fixture_id = ?
        AND pronostico = ?
        """,
        (
            fixture_id,
            pronostico
        )
    )

    esistente = cursor.fetchone()

    if esistente and not forza:

        print(
            f"📚 STORICO: già presente | "
            f"{casa} - {trasferta} | "
            f"{pronostico}"
        )

        conn.close()

        return False

    # ========================================================
    # DATA SALVATAGGIO
    # ========================================================

    data_salvataggio = (
        datetime.now().isoformat()
    )

    # ========================================================
    # INSERIMENTO
    # ========================================================

    cursor.execute(
        """
        INSERT INTO storico (

            fixture_id,
            data,
            data_partita,
            campionato,
            casa,
            trasferta,
            pronostico,
            fiducia,
            ai_score,
            rischio,
            risultato,
            esito

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            fixture_id,
            data_salvataggio,
            data_partita,
            campionato,
            casa,
            trasferta,
            pronostico,
            fiducia,
            ai_score,
            rischio,
            None,
            None
        )
    )

    conn.commit()

    nuovo_id = cursor.lastrowid

    conn.close()

    print(
        f"📚 STORICO SALVATO | "
        f"ID: {nuovo_id} | "
        f"{casa} - {trasferta} | "
        f"{pronostico}"
    )

    return True


# ============================================================
# STATISTICHE STORICO
# ============================================================

def statistiche_storico():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM storico
        """
    )

    totale = (
        cursor.fetchone()[0]
        or 0
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM storico
        WHERE esito IS NULL
        """
    )

    pending = (
        cursor.fetchone()[0]
        or 0
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM storico
        WHERE esito = 'CORRETTO'
        """
    )

    corrette = (
        cursor.fetchone()[0]
        or 0
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM storico
        WHERE esito = 'ERRATO'
        """
    )

    errate = (
        cursor.fetchone()[0]
        or 0
    )

    conn.close()

    verificate = (
        corrette
        +
        errate
    )

    if verificate:

        precisione = round(
            corrette
            /
            verificate
            *
            100,
            1
        )

    else:

        precisione = 0

    return {
        "totale": totale,
        "pending": pending,
        "corrette": corrette,
        "errate": errate,
        "precisione": precisione
    }


# ============================================================
# AGGIORNA ESITO
# ============================================================

def aggiorna_esito(
    id_analisi,
    risultato,
    esito
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE storico

        SET
            risultato = ?,
            esito = ?

        WHERE id = ?
        """,

        (
            risultato,
            esito,
            id_analisi
        )
    )

    conn.commit()

    modificati = cursor.rowcount

    conn.close()

    if modificati:

        print(
            f"📊 STORICO AGGIORNATO | "
            f"ID: {id_analisi} | "
            f"Risultato: {risultato} | "
            f"Esito: {esito}"
        )

        return True

    print(
        f"⚠️ NESSUNA ANALISI TROVATA | "
        f"ID: {id_analisi}"
    )

    return False


# ============================================================
# PRONOSTICI IN ATTESA
# ============================================================

def pronostici_in_attesa():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            id,
            fixture_id,
            data_partita,
            campionato,
            casa,
            trasferta,
            pronostico,
            fiducia,
            ai_score,
            rischio

        FROM storico

        WHERE esito IS NULL

        ORDER BY data_partita ASC
        """
    )

    righe = cursor.fetchall()

    conn.close()

    risultati = []

    for riga in righe:

        risultati.append({

            "id": riga[0],

            "fixture_id": riga[1],

            "data_partita": riga[2],

            "campionato": riga[3],

            "casa": riga[4],

            "trasferta": riga[5],

            "pronostico": riga[6],

            "fiducia": riga[7],

            "ai_score": riga[8],

            "rischio": riga[9]
        })

    return risultati


# ============================================================
# MEDIA FIDUCIA
# ============================================================

def media_fiducia():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT AVG(fiducia)

        FROM storico

        WHERE esito IN (
            'CORRETTO',
            'ERRATO'
        )
        """
    )

    risultato = cursor.fetchone()[0]

    conn.close()

    if risultato is None:
        return 0

    return round(
        risultato,
        1
    )


# ============================================================
# ULTIMO PRONOSTICO
# ============================================================

def ultimo_pronostico():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            id,
            fixture_id,
            data_partita,
            campionato,
            casa,
            trasferta,
            pronostico,
            fiducia,
            ai_score,
            rischio,
            risultato,
            esito

        FROM storico

        ORDER BY id DESC

        LIMIT 1
        """
    )

    riga = cursor.fetchone()

    conn.close()

    if not riga:
        return None

    return {

        "id": riga[0],

        "fixture_id": riga[1],

        "data_partita": riga[2],

        "campionato": riga[3],

        "casa": riga[4],

        "trasferta": riga[5],

        "pronostico": riga[6],

        "fiducia": riga[7],

        "ai_score": riga[8],

        "rischio": riga[9],

        "risultato": riga[10],

        "esito": riga[11]
    }


# ============================================================
# STATISTICHE MERCATI
# ============================================================

def statistiche_mercati():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
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

        WHERE esito IN (
            'CORRETTO',
            'ERRATO'
        )

        GROUP BY pronostico
        """
    )

    righe = cursor.fetchall()

    conn.close()

    risultati = {}

    for mercato, totale, corrette in righe:

        corrette = corrette or 0

        precisione = (
            round(
                corrette
                /
                totale
                *
                100,
                1
            )
            if totale
            else 0
        )

        risultati[mercato] = {

            "totale":
                totale,

            "corrette":
                corrette,

            "precisione":
                precisione
        }

    return risultati