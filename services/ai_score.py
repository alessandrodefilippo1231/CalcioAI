from services.apprendimento_ai import statistiche_mercati


def analizza_componenti_score(
    stats_casa,
    stats_trasferta,
    indicatori
):

    componenti = {}


    # =========================
    # FORMA RECENTE
    # =========================

    forma_casa = stats_casa.get("forma", "")
    forma_trasferta = stats_trasferta.get("forma", "")

    vittorie = (
        forma_casa.count("V")
        +
        forma_trasferta.count("V")
    )

    pareggi = (
        forma_casa.count("P")
        +
        forma_trasferta.count("P")
    )

    sconfitte = (
        forma_casa.count("S")
        +
        forma_trasferta.count("S")
    )

    forma_score = (
        vittorie * 2
        +
        pareggi
        -
        sconfitte * 2
    )

    componenti["📈 Forma"] = forma_score



    # =========================
    # ATTACCO
    # =========================

    media_gol = (
        stats_casa.get("media_gol_fatti", 0)
        +
        stats_trasferta.get("media_gol_fatti", 0)
    )


    if media_gol >= 3:
        attacco = 12

    elif media_gol >= 2:
        attacco = 8

    elif media_gol >= 1:
        attacco = 4

    else:
        attacco = -3


    componenti["⚽ Attacco"] = attacco



    # =========================
    # DIFESA
    # =========================

    media_subiti = (
        stats_casa.get("media_gol_subiti", 0)
        +
        stats_trasferta.get("media_gol_subiti", 0)
    )


    if media_subiti <= 1:
        difesa = 8

    elif media_subiti <= 2:
        difesa = 3

    else:
        difesa = -4


    componenti["🛡 Difesa"] = difesa



    # =========================
    # MERCATI GOL
    # =========================

    mercato_score = 0


    if indicatori.get("over15", 0) >= 70:
        mercato_score += 5


    if indicatori.get("over25", 0) >= 60:
        mercato_score += 5


    if indicatori.get("golgol", 0) >= 60:
        mercato_score += 4


    componenti["📊 Mercati"] = mercato_score



    # =========================
    # EQUILIBRIO
    # =========================

    differenza = abs(
        stats_casa.get("media_gol_fatti", 0)
        -
        stats_trasferta.get("media_gol_fatti", 0)
    )


    if differenza <= 0.5:
        equilibrio = 3

    elif differenza >= 2:
        equilibrio = -3

    else:
        equilibrio = 0


    componenti["⚖️ Equilibrio"] = equilibrio


    return componenti



def bonus_learning(pronostico):

    mercati = statistiche_mercati()


    if pronostico not in mercati:
        return 0


    precisione = mercati[pronostico]["precisione"]
    totale = mercati[pronostico]["totale"]


    if totale < 5:
        return 0


    if precisione >= 80:
        return 5

    elif precisione >= 70:
        return 3

    elif precisione >= 60:
        return 1

    elif precisione <= 40:
        return -5

    elif precisione <= 50:
        return -3


    return 0




def calcola_ai_score(
    stats_casa,
    stats_trasferta,
    indicatori,
    lega,
    pronostico=None
):


    score = 50


    componenti = analizza_componenti_score(
        stats_casa,
        stats_trasferta,
        indicatori
    )


    for valore in componenti.values():
        score += valore



    # =========================
    # QUALITA CAMPIONATO
    # =========================

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

        score += 5


    elif lega in campionati_buoni:

        score += 2


    else:

        score -= 2



    # =========================
    # LEARNING STORICO
    # =========================

    if pronostico:

        score += bonus_learning(
            pronostico
        )



    # =========================
    # LIMITI FINALI
    # =========================

    score = max(
        20,
        min(score, 95)
    )


    return score