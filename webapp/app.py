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
# DASHBOARD
# ============================================================

@app.route("/")
def home():

    data_test = request.args.get("data")

    print("\n==============================================")
    print("🌐 CALCIOAI - WEB APP")
    print("==============================================")

    if data_test:
        print(f"📅 DATA SELEZIONATA: {data_test}")
        partite = partite_oggi(data_test=data_test)
    else:
        print("📅 DATA: OGGI")
        partite = partite_oggi()

    print(f"⚽ PARTITE TROVATE: {len(partite)}")

    return render_template(
        "index.html",
        partite=partite,
        data_test=data_test
    )


# ============================================================
# MERCATI AI
# ============================================================

@app.route("/mercati")
def mercati():

    data_test = request.args.get("data")

    print("\n==============================================")
    print("🎯 CALCIOAI - MERCATI AI")
    print("==============================================")

    if data_test:
        partite = partite_oggi(data_test=data_test)
    else:
        partite = partite_oggi()

    partite_mercati = []

    for partita in partite:

        try:

            casa = partita.get("casa", "")
            trasferta = partita.get("trasferta", "")

            home_id = partita.get("home_id")
            away_id = partita.get("away_id")

            lega = partita.get("lega", "")
            paese = partita.get("paese", "")
            ora = partita.get("ora", "")

            statistiche_casa = ultime_partite(home_id)
            statistiche_trasferta = ultime_partite(away_id)

            indicatori = calcola_indicatori(
                statistiche_casa,
                statistiche_trasferta
            )

            mercati = calcola_mercati_ai(
                statistiche_casa,
                statistiche_trasferta,
                indicatori
            )

            partite_mercati.append({
                "fixture_id": partita.get("id"),
                "casa": casa,
                "trasferta": trasferta,
                "lega": lega,
                "paese": paese,
                "ora": ora,
                "mercati": mercati,
                "indicatori": indicatori
            })

        except Exception as e:

            print(
                f"⚠️ ERRORE MERCATI "
                f"{partita.get('casa')} - "
                f"{partita.get('trasferta')}: {e}"
            )

    return render_template(
        "mercati.html",
        partite=partite_mercati,
        data_test=data_test
    )


# ============================================================
# TEST DATA
# ============================================================

@app.route("/test/<data_test>")
def test_data(data_test):

    print("\n==============================================")
    print("🧪 CALCIOAI - TEST DATA")
    print("==============================================")
    print(f"📅 DATA TEST: {data_test}")

    partite = partite_oggi(data_test=data_test)

    return render_template(
        "index.html",
        partite=partite,
        data_test=data_test
    )


# ============================================================
# ANALISI PARTITA
# ============================================================

