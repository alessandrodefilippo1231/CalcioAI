import sys
import os

# ============================================================
# PATH PROGETTO PRINCIPALE
# ============================================================

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# ============================================================
# FLASK
# ============================================================

from flask import Flask, render_template

# ============================================================
# CALCIOAI
# ============================================================

from services.partite_oggi import partite_oggi
from services.statistiche import ultime_partite
from services.ai_pronostico import calcola_indicatori
from services.ai_score import calcola_ai_score
from services.mercati_ai import calcola_mercati_ai
from services.decision_engine import scegli_pronostico
from services.risultati_ai import calcola_risultati_esatti


# ============================================================
# APP
# ============================================================

app = Flask(__name__)


# ============================================================
# FUNZIONI UTILI
# ============================================================

def numero(valore, decimali=1):
    """
    Converte un valore in numero per la visualizzazione.
    """
    try:
        valore = float(valore)

        if decimali == 0:
            return str(int(round(valore)))

        return f"{valore:.{decimali}f}"

    except Exception:
        return "0"


def classe_probabilita(probabilita):
    """
    Classe grafica in base alla probabilità.
    """

    try:
        probabilita = float(probabilita)
    except Exception:
        probabilita = 0

    if probabilita >= 80:
        return "prob-high"

    if probabilita >= 65:
        return "prob-medium"

    return "prob-low"


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    print("")
    print("🌐 WEB APP - CARICAMENTO PARTITE")

    try:

        partite = partite_oggi()

        print(
            f"⚽ Partite trovate: {len(partite)}"
        )

        return render_template(
            "index.html",
            partite=partite
        )

    except Exception as e:

        print(
            f"❌ ERRORE HOME: {e}"
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
    print("=" * 70)
    print(
        f"🔍 WEB APP - ANALISI FIXTURE {fixture_id}"
    )
    print("=" * 70)

    try:

        # ====================================================
        # PARTITE
        # ====================================================

        partite = partite_oggi()

        partita = None

        for p in partite:

            if int(
                p.get("id", 0)
            ) == int(fixture_id):

                partita = p
                break

        if partita is None:

            return (
                """
                <h1>Partita non trovata</h1>

                <a href="/">
                    ⬅ Torna alle partite
                </a>
                """,
                404
            )

        # ====================================================
        # DATI PARTITA
        # ====================================================

        casa = partita.get(
            "casa",
            "Casa"
        )

        trasferta = partita.get(
            "trasferta",
            "Trasferta"
        )

        lega = partita.get(
            "lega",
            "Campionato"
        )

        ora = partita.get(
            "ora",
            ""
        )

        home_id = partita.get(
            "home_id"
        )

        away_id = partita.get(
            "away_id"
        )

        print("")
        print(
            f"🏠 {casa}"
        )

        print(
            f"✈️ {trasferta}"
        )

        print(
            f"🏆 {lega}"
        )

        print(
            f"⏰ {ora}"
        )

        # ====================================================
        # STATISTICHE
        # ====================================================

        print("")
        print("📊 Recupero statistiche...")

        stats_casa = ultime_partite(
            home_id
        )

        stats_trasferta = ultime_partite(
            away_id
        )

        if not isinstance(
            stats_casa,
            dict
        ):
            stats_casa = {}

        if not isinstance(
            stats_trasferta,
            dict
        ):
            stats_trasferta = {}

        print(
            f"📊 Stats casa: {stats_casa}"
        )

        print(
            f"📊 Stats trasferta: {stats_trasferta}"
        )

        # ====================================================
        # INDICATORI
        # ====================================================

        print("")
        print("📈 Calcolo indicatori...")

        indicatori = calcola_indicatori(
            stats_casa,
            stats_trasferta
        )

        if not isinstance(
            indicatori,
            dict
        ):
            indicatori = {}

        print(
            f"📈 Indicatori: {indicatori}"
        )

        # ====================================================
        # INDICATORI AI - VISUALIZZAZIONE
        # ====================================================

        indicatori_visuali = []

        nomi_indicatori = {
            "over15": "📈 Over 1.5",
            "over25": "📈 Over 2.5",
            "golgol": "⚽ Goal",
            "under35": "📉 Under 3.5"
        }

        for key, value in indicatori.items():

            nome = nomi_indicatori.get(
                key,
                key
            )

            try:
                valore = float(value)
            except Exception:
                valore = 0

            indicatori_visuali.append(
                (
                    nome,
                    valore
                )
            )

        # ====================================================
        # AI SCORE
        # ====================================================

        print("")
        print("🤖 Calcolo AI SCORE...")

        ai_score_base = calcola_ai_score(
            stats_casa,
            stats_trasferta,
            indicatori,
            lega
        )

        try:

            ai_score_base = float(
                ai_score_base
            )

        except Exception:

            ai_score_base = 0

        print(
            f"🤖 AI SCORE: {ai_score_base:.1f}"
        )

        # ====================================================
        # RISCHIO BASE
        # ====================================================

        if ai_score_base >= 85:

            rischio_base = "Basso"

        elif ai_score_base >= 70:

            rischio_base = "Medio"

        else:

            rischio_base = "Alto"

        print(
            f"⚠️ Rischio base: {rischio_base}"
        )

        # ====================================================
        # MERCATI AI
        # ====================================================

        print("")
        print("🎯 Calcolo mercati AI...")

        mercati = calcola_mercati_ai(
            stats_casa,
            stats_trasferta,
            indicatori
        )

        if not isinstance(
            mercati,
            dict
        ):
            mercati = {}

        print(
            f"🎯 Mercati: {mercati}"
        )

        # ====================================================
        # DECISION ENGINE
        # ====================================================

        print("")
        print("🧠 Avvio Decision Engine...")

        decisione = scegli_pronostico(
            mercati=mercati,
            ai_score=ai_score_base,
            indicatori=indicatori,
            lega=lega,
            rischio=rischio_base
        )

        if not isinstance(
            decisione,
            dict
        ):

            decisione = {}

        print("")
        print(
            f"🧠 Decisione: {decisione}"
        )

        # ====================================================
        # PRONOSTICO
        # ====================================================

        pronostico = decisione.get(
            "mercato",
            "Nessun pronostico"
        )

        probabilita = decisione.get(
            "probabilita",
            0
        )

        value_index = decisione.get(
            "value_index",
            0
        )

        rischio = decisione.get(
            "rischio",
            rischio_base
        )

        score_finale = decisione.get(
            "score_finale",
            ai_score_base
        )

        affidabilita = decisione.get(
            "affidabilita_complessiva",
            0
        )

        giudizio = decisione.get(
            "giudizio",
            ""
        )

        classifica = decisione.get(
            "classifica",
            []
        )

        # ====================================================
        # RISULTATI ESATTI
        # ====================================================

        print("")
        print("🎯 Calcolo risultati esatti...")

        risultati_esatti = calcola_risultati_esatti(
            stats_casa,
            stats_trasferta,
            indicatori,
            numero_risultati=3
        )

        if not isinstance(
            risultati_esatti,
            list
        ):
            risultati_esatti = []

        print("")
        print(
            f"🎯 RISULTATI ESATTI DA MOSTRARE: "
            f"{risultati_esatti}"
        )

        # ====================================================
        # FORMA
        # ====================================================

        forma_casa = stats_casa.get(
            "forma",
            ""
        )

        forma_trasferta = stats_trasferta.get(
            "forma",
            ""
        )

        # ====================================================
        # STATISTICHE GOL
        # ====================================================

        gol_fatti_casa = stats_casa.get(
            "gol_fatti",
            0
        )

        gol_subiti_casa = stats_casa.get(
            "gol_subiti",
            0
        )

        gol_fatti_trasferta = stats_trasferta.get(
            "gol_fatti",
            0
        )

        gol_subiti_trasferta = stats_trasferta.get(
            "gol_subiti",
            0
        )

        # ====================================================
        # HTML RISULTATI ESATTI
        # ====================================================

        risultati_html = ""

        if risultati_esatti:

            for indice, risultato in enumerate(
                risultati_esatti,
                start=1
            ):

                if isinstance(
                    risultato,
                    dict
                ):

                    score = risultato.get(
                        "risultato",
                        "-"
                    )

                    prob = risultato.get(
                        "probabilita",
                        0
                    )

                else:

                    score = str(
                        risultato
                    )

                    prob = 0

                risultati_html += f"""
                <div class="exact-score">

                    <div class="exact-position">
                        #{indice}
                    </div>

                    <div class="exact-result">
                        ⚽ {score}
                    </div>

                    <div class="exact-probability">
                        {numero(prob, 1)}%
                    </div>

                </div>
                """

        else:

            risultati_html = """
            <div class="no-results">
                Nessun risultato esatto disponibile.
            </div>
            """

        # ====================================================
        # HTML MERCATI AI
        # ====================================================

        mercati_1x2 = [
            ("1", mercati.get("1", 0)),
            ("X", mercati.get("X", 0)),
            ("2", mercati.get("2", 0)),
        ]

        mercati_over_under = [
            ("Over 1.5", mercati.get("Over 1.5", 0)),
            ("Over 2.5", mercati.get("Over 2.5", 0)),
            ("Under 3.5", mercati.get("Under 3.5", 0)),
        ]

        mercati_goal = [
            ("Goal", mercati.get("Goal", 0)),
            ("No Goal", mercati.get("No Goal", 0)),
        ]

        mercati_doppia_chance = [
            ("1X", mercati.get("1X", 0)),
            ("X2", mercati.get("X2", 0)),
            ("12", mercati.get("12", 0)),
        ]

        # ----------------------------------------------------
        # HTML 1X2
        # ----------------------------------------------------

        html_1x2 = ""

        for nome, prob in mercati_1x2:

            html_1x2 += f"""
            <div class="market-row">

                <div class="market-name">
                    <strong>
                        {nome}
                    </strong>
                </div>

                <div class="market-bar-container">

                    <div class="market-bar">

                        <div
                            class="market-fill {classe_probabilita(prob)}"
                            style="width:{prob}%"
                        ></div>

                    </div>

                </div>

                <div class="market-value">
                    {numero(prob, 0)}%
                </div>

            </div>
            """

        # ----------------------------------------------------
        # HTML OVER / UNDER
        # ----------------------------------------------------

        html_over_under = ""

        for nome, prob in mercati_over_under:

            html_over_under += f"""
            <div class="market-row">

                <div class="market-name">
                    <strong>
                        {nome}
                    </strong>
                </div>

                <div class="market-bar-container">

                    <div class="market-bar">

                        <div
                            class="market-fill {classe_probabilita(prob)}"
                            style="width:{prob}%"
                        ></div>

                    </div>

                </div>

                <div class="market-value">
                    {numero(prob, 0)}%
                </div>

            </div>
            """

        # ----------------------------------------------------
        # HTML GOAL
        # ----------------------------------------------------

        html_goal = ""

        for nome, prob in mercati_goal:

            html_goal += f"""
            <div class="market-row">

                <div class="market-name">
                    <strong>
                        {nome}
                    </strong>
                </div>

                <div class="market-bar-container">

                    <div class="market-bar">

                        <div
                            class="market-fill {classe_probabilita(prob)}"
                            style="width:{prob}%"
                        ></div>

                    </div>

                </div>

                <div class="market-value">
                    {numero(prob, 0)}%
                </div>

            </div>
            """

        # ----------------------------------------------------
        # HTML DOPPIA CHANCE
        # ----------------------------------------------------

        html_doppia_chance = ""

        for nome, prob in mercati_doppia_chance:

            html_doppia_chance += f"""
            <div class="market-row">

                <div class="market-name">
                    <strong>
                        {nome}
                    </strong>
                </div>

                <div class="market-bar-container">

                    <div class="market-bar">

                        <div
                            class="market-fill {classe_probabilita(prob)}"
                            style="width:{prob}%"
                        ></div>

                    </div>

                </div>

                <div class="market-value">
                    {numero(prob, 0)}%
                </div>

            </div>
            """

        # ====================================================
        # HTML CLASSIFICA VALUE INDEX
        # ====================================================

        classifica_html = ""

        if isinstance(
            classifica,
            list
        ):

            for indice, elemento in enumerate(
                classifica,
                start=1
            ):

                try:

                    mercato = elemento[0]
                    valore = elemento[1]

                except Exception:

                    continue

                classifica_html += f"""
                <div class="ranking-row">

                    <span>
                        #{indice} {mercato}
                    </span>

                    <strong>
                        VI {valore}
                    </strong>

                </div>
                """

        # ====================================================
        # AI SCORE VISUALE
        # ====================================================

        ai_score_visuale = max(
            0,
            min(
                100,
                ai_score_base
            )
        )

        # ====================================================
        # HTML FINALE
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
    CalcioAI - Analisi {casa} vs {trasferta}
</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    padding: 20px;

    background:
        linear-gradient(
            135deg,
            #050505,
            #101010
        );

    color: #ffffff;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

}}

.container {{

    max-width: 1000px;

    margin: auto;

}}

.back-button {{

    display: inline-block;

    padding: 10px 18px;

    margin-bottom: 20px;

    background: #1c1c1c;

    color: #ffffff;

    text-decoration: none;

    border-radius: 10px;

    border: 1px solid #333;

}}

.back-button:hover {{

    background: #292929;

}}

.header {{

    background:
        linear-gradient(
            135deg,
            #171717,
            #0d0d0d
        );

    border: 1px solid #2d2d2d;

    border-radius: 20px;

    padding: 30px;

    text-align: center;

    margin-bottom: 20px;

}}

.header h1 {{

    margin: 0 0 15px 0;

    font-size: 30px;

}}

.match-info {{

    color: #aaa;

    font-size: 15px;

}}

.vs {{

    margin: 12px 0;

    font-size: 18px;

    color: #777;

}}

.grid {{

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                280px,
                1fr
            )
        );

    gap: 18px;

}}

.card {{

    background: #111111;

    border: 1px solid #2b2b2b;

    border-radius: 18px;

    padding: 22px;

    margin-bottom: 18px;

}}

.card h2 {{

    margin-top: 0;

    font-size: 19px;

}}

.prediction {{

    text-align: center;

}}

.prediction-market {{

    font-size: 30px;

    font-weight: bold;

    margin: 15px 0;

}}

