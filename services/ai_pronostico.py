def genera_pronostico(
    statistiche_casa,
    statistiche_ospite,
    indicatori,
    ai_score=None
):

    # ------------------------
    # SCELTA RISCHIO AI
    # ------------------------

    if ai_score is None:
        rischio = "🟡 Medio"

    elif ai_score >= 90:
        rischio = "🟢 Basso"

    elif ai_score >= 75:
        rischio = "🟡 Medio"

    else:
        rischio = "🔴 Alto"

    # ------------------------
    # INDICATORI AI
    # ------------------------

    over15 = indicatori["over15"]
    over25 = indicatori["over25"]
    golgol = indicatori["golgol"]
    under35 = indicatori["under35"]

    mercati = {
        "Over 1.5 Gol": over15,
        "Over 2.5 Gol": over25,
        "Goal": golgol,
        "Under 3.5 Gol": under35,
    }

    pronostico = max(mercati, key=mercati.get)
    fiducia = mercati[pronostico]

    motivi = {
        "Over 1.5 Gol": "Le statistiche indicano almeno due reti nella partita.",
        "Over 2.5 Gol": "Entrambe le squadre hanno una buona produzione offensiva.",
        "Goal": "Entrambe le squadre hanno buone probabilità di segnare.",
        "Under 3.5 Gol": "La partita dovrebbe rimanere sotto le quattro reti."
    }

    motivo = motivi[pronostico]

    return {
        "pronostico": pronostico,
        "fiducia": fiducia,
        "rischio": rischio,
        "motivo": motivo
    }


def calcola_indicatori(statistiche_casa, statistiche_ospite):

    gol_fatti = (
        statistiche_casa["gol_fatti"] +
        statistiche_ospite["gol_fatti"]
    )

    gol_subiti = (
        statistiche_casa["gol_subiti"] +
        statistiche_ospite["gol_subiti"]
    )

    totale = gol_fatti + gol_subiti

    over15 = min(95, int((totale / 30) * 100))
    over25 = min(90, int((totale / 40) * 100))
    golgol = min(
        90,
        int(totale / 35 * 100)
    )
    under35 = 100 - int(over25 / 2)

    return {
        "over15": over15,
        "over25": over25,
        "golgol": golgol,
        "under35": under35
    }