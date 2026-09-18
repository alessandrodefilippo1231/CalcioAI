from services.partite_oggi import partite_oggi


def seleziona_partita(numero):

    partite = partite_oggi()


    try:

        indice = int(numero) - 1


        if indice < 0 or indice >= len(partite):

            return None


        return partite[indice]


    except:

        return None