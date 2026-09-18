from services.apprendimento_ai import (
    statistiche_mercati,
    statistiche_ai_score,
    statistiche_fiducia,
    peso_learning,
    correzione_learning_mercato,
    normalizza_mercato,
    correzione_ai_score,
    correzione_fiducia,
    correzione_value_index
)

from services.value_index import calcola_value_index


# ============================================================
# DECISION ENGINE 4.2
# ============================================================
#
# AI + Indicatori + Value Index + Storico + Learning
#
# PRINCIPI:
#
# 1. Il Learning deve usare SOLO dati realmente verificati.
# 2. Nessuno storico = nessun bonus/penalizzazione.
# 3. Pochi dati = influenza ridotta.
# 4. Molti dati = influenza maggiore.
# 5. Mercato con precisione bassa = penalizzazione reale.
# 6. Mercato con precisione alta = premio reale.
# 7. Le fasce AI Score vengono imparate dai dati.
# 8. Le fasce Fiducia vengono imparate dai dati.
# 9. Il rischio finale deve essere coerente con il risultato.
#
# DATI ATTUALI:
#
# 44 pronostici verificati
# Precisione generale: 70.5%
#
# AI SCORE:
# 60-69 -> 75.0%
# 70-79 -> 47.4%
# 80-89 -> 93.8%
#
# FIDUCIA:
# 70-79 -> 62.5%
# 80-89 -> 81.8%
# 90-100 -> 66.7%
#
# MERCATI:
# Over 1.5 -> 72.0%
# Under 3.5 -> 87.5%
# Goal -> 66.7%
# Over 2.5 -> 40.0%
#
# ============================================================


def _numero(value, default=0):
    """
    Conversione sicura a float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, minimo=0, massimo=100):
    """
    Mantiene un valore nell'intervallo specificato.
    """
    return max(minimo, min(value, massimo))


def _affidabilita_storico(totale):
    """
    Affidabilità progressiva dello storico.

    <3  = nessuna influenza
    3-4 = 25%
    5-9 = 50%
    10-19 = 75%
    20+ = 100%
    """

    try:
        totale = int(totale)
    except (TypeError, ValueError):
        totale = 0

    if totale < 3:
        return 0.0

    if totale < 5:
        return 0.25

    if totale < 10:
        return 0.50

    if totale < 20:
        return 0.75

    return 1.0


def _trova_fascia(dati, valore):
    """
    Trova la fascia corrispondente a un valore.

    Compatibile con:
    statistiche_ai_score()
    statistiche_fiducia()
    """

    valore = _numero(valore)

    if valore < 60:
        fascia = "0-59"

    elif valore < 70:
        fascia = "60-69"

    elif valore < 80:
        fascia = "70-79"

    elif valore < 90:
        fascia = "80-89"

    else:
        fascia = "90-100"

    if not isinstance(dati, dict):
        return {
            "fascia": fascia,
            "totale": 0,
            "precisione": 0
        }

    elemento = dati.get(fascia)

    if not isinstance(elemento, dict):
        return {
            "fascia": fascia,
            "totale": 0,
            "precisione": 0
        }

    totale = int(
        _numero(
            elemento.get(
                "totale",
                0
            )
        )
    )

    precisione = _numero(
        elemento.get(
            "precisione",
            elemento.get(
                "accuracy",
                0
            )
        )
    )

    return {
        "fascia": fascia,
        "totale": totale,
        "precisione": precisione
    }


def _correzione_fascia(
    precisione,
    totale,
    peso,
    forza=0.10,
    massimo=2.0
):
    """
    Correzione basata sulla precisione reale della fascia.

    50% = neutro.

    >50% = premio.
    <50% = penalizzazione.

    Con meno di 3 dati:
    nessuna influenza.
    """

    try:
        totale = int(totale)
    except (TypeError, ValueError):
        totale = 0

    if totale < 3:
        return 0

    precisione = _numero(
        precisione
    )

    affidabilita = _affidabilita_storico(
        totale
    )

    correzione = (
        (precisione - 50)
        * forza
        * affidabilita
        * peso
    )

    return round(
        max(
            -massimo,
            min(
                correzione,
                massimo
            )
        ),
        2
    )


def _correzione_mercato_reale(
    precisione,
    totale,
    peso
):
    """
    Correzione specifica del mercato.

    Questa funzione è volutamente più sensibile
    rispetto alle fasce generali.

    Motivo:
    se abbiamo già molti risultati di uno specifico
    mercato, vogliamo che CalcioAI li consideri
    seriamente.

    Esempi:

    40% -> penalizzazione
    50% -> neutro
    70% -> premio
    85% -> premio forte
    """

    try:
        totale = int(totale)
    except (TypeError, ValueError):
        totale = 0

    if totale < 3:
        return 0

    precisione = _numero(
        precisione
    )

    affidabilita = _affidabilita_storico(
        totale
    )

    differenza = precisione - 50

    # Sensibilità maggiore rispetto alla correzione
    # generale del mercato.
    correzione = (
        differenza
        * 0.12
        * affidabilita
        * peso
    )

    return round(
        max(
            -3.5,
            min(
                correzione,
                3.5
            )
        ),
        2
    )


def scegli_pronostico(
    mercati,
    ai_score,
    rischio,
    stats_casa=None,
    stats_trasferta=None,
    indicatori=None,
    lega="",
    fiducia=None
):

    # ========================================================
    # NESSUN MERCATO
    # ========================================================

    if not mercati:

        return {
            "mercato": "Nessun pronostico",
            "probabilita": 0,
            "score_finale": 0,
            "value_index": 0,
            "rischio": "🔴 Alto",
            "classifica": [],
            "giudizio": (
                "❌ Nessun mercato disponibile."
            )
        }

    # ========================================================
    # NORMALIZZAZIONE
    # ========================================================

    if fiducia is None:
        fiducia = 0

    fiducia = _clamp(
        _numero(fiducia),
        0,
        100
    )

    ai_score = _clamp(
        _numero(ai_score),
        0,
        100
    )

    # ========================================================
    # STORICO GLOBALE
    # ========================================================

    storico = statistiche_mercati()

    if not isinstance(storico, dict):
        storico = {}

    totale_storico = sum(
        int(
            _numero(
                dati.get(
                    "totale",
                    0
                )
            )
        )
        for dati in storico.values()
        if isinstance(dati, dict)
    )

    peso = peso_learning(
        totale_storico
    )

    print("")
    print(
        f"🧠 LEARNING ENGINE 4.2 | "
        f"Pronostici verificati: "
        f"{totale_storico} | "
        f"Peso learning: "
        f"{peso * 100:.0f}%"
    )

    # ========================================================
    # STATISTICHE FASCE
    # ========================================================

    try:
        statistiche_score = (
            statistiche_ai_score()
        )
    except Exception as e:

        print(
            "⚠️ ERRORE STATISTICHE AI SCORE:",
            e
        )

        statistiche_score = {}

    try:
        statistiche_confidenza = (
            statistiche_fiducia()
        )
    except Exception as e:

        print(
            "⚠️ ERRORE STATISTICHE FIDUCIA:",
            e
        )

        statistiche_confidenza = {}

    # ========================================================
    # CORREZIONI GLOBALI
    # ========================================================

    correzione_score_globale = (
        correzione_ai_score(
            ai_score
        )
    )

    correzione_fiducia_globale = (
        correzione_fiducia(
            fiducia
        )
    )

    fascia_score = _trova_fascia(
        statistiche_score,
        ai_score
    )

    fascia_fiducia = _trova_fascia(
        statistiche_confidenza,
        fiducia
    )

    # --------------------------------------------------------
    # FASCE DATA-DRIVEN
    # --------------------------------------------------------

    bonus_fascia_score = (
        _correzione_fascia(
            fascia_score["precisione"],
            fascia_score["totale"],
            peso,
            forza=0.10,
            massimo=2.0
        )
    )

    bonus_fascia_fiducia = (
        _correzione_fascia(
            fascia_fiducia["precisione"],
            fascia_fiducia["totale"],
            peso,
            forza=0.08,
            massimo=1.5
        )
    )

    print(
        f"🧠 LEARNING SCORE | "
        f"{fascia_score['fascia']} | "
        f"Storico: "
        f"{fascia_score['totale']} | "
        f"Precisione: "
        f"{fascia_score['precisione']:.1f} | "
        f"Correzione: "
        f"{bonus_fascia_score:+.2f}"
    )

    print(
        f"🧠 LEARNING FIDUCIA | "
        f"{fascia_fiducia['fascia']} | "
        f"Storico: "
        f"{fascia_fiducia['totale']} | "
        f"Precisione: "
        f"{fascia_fiducia['precisione']:.1f} | "
        f"Correzione: "
        f"{bonus_fascia_fiducia:+.2f}"
    )

    print(
        f"🧠 LEARNING GLOBALE | "
        f"AI Score: {ai_score:.1f} | "
        f"Correzione: "
        f"{correzione_score_globale:+.2f} | "
        f"Fiducia: {fiducia:.1f} | "
        f"Correzione: "
        f"{correzione_fiducia_globale:+.2f}"
    )

    # ========================================================
    # RISULTATI
    # ========================================================

    risultati = {}

    # ========================================================
    # ANALISI MERCATI
    # ========================================================

    for mercato, probabilita in mercati.items():

        mercato_storico = normalizza_mercato(
            mercato
        )

        probabilita = _clamp(
            _numero(probabilita),
            0,
            100
        )

        # ----------------------------------------------------
        # STORICO DEL MERCATO
        # ----------------------------------------------------

        storico_totale = 0
        precisione_storica = 0

        if mercato_storico in storico:

            dati = storico[
                mercato_storico
            ]

            if isinstance(dati, dict):

                storico_totale = int(
                    _numero(
                        dati.get(
                            "totale",
                            0
                        )
                    )
                )

                precisione_storica = _numero(
                    dati.get(
                        "precisione",
                        0
                    )
                )

        affidabilita_storico = (
            _affidabilita_storico(
                storico_totale
            )
        )

        # ----------------------------------------------------
        # CORREZIONE MERCATO
        # ----------------------------------------------------

        correzione_learning = (
            correzione_learning_mercato(
                mercato_storico
            )
        )

        correzione_learning = _numero(
            correzione_learning
        )

        learning_effect_mercato_base = (
            correzione_learning
            * peso
            * affidabilita_storico
        )

        # ----------------------------------------------------
        # CORREZIONE MERCATO REALE
        # ----------------------------------------------------
        #
        # Questa è la nuova componente 4.2.
        #
        # Serve a rendere realmente incisivo lo storico
        # del singolo mercato.
        #

        learning_effect_mercato_reale = (
            _correzione_mercato_reale(
                precisione_storica,
                storico_totale,
                peso
            )
        )

        # ----------------------------------------------------
        # STORICO BONUS
        # ----------------------------------------------------

        storico_bonus = 0

        if storico_totale >= 3:

            if precisione_storica >= 90:
                storico_bonus = 4

            elif precisione_storica >= 85:
                storico_bonus = 3

            elif precisione_storica >= 80:
                storico_bonus = 2.5

            elif precisione_storica >= 75:
                storico_bonus = 2

            elif precisione_storica >= 70:
                storico_bonus = 1

            elif precisione_storica <= 40:
                storico_bonus = -4

            elif precisione_storica <= 50:
                storico_bonus = -3

            elif precisione_storica <= 60:
                storico_bonus = -1.5

        storico_bonus *= (
            affidabilita_storico
        )

        # ----------------------------------------------------
        # STORICO SCORE
        # ----------------------------------------------------

        storico_score = 0

        if storico_totale >= 3:

            if precisione_storica >= 90:
                storico_score = 5

            elif precisione_storica >= 85:
                storico_score = 4

            elif precisione_storica >= 80:
                storico_score = 3

            elif precisione_storica >= 75:
                storico_score = 2

            elif precisione_storica >= 70:
                storico_score = 1

            elif precisione_storica <= 40:
                storico_score = -5

            elif precisione_storica <= 50:
                storico_score = -4

            elif precisione_storica <= 60:
                storico_score = -2

        storico_score *= (
            affidabilita_storico
        )

        # ----------------------------------------------------
        # VALUE INDEX
        # ----------------------------------------------------

        value_index = calcola_value_index(
            ai_score=ai_score,
            probabilita=probabilita,
            mercato=mercato,
            indicatori=indicatori,
            lega=lega,
            storico_bonus=storico_bonus,
            storico_totale=storico_totale
        )

        value_index = _clamp(
            _numero(value_index),
            0,
            100
        )

        # ----------------------------------------------------
        # LEARNING VALUE
        # ----------------------------------------------------

        correzione_value = (
            correzione_value_index(
                value_index
            )
        )

        correzione_value = _numero(
            correzione_value
        )

        learning_effect_value = (
            correzione_value
            * peso
            * affidabilita_storico
        )

        # ----------------------------------------------------
        # LEARNING SCORE GLOBALE
        # ----------------------------------------------------

        learning_effect_score = (
            correzione_score_globale
            * peso
        )

        # ----------------------------------------------------
        # LEARNING FIDUCIA
        # ----------------------------------------------------

        learning_effect_fiducia = (
            correzione_fiducia_globale
            * peso
        )

        # ----------------------------------------------------
        # MERCATI SENZA STORICO
        # ----------------------------------------------------

        if storico_totale == 0:

            # IMPORTANTISSIMO:
            #
            # Nessuno storico = nessun effetto
            # specifico del mercato.
            #
            learning_effect_mercato_base = 0
            learning_effect_mercato_reale = 0
            storico_bonus = 0
            storico_score = 0

            print(
                f"🧠 LEARNING MERCATO | "
                f"{mercato} | "
                f"Nessuno storico disponibile."
            )

        # ----------------------------------------------------
        # LEARNING TOTALE
        # ----------------------------------------------------

        learning_effect_totale = (
            learning_effect_mercato_base
            + learning_effect_mercato_reale
            + learning_effect_score
            + learning_effect_fiducia
            + learning_effect_value
            + bonus_fascia_score
            + bonus_fascia_fiducia
        )

        # ----------------------------------------------------
        # SCORE BASE
        # ----------------------------------------------------
        #
        # Value Index = componente principale.
        #
        # Probabilità = supporto.
        #
        # AI Score = componente indipendente.
        #
        # Storico Score = componente specifica.
        #

        score_base = (
            value_index * 0.55
            + probabilita * 0.20
            + ai_score * 0.10
            + storico_score
        )

        # ----------------------------------------------------
        # SCORE FINALE
        # ----------------------------------------------------

        score_learning = (
            score_base
            + learning_effect_totale
        )

        score_mercato = round(
            _clamp(
                score_learning,
                0,
                100
            ),
            2
        )

        # ----------------------------------------------------
        # AFFIDABILITÀ COMPLESSIVA
        # ----------------------------------------------------

        affidabilita_complessiva = (
            probabilita * 0.35
            + ai_score * 0.20
            + value_index * 0.25
            + precisione_storica
            * 0.20
            * affidabilita_storico
        )

        affidabilita_complessiva = round(
            _clamp(
                affidabilita_complessiva,
                0,
                100
            ),
            2
        )

        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        print(
            f"🧠 LEARNING | "
            f"{mercato} | "
            f"Storico: {storico_totale} | "
            f"Precisione: "
            f"{precisione_storica:.1f}% | "
            f"Affidabilità storico: "
            f"{affidabilita_storico * 100:.0f}% | "
            f"Mercato Base: "
            f"{learning_effect_mercato_base:+.2f} | "
            f"Mercato Reale: "
            f"{learning_effect_mercato_reale:+.2f} | "
            f"Score: "
            f"{learning_effect_score:+.2f} | "
            f"Fiducia: "
            f"{learning_effect_fiducia:+.2f} | "
            f"Value: "
            f"{learning_effect_value:+.2f} | "
            f"Fascia Score: "
            f"{bonus_fascia_score:+.2f} | "
            f"Fascia Fiducia: "
            f"{bonus_fascia_fiducia:+.2f} | "
            f"Learning Totale: "
            f"{learning_effect_totale:+.2f} | "
            f"Score Base: "
            f"{score_base:.2f} | "
            f"Score Finale: "
            f"{score_mercato}"
        )

        # ----------------------------------------------------
        # RISULTATO MERCATO
        # ----------------------------------------------------

        risultati[mercato] = {

            "probabilita": (
                probabilita
            ),

            "value_index": round(
                value_index,
                2
            ),

            "storico_totale": (
                storico_totale
            ),

            "precisione_storica": (
                precisione_storica
            ),

            "affidabilita_storico": round(
                affidabilita_storico,
                2
            ),

            "storico_bonus": round(
                storico_bonus,
                2
            ),

            "storico_score": round(
                storico_score,
                2
            ),

            "correzione_learning": round(
                correzione_learning,
                2
            ),

            "learning_effect": round(
                learning_effect_totale,
                2
            ),

            "learning_effect_mercato": round(
                learning_effect_mercato_base
                + learning_effect_mercato_reale,
                2
            ),

            "learning_effect_mercato_base": round(
                learning_effect_mercato_base,
                2
            ),

            "learning_effect_mercato_reale": round(
                learning_effect_mercato_reale,
                2
            ),

            "learning_effect_score": round(
                learning_effect_score,
                2
            ),

            "learning_effect_fiducia": round(
                learning_effect_fiducia,
                2
            ),

            "learning_effect_value": round(
                learning_effect_value,
                2
            ),

            "correzione_score": round(
                correzione_score_globale,
                2
            ),

            "correzione_fiducia": round(
                correzione_fiducia_globale,
                2
            ),

            "correzione_value": round(
                correzione_value,
                2
            ),

            "bonus_fascia_score": round(
                bonus_fascia_score,
                2
            ),

            "bonus_fascia_fiducia": round(
                bonus_fascia_fiducia,
                2
            ),

            "score_base": round(
                score_base,
                2
            ),

            "score_mercato": (
                score_mercato
            ),

            "affidabilita_complessiva": (
                affidabilita_complessiva
            ),

            "fascia_score": (
                fascia_score["fascia"]
            ),

            "fascia_score_totale": (
                fascia_score["totale"]
            ),

            "fascia_score_precisione": (
                fascia_score["precisione"]
            ),

            "fascia_fiducia": (
                fascia_fiducia["fascia"]
            ),

            "fascia_fiducia_totale": (
                fascia_fiducia["totale"]
            ),

            "fascia_fiducia_precisione": (
                fascia_fiducia["precisione"]
            )
        }

    # ========================================================
    # CLASSIFICA
    # ========================================================

    classifica = sorted(
        risultati.items(),
        key=lambda x: (
            x[1]["score_mercato"],
            x[1]["affidabilita_complessiva"],
            x[1]["value_index"],
            x[1]["probabilita"],
            x[1]["precisione_storica"]
        ),
        reverse=True
    )

    if not classifica:

        return {
            "mercato": "Nessun pronostico",
            "probabilita": 0,
            "score_finale": 0,
            "value_index": 0,
            "rischio": "🔴 Alto",
            "classifica": [],
            "giudizio": (
                "❌ Nessun mercato analizzabile."
            )
        }

    # ========================================================
    # MIGLIORE MERCATO
    # ========================================================

    migliore_mercato = (
        classifica[0][0]
    )

    migliore = risultati[
        migliore_mercato
    ]

    probabilita = (
        migliore["probabilita"]
    )

    value_index = (
        migliore["value_index"]
    )

    score_finale = (
        migliore["score_mercato"]
    )

    affidabilita_complessiva = (
        migliore["affidabilita_complessiva"]
    )

    # ========================================================
    # RISCHIO
    # ========================================================

    rischio_input = str(
        rischio or ""
    ).lower()

    # --------------------------------------------------------
    # NESSUN PRONOSTICO
    # --------------------------------------------------------

    if value_index < 65:

        mercato_finale = (
            "Nessun pronostico"
        )

        giudizio = (
            "❌ Value Index troppo basso. "
            "L'AI preferisce non esporsi."
        )

        rischio_finale = (
            "🔴 Alto"
        )

    elif score_finale < 60:

        mercato_finale = (
            "Nessun pronostico"
        )

        giudizio = (
            "❌ Il punteggio decisionale "
            "non raggiunge una soglia sufficiente."
        )

        rischio_finale = (
            "🔴 Alto"
        )

    elif score_finale < 70:

        mercato_finale = (
            migliore_mercato
        )

        giudizio = (
            "🟡 Pronostico prudente. "
            "I dati sono positivi ma ancora "
            "non abbastanza forti."
        )

        rischio_finale = (
            "🟡 Medio"
        )

    elif score_finale < 78:

        mercato_finale = (
            migliore_mercato
        )

        giudizio = (
            "🟢 Pronostico supportato da una "
            "buona convergenza tra AI, "
            "Value Index e Learning."
        )

        rischio_finale = (
            "🟡 Medio"
        )

    elif score_finale < 85:

        mercato_finale = (
            migliore_mercato
        )

        giudizio = (
            "🟢 Pronostico molto interessante. "
            "Buona convergenza dei dati e "
            "supporto del Learning."
        )

        rischio_finale = (
            "🟢 Basso"
        )

    else:

        mercato_finale = (
            migliore_mercato
        )

        giudizio = (
            "🔥 TOP PICK AI. "
            "Elevata convergenza tra probabilità, "
            "AI Score, Value Index e storico."
        )

        rischio_finale = (
            "🟢 Basso"
        )

    # ========================================================
    # PROTEZIONE RISCHIO INPUT
    # ========================================================
    #
    # Il rischio originale non può più trasformare
    # automaticamente un buon pronostico in Alto.
    #
    # Può però abbassare il livello quando i dati
    # finali sono realmente borderline.
    #

    if rischio_input in (
        "alto",
        "high",
        "🔴 alto"
    ):

        if (
            score_finale < 70
            or value_index < 70
            or affidabilita_complessiva < 65
        ):

            rischio_finale = (
                "🔴 Alto"
            )

        elif score_finale < 78:

            rischio_finale = (
                "🟡 Medio"
            )

    # ========================================================
    # TOP 3
    # ========================================================

    top_mercati = []

    for mercato, dati in classifica[:3]:

        top_mercati.append(
            (
                mercato,
                dati["value_index"]
            )
        )

    # ========================================================
    # LOG FINALE
    # ========================================================

    print("")
    print(
        "🏆 DECISION ENGINE 4.2"
    )

    print(
        f"🥇 Mercato scelto: "
        f"{mercato_finale}"
    )

    print(
        f"📊 Probabilità: "
        f"{probabilita:.1f}%"
    )

    print(
        f"💰 Value Index: "
        f"{value_index:.1f}"
    )

    print(
        f"🤖 AI Score: "
        f"{ai_score:.1f}"
    )

    print(
        f"🧠 Score Decisione: "
        f"{score_finale:.2f}"
    )

    print(
        f"📚 Storico mercato: "
        f"{migliore['storico_totale']}"
    )

    print(
        f"🎯 Precisione storico: "
        f"{migliore['precisione_storica']:.1f}%"
    )

    print(
        f"⚖️ Affidabilità storico: "
        f"{migliore['affidabilita_storico'] * 100:.0f}%"
    )

    print(
        f"🧠 Effetto Learning: "
        f"{migliore['learning_effect']:+.2f}"
    )

    print(
        f"📈 Affidabilità complessiva: "
        f"{affidabilita_complessiva:.2f}"
    )

    print(
        f"⚠️ Rischio: "
        f"{rischio_finale}"
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "mercato": (
            mercato_finale
        ),

        "probabilita": (
            probabilita
            if mercato_finale
            != "Nessun pronostico"
            else 0
        ),

        "score_finale": (
            score_finale
        ),

        "value_index": (
            value_index
        ),

        "rischio": (
            rischio_finale
        ),

        "classifica": (
            top_mercati
        ),

        "giudizio": (
            giudizio
        ),

        "storico_totale": (
            migliore[
                "storico_totale"
            ]
        ),

        "precisione_storica": (
            migliore[
                "precisione_storica"
            ]
        ),

        "storico_bonus": (
            migliore[
                "storico_bonus"
            ]
        ),

        "storico_score": (
            migliore[
                "storico_score"
            ]
        ),

        "peso_learning": (
            peso
        ),

        "correzione_learning": (
            migliore[
                "correzione_learning"
            ]
        ),

        "learning_effect": (
            migliore[
                "learning_effect"
            ]
        ),

        "learning_effect_mercato": (
            migliore[
                "learning_effect_mercato"
            ]
        ),

        "learning_effect_mercato_base": (
            migliore[
                "learning_effect_mercato_base"
            ]
        ),

        "learning_effect_mercato_reale": (
            migliore[
                "learning_effect_mercato_reale"
            ]
        ),

        "learning_effect_score": (
            migliore[
                "learning_effect_score"
            ]
        ),

        "learning_effect_fiducia": (
            migliore[
                "learning_effect_fiducia"
            ]
        ),

        "learning_effect_value": (
            migliore[
                "learning_effect_value"
            ]
        ),

        "correzione_score": (
            migliore[
                "correzione_score"
            ]
        ),

        "correzione_fiducia": (
            migliore[
                "correzione_fiducia"
            ]
        ),

        "correzione_value": (
            migliore[
                "correzione_value"
            ]
        ),

        "score_base": (
            migliore[
                "score_base"
            ]
        ),

        "affidabilita_storico": (
            migliore[
                "affidabilita_storico"
            ]
        ),

        "affidabilita_complessiva": (
            migliore[
                "affidabilita_complessiva"
            ]
        ),

        "bonus_fascia_score": (
            migliore[
                "bonus_fascia_score"
            ]
        ),

        "bonus_fascia_fiducia": (
            migliore[
                "bonus_fascia_fiducia"
            ]
        ),

        "fascia_score": (
            migliore[
                "fascia_score"
            ]
        ),

        "fascia_score_totale": (
            migliore[
                "fascia_score_totale"
            ]
        ),

        "fascia_score_precisione": (
            migliore[
                "fascia_score_precisione"
            ]
        ),

        "fascia_fiducia": (
            migliore[
                "fascia_fiducia"
            ]
        ),

        "fascia_fiducia_totale": (
            migliore[
                "fascia_fiducia_totale"
            ]
        ),

        "fascia_fiducia_precisione": (
            migliore[
                "fascia_fiducia_precisione"
            ]
        )
    }