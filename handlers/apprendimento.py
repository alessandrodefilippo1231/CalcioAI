from telegram import Update
from telegram.ext import ContextTypes

from services.apprendimento_ai import riepilogo_apprendimento


async def apprendimento(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        dati = riepilogo_apprendimento()

        verificati = dati.get("pronostici_verificati", 0)
        peso_learning = dati.get("peso_learning", 0)
        livello = dati.get("livello", "INIZIALE")

        precisione = dati.get("precisione_generale", 0)
        media_score = dati.get("media_ai_score", 0)
        media_fiducia = dati.get("media_fiducia", 0)

        mercati = dati.get("mercati", {})
        score_fasce = dati.get("ai_score", {})
        fiducia_fasce = dati.get("fiducia", {})
        value_fasce = dati.get("value_index", {})

        messaggio = (
            "🧠 CALCIOAI LEARNING\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📚 Pronostici verificati: {verificati}\n"
            f"🎯 Precisione generale: {precisione}%\n"
            f"⭐ Media AI Score: {media_score}\n"
            f"📊 Media Fiducia: {media_fiducia}%\n\n"
            f"🧠 Livello Learning: {livello}\n"
            f"⚖️ Peso Learning: {peso_learning}%\n"
        )

        # ====================================================
        # MERCATI
        # ====================================================

        if mercati:

            messaggio += (
                "\n\n📈 LEARNING PER MERCATO\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
            )

            ordinati = sorted(
                mercati.items(),
                key=lambda x: (
                    x[1].get("precisione", 0),
                    x[1].get("totale", 0)
                ),
                reverse=True
            )

            for mercato, valori in ordinati:

                totale = valori.get("totale", 0)
                corrette = valori.get("corrette", 0)
                precisione_mercato = valori.get("precisione", 0)

                messaggio += (
                    f"\n• {mercato}\n"
                    f"  └ {corrette}/{totale} "
                    f"({precisione_mercato}%)"
                )

        # ====================================================
        # AI SCORE
        # ====================================================

        messaggio += (
            "\n\n⭐ LEARNING AI SCORE\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
        )

        for fascia, valori in score_fasce.items():

            totale = valori.get("totale", 0)
            precisione_fascia = valori.get("precisione", 0)

            if totale > 0:

                messaggio += (
                    f"\n• Score {fascia}: "
                    f"{precisione_fascia}% "
                    f"({totale})"
                )

        # ====================================================
        # FIDUCIA
        # ====================================================

        messaggio += (
            "\n\n🎯 LEARNING FIDUCIA\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
        )

        for fascia, valori in fiducia_fasce.items():

            totale = valori.get("totale", 0)
            precisione_fascia = valori.get("precisione", 0)

            if totale > 0:

                messaggio += (
                    f"\n• Fiducia {fascia}: "
                    f"{precisione_fascia}% "
                    f"({totale})"
                )

        # ====================================================
        # VALUE INDEX
        # ====================================================

        messaggio += (
            "\n\n💰 LEARNING VALUE INDEX\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
        )

        for fascia, valori in value_fasce.items():

            totale = valori.get("totale", 0)
            precisione_fascia = valori.get("precisione", 0)

            if totale > 0:

                messaggio += (
                    f"\n• Value {fascia}: "
                    f"{precisione_fascia}% "
                    f"({totale})"
                )

        # ====================================================
        # STATO
        # ====================================================

        if verificati < 5:

            messaggio += (
                "\n\n🟡 STATO: RACCOLTA DATI\n"
                "Il Learning ha ancora pochi dati."
            )

        elif verificati < 20:

            messaggio += (
                "\n\n🟠 STATO: LEARNING ATTIVO\n"
                "Il sistema sta iniziando a riconoscere "
                "i mercati e le fasce più affidabili."
            )

        elif verificati < 50:

            messaggio += (
                "\n\n🟢 STATO: LEARNING CONSOLIDATO\n"
                "Il sistema dispone di uno storico "
                "sufficientemente interessante."
            )

        else:

            messaggio += (
                "\n\n🔥 STATO: LEARNING AVANZATO\n"
                "Lo storico contiene un volume importante "
                "di dati verificati."
            )

        await update.message.reply_text(messaggio)

    except Exception as e:

        print(
            "❌ ERRORE COMANDO /APPRENDIMENTO:",
            e
        )

        await update.message.reply_text(
            "❌ Errore durante la lettura del Learning AI."
        )