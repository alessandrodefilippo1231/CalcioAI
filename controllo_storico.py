import sqlite3

DATABASE = "database/calcioai.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
    SELECT
        pronostico,
        COUNT(*),
        SUM(
            CASE
                WHEN esito = 'CORRETTO'
                THEN 1
                ELSE 0
            END
        )
    FROM storico
    WHERE esito IN ('CORRETTO', 'ERRATO')
    GROUP BY pronostico
    ORDER BY COUNT(*) DESC
""")

risultati = cursor.fetchall()

print()
print("========================================")
print("      STORICO CALCIOAI")
print("========================================")
print()

if not risultati:

    print("NESSUN RISULTATO PRESENTE")

else:

    for mercato, totale, corrette in risultati:

        corrette = corrette or 0

        precisione = round(
            corrette / totale * 100,
            1
        ) if totale else 0

        print(
            f"{mercato} | "
            f"Totale: {totale} | "
            f"Corrette: {corrette} | "
            f"Precisione: {precisione}%"
        )

print()
print("========================================")

conn.close()