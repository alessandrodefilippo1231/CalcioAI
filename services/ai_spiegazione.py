def genera_spiegazione(
    stats_casa,
    stats_trasferta,
    mercato
):

    spiegazione = []


    # FORMA

    if "V" in stats_casa["forma"]:

        spiegazione.append(
            "🏠 La squadra di casa presenta una forma recente positiva."
        )


    if "V" in stats_trasferta["forma"]:

        spiegazione.append(
            "✈️ La squadra ospite arriva con risultati incoraggianti."
        )



    # GOL

    gol_totali = (
        stats_casa["gol_fatti"]
        +
        stats_trasferta["gol_fatti"]
    )


    if gol_totali >= 15:

        spiegazione.append(
            "⚽ Entrambe le squadre mostrano una buona produzione offensiva."
        )

    elif gol_totali <= 5:

        spiegazione.append(
            "🛡 Le statistiche indicano una possibile partita chiusa."
        )



    # DIFESA

    subiti = (
        stats_casa["gol_subiti"]
        +
        stats_trasferta["gol_subiti"]
    )


    if subiti >= 12:

        spiegazione.append(
            "⚠️ Le difese hanno concesso diversi gol nelle ultime gare."
        )



    # MERCATO

    if "Over" in mercato:

        spiegazione.append(
            "📈 Gli indicatori AI supportano una scelta orientata ai gol."
        )


    elif "Gol/Gol" in mercato:

        spiegazione.append(
            "🤝 Entrambe le squadre hanno caratteristiche compatibili con il Gol/Gol."
        )


    elif "Under" in mercato:

        spiegazione.append(
            "🛡 I dati suggeriscono attenzione ai pochi gol."
        )



    if not spiegazione:

        spiegazione.append(
            "🤖 Analisi basata sui dati disponibili delle squadre."
        )



    return "\n".join(spiegazione)