@app.route("/analizza/<int:fixture_id>")
def analizza(fixture_id):

    print("\n==============================================")
    print("🧠 CALCIOAI - ANALISI PARTITA")
    print("==============================================")

    print(f"🔔 FIXTURE ID: {fixture_id}")

    data_test = request.args.get("data")

    print(f"📅 DATA ANALISI TEST: {data_test}")

    # --------------------------------------------------------
    # CARICAMENTO PARTITE
    # --------------------------------------------------------

    print("\n🌐 WEB APP - CARICAMENTO PARTITE")

    if data_test:

        print(f"📅 DATA CALCIOAI: {data_test}")

        partite = partite_oggi(
            data_test=data_test
        )

    else:

        print("📅 DATA CALCIOAI: OGGI")

        partite = partite_oggi()

    print(f"⚽ Partite trovate: {len(partite)}")

    # --------------------------------------------------------
    # CERCA PARTITA
    # --------------------------------------------------------

    partita = None

    for p in partite:

        if str(p.get("id")) == str(fixture_id):

            partita = p
            break

    if partita is None:

        print("❌ PARTITA NON TROVATA")

        return """
        <html>
            <body style="
                background:#080b12;
                color:white;
                font-family:Arial;
                padding:40px;
            ">
                <h1>Partita non trovata</h1>
                <p>
                    La partita richiesta non è disponibile
                    per la data selezionata.
                </p>
            </body>
        </html>
        """, 404

    # --------------------------------------------------------
    # DATI PARTITA
    # --------------------------------------------------------

    casa = partita.get("casa", "")
    trasferta = partita.get("trasferta", "")

    home_id = partita.get("home_id")
    away_id = partita.get("away_id")

    lega = partita.get("lega", "")
    paese = partita.get("paese", "")
    ora = partita.get("ora", "")

    print(f"⚽ {casa} - {trasferta}")
    print(f"🏆 {lega}")

    # --------------------------------------------------------
    # MARCATORI
    # --------------------------------------------------------

    print("\n⚽ ANALISI PROBABILI MARCATORI")

    try:

        marcatori = analizza_marcatori_partite(
            [partita]
        )

    except Exception as e:

        print(
            f"⚠️ ERRORE ANALISI MARCATORI: {e}"
        )

        marcatori = []

    marcatori_casa = []
    marcatori_trasferta = []

    if marcatori:

        try:

            dati_marcatori = marcatori[0]

            marcatori_casa = dati_marcatori.get(
                "marcatori_casa",
                []
            )

            marcatori_trasferta = dati_marcatori.get(
                "marcatori_trasferta",
                []
            )

        except Exception:

            marcatori_casa = []
            marcatori_trasferta = []

    # --------------------------------------------------------
    # STATISTICHE
    # --------------------------------------------------------

    print("\n📊 RECUPERO STATISTICHE")

    statistiche_casa = ultime_partite(
        home_id
    )

    statistiche_trasferta = ultime_partite(
        away_id
    )

    print(
        f"📊 STATISTICHE CASA: "
        f"{statistiche_casa}"
    )

    print(
        f"📊 STATISTICHE TRASFERTA: "
        f"{statistiche_trasferta}"
    )

    # --------------------------------------------------------
    # INDICATORI AI
    # --------------------------------------------------------

    print("\n📈 CALCOLO INDICATORI")

    indicatori = calcola_indicatori(
        statistiche_casa,
        statistiche_trasferta
    )

    print(
        f"📈 INDICATORI AI: "
        f"{indicatori}"
    )

    # --------------------------------------------------------
    # AI SCORE
    # --------------------------------------------------------

    print("\n🤖 CALCOLO AI SCORE")

    ai_score = calcola_ai_score(
        statistiche_casa,
        statistiche_trasferta,
        indicatori,
        lega
    )

    print(
        f"🤖 AI SCORE: {ai_score}"
    )

    # --------------------------------------------------------
    # MERCATI AI
    # --------------------------------------------------------

    print("\n🎯 CALCOLO MERCATI AI")

    mercati = calcola_mercati_ai(
        statistiche_casa,
        statistiche_trasferta,
        indicatori
    )

    print(
        f"🎯 MERCATI AI: {mercati}"
    )

    # --------------------------------------------------------
    # RISCHIO BASE
    # --------------------------------------------------------

    if ai_score >= 90:

        rischio = "🟢 Basso"

    elif ai_score >= 75:

        rischio = "🟡 Medio"

    else:

        rischio = "🔴 Alto"

    print(
        f"⚠️ RISCHIO BASE: {rischio}"
    )

    # --------------------------------------------------------
    # DECISION ENGINE
    # --------------------------------------------------------

    print("\n🧠 DECISION ENGINE")

    decisione = scegli_pronostico(
        mercati,
        ai_score,
        rischio,
        statistiche_casa,
        statistiche_trasferta,
        indicatori,
        lega
    )

    pronostico = decisione.get(
        "mercato",
        decisione.get("pronostico", "")
    )

    fiducia = decisione.get(
        "probabilita",
        decisione.get("fiducia", 0)
    )

    value_index = decisione.get(
        "value_index",
        0
    )

    rischio = decisione.get(
        "rischio",
        rischio
    )

    # --------------------------------------------------------
    # RISULTATI ESATTI
    # --------------------------------------------------------

    print("\n🔢 CALCOLO RISULTATI ESATTI")

    try:

        risultati_esatti = calcola_risultati_esatti(
            statistiche_casa,
            statistiche_trasferta,
            indicatori
        )

        print(
            f"🔢 RISULTATI ESATTI: "
            f"{risultati_esatti}"
        )

    except Exception as e:

        print(
            f"⚠️ ERRORE RISULTATI ESATTI: {e}"
        )

        risultati_esatti = []

    # --------------------------------------------------------
    # RISULTATO DECISIONE
    # --------------------------------------------------------

    print("\n==============================================")
    print("🏆 RISULTATO ANALISI")
    print("==============================================")

    print(
        f"🎯 Pronostico: {pronostico}"
    )

    print(
        f"📊 Fiducia: {fiducia}"
    )

    print(
        f"🤖 AI Score: {ai_score}"
    )

    print(
        f"💰 Value Index: {value_index}"
    )

    print(
        f"⚠️ Rischio: {rischio}"
    )

    # --------------------------------------------------------
    # RENDER TEMPLATE
    # --------------------------------------------------------

    return render_template(
        "analisi.html",

        # DATI PARTITA
        partita=partita,
        data_test=data_test,

        lega=lega,
        casa=casa,
        trasferta=trasferta,
        ora=ora,
        paese=paese,

        # AI
        pronostico=pronostico,
        fiducia=fiducia,
        ai_score=ai_score,
        value_index=value_index,
        rischio=rischio,

        # STATISTICHE
        statistiche_casa=statistiche_casa,
        statistiche_trasferta=statistiche_trasferta,

        # INDICATORI
        indicatori=indicatori,

        # MERCATI
        mercati=mercati,

        # RISULTATI ESATTI
        risultati_esatti=risultati_esatti,

        # MARCATORI
        marcatori_casa=marcatori_casa,
        marcatori_trasferta=marcatori_trasferta,

        # FUNZIONI UTILIZZATE DAL TEMPLATE
        numero=numero,
        classe_probabilita=classe_probabilita
    )


# ============================================================
# AVVIO LOCALE
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )