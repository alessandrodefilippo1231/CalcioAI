from telegram import Update
from telegram.ext import ContextTypes

from services.partite_oggi import partite_oggi
from services.cache_statistiche import prendi_statistiche
from services.risultati_ai import analizza_risultato


# ============================================================
# CALCIOAI - RISULTATI AI
# ============================================================
#
# Modulo completamente separato dalla SCHEDINA.
#
# Utilizza:
# - statistiche già presenti nella cache
# - media gol fatti
# - media gol subiti
# - Over 1.5
# - Over 2.5
# - Goal/GG
# - fattore campo
#
# NON utilizza il Decision Engine.
# NON salva pronostici nello storico.
# NON modifica la schedina.
#
# ============================================================


MAX_PARTITE_RISULTATI = 5


# ============================================================
# CONVERSIONE SICURA
# ============================================================

def numero(valore, default=0.0):

    try:
        return float(valore)
    except (TypeError, ValueError):
        return default


# ============================================================
# PREPARA PARTITA
# ============================================================

def prepara_partita(partita):

    if (
        "teams" in partita
        and "league" in partita
    ):
        return partita

    return {
        "id": partita.get("id"),

        "fixture": {
            "id": partita.get("id"),
            "date": (
                partita.get("data")
                or partita.get("date")
                or ""
            )
        },

        "teams": {
            "home": {
                "id": partita.get("home_id"),
                "name": partita.get(
                    "casa",
                    "Casa"
                )
            },

            "away": {
                "id": partita.get("away_id"),
                "name": partita.get(
                    "trasferta",
                    "Trasferta"
                )
            }
        },

        "league": {
            "name": partita.get(
                "lega",
                "Campionato"
            ),

            "country": partita.get(
                "paese",
                ""
            )
        }
    }


# ============================================================
# CALCOLO GOL ATTESI
# ============================================================

def calcola_gol_attesi(
    statistiche_casa,
    statistiche_trasferta
):
    """
    Calcola i gol attesi utilizzando più indicatori
    rispetto alla versione precedente.

    Indicatori utilizzati:

    - media gol fatti
    - media gol subiti
    - Over 1.5
    - Over 2.5
    - Goal/GG

    L'obiettivo è evitare che il modello finisca
    troppo spesso automaticamente sull'1-1.
    """

    # --------------------------------------------------------
    # DATI CASA
    # --------------------------------------------------------

    casa_fatti = numero(
        statistiche_casa.get(
            "media_gol_fatti"
        )
    )

    casa_subiti = numero(
        statistiche_casa.get(
            "media_gol_subiti"
        )
    )

    casa_over15 = numero(
        statistiche_casa.get(
            "over15"
        )
    )

    casa_over25 = numero(
        statistiche_casa.get(
            "over25"
        )
    )

    casa_goal = numero(
        statistiche_casa.get(
            "golgol"
        )
    )

    # --------------------------------------------------------
    # DATI TRASFERTA
    # --------------------------------------------------------

    trasferta_fatti = numero(
        statistiche_trasferta.get(
            "media_gol_fatti"
        )
    )

    trasferta_subiti = numero(
        statistiche_trasferta.get(
            "media_gol_subiti"
        )
    )

    trasferta_over15 = numero(
        statistiche_trasferta.get(
            "over15"
        )
    )

    trasferta_over25 = numero(
        statistiche_trasferta.get(
            "over25"
        )
    )

    trasferta_goal = numero(
        statistiche_trasferta.get(
            "golgol"
        )
    )

    # ========================================================
    # BASE GOL ATTESI
    # ========================================================

    gol_casa_base = (
        casa_fatti
        + trasferta_subiti
    ) / 2

    gol_trasferta_base = (
        trasferta_fatti
        + casa_subiti
    ) / 2

    # ========================================================
    # FATTORE OFFENSIVO
    # ========================================================
    #
    # Se una squadra segna molto, aumentiamo leggermente
    # il suo valore.
    #
    # Se segna poco, lo riduciamo.
    #
    # Non esageriamo con la correzione.
    # ========================================================

    if casa_fatti >= 1.80:
        gol_casa_base *= 1.10

    elif casa_fatti >= 1.40:
        gol_casa_base *= 1.05

    elif casa_fatti <= 0.70:
        gol_casa_base *= 0.90

    # --------------------------------------------------------

    if trasferta_fatti >= 1.80:
        gol_trasferta_base *= 1.10

    elif trasferta_fatti >= 1.40:
        gol_trasferta_base *= 1.05

    elif trasferta_fatti <= 0.70:
        gol_trasferta_base *= 0.90

    # ========================================================
    # CORREZIONE OVER 2.5
    # ========================================================
    #
    # Se entrambe le squadre hanno percentuali Over 2.5
    # alte, aumentiamo leggermente i gol attesi.
    #
    # Se entrambe sono basse, li riduciamo.
    # ========================================================

    media_over25 = (
        casa_over25
        + trasferta_over25
    ) / 2

    if media_over25 >= 70:
        gol_casa_base *= 1.08
        gol_trasferta_base *= 1.08

    elif media_over25 >= 55:
        gol_casa_base *= 1.04
        gol_trasferta_base *= 1.04

    elif media_over25 <= 30:
        gol_casa_base *= 0.94
        gol_trasferta_base *= 0.94

    # ========================================================
    # CORREZIONE OVER 1.5
    # ========================================================

    media_over15 = (
        casa_over15
        + trasferta_over15
    ) / 2

    if media_over15 >= 80:
        gol_casa_base *= 1.04
        gol_trasferta_base *= 1.04

    elif media_over15 <= 55:
        gol_casa_base *= 0.97
        gol_trasferta_base *= 0.97

    # ========================================================
    # CORREZIONE GOAL / GG
    # ========================================================
    #
    # Se entrambe le squadre hanno alta frequenza GG,
    # aumentiamo leggermente la probabilità di gol
    # della squadra ospite e della partita in generale.
    # ========================================================

    media_goal = (
        casa_goal
        + trasferta_goal
    ) / 2

    if media_goal >= 70:

        gol_casa_base *= 1.04
        gol_trasferta_base *= 1.06

    elif media_goal <= 35:

        gol_casa_base *= 0.97
        gol_trasferta_base *= 0.95

    # ========================================================
    # FATTORE CAMPO
    # ========================================================

    gol_casa = gol_casa_base * 1.05
    gol_trasferta = gol_trasferta_base * 0.95

    # ========================================================
    # CORREZIONE LEGGERA PER EVITARE RISULTATI TROPPO
    # COMPRESSI INTORNO ALL'1-1
    # ========================================================
    #
    # Se una squadra è chiaramente più produttiva
    # dell'altra, lasciamo emergere maggiormente
    # la differenza.
    # ========================================================

    differenza_offensiva = (
        casa_fatti
        - trasferta_fatti
    )

    if differenza_offensiva >= 0.80:

        gol_casa *= 1.06
        gol_trasferta *= 0.96

    elif differenza_offensiva <= -0.80:

        gol_casa *= 0.96
        gol_trasferta *= 1.06

    # ========================================================
    # LIMITI REALISTICI
    # ========================================================

    gol_casa = max(
        0.20,
        min(gol_casa, 4.00)
    )

    gol_trasferta = max(
        0.20,
        min(gol_trasferta, 4.00)
    )

    return (
        round(gol_casa, 2),
        round(gol_trasferta, 2)
    )


# ============================================================
# RECUPERA STATISTICHE
# ============================================================

def recupera_statistiche_squadra(
    team_id,
    nome
):
    """
    Recupera le statistiche dalla cache.

    Se la squadra è già presente:
    nessuna nuova chiamata API.
    """

    if not team_id:

        print(
            f"⚠️ ID SQUADRA MANCANTE: {nome}"
        )

        return None

    try:

        statistiche = prendi_statistiche(
            team_id
        )

        if statistiche:

            print(
                f"💾 RISULTATI CACHE: "
                f"{nome} | ID {team_id}"
            )

            return statistiche

        print(
            f"⚠️ STATISTICHE NON IN CACHE: "
            f"{nome} | ID {team_id}"
        )

        return None

    except Exception as e:

        print(
            f"❌ ERRORE CACHE {nome}: {e}"
        )

        return None


# ============================================================
# FORMATTA PERCENTUALE
# ============================================================

def formatta_percentuale(valore):

    try:
        return f"{float(valore):.1f}%"
    except (TypeError, ValueError):
        return "N/D"


# ============================================================
# COMANDO /RISULTATI
# ============================================================

async def risultati(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print("")
    print("=" * 55)
    print("🎯 AVVIO COMANDO /RISULTATI")
    print("=" * 55)

    # ========================================================
    # PARTITE
    # ========================================================

    try:

        partite = await partite_oggi()

    except TypeError:

        try:

            partite = partite_oggi()

        except Exception as e:

            print(
                "❌ ERRORE RECUPERO PARTITE:",
                e
            )

            await update.message.reply_text(
                "❌ Errore durante il recupero delle partite."
            )

            return

    except Exception as e:

        print(
            "❌ ERRORE RECUPERO PARTITE:",
            e
        )

        await update.message.reply_text(
            "❌ Errore durante il recupero delle partite."
        )

        return

    if not partite:

        print(
            "⚠️ NESSUNA PARTITA DISPONIBILE"
        )

        await update.message.reply_text(
            "🔥 Nessuna partita disponibile oggi."
        )

        return

    print(
        f"📦 PARTITE DISPONIBILI: {len(partite)}"
    )

    # ========================================================
    # ANALISI
    # ========================================================

    risultati_generati = []

    for partita in partite:

        if len(risultati_generati) >= MAX_PARTITE_RISULTATI:
            break

        try:

            casa = partita.get(
                "casa",
                "Casa"
            )

            trasferta = partita.get(
                "trasferta",
                "Trasferta"
            )

            home_id = partita.get(
                "home_id"
            )

            away_id = partita.get(
                "away_id"
            )

            print("")
            print(
                f"🔎 RISULTATO AI: "
                f"{casa} - {trasferta}"
            )

            # ------------------------------------------------
            # CACHE CASA
            # ------------------------------------------------

            stats_casa = (
                recupera_statistiche_squadra(
                    home_id,
                    casa
                )
            )

            # ------------------------------------------------
            # CACHE TRASFERTA
            # ------------------------------------------------

            stats_trasferta = (
                recupera_statistiche_squadra(
                    away_id,
                    trasferta
                )
            )

            # ------------------------------------------------
            # STATISTICHE INSUFFICIENTI
            # ------------------------------------------------

            if not stats_casa or not stats_trasferta:

                print(
                    f"⏭️ SALTATA: "
                    f"{casa} - {trasferta}"
                    f" | statistiche insufficienti"
                )

                continue

            # ------------------------------------------------
            # GOL ATTESI
            # ------------------------------------------------

            gol_casa, gol_trasferta = (
                calcola_gol_attesi(
                    stats_casa,
                    stats_trasferta
                )
            )

            print(
                f"⚽ GOL ATTESI: "
                f"{casa} {gol_casa}"
                f" - "
                f"{trasferta} {gol_trasferta}"
            )

            # ------------------------------------------------
            # ANALISI RISULTATO
            # ------------------------------------------------

            risultato = analizza_risultato(
                casa,
                trasferta,
                gol_casa,
                gol_trasferta
            )

            if not risultato:

                print(
                    "⚠️ ANALISI RISULTATO VUOTA"
                )

                continue

            risultato["gol_casa_attesi"] = (
                gol_casa
            )

            risultato["gol_trasferta_attesi"] = (
                gol_trasferta
            )

            risultati_generati.append(
                risultato
            )

        except Exception as e:

            print(
                f"❌ ERRORE RISULTATO "
                f"{partita.get('casa', '')} - "
                f"{partita.get('trasferta', '')}: "
                f"{e}"
            )

    # ========================================================
    # NESSUN RISULTATO
    # ========================================================

    if not risultati_generati:

        await update.message.reply_text(
            "🔥 Non ci sono abbastanza statistiche "
            "in cache per generare i risultati AI."
        )

        return

    # ========================================================
    # MESSAGGIO TELEGRAM
    # ========================================================

    testo = (
        "🎯 *CALCIOAI RISULTATI AI*\n\n"
        "🔮 Analisi separata dalla schedina.\n"
        "📊 Basata sulle statistiche delle squadre.\n\n"
    )

    for posizione, risultato in enumerate(
        risultati_generati,
        start=1
    ):

        casa = risultato.get(
            "casa",
            "Casa"
        )

        trasferta = risultato.get(
            "trasferta",
            "Trasferta"
        )

        gol_casa = risultato.get(
            "gol_casa_attesi",
            0
        )

        gol_trasferta = risultato.get(
            "gol_trasferta_attesi",
            0
        )

        risultato_esatto = risultato.get(
            "risultato_esatto",
            "N/D"
        )

        probabilita_esatto = risultato.get(
            "probabilita_risultato",
            0
        )

        parziale = risultato.get(
            "parziale_primo_tempo",
            "N/D"
        )

        probabilita_parziale = risultato.get(
            "probabilita_parziale",
            0
        )

        top_risultati = risultato.get(
            "top_risultati",
            []
        )

        top_parziali = risultato.get(
            "top_parziali",
            []
        )

        testo += (
            f"*{posizione}️⃣ "
            f"{casa} - {trasferta}*\n\n"

            f"⚽ Gol attesi: "
            f"{gol_casa:.2f} - "
            f"{gol_trasferta:.2f}\n\n"

            f"🔢 *RISULTATO ESATTO*\n"
            f"🥇 {risultato_esatto} "
            f"→ {formatta_percentuale(probabilita_esatto)}\n"
        )

        # ----------------------------------------------------
        # TOP 3 RISULTATI FINALI
        # ----------------------------------------------------

        if len(top_risultati) > 1:

            testo += "\n📊 *Top 3 finali:*\n"

            for indice, item in enumerate(
                top_risultati[:3],
                start=1
            ):

                testo += (
                    f"{indice}. "
                    f"{item.get('risultato', 'N/D')} "
                    f"→ "
                    f"{formatta_percentuale(item.get('probabilita', 0))}\n"
                )

        # ----------------------------------------------------
        # PRIMO TEMPO
        # ----------------------------------------------------

        testo += (
            f"\n⏱️ *PARZIALE 1° TEMPO*\n"
            f"🥇 {parziale} "
            f"→ {formatta_percentuale(probabilita_parziale)}\n"
        )

        # ----------------------------------------------------
        # TOP 3 PRIMO TEMPO
        # ----------------------------------------------------

        if len(top_parziali) > 1:

            testo += "\n📊 *Top 3 primo tempo:*\n"

            for indice, item in enumerate(
                top_parziali[:3],
                start=1
            ):

                testo += (
                    f"{indice}. "
                    f"{item.get('risultato', 'N/D')} "
                    f"→ "
                    f"{formatta_percentuale(item.get('probabilita', 0))}\n"
                )

        # ----------------------------------------------------
        # FINALE AI
        # ----------------------------------------------------

        testo += (
            f"\n🏁 *FINALE AI:* "
            f"{risultato_esatto}\n\n"
            "━━━━━━━━━━━━━━\n\n"
        )

    testo += (
        "🤖 *CalcioAI Risultati AI*\n"
        "📚 Modulo separato dalla schedina.\n"
        "⚠️ Previsione statistica, non garanzia di risultato."
    )

    await update.message.reply_text(
        testo,
        parse_mode="Markdown"
    )

    print("")
    print(
        f"✅ RISULTATI GENERATI: "
        f"{len(risultati_generati)}"
    )
    print("=" * 55)