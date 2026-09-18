import sys
import os

# Permette alla Web App di utilizzare i servizi di CalcioAI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string
from services.partite_oggi import partite_oggi

app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>CalcioAI</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: #07111f;
            color: white;
        }

        .header {
            background: linear-gradient(135deg, #0b1d35, #102b4d);
            padding: 28px 20px;
            text-align: center;
            border-bottom: 1px solid #1c395b;
        }

        .logo {
            font-size: 32px;
            font-weight: bold;
        }

        .subtitle {
            margin-top: 8px;
            color: #9fb3c8;
            font-size: 15px;
        }

        .container {
            max-width: 1100px;
            margin: auto;
            padding: 25px 18px 50px;
        }

        .section-title {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 18px;
        }

        .matches {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
            gap: 18px;
        }

        .match-card {
            background: #0d1c2f;
            border: 1px solid #1c3857;
            border-radius: 18px;
            padding: 20px;
            transition: 0.2s;
        }

        .match-card:hover {
            transform: translateY(-3px);
            border-color: #2d70ad;
        }

        .league {
            color: #79a9d6;
            font-size: 13px;
            margin-bottom: 15px;
        }

        .teams {
            font-size: 19px;
            font-weight: bold;
            line-height: 1.5;
        }

        .vs {
            color: #71859b;
            font-size: 13px;
            margin: 4px 0;
        }

        .time {
            margin-top: 15px;
            font-size: 17px;
            font-weight: bold;
        }

        .analyse-button {
            display: block;
            width: 100%;
            margin-top: 18px;
            padding: 13px;
            border: none;
            border-radius: 12px;
            background: #1769aa;
            color: white;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
        }

        .analyse-button:hover {
            background: #2181cd;
        }

        .empty {
            background: #0d1c2f;
            border: 1px solid #1c3857;
            border-radius: 18px;
            padding: 25px;
            text-align: center;
            color: #9fb3c8;
        }

        .menu {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 35px;
        }

        .menu-item {
            background: #0d1c2f;
            border: 1px solid #1c3857;
            border-radius: 14px;
            padding: 18px 12px;
            text-align: center;
            color: #dce8f4;
            font-weight: bold;
        }

        .footer {
            text-align: center;
            color: #657a90;
            font-size: 12px;
            margin-top: 35px;
        }
    </style>
</head>

<body>

    <div class="header">

        <div class="logo">
            ⚽ CalcioAI
        </div>

        <div class="subtitle">
            Analisi intelligente delle partite
        </div>

    </div>


    <div class="container">

        <div class="section-title">
            🔥 Partite di oggi
        </div>


        {% if partite %}

        <div class="matches">

            {% for partita in partite %}

            <div class="match-card">

                <div class="league">
                    {{ partita.get("lega", "Campionato") }}
                </div>

                <div class="teams">
                    {{ partita.get("casa", "Squadra casa") }}
                </div>

                <div class="vs">
                    VS
                </div>

                <div class="teams">
                    {{ partita.get("trasferta", "Squadra ospite") }}
                </div>

                <div class="time">
                    🕐 {{ partita.get("ora", "--:--") }}
                </div>


                <a
                    class="analyse-button"
                    href="/analizza/{{ partita.get('id') }}"
                >
                    ANALIZZA PARTITA
                </a>

            </div>

            {% endfor %}

        </div>

        {% else %}

        <div class="empty">
            ⚠️ Nessuna partita trovata per oggi.
        </div>

        {% endif %}


        <div class="menu">

            <div class="menu-item">
                ⚽ Partite
            </div>

            <div class="menu-item">
                🎯 Marcatori
            </div>

            <div class="menu-item">
                🎟️ Schedina
            </div>

            <div class="menu-item">
                📊 Statistiche
            </div>

            <div class="menu-item">
                📚 Storico
            </div>

            <div class="menu-item">
                🏆 Ranking
            </div>

        </div>


        <div class="footer">
            CalcioAI — Analisi statistiche e probabilistiche
        </div>

    </div>

</body>
</html>
"""


@app.route("/")
def home():

    try:
        partite = partite_oggi()

        if not partite:
            partite = []

    except Exception as e:

        print(
            f"⚠️ Errore caricamento partite Web App: {e}"
        )

        partite = []

    return render_template_string(
        HTML,
        partite=partite
    )


@app.route("/analizza/<int:fixture_id>")
def analizza(fixture_id):

    return """
    <!DOCTYPE html>
    <html lang="it">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Analisi CalcioAI</title>


        <style>

            * {
                box-sizing: border-box;
            }

            body {

                margin: 0;

                background: #07111f;

                color: white;

                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;

                display: flex;

                justify-content: center;

                align-items: center;

                min-height: 100vh;
            }


            .box {

                width: 90%;

                max-width: 500px;

                background: #0d1c2f;

                border: 1px solid #1c3857;

                border-radius: 20px;

                padding: 30px;

                text-align: center;

                box-shadow:
                    0 15px 40px
                    rgba(0, 0, 0, 0.35);
            }


            h1 {

                margin-top: 0;

                font-size: 27px;
            }


            .fixture {

                color: #79a9d6;

                margin: 20px 0;

                font-size: 16px;
            }


            .status {

                color: #dce8f4;

                line-height: 1.6;
            }


            .back {

                display: inline-block;

                margin-top: 20px;

                padding: 12px 20px;

                background: #1769aa;

                color: white;

                text-decoration: none;

                border-radius: 10px;

                font-weight: bold;
            }


            .back:hover {

                background: #2181cd;
            }

        </style>

    </head>


    <body>


        <div class="box">

            <h1>
                ⚽ Analisi partita
            </h1>


            <div class="fixture">

                ID partita:
                """ + str(fixture_id) + """

            </div>


            <div class="status">

                <p>
                    ✅ Partita selezionata correttamente.
                </p>

                <p>
                    🔄 Motore AI in collegamento...
                </p>

            </div>


            <a
                class="back"
                href="/"
            >
                ← Torna alle partite
            </a>

        </div>


    </body>

    </html>
    """


if __name__ == "__main__":

    print("🌐 CalcioAI Web App avviata")

    print("🔗 http://127.0.0.1:5000")


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False,

        use_reloader=False

    )