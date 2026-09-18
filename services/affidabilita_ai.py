def livello_affidabilita(ai_score):

    if ai_score >= 85:

        return {
            "livello": "🟢 Molto alta",
            "barra": "█████████░",
            "percentuale": ai_score
        }


    elif ai_score >= 70:

        return {
            "livello": "🟡 Buona",
            "barra": "███████░░░",
            "percentuale": ai_score
        }


    elif ai_score >= 55:

        return {
            "livello": "🟠 Media",
            "barra": "█████░░░░░",
            "percentuale": ai_score
        }


    else:

        return {
            "livello": "🔴 Bassa",
            "barra": "███░░░░░░░",
            "percentuale": ai_score
        }