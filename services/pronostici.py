import json
import os


def genera_pronostici():
    percorso = os.path.join("data", "pronostici.json")

    with open(percorso, "r", encoding="utf-8") as file:
        pronostici = json.load(file)

    testo = "⚽ Pronostici di oggi\n\n"

    for p in pronostici:
        testo += (
            f"🔥 {p['partita']}\n"
            f"📌 Pronostico: {p['pronostico']}\n"
            f"📊 Mercato: {p['mercato']}\n"
            f"🎯 Fiducia: {p['fiducia']}\n"
            f"💡 Analisi: {p['analisi']}\n\n"
        )

    testo += "🤖 CalcioAI"

    return testo