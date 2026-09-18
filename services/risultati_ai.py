import math


# ============================================================
# UTILITY
# ============================================================

def _clamp(valore, minimo=0, massimo=100):
    return max(
        minimo,
        min(
            massimo,
            valore
        )
    )


def _poisson(lam, gol):
    """
    Probabilità di segnare esattamente 'gol'
    con distribuzione di Poisson.
    """

    if lam <= 0:

        return 1.0 if gol == 0 else 0.0

    return (
        math.exp(-lam)
        * (lam ** gol)
        / math.factorial(gol)
    )


def _numero_partite(stats):
    """
    Determina quante partite sono rappresentate
    dalle statistiche.

    La forma normalmente contiene 5 risultati:
    esempio: VVPVS

    Se la forma non è disponibile, utilizziamo
    5 come fallback perché il motore lavora
    normalmente sulle ultime 5 partite.
    """

    forma = stats.get(
        "forma",
        ""
    )

    if isinstance(
        forma,
        str
    ):

        forma = forma.strip()

        if len(forma) > 0:

            return len(forma)

    return 5


# ============================================================
# RISULTATI ESATTI
# ============================================================

def calcola_risultati_esatti(
    stats_casa,
    stats_trasferta,
    indicatori=None,
    numero_risultati=3
):
    """
    Calcola i risultati esatti più probabili.

    IMPORTANTE:
    gol_fatti e gol_subiti rappresentano i gol
    complessivi delle ultime partite, quindi vengono
    trasformati in medie per partita prima di
    calcolare gli expected goals.

    Il modulo è separato dal Decision Engine.
    """

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

    if not isinstance(
        indicatori,
        dict
    ):
        indicatori = {}

    # ========================================================
    # DATI CASA
    # ========================================================

    gol_fatti_casa = float(
        stats_casa.get(
            "gol_fatti",
            0
        ) or 0
    )

    gol_subiti_casa = float(
        stats_casa.get(
            "gol_subiti",
            0
        ) or 0
    )

    # ========================================================
    # DATI TRASFERTA
    # ========================================================

    gol_fatti_trasferta = float(
        stats_trasferta.get(
            "gol_fatti",
            0
        ) or 0
    )

    gol_subiti_trasferta = float(
        stats_trasferta.get(
            "gol_subiti",
            0
        ) or 0
    )

    # ========================================================
    # NUMERO PARTITE
    # ========================================================

    partite_casa = _numero_partite(
        stats_casa
    )

    partite_trasferta = _numero_partite(
        stats_trasferta
    )

    # Evitiamo divisioni per zero

    partite_casa = max(
        1,
        partite_casa
    )

    partite_trasferta = max(
        1,
        partite_trasferta
    )

    # ========================================================
    # MEDIE GOL PER PARTITA
    # ========================================================

    media_gol_fatti_casa = (
        gol_fatti_casa
        / partite_casa
    )

    media_gol_subiti_casa = (
        gol_subiti_casa
        / partite_casa
    )

    media_gol_fatti_trasferta = (
        gol_fatti_trasferta
        / partite_trasferta
    )

    media_gol_subiti_trasferta = (
        gol_subiti_trasferta
        / partite_trasferta
    )

    # ========================================================
    # EXPECTED GOALS BASE
    # ========================================================

    # Attacco casa + difesa trasferta

    lambda_casa = (
        media_gol_fatti_casa
        + media_gol_subiti_trasferta
    ) / 2

    # Attacco trasferta + difesa casa

    lambda_trasferta = (
        media_gol_fatti_trasferta
        + media_gol_subiti_casa
    ) / 2

    # ========================================================
    # PICCOLI AGGIUSTAMENTI AI
    # ========================================================

    over15 = float(
        indicatori.get(
            "over15",
            0
        ) or 0
    )

    over25 = float(
        indicatori.get(
            "over25",
            0
        ) or 0
    )

    golgol = float(
        indicatori.get(
            "golgol",
            0
        ) or 0
    )

    under35 = float(
        indicatori.get(
            "under35",
            0
        ) or 0
    )

    # --------------------------------------------------------
    # OVER 2.5
    # --------------------------------------------------------

    if over25 >= 80:

        lambda_casa *= 1.08
        lambda_trasferta *= 1.08

    elif over25 >= 65:

        lambda_casa *= 1.04
        lambda_trasferta *= 1.04

    elif over25 <= 35:

        lambda_casa *= 0.96
        lambda_trasferta *= 0.96

    # --------------------------------------------------------
    # OVER 1.5
    # --------------------------------------------------------

    if over15 >= 90:

        lambda_casa *= 1.03
        lambda_trasferta *= 1.03

    # --------------------------------------------------------
    # GOAL / GOAL
    # --------------------------------------------------------

    if golgol >= 80:

        lambda_casa *= 1.03
        lambda_trasferta *= 1.03

    elif golgol <= 40:

        # Leggero abbassamento,
        # evitando di forzare troppo il modello.

        lambda_casa *= 0.98
        lambda_trasferta *= 0.98

    # --------------------------------------------------------
    # UNDER 3.5
    # --------------------------------------------------------

    if under35 >= 80:

        lambda_casa *= 0.96
        lambda_trasferta *= 0.96

    # ========================================================
    # LIMITI REALISTICI
    # ========================================================

    # Evitiamo valori estremi.

    lambda_casa = max(
        0.20,
        min(
            3.50,
            lambda_casa
        )
    )

    lambda_trasferta = max(
        0.20,
        min(
            3.50,
            lambda_trasferta
        )
    )

    print("")
    print("🎯 RISULTATI ESATTI AI")
    print(
        f"📊 Media gol {stats_casa.get('forma', '')}: "
        f"{media_gol_fatti_casa:.2f} fatti / "
        f"{media_gol_subiti_casa:.2f} subiti"
    )

    print(
        f"📊 Media gol {stats_trasferta.get('forma', '')}: "
        f"{media_gol_fatti_trasferta:.2f} fatti / "
        f"{media_gol_subiti_trasferta:.2f} subiti"
    )

    print(
        f"⚽ Expected Goals casa: "
        f"{lambda_casa:.2f}"
    )

    print(
        f"⚽ Expected Goals trasferta: "
        f"{lambda_trasferta:.2f}"
    )

    # ========================================================
    # CALCOLO RISULTATI
    # ========================================================

    risultati = []

    # Consideriamo risultati da 0-0 fino a 6-6.

    for gol_casa in range(7):

        probabilita_casa = _poisson(
            lambda_casa,
            gol_casa
        )

        for gol_trasferta in range(7):

            probabilita_trasferta = _poisson(
                lambda_trasferta,
                gol_trasferta
            )

            probabilita = (
                probabilita_casa
                * probabilita_trasferta
            )

            risultati.append(
                {
                    "risultato":
                        f"{gol_casa}-{gol_trasferta}",

                    "probabilita_raw":
                        probabilita
                }
            )

    # ========================================================
    # NORMALIZZAZIONE
    # ========================================================

    totale = sum(
        r["probabilita_raw"]
        for r in risultati
    )

    if totale > 0:

        for r in risultati:

            r["probabilita"] = (
                r["probabilita_raw"]
                / totale
                * 100
            )

    else:

        for r in risultati:

            r["probabilita"] = 0

    # ========================================================
    # ORDINAMENTO
    # ========================================================

    risultati.sort(
        key=lambda x: x["probabilita"],
        reverse=True
    )

    # ========================================================
    # TOP RISULTATI
    # ========================================================

    top = risultati[
        :max(
            1,
            int(numero_risultati)
        )
    ]

    # ========================================================
    # OUTPUT PULITO
    # ========================================================

    output = []

    for risultato in top:

        output.append(
            {
                "risultato":
                    risultato["risultato"],

                "probabilita":
                    round(
                        _clamp(
                            risultato["probabilita"]
                        ),
                        1
                    )
            }
        )

    print(
        "🏆 TOP RISULTATI:",
        output
    )

    return output