.probability {{

    font-size: 22px;

    font-weight: bold;

}}

.value-index {{

    font-size: 18px;

    margin-top: 8px;

    color: #cccccc;

}}

.risk {{

    margin-top: 15px;

    font-size: 18px;

    font-weight: bold;

}}

.ai-score-number {{

    font-size: 42px;

    font-weight: bold;

    text-align: center;

    margin: 10px 0;

}}

.score-bar {{

    width: 100%;

    height: 14px;

    background: #292929;

    border-radius: 20px;

    overflow: hidden;

}}

.score-fill {{

    height: 100%;

    width: {ai_score_visuale}%;

    background:
        linear-gradient(
            90deg,
            #555555,
            #ffffff
        );

    border-radius: 20px;

}}

.stat-row {{

    display: flex;

    justify-content: space-between;

    align-items: center;

    padding: 9px 0;

    border-bottom: 1px solid #222;

}}

.stat-row:last-child {{

    border-bottom: none;

}}

.stat-label {{

    color: #999;

}}

.stat-value {{

    font-weight: bold;

}}

.form {{

    font-size: 20px;

    letter-spacing: 5px;

    margin-top: 8px;

}}

.form-casa {{

    color: #ffffff;

}}

.form-trasferta {{

    color: #bbbbbb;

}}

