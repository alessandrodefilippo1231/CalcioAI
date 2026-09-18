import json
import os
from datetime import datetime

FILE_STORICO = "data/storico.json"


def salva_pronostico(partita, analisi):

    if not os.path.exists(FILE_STORICO):
        with open(FILE_STORICO, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(FILE_STORICO, "r", encoding="utf-8") as f:
        storico = json.load(f)

    record = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "campionato": partita["league"]["name"],
        "casa": partita["teams"]["home"]["name"],
        "trasferta": partita["teams"]["away"]["name"],
        "pronostico": analisi["pronostico"],
        "fiducia": analisi["fiducia"],
        "ai_score": analisi["ai_score"],
        "rischio": analisi["rischio"],
        "risultato": None
    }

    storico.append(record)

    with open(FILE_STORICO, "w", encoding="utf-8") as f:
        json.dump(storico, f, indent=4, ensure_ascii=False)