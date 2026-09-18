import sqlite3
import requests

from config import FOOTBALL_API_KEY
from services.storico_ai import aggiorna_esito


DATABASE = "database/calcioai.db"



def partite_da_verificare():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    cursor.execute("""
        SELECT
            id,
            fixture_id,
            casa,
            trasferta,
            pronostico

        FROM storico

        WHERE esito IS NULL

        AND fixture_id IS NOT NULL
    """)


    dati = cursor.fetchall()

    conn.close()



    lista = []



    for partita in dati:

        lista.append({

            "id": partita[0],

            "fixture_id": partita[1],

            "casa": partita[2],

            "trasferta": partita[3],

            "pronostico": partita[4]

        })


    return lista






def risultato_partita(fixture_id):


    url = (
        "https://v3.football.api-sports.io/fixtures"
        f"?id={fixture_id}"
    )


    headers = {

        "x-apisports-key": FOOTBALL_API_KEY

    }



    try:

        response = requests.get(

            url,

            headers=headers,

            timeout=10

        )


        dati = response.json()


        partite = dati.get(
            "response",
            []
        )



        if not partite:

            return None



        partita = partite[0]


        stato = partita["fixture"]["status"]["short"]



        # Partita non ancora terminata

        stati_finiti = [

            "FT",

            "AET",

            "PEN"

        ]


        if stato not in stati_finiti:


            return None





        gol_casa = partita["goals"]["home"]

        gol_trasferta = partita["goals"]["away"]



        if gol_casa is None or gol_trasferta is None:

            return None





        return {

            "stato": "FINITA",

            "casa": gol_casa,

            "trasferta": gol_trasferta,

            "risultato":

                f"{gol_casa}-{gol_trasferta}"

        }




    except Exception as e:


        print(
            "Errore recupero risultato:",
            e
        )


        return None
def controlla_pronostico(
        pronostico,
        gol_casa,
        gol_trasferta
):


    totale = gol_casa + gol_trasferta



    if "Over 1.5" in pronostico:

        return totale >= 2



    if "Over 2.5" in pronostico:

        return totale >= 3



    if "Under 3.5" in pronostico:

        return totale <= 3



    if "Goal" in pronostico:

        return (

            gol_casa > 0

            and

            gol_trasferta > 0

        )



    if "No Goal" in pronostico:

        return (

            gol_casa == 0

            or

            gol_trasferta == 0

        )



    if pronostico == "1X":

        return gol_casa >= gol_trasferta



    if pronostico == "X2":

        return gol_trasferta >= gol_casa



    return False







def verifica_tutte():


    partite = partite_da_verificare()


    risultati = []



    for partita in partite:



        risultato = risultato_partita(

            partita["fixture_id"]

        )



        if risultato is None:

            continue





        corretto = controlla_pronostico(

            partita["pronostico"],

            risultato["casa"],

            risultato["trasferta"]

        )





        if corretto:

            esito = "CORRETTO"

        else:

            esito = "ERRATO"






        aggiorna_esito(

            partita["id"],

            risultato["risultato"],

            esito

        )





        risultati.append({

            "partita":

                f'{partita["casa"]} - {partita["trasferta"]}',


            "pronostico":

                partita["pronostico"],


            "risultato":

                risultato["risultato"],


            "esito":

                esito

        })



    return risultati