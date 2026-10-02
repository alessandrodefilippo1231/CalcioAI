import math


# ============================================================
# UTILITÀ
# ============================================================

def _clamp(valore, minimo, massimo):

    return max(
        minimo,
        min(
            massimo,
            valore
        )
    )


def _poisson(k, lamb):

    if lamb <= 0:

        return 1.0 if k == 0 else 0.0

    return (
        math.exp(-lamb)
        * (lamb ** k)
        / math.factorial(k)
    )


# ============================================================
# NUMERO PARTITE ANALIZZATE
# ============================================================

def _numero_partite(stats):

    """
    Recupera il numero reale di partite analizzate.

    Priorità:
    1. partite_analizzate
    2. conteggio della forma
    3. fallback 5
    """

    # --------------------------------------------------------
    # METODO PRINCIPALE
    # --------------------------------------------------------

    partite = stats.get(
        "partite_analizzate"
    )

    try:

        partite = int(partite)

        if partite > 0:

            return partite

    except (
        TypeError,
        ValueError
    ):

        pass

    # --------------------------------------------------------
    # FALLBACK: LETTURA FORMA
    # --------------------------------------------------------

    forma = stats.get(
        "forma",
        ""
    )

    if isinstance(
        forma,
        str
    ):

        forma = forma.strip()

        if forma:

            risultati = []

            for elemento in forma.replace(
                ",",
                " "
            ).split():

                if elemento:

                    simbolo = elemento[-1].upper()

                    if simbolo in (
                        "V",
                        "P",
                        "S"
                    ):

                        risultati.append(
                            simbolo
                        )

            if risultati:

                return len(
                    risultati
                )

    # --------------------------------------------------------
    # FALLBACK FINALE
    # --------------------------------------------------------

    return 5


# ============================================================
# RISULTATI ESATTI AI
# ============================================================

def calcola_risultati_esatti(
    stats_casa,
    stats_trasferta,
    indicatori=None,
    numero_risultati=3
):

    print("")
    print(
        "🎯 RISULTATI ESATTI AI"
    )

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

    partite_casa = _numero_partite(
        stats_casa
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

    partite_trasferta = _numero_partite(
        stats_trasferta
    )

    # ========================================================
    # MEDIE REALI
    # ========================================================

    media_gol_fatti_casa = (
        gol_fatti_casa
        / max(
            partite_casa,
            1
        )
    )

    media_gol_subiti_casa = (
        gol_subiti_casa
        / max(
            partite_casa,
            1
        )
    )

    media_gol_fatti_trasferta = (
        gol_fatti_trasferta
        / max(
            partite_trasferta,
            1
        )
    )

    media_gol_subiti_trasferta = (
        gol_subiti_trasferta
        / max(
            partite_trasferta,
            1
        )
    )

    print(
        f"📊 Media gol "
        f"{stats_casa.get('forma', 'N/D')}: "
        f"{media_gol_fatti_casa:.2f} fatti / "
        f"{media_gol_subiti_casa:.2f} subiti"
    )

    print(
        f"📊 Media gol "
        f"{stats_trasferta.get('forma', 'N/D')}: "
        f"{media_gol_fatti_trasferta:.2f} fatti / "
        f"{media_gol_subiti_trasferta:.2f} subiti"
    )

    # ========================================================
    # EXPECTED GOALS BASE
    # ========================================================

    lambda_casa = (
        media_gol_fatti_casa
        +
        media_gol_subiti_trasferta
    ) / 2

    lambda_trasferta = (
        media_gol_fatti_trasferta
        +
        media_gol_subiti_casa
    ) / 2

    # ========================================================
    # AGGIUSTAMENTO INDICATORI AI
    # ========================================================

    if isinstance(
        indicatori,
        dict
    ):

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

        # ----------------------------------------------------
        # OVER 1.5
        # ----------------------------------------------------

        if over15 > 0:

            fattore_over15 = (
                1
                +
                (
                    over15 - 50
                )
                / 1000
            )

            lambda_casa *= fattore_over15
            lambda_trasferta *= fattore_over15

        # ----------------------------------------------------
        # OVER 2.5
        # ----------------------------------------------------

        if over25 > 0:

            fattore_over25 = (
                1
                +
                (
                    over25 - 50
                )
                / 1500
            )

            lambda_casa *= fattore_over25
            lambda_trasferta *= fattore_over25

        # ----------------------------------------------------
        # GOAL / GOAL
        # ----------------------------------------------------

        if golgol > 0:

            fattore_golgol = (
                1
                +
                (
                    golgol - 50
                )
                / 1500
            )

            lambda_casa *= fattore_golgol
            lambda_trasferta *= fattore_golgol

    # ========================================================
    # LIMITI DI SICUREZZA
    # ========================================================

    lambda_casa = _clamp(
        lambda_casa,
        0.20,
        4.00
    )

    lambda_trasferta = _clamp(
        lambda_trasferta,
        0.20,
        4.00
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
    # CALCOLO POISSON
    # ========================================================

    risultati = []

    for gol_casa in range(
        0,
        7
    ):

        probabilita_casa = _poisson(
            gol_casa,
            lambda_casa
        )

        for gol_trasferta in range(
            0,
            7
        ):

            probabilita_trasferta = _poisson(
                gol_trasferta,
                lambda_trasferta
            )

            probabilita = (
                probabilita_casa
                *
                probabilita_trasferta
            )

            risultati.append(
                {
                    "risultato": (
                        f"{gol_casa}-"
                        f"{gol_trasferta}"
                    ),
                    "probabilita_raw": probabilita
                }
            )

    # ========================================================
    # NORMALIZZAZIONE
    # ========================================================

    totale = sum(
        risultato[
            "probabilita_raw"
        ]
        for risultato in risultati
    )

    if totale <= 0:

        return []

    for risultato in risultati:

        risultato["probabilita"] = round(
            (
                risultato[
                    "probabilita_raw"
                ]
                / totale
            )
            * 100,
            1
        )

    # ========================================================
    # ORDINAMENTO
    # ========================================================

    risultati.sort(
        key=lambda x: x[
            "probabilita"
        ],
        reverse=True
    )

    # ========================================================
    # TOP RISULTATI
    # ========================================================

    migliori = risultati[
        :numero_risultati
    ]

    # Rimuoviamo il valore tecnico
    # utilizzato per il calcolo.

    for risultato in migliori:

        risultato.pop(
            "probabilita_raw",
            None
        )

    print(
        f"🏆 TOP RISULTATI: "
        f"{migliori}"
    )

    return migliori