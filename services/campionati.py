# ==========================================
# CALCIOAI - CAMPIONATI PREMIUM
# ==========================================


CAMPIONATI_CALCIOAI = {


    # 🏆 COMPETIZIONI EUROPEE
    ("World", "Champions League"): 100,
    ("World", "UEFA Champions League"): 100,

    ("World", "Europa League"): 99,
    ("World", "UEFA Europa League"): 99,

    ("World", "Conference League"): 98,
    ("World", "UEFA Europa Conference League"): 98,


    # 🏴 INGHILTERRA
    ("England", "Premier League"): 97,
    ("England", "Championship"): 70,


    # 🇪🇸 SPAGNA
    ("Spain", "La Liga"): 96,
    ("Spain", "Primera División"): 96,


    # 🇩🇪 GERMANIA
    ("Germany", "Bundesliga"): 96,
    ("Germany", "2. Bundesliga"): 70,


    # 🇫🇷 FRANCIA
    ("France", "Ligue 1"): 95,
    ("France", "Ligue 2"): 65,


    # 🇮🇹 ITALIA
    ("Italy", "Serie A"): 95,
    ("Italy", "Serie B"): 65,


    # 🇵🇹 PORTOGALLO
    ("Portugal", "Primeira Liga"): 92,


    # 🇳🇱 OLANDA
    ("Netherlands", "Eredivisie"): 92,


    # 🇧🇪 BELGIO
    ("Belgium", "Jupiler Pro League"): 90,


    # 🇹🇷 TURCHIA
    ("Turkey", "Süper Lig"): 90,


    # 🇧🇷 BRASILE
    ("Brazil", "Serie A"): 88,


    # 🇦🇷 ARGENTINA
    ("Argentina", "Liga Profesional Argentina"): 88,


    # 🇨🇴 COLOMBIA
    ("Colombia", "Primera A"): 80,


    # 🇪🇨 ECUADOR
    ("Ecuador", "Liga Pro"): 78,


    # 🇨🇭 SVIZZERA
    ("Switzerland", "Super League"): 70,


    # 🇦🇹 AUSTRIA
    ("Austria", "Bundesliga"): 70,


    # 🇬🇷 GRECIA
    ("Greece", "Super League 1"): 65,


    # 🇩🇰 DANIMARCA
    ("Denmark", "Superliga"): 65,


    # 🇸🇪 SVEZIA
    ("Sweden", "Allsvenskan"): 60,


    # 🇳🇴 NORVEGIA
    ("Norway", "Eliteserien"): 60,

}





def campionato_consentito(
        paese,
        lega
):

    return (
        paese,
        lega
    ) in CAMPIONATI_CALCIOAI





def priorita_campionato(
        paese,
        lega
):

    return CAMPIONATI_CALCIOAI.get(
        (
            paese,
            lega
        ),
        0
    )