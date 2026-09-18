def calcola_value_index(
    ai_score,
    probabilita,
    mercato,
    indicatori,
    lega,
    storico_bonus=0,
    storico_totale=0
):
    """
    Calcola il Value Index del singolo mercato.

    Il punteggio va da 0 a 100.

    Tiene conto di:
    - AI Score
    - probabilità del mercato
    - indicatori specifici
    - qualità della competizione
    - apprendimento storico

    Il Value Index NON deve essere semplicemente uguale
    alla probabilità del mercato.
    """

    # ==========================================================
    # CONTROLLO DATI
    # ==========================================================

    ai_score = max(0, min(float(ai_score or 0), 100))
    probabilita = max(0, min(float(probabilita or 0), 100))

    storico_bonus = float(storico_bonus or 0)
    storico_totale = int(storico_totale or 0)

    indicatori = indicatori or {}

    # ==========================================================
    # BASE SCORE
    # ==========================================================
    #
    # Diamo maggiore importanza alla combinazione tra
    # AI Score e probabilità.
    #
    # 55% AI Score
    # 45% probabilità
    #
    # Questo evita che una probabilità molto alta
    # faccia automaticamente arrivare il Value Index a 100.
    # ==========================================================

    value = (
        ai_score * 0.55
        +
        probabilita * 0.45
    )

    # ==========================================================
    # COERENZA AI SCORE / PROBABILITÀ
    # ==========================================================
    #
    # Se AI Score e probabilità sono molto distanti,
    # riduciamo leggermente il Value Index.
    #
    # Esempio:
    #
    # AI Score 82
    # Probabilità 95
    #
    # differenza = 13
    #
    # Il mercato rimane forte, ma non viene gonfiato.
    # ==========================================================

    differenza = abs(ai_score - probabilita)

    if differenza <= 5:
        value += 3

    elif differenza <= 10:
        value += 1

    elif differenza >= 20:
        value -= 5

    elif differenza >= 15:
        value -= 3

    # ==========================================================
    # BONUS INDICATORI
    # ==========================================================

    if mercato in ("Over 1.5", "Over 1.5 Gol"):

        over15 = indicatori.get("over15", 0)

        if over15 >= 90:
            value += 2

        elif over15 >= 80:
            value += 1


    elif mercato in ("Over 2.5", "Over 2.5 Gol"):

        over25 = indicatori.get("over25", 0)

        if over25 >= 80:
            value += 3

        elif over25 >= 70:
            value += 2

        elif over25 >= 60:
            value += 1


    elif mercato == "Goal":

        golgol = indicatori.get("golgol", 0)

        if golgol >= 85:
            value += 3

        elif golgol >= 75:
            value += 2

        elif golgol >= 65:
            value += 1


    elif mercato in ("Under 3.5", "Under 3.5 Gol"):

        under35 = indicatori.get("under35", 0)

        if under35 >= 80:
            value += 3

        elif under35 >= 70:
            value += 2

        elif under35 >= 60:
            value += 1

    # ==========================================================
    # QUALITÀ CAMPIONATO
    # ==========================================================

    campionati_elite = [

        "Serie A",
        "Premier League",
        "La Liga",
        "Bundesliga",
        "Ligue 1",
        "UEFA Champions League",
        "UEFA Europa League"

    ]

    campionati_buoni = [

        "Liga Profesional Argentina",
        "Liga MX",
        "Brasileirão Série A",
        "Primeira Liga",
        "Eredivisie",
        "Liga Pro",
        "Primera A"

    ]

    if lega in campionati_elite:

        value += 2

    elif lega in campionati_buoni:

        value += 1

    else:

        value -= 1

    # ==========================================================
    # APPRENDIMENTO STORICO
    # ==========================================================
    #
    # Il bonus storico viene applicato solamente quando
    # abbiamo almeno 5 casi.
    #
    # In questo modo pochi risultati non possono alterare
    # pesantemente il modello.
    # ==========================================================

    if storico_totale >= 5:

        value += storico_bonus

    # ==========================================================
    # PENALITÀ DATI INSUFFICIENTI
    # ==========================================================

    if storico_totale == 0:

        # Nessuna penalizzazione forte.
        # Il mercato può comunque essere valutato
        # attraverso i dati attuali.
        value += 0

    elif storico_totale < 5:

        # Piccolo vantaggio di stabilità quando abbiamo
        # iniziato a raccogliere dati ma non abbastanza
        # per considerarli affidabili.
        value -= 1

    # ==========================================================
    # LIMITE FINALE
    # ==========================================================

    value = round(value)

    value = max(
        0,
        min(value, 100)
    )

    return value