.exact-results-card {{

    background:
        linear-gradient(
            135deg,
            #151515,
            #0d0d0d
        );

    border: 1px solid #3a3a3a;

    border-radius: 20px;

    padding: 25px;

    margin-bottom: 20px;

}}

.exact-results-title {{

    text-align: center;

    font-size: 23px;

    font-weight: bold;

    margin-bottom: 20px;

}}

.exact-results-subtitle {{

    text-align: center;

    color: #888;

    font-size: 13px;

    margin-top: -12px;

    margin-bottom: 20px;

}}

.exact-score {{

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 17px 18px;

    margin: 10px 0;

    background: #1a1a1a;

    border: 1px solid #303030;

    border-radius: 14px;

}}

.exact-position {{

    width: 55px;

    color: #888;

    font-weight: bold;

}}

.exact-result {{

    flex: 1;

    text-align: center;

    font-size: 25px;

    font-weight: bold;

}}

.exact-probability {{

    width: 75px;

    text-align: right;

    font-size: 20px;

    font-weight: bold;

}}

.no-results {{

    text-align: center;

    color: #888;

    padding: 20px;

}}

.markets-section {{

    margin-bottom: 20px;

}}

.market-card {{

    background: #111111;

    border: 1px solid #2b2b2b;

    border-radius: 18px;

    padding: 22px;

    margin-bottom: 18px;

}}

.market-card h3 {{

    margin: 0 0 18px 0;

    font-size: 18px;

}}

.market-row {{

    display: flex;

    align-items: center;

    gap: 12px;

    padding: 12px 0;

    border-bottom: 1px solid #222;

}}

.market-row:last-child {{

    border-bottom: none;

}}

.market-name {{

    width: 105px;

    min-width: 105px;

}}

.market-bar-container {{

    flex: 1;

}}

.market-bar {{

    height: 10px;

    width: 100%;

    background: #292929;

    border-radius: 20px;

    overflow: hidden;

}}

.market-fill {{

    height: 100%;

    border-radius: 20px;

}}

.prob-high {{

    background: #ffffff;

}}

.prob-medium {{

    background: #bbbbbb;

}}

.prob-low {{

    background: #666666;

}}

.market-value {{

    width: 55px;

    min-width: 55px;

    text-align: right;

    font-weight: bold;

}}

.ranking-row {{

    display: flex;

    justify-content: space-between;

    padding: 11px 0;

    border-bottom: 1px solid #222;

}}

.ranking-row:last-child {{

    border-bottom: none;

}}

.judgment {{

    color: #cccccc;

    line-height: 1.5;

}}

.small-note {{

    color: #777;

    font-size: 12px;

    margin-top: 15px;

    text-align: center;

}}

@media (max-width: 600px) {{

    body {{
        padding: 12px;
    }}

    .header {{
        padding: 22px 15px;
    }}

    .header h1 {{
        font-size: 24px;
    }}

    .market-row {{
        gap: 8px;
    }}

    .market-name {{
        width: 85px;
        min-width: 85px;
        font-size: 14px;
    }}

    .market-value {{
        width: 50px;
        min-width: 50px;
    }}

    .exact-result {{
        font-size: 22px;
    }}

}}

</style>

</head>

<body>

<div class="container">

    <!-- ==================================================
         BACK
         ================================================== -->

    <a
        href="/"
        class="back-button"
    >
        ⬅ Torna alle partite
    </a>


    <!-- ==================================================
         HEADER PARTITA
         ================================================== -->

    <div class="header">

        <h1>

            ⚽ {casa}

            <br>

            <span class="vs">
                VS
            </span>

            <br>

            {trasferta}

        </h1>

        <div class="match-info">

            🏆 {lega}

            &nbsp;&nbsp; | &nbsp;&nbsp;

            ⏰ {ora}

        </div>

    </div>


    <!-- ==================================================
         PRONOSTICO + AI SCORE
         ================================================== -->

    <div class="grid">

        <div class="card prediction">

            <h2>
                🎯 Pronostico AI
            </h2>

            <div class="prediction-market">

                {pronostico}

            </div>

            <div class="probability">

                Probabilità:
                {numero(probabilita, 1)}%

            </div>

            <div class="value-index">

                Value Index:

                <strong>
                    {numero(value_index, 1)}
                </strong>

            </div>

            <div class="risk">

                Rischio:
                {rischio}

            </div>

        </div>


        <div class="card">

            <h2>
                🤖 AI SCORE
            </h2>

            <div class="ai-score-number">

                {numero(ai_score_base, 1)}

            </div>

            <div class="score-bar">

                <div class="score-fill"></div>

            </div>

            <div class="small-note">

                Score base del motore AI

            </div>

        </div>

    </div>


    <!-- ==================================================
         RISULTATI ESATTI
         ================================================== -->

    <div class="exact-results-card">

        <div class="exact-results-title">

            🎯 RISULTATI ESATTI AI

        </div>

        <div class="exact-results-subtitle">

            I 3 risultati con la probabilità stimata più alta

        </div>

        {risultati_html}

        <div class="small-note">

            Le percentuali sono probabilità individuali
            dei singoli risultati.

        </div>

    </div>


    <!-- ==================================================
         MERCATI AI
         ================================================== -->

    <div class="markets-section">

        <div class="market-card">

            <h3>
                ⚽ 1X2
            </h3>

            {html_1x2}

        </div>


        <div class="market-card">

            <h3>
                📈 Over / Under
            </h3>

            {html_over_under}

        </div>


        <div class="market-card">

            <h3>
                🎯 Goal / No Goal
            </h3>

            {html_goal}

        </div>


        <div class="market-card">

            <h3>
                🛡️ Doppia Chance
            </h3>

            {html_doppia_chance}

        </div>

    </div>


    <!-- ==================================================
         STATISTICHE SQUADRE
         ================================================== -->

    <div class="grid">

        <div class="card">

            <h2>
                🏠 {casa}
            </h2>

            <div class="stat-row">

                <span class="stat-label">
                    Forma
                </span>

                <span class="stat-value form form-casa">
                    {forma_casa}
                </span>

            </div>

            <div class="stat-row">

                <span class="stat-label">
                    Gol fatti
                </span>

                <span class="stat-value">
                    {gol_fatti_casa}
                </span>

            </div>

            <div class="stat-row">

                <span class="stat-label">
                    Gol subiti
                </span>

                <span class="stat-value">
                    {gol_subiti_casa}
                </span>

            </div>

        </div>


        <div class="card">

            <h2>
                ✈️ {trasferta}
            </h2>

            <div class="stat-row">

                <span class="stat-label">
                    Forma
                </span>

                <span class="stat-value form form-trasferta">
                    {forma_trasferta}
                </span>

            </div>

            <div class="stat-row">

                <span class="stat-label">
                    Gol fatti
                </span>

                <span class="stat-value">
                    {gol_fatti_trasferta}
                </span>

            </div>

            <div class="stat-row">

                <span class="stat-label">
                    Gol subiti
                </span>

                <span class="stat-value">
                    {gol_subiti_trasferta}
                </span>

            </div>

        </div>

    </div>


    <!-- ==================================================
         INDICATORI
         ================================================== -->

    <div class="card">

        <h2>
            📊 Indicatori AI
        </h2>

        <div class="grid">

            {
                "".join(
                    f'''
                    <div class="stat-row">

                        <span class="stat-label">
                            {nome}
                        </span>

                        <span class="stat-value">
                            {numero(value, 0)}%
                        </span>

                    </div>
                    '''
                    for nome, value
                    in indicatori_visuali
                )
            }

        </div>

    </div>


    <!-- ==================================================
         VALUE INDEX
         ================================================== -->

    <div class="card">

        <h2>
            🏆 Classifica Value Index
        </h2>

        {classifica_html}

    </div>


    <!-- ==================================================
         GIUDIZIO
         ================================================== -->

    <div class="card">

        <h2>
            🧠 Giudizio AI
        </h2>

        <p class="judgment">

            {giudizio}

        </p>

        <div class="stat-row">

            <span class="stat-label">
                Score finale
            </span>

            <span class="stat-value">
                {numero(score_finale, 2)}
            </span>

        </div>

        <div class="stat-row">

            <span class="stat-label">
                Affidabilità complessiva
            </span>

            <span class="stat-value">
                {numero(affidabilita, 1)}%
            </span>

        </div>

    </div>


    <!-- ==================================================
         FOOTER
         ================================================== -->

    <div class="small-note">

        CalcioAI • Analisi statistica automatizzata

    </div>

</div>

</body>

</html>
        """

        return html

    # ========================================================
    # ERRORE
    # ========================================================

    except Exception as e:

        print("")
        print(
            "❌ ERRORE ANALISI WEB:"
        )

        print(
            repr(e)
        )

        return (
            f"""
            <html>

            <head>

                <title>
                    Errore CalcioAI
                </title>

            </head>

            <body
                style="
                    background:#111;
                    color:white;
                    font-family:Arial;
                    padding:30px;
                "
            >

                <h1>
                    ❌ Errore durante l'analisi
                </h1>

                <p>
                    {e}
                </p>

                <br>

                <a
                    href="/"
                    style="color:white;"
                >
                    ⬅ Torna alle partite
                </a>

            </body>

            </html>
            """,
            500
        )


# ============================================================
# AVVIO
# ============================================================

if __name__ == "__main__":

    print("")
    print("🌐 CalcioAI Web App avviata")
    print("🔗 http://127.0.0.1:5000")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )