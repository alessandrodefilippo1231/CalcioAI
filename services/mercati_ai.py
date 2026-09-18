def calcola_mercati_ai(stats_casa, stats_trasferta, indicatori):
    """
    Calcola le probabilità stimate dei principali mercati.

    I mercati 1/X/2 e le doppie chance vengono calcolati
    in modo dinamico usando:
    - forma recente
    - gol fatti
    - gol subiti
    - forza offensiva
    - solidità difensiva
    - indicatori AI

    Il modulo NON decide il pronostico finale.
    La scelta finale rimane al Decision Engine.
    """

    mercati = {}

    indicatori = indicatori or {}

    # ==========================================================
    # DATI BASE
    # ==========================================================

    gol_casa = float(stats_casa.get("gol_fatti", 0) or 0)
    subiti_casa = float(stats_casa.get("gol_subiti", 0) or 0)

    gol_trasferta = float(stats_trasferta.get("gol_fatti", 0) or 0)
    subiti_trasferta = float(stats_trasferta.get("gol_subiti", 0) or 0)

    forma_casa = stats_casa.get("forma", "") or ""
    forma_trasferta = stats_trasferta.get("forma", "") or ""

    # ==========================================================
    # FORMA
    # ==========================================================

    vittorie_casa = forma_casa.count("V")
    pareggi_casa = forma_casa.count("P")
    sconfitte_casa = forma_casa.count("S")

    vittorie_trasferta = forma_trasferta.count("V")
    pareggi_trasferta = forma_trasferta.count("P")
    sconfitte_trasferta = forma_trasferta.count("S")

    # ==========================================================
    # FORZA SQUADRE
    # ==========================================================

    # La forma pesa molto, ma non deve essere l'unico elemento.
    forza_casa = (
        vittorie_casa * 4
        + pareggi_casa * 1
        - sconfitte_casa * 3
    )

    forza_trasferta = (
        vittorie_trasferta * 4
        + pareggi_trasferta * 1
        - sconfitte_trasferta * 3
    )

    # ==========================================================
    # DIFFERENZA OFFENSIVA
    # ==========================================================

    differenza_attacco = gol_casa - gol_trasferta

    if differenza_attacco > 0:
        forza_casa += min(12, differenza_attacco * 2)

    elif differenza_attacco < 0:
        forza_trasferta += min(12, abs(differenza_attacco) * 2)

    # ==========================================================
    # DIFFERENZA DIFENSIVA
    # ==========================================================

    # Meno gol subiti = maggiore solidità.
    differenza_difesa = subiti_trasferta - subiti_casa

    if differenza_difesa > 0:
        forza_casa += min(8, differenza_difesa * 1.5)

    elif differenza_difesa < 0:
        forza_trasferta += min(8, abs(differenza_difesa) * 1.5)

    # ==========================================================
    # VANTAGGIO CASA
    # ==========================================================

    forza_casa += 5

    # ==========================================================
    # INDICATORI GOAL
    # ==========================================================

    over15 = float(indicatori.get("over15", 0) or 0)
    over25 = float(indicatori.get("over25", 0) or 0)
    golgol = float(indicatori.get("golgol", 0) or 0)
    under35 = float(indicatori.get("under35", 0) or 0)

    # Partite con molti gol tendono a ridurre leggermente
    # la probabilità di pareggio.
    totale_gol = gol_casa + gol_trasferta

    bonus_no_pareggio = 0

    if over15 >= 85:
        bonus_no_pareggio += 3

    if over25 >= 75:
        bonus_no_pareggio += 3

    if totale_gol >= 14:
        bonus_no_pareggio += 3

    # ==========================================================
    # CALCOLO 1 X 2
    # ==========================================================

    differenza_forza = forza_casa - forza_trasferta

    # Base equilibrata.
    prob_1 = 36
    prob_x = 30
    prob_2 = 34

    # ----------------------------------------------------------
    # FORZA RELATIVA
    # ----------------------------------------------------------

    if differenza_forza >= 15:

        prob_1 += 13
        prob_x -= 5
        prob_2 -= 8

    elif differenza_forza >= 9:

        prob_1 += 9
        prob_x -= 3
        prob_2 -= 6

    elif differenza_forza >= 4:

        prob_1 += 5
        prob_x -= 1
        prob_2 -= 4

    elif differenza_forza <= -15:

        prob_2 += 13
        prob_x -= 5
        prob_1 -= 8

    elif differenza_forza <= -9:

        prob_2 += 9
        prob_x -= 3
        prob_1 -= 6

    elif differenza_forza <= -4:

        prob_2 += 5
        prob_x -= 1
        prob_1 -= 4

    else:

        # Squadre molto vicine:
        # aumenta leggermente il pareggio.
        prob_x += 5

    # ==========================================================
    # FORMA ESTREMA
    # ==========================================================

    if vittorie_casa >= 4 and sconfitte_trasferta >= 3:

        prob_1 += 5

    if vittorie_trasferta >= 4 and sconfitte_casa >= 3:

        prob_2 += 5

    if (
        vittorie_casa <= 1
        and vittorie_trasferta <= 1
        and abs(differenza_forza) <= 5
    ):

        prob_x += 4

    # ==========================================================
    # DIFESA / GOAL
    # ==========================================================

    if under35 >= 80 and over25 < 60:

        # Partita potenzialmente più chiusa.
        prob_x += 4

    if golgol >= 80 and over25 >= 70:

        # Partita più aperta.
        prob_x -= 4

    prob_x -= bonus_no_pareggio

    # ==========================================================
    # NORMALIZZAZIONE 1 X 2
    # ==========================================================

    prob_1 = max(5, min(80, prob_1))
    prob_x = max(10, min(55, prob_x))
    prob_2 = max(5, min(80, prob_2))

    totale = prob_1 + prob_x + prob_2

    prob_1 = round((prob_1 / totale) * 100)
    prob_x = round((prob_x / totale) * 100)

    prob_2 = 100 - prob_1 - prob_x

    # Sicurezza finale.
    prob_1 = max(5, min(85, prob_1))
    prob_x = max(5, min(65, prob_x))
    prob_2 = max(5, min(85, prob_2))

    # ==========================================================
    # MERCATI 1 X 2
    # ==========================================================

    mercati["1"] = prob_1
    mercati["X"] = prob_x
    mercati["2"] = prob_2

    # ==========================================================
    # OVER / UNDER
    # ==========================================================

    mercati["Over 1.5"] = round(
        max(5, min(95, over15))
    )

    mercati["Over 2.5"] = round(
        max(5, min(95, over25))
    )

    mercati["Under 3.5"] = round(
        max(5, min(95, under35))
    )

    # ==========================================================
    # GOAL / NO GOAL
    # ==========================================================

    goal = golgol

    if gol_casa >= 6 and gol_trasferta >= 6:
        goal += 3

    if subiti_casa >= 8 and subiti_trasferta >= 8:
        goal += 3

    goal = round(max(5, min(90, goal)))

    mercati["Goal"] = goal
    mercati["No Goal"] = 100 - goal

    # ==========================================================
    # DOPPIA CHANCE
    # ==========================================================

    # Non facciamo più una semplice somma matematica.
    #
    # Le doppie chance ricevono una piccola correzione
    # perché rappresentano due risultati contemporaneamente.

    prob_1x = prob_1 + prob_x
    prob_x2 = prob_x + prob_2
    prob_12 = prob_1 + prob_2

    # Correzioni realistiche.
    if abs(differenza_forza) <= 4:
        prob_1x += 2
        prob_x2 += 2

    if differenza_forza >= 8:
        prob_1x += 3
        prob_x2 -= 2

    elif differenza_forza <= -8:
        prob_x2 += 3
        prob_1x -= 2

    # 12 diventa interessante soprattutto quando
    # il pareggio è poco probabile.
    if prob_x <= 25:
        prob_12 += 4

    elif prob_x >= 38:
        prob_12 -= 5

    mercati["1X"] = max(5, min(90, round(prob_1x)))
    mercati["X2"] = max(5, min(90, round(prob_x2)))
    mercati["12"] = max(5, min(90, round(prob_12)))

    return mercati


def miglior_mercato(mercati):
    """
    Restituisce i migliori 5 mercati ordinati
    dal punteggio più alto al più basso.
    """

    ordinati = sorted(
        mercati.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ordinati[:5]