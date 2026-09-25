import os

from flask import Flask, render_template, request

from services.partite_oggi import partite_oggi
from services.statistiche import ultime_partite
from services.ai_pronostico import calcola_indicatori
from services.ai_score import calcola_ai_score
from services.mercati_ai import calcola_mercati_ai
from services.decision_engine import scegli_pronostico
from services.risultati_ai import calcola_risultati_esatti
from services.marcatori import analizza_marcatori_partite


app = Flask(__name__)


# ============================================================
# UTILITY
# ============================================================

def numero(valore, default=0):

    try:
        return float(valore)

    except (TypeError, ValueError):
        return default


def classe_probabilita(probabilita):

    probabilita = numero(probabilita)

    if probabilita >= 75:
        return "alta"

    if probabilita >= 55:
        return "media"

    return "bassa"


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    print("")
    print("ðŸŒ WEB APP - CARICAMENTO PARTITE")

    try:

        partite = partite_oggi()

        print(
            f"âš½ Partite trovate: {len(partite)}"
        )

        return render_template(
            "index.html",
            partite=partite
        )

    except Exception as e:

        print(
            f"âŒ ERRORE HOME: {e}"
        )

        return (
            f"""
            <h1>Errore CalcioAI</h1>
            <p>{e}</p>
            """,
            500
        )


# ============================================================
# ============================================================
# MERCATI AI
# ============================================================

@app.route("/mercati")
def mercati():

    try:

        data_test = request.args.get("data")

        if data_test:
            partite = partite_oggi(data_test=data_test)
        else:
            partite = partite_oggi()

        print("")
        print(f"Partite Mercati AI: {len(partite)}")

        partite_mercati = []

        for partita in partite:

            try:

                home_id = partita.get("home_id")
                away_id = partita.get("away_id")

                casa = partita.get("casa", "")
                trasferta = partita.get("trasferta", "")
                lega = partita.get("lega", "")
                ora = partita.get("ora", "")
                paese = partita.get("paese", "")

                statistiche_casa = ultime_partite(home_id)
                statistiche_trasferta = ultime_partite(away_id)

                try:

                    indicatori = calcola_indicatori(
                        statistiche_casa,
                        statistiche_trasferta
                    )

                except TypeError:

                    indicatori = calcola_indicatori(
                        statistiche_casa,
                        statistiche_trasferta,
                        casa,
                        trasferta
                    )

                try:

                    mercati = calcola_mercati_ai(
                        statistiche_casa,
                        statistiche_trasferta,
                        indicatori
                    )

                except TypeError:

                    mercati = calcola_mercati_ai(
                        statistiche_casa,
                        statistiche_trasferta
                    )

                partite_mercati.append({
                    "id": partita.get("id"),
                    "casa": casa,
                    "trasferta": trasferta,
                    "lega": lega,
                    "ora": ora,
                    "paese": paese,
                    "data": partita.get("data"),
                    "mercati": mercati
                })

            except Exception as e:

                print(
                    f"Errore Mercati {partita.get('casa')} - "
                    f"{partita.get('trasferta')}: {e}"
                )

        return render_template(
            "mercati.html",
            partite=partite_mercati,
            data_test=data_test
        )

    except Exception as e:

        print(f"Errore Mercati AI: {e}")

        return render_template(
            "mercati.html",
            partite=[],
            data_test=request.args.get("data")
        )

# HOME TEST - DATA STORICA
# ============================================================

@app.route("/test/<data_test>")
def home_test(data_test):

    print("")
    print("ðŸŒ WEB APP - TEST DATA STORICA")
    print(f"ðŸ“… DATA TEST: {data_test}")

    try:

        partite = partite_oggi(
            data_test=data_test
        )

        print(
            f"âš½ Partite trovate: {len(partite)}"
        )

        return render_template(
            "index.html",
            partite=partite
        )

    except Exception as e:

        print(
            f"âŒ ERRORE HOME TEST: {e}"
        )

        return (
            f"""
            <h1>Errore CalcioAI</h1>
            <p>{e}</p>
            """,
            500
        )


# ============================================================
# ANALISI PARTITA
# ============================================================

@app.route("/analizza/<int:fixture_id>")
def analizza(fixture_id):

    print("")
    print("==============================================")
    print("ðŸ§  CALCIOAI - ANALISI PARTITA")
    print("==============================================")
    print(f"ðŸ†” FIXTURE ID: {fixture_id}")

    try:

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        data_test = request.args.get("data")

        if data_test:

            print(
                f"ðŸ“… DATA ANALISI TEST: {data_test}"
            )

        else:

            print(
                "ðŸ“… DATA ANALISI: OGGI"
            )

        # ----------------------------------------------------
        # RECUPERO PARTITE
        # ----------------------------------------------------

        if data_test:

            partite = partite_oggi(
                data_test=data_test
            )

        else:

            partite = partite_oggi()

        partita = None

        for p in partite:

            if int(p["id"]) == int(fixture_id):

                partita = p

                break

        # ----------------------------------------------------
        # PARTITA NON TROVATA
        # ----------------------------------------------------

        if not partita:

            return (
                f"""
                <!DOCTYPE html>

                <html lang="it">

                <head>

                    <meta charset="UTF-8">

                    <title>
                        CalcioAI - Partita non trovata
                    </title>

                </head>

                <body
                    style="
                        background:#0b1020;
                        color:white;
                        font-family:Arial;
                        padding:40px;
                    "
                >

                    <h1>
                        âš ï¸ Partita non trovata
                    </h1>

                    <p>
                        Fixture ID:
                        <strong>{fixture_id}</strong>
                    </p>

                    <p>
                        Data utilizzata:
                        <strong>
                            {data_test if data_test else "oggi"}
                        </strong>
                    </p>

                    <p>
                        La partita non Ã¨ presente
                        nei dati restituiti da Football-Data.org
                        per questa data.
                    </p>

                </body>

                </html>
                """,
                404
            )

        # ----------------------------------------------------
        # DATI PARTITA
        # ----------------------------------------------------

        casa = partita["casa"]
        trasferta = partita["trasferta"]

        home_id = partita["home_id"]
        away_id = partita["away_id"]

        lega = partita.get(
            "lega",
            "Campionato"
        )

        paese = partita.get(
            "paese",
            ""
        )

        ora = partita.get(
            "ora",
            "--:--"
        )

        print(
            f"âš½ {casa} - {trasferta}"
        )

        print(
            f"ðŸ† {lega}"
        )

        # ----------------------------------------------------
        # MARCATORI AI
        # ----------------------------------------------------

        print("")
        print("âš½ ANALISI PROBABILI MARCATORI")

        try:

            analisi_marcatori = analizza_marcatori_partite(
                [partita]
            )

            if analisi_marcatori:

                dati_marcatori = analisi_marcatori[0]

            else:

                dati_marcatori = {
                    "marcatori_casa": [],
                    "marcatori_trasferta": []
                }

        except Exception as e:

            print(
                f"âš ï¸ ERRORE MARCATORI: {e}"
            )

            dati_marcatori = {
                "marcatori_casa": [],
                "marcatori_trasferta": []
            }

        marcatori_casa = dati_marcatori.get(
            "marcatori_casa",
            []
        )

        marcatori_trasferta = dati_marcatori.get(
            "marcatori_trasferta",
            []
        )

        # ----------------------------------------------------
        # STATISTICHE
        # ----------------------------------------------------

        print("")
        print("ðŸ“Š RECUPERO STATISTICHE")

        statistiche_casa = ultime_partite(
            home_id
        )

        statistiche_trasferta = ultime_partite(
            away_id
        )

        # ----------------------------------------------------
        # INDICATORI
        # ----------------------------------------------------

        print("")
        print("ðŸ“ˆ CALCOLO INDICATORI")

        try:

            indicatori = calcola_indicatori(
                statistiche_casa,
                statistiche_trasferta
            )

        except TypeError:

            indicatori = calcola_indicatori(
                statistiche_casa,
                statistiche_trasferta,
                casa,
                trasferta
            )

        # ----------------------------------------------------
        # AI SCORE
        # ----------------------------------------------------

        print("")
        print("ðŸ¤– CALCOLO AI SCORE")

        ai_score = calcola_ai_score(
            statistiche_casa,
            statistiche_trasferta,
            indicatori,
            lega
        )

        print(
            f"ðŸ¤– AI SCORE: {ai_score}"
        )

        # ----------------------------------------------------
        # RISCHIO
        # ----------------------------------------------------

        rischio = "Medio"

        if numero(ai_score) >= 80:

            rischio = "Basso"

        elif numero(ai_score) < 60:

            rischio = "Alto"

        # ----------------------------------------------------
        # MERCATI AI
        # ----------------------------------------------------

        print("")
        print("ðŸŽ¯ CALCOLO MERCATI AI")

        try:

            mercati = calcola_mercati_ai(
                statistiche_casa,
                statistiche_trasferta,
                indicatori
            )

        except TypeError:

            try:

                mercati = calcola_mercati_ai(
                    statistiche_casa,
                    statistiche_trasferta
                )

            except Exception as e:

                print(
                    f"âš ï¸ ERRORE MERCATI: {e}"
                )

                mercati = {}

        except Exception as e:

            print(
                f"âš ï¸ ERRORE MERCATI: {e}"
            )

            mercati = {}

        # ----------------------------------------------------
        # DECISION ENGINE
        # ----------------------------------------------------

        print("")
        print("ðŸ§  DECISION ENGINE")

        try:

            decisione = scegli_pronostico(
                mercati,
                ai_score,
                rischio,
                statistiche_casa,
                statistiche_trasferta,
                indicatori,
                lega
            )

            print(
                f"ðŸ§  DECISIONE AI: {decisione}"
            )

        except Exception as e:

            print(
                f"âš ï¸ ERRORE DECISION ENGINE: {e}"
            )

            decisione = {}

        # ----------------------------------------------------
        # LETTURA PRONOSTICO
        # ----------------------------------------------------

        if isinstance(decisione, dict):

            pronostico = decisione.get(
                "pronostico",
                decisione.get(
                    "mercato",
                    decisione.get(
                        "scelta",
                        "N/D"
                    )
                )
            )

            fiducia = decisione.get(
                "fiducia",
                decisione.get(
                    "probabilita",
                    decisione.get(
                        "confidence",
                        0
                    )
                )
            )

            value_index = decisione.get(
                "value_index",
                decisione.get(
                    "vi",
                    decisione.get(
                        "value",
                        0
                    )
                )
            )

        else:

            pronostico = str(
                decisione
            )

            fiducia = 0
            value_index = 0

        # ----------------------------------------------------
        # RISULTATI ESATTI
        # ----------------------------------------------------

        print("")
        print("ðŸ”¢ CALCOLO RISULTATI ESATTI")

        try:

            risultati_esatti = calcola_risultati_esatti(
                statistiche_casa,
                statistiche_trasferta
            )

        except TypeError:

            try:

                risultati_esatti = calcola_risultati_esatti(
                    statistiche_casa,
                    statistiche_trasferta,
                    indicatori
                )

            except Exception as e:

                print(
                    f"âš ï¸ ERRORE RISULTATI ESATTI: {e}"
                )

                risultati_esatti = []

        except Exception as e:

            print(
                f"âš ï¸ ERRORE RISULTATI ESATTI: {e}"
            )

            risultati_esatti = []

        # ====================================================
        # HTML
        # ====================================================

        html = f"""
        <!DOCTYPE html>

        <html lang="it">

        <head>

            <meta charset="UTF-8">

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1.0"
            >

            <title>
                CalcioAI - {casa} vs {trasferta}
            </title>

            <style>

                body {{
                    margin: 0;
                    padding: 0;
                    background: #0b1020;
                    color: white;
                    font-family: Arial, sans-serif;
                }}

                .container {{
                    max-width: 1100px;
                    margin: auto;
                    padding: 25px;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 25px;
                }}

                .header h1 {{
                    margin-bottom: 5px;
                }}

                .match {{
                    background: #151c32;
                    border-radius: 18px;
                    padding: 25px;
                    text-align: center;
                    margin-bottom: 20px;
                }}

                .teams {{
                    font-size: 28px;
                    font-weight: bold;
                    margin: 15px 0;
                }}

                .meta {{
                    color: #aaa;
                    margin: 5px 0;
                }}

                .card {{
                    background: #151c32;
                    border-radius: 18px;
                    padding: 22px;
                    margin-bottom: 20px;
                }}

                .card h2 {{
                    margin-top: 0;
                }}

                .grid {{
                    display: grid;
                    grid-template-columns:
                        repeat(auto-fit, minmax(220px, 1fr));
                    gap: 15px;
                }}

                .box {{
                    background: #202943;
                    border-radius: 14px;
                    padding: 18px;
                }}

                .value {{
                    font-size: 28px;
                    font-weight: bold;
                    margin-top: 8px;
                }}

                .prediction {{
                    font-size: 30px;
                    font-weight: bold;
                    text-align: center;
                    padding: 20px;
                    background: #202943;
                    border-radius: 15px;
                }}

                .player {{
                    background: #202943;
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 10px;
                }}

                .player-name {{
                    font-size: 19px;
                    font-weight: bold;
                }}

                .small {{
                    color: #aaa;
                    font-size: 14px;
                    margin-top: 5px;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}

                th,
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #303952;
                    text-align: left;
                }}

                th {{
                    color: #aaa;
                }}

                .footer {{
                    text-align: center;
                    color: #777;
                    margin-top: 30px;
                    font-size: 13px;
                }}

            </style>

        </head>

        <body>

        <div class="container">

            <div class="header">

                <h1>
                    âš½ CalcioAI
                </h1>

                <div>
                    Analisi intelligente della partita
                </div>

            </div>


            <!-- PARTITA -->

            <div class="match">

                <div class="meta">
                    ðŸ† {lega}
                </div>

                <div class="teams">

                    {casa}

                    <br>

                    <span style="color:#777;">
                        VS
                    </span>

                    <br>

                    {trasferta}

                </div>

                <div class="meta">
                    ðŸ•’ {ora}
                </div>

                <div class="meta">
                    ðŸŒ {paese}
                </div>

            </div>


            <!-- AI -->

            <div class="card">

                <h2>
                    ðŸ¤– Pronostico AI
                </h2>

                <div class="prediction">

                    {pronostico}

                </div>

                <br>

                <div class="grid">

                    <div class="box">

                        <div>
                            Fiducia
                        </div>

                        <div class="value">

                            {numero(fiducia):.0f}%

                        </div>

                    </div>


                    <div class="box">

                        <div>
                            AI Score
                        </div>

                        <div class="value">

                            {numero(ai_score):.0f}

                        </div>

                    </div>


                    <div class="box">

                        <div>
                            Value Index
                        </div>

                        <div class="value">

                            {numero(value_index):.0f}

                        </div>

                    </div>


                    <div class="box">

                        <div>
                            Rischio
                        </div>

                        <div class="value">

                            {rischio}

                        </div>

                    </div>

                </div>

            </div>


            <!-- STATISTICHE -->

            <div class="card">

                <h2>
                    ðŸ“Š Statistiche recenti
                </h2>

                <div class="grid">

                    <div class="box">

                        <h3>
                            {casa}
                        </h3>

                        <p>
                            Forma:
                            <strong>
                                {statistiche_casa.get("forma", "N/D")}
                            </strong>
                        </p>

                        <p>
                            Gol fatti:
                            <strong>
                                {statistiche_casa.get("gol_fatti", 0)}
                            </strong>
                        </p>

                        <p>
                            Gol subiti:
                            <strong>
                                {statistiche_casa.get("gol_subiti", 0)}
                            </strong>
                        </p>

                        <p>
                            Media gol fatti:
                            <strong>
                                {numero(statistiche_casa.get("media_gol_fatti")):.2f}
                            </strong>
                        </p>

                        <p>
                            Media gol subiti:
                            <strong>
                                {numero(statistiche_casa.get("media_gol_subiti")):.2f}
                            </strong>
                        </p>

                        <p>
                            Over 1.5:
                            <strong>
                                {statistiche_casa.get("over15", 0)}%
                            </strong>
                        </p>

                        <p>
                            Over 2.5:
                            <strong>
                                {statistiche_casa.get("over25", 0)}%
                            </strong>
                        </p>

                        <p>
                            Goal/Goal:
                            <strong>
                                {statistiche_casa.get("golgol", 0)}%
                            </strong>
                        </p>

                    </div>


                    <div class="box">

                        <h3>
                            {trasferta}
                        </h3>

                        <p>
                            Forma:
                            <strong>
                                {statistiche_trasferta.get("forma", "N/D")}
                            </strong>
                        </p>

                        <p>
                            Gol fatti:
                            <strong>
                                {statistiche_trasferta.get("gol_fatti", 0)}
                            </strong>
                        </p>

                        <p>
                            Gol subiti:
                            <strong>
                                {statistiche_trasferta.get("gol_subiti", 0)}
                            </strong>
                        </p>

                        <p>
                            Media gol fatti:
                            <strong>
                                {numero(statistiche_trasferta.get("media_gol_fatti")):.2f}
                            </strong>
                        </p>

                        <p>
                            Media gol subiti:
                            <strong>
                                {numero(statistiche_trasferta.get("media_gol_subiti")):.2f}
                            </strong>
                        </p>

                        <p>
                            Over 1.5:
                            <strong>
                                {statistiche_trasferta.get("over15", 0)}%
                            </strong>
                        </p>

                        <p>
                            Over 2.5:
                            <strong>
                                {statistiche_trasferta.get("over25", 0)}%
                            </strong>
                        </p>

                        <p>
                            Goal/Goal:
                            <strong>
                                {statistiche_trasferta.get("golgol", 0)}%
                            </strong>
                        </p>

                    </div>

                </div>

            </div>


            <!-- INDICATORI -->

            <div class="card">

                <h2>
                    ðŸ“ˆ Indicatori AI
                </h2>

                <div class="grid">
        """

        if isinstance(indicatori, dict):

            for nome, valore in indicatori.items():

                html += f"""
                    <div class="box">

                        <div>
                            {nome}
                        </div>

                        <div class="value">

                            {valore}

                        </div>

                    </div>
                """

        html += """

                </div>

            </div>


            <!-- MERCATI -->

            <div class="card">

                <h2>
                    ðŸŽ¯ Mercati AI
                </h2>

        """

        if isinstance(mercati, dict) and mercati:

            html += """

                <table>

                    <thead>

                        <tr>

                            <th>
                                Mercato
                            </th>

                            <th>
                                ProbabilitÃ 
                            </th>

                        </tr>

                    </thead>

                    <tbody>

            """

            for mercato, dati in mercati.items():

                if isinstance(dati, dict):

                    probabilita = dati.get(
                        "probabilita",
                        dati.get(
                            "prob",
                            dati.get(
                                "confidence",
                                0
                            )
                        )
                    )

                else:

                    probabilita = dati

                html += f"""

                        <tr>

                            <td>
                                {mercato}
                            </td>

                            <td>
                                {numero(probabilita):.0f}%
                            </td>

                        </tr>

                """

            html += """

                    </tbody>

                </table>

            """

        else:

            html += """

                <p>
                    Nessun mercato disponibile.
                </p>

            """

        html += """

            </div>


            <!-- RISULTATI ESATTI -->

            <div class="card">

                <h2>
                    ðŸ”¢ Probabili risultati esatti
                </h2>

        """

        if isinstance(risultati_esatti, list) and risultati_esatti:

            for risultato in risultati_esatti:

                if isinstance(risultato, dict):

                    score = risultato.get(
                        "risultato",
                        risultato.get(
                            "score",
                            risultato.get(
                                "esito",
                                "N/D"
                            )
                        )
                    )

                    probabilita = risultato.get(
                        "probabilita",
                        risultato.get(
                            "prob",
                            0
                        )
                    )

                else:

                    score = str(
                        risultato
                    )

                    probabilita = 0

                html += f"""

                    <div class="player">

                        <div class="player-name">
                            {score}
                        </div>

                        <div class="small">
                            ProbabilitÃ :
                            {numero(probabilita):.0f}%
                        </div>

                    </div>

                """

        else:

            html += """

                <p>
                    Nessun risultato disponibile.
                </p>

            """

        html += """

            </div>


            <!-- MARCATORI -->

            <div class="card">

                <h2>
                    âš½ Probabili Marcatori AI
                </h2>

                <div class="grid">

                    <div>

                        <h3>
        """

        html += casa

        html += """

                        </h3>

        """

        if marcatori_casa:

            for giocatore in marcatori_casa:

                nome = giocatore.get(
                    "nome",
                    "Giocatore"
                )

                gol = giocatore.get(
                    "gol",
                    0
                )

                assist = giocatore.get(
                    "assist",
                    0
                )

                rigori = giocatore.get(
                    "rigori",
                    0
                )

                probabilita = giocatore.get(
                    "probabilita",
                    0
                )

                html += f"""

                        <div class="player">

                            <div class="player-name">
                                âš½ {nome}
                            </div>

                            <div class="small">
                                Gol: {gol}
                                |
                                Assist: {assist}
                                |
                                Rigori: {rigori}
                            </div>

                            <div class="small">
                                ProbabilitÃ  gol:
                                <strong>
                                    {numero(probabilita):.0f}%
                                </strong>
                            </div>

                        </div>

                """

        else:

            html += """

                        <p>
                            Nessun marcatore disponibile.
                        </p>

            """

        html += """

                    </div>


                    <div>

                        <h3>
        """

        html += trasferta

        html += """

                        </h3>

        """

        if marcatori_trasferta:

            for giocatore in marcatori_trasferta:

                nome = giocatore.get(
                    "nome",
                    "Giocatore"
                )

                gol = giocatore.get(
                    "gol",
                    0
                )

                assist = giocatore.get(
                    "assist",
                    0
                )

                rigori = giocatore.get(
                    "rigori",
                    0
                )

                probabilita = giocatore.get(
                    "probabilita",
                    0
                )

                html += f"""

                        <div class="player">

                            <div class="player-name">
                                âš½ {nome}
                            </div>

                            <div class="small">
                                Gol: {gol}
                                |
                                Assist: {assist}
                                |
                                Rigori: {rigori}
                            </div>

                            <div class="small">
                                ProbabilitÃ  gol:
                                <strong>
                                    {numero(probabilita):.0f}%
                                </strong>
                            </div>

                        </div>

                """

        else:

            html += """

                        <p>
                            Nessun marcatore disponibile.
                        </p>

            """

        html += """

                    </div>

                </div>

            </div>


            <div class="footer">

                CalcioAI
                â€”
                Analisi automatizzata
                Football-Data.org

            </div>

        </div>

        </body>

        </html>
        """

        return render_template(
            "analisi.html",
            lega=lega,
            casa=casa,
            trasferta=trasferta,
            ora=ora,
            paese=paese,
            pronostico=pronostico,
            fiducia=fiducia,
            ai_score=ai_score,
            value_index=value_index,
            rischio=rischio,
            statistiche_casa=statistiche_casa,
            statistiche_trasferta=statistiche_trasferta,
            indicatori=indicatori,
            mercati=mercati,
            risultati_esatti=risultati_esatti,
            marcatori_casa=marcatori_casa,
            marcatori_trasferta=marcatori_trasferta
        )

    except Exception as e:

        print("")
        print("âŒ ERRORE ANALISI WEB")
        print(e)

        return (
            f"""
            <h1>Errore durante l'analisi</h1>

            <p>
                {e}
            </p>
            """,
            500
        )


# ============================================================
# AVVIO
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )



