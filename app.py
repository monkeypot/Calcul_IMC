from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Création de la BD si elle n'existe pas
def init_db():
    conn = sqlite3.connect("imc.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imc_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poids REAL,
            taille REAL,
            imc REAL,
            interpretation TEXT
        )
    """)
    conn.commit()
    conn.close()

# Sauvegarde dans la BD
def save_result(poids, taille, imc, interpretation):
    conn = sqlite3.connect("imc.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO imc_results (poids, taille, imc, interpretation) VALUES (?, ?, ?, ?)",
                   (poids, taille, imc, interpretation))
    conn.commit()
    conn.close()

# Récupérer les résultats stockés
def get_results():
    conn = sqlite3.connect("imc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT poids, taille, imc, interpretation FROM imc_results ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    results = get_results()

    if request.method == "POST":
        try:
            # Récupération et conversion des valeurs
            poids = float(request.form.get("poids", 0))
            taille = float(request.form.get("taille", 0))

            # Validation des valeurs
            if poids <= 0 or poids > 1000:
                error = "Poids invalide (0 < poids ≤ 1000 kg)"
            elif taille <= 0 or taille > 3:
                error = "Taille invalide (0 < taille ≤ 3 m)"
            else:
                # Calcul IMC
                imc = round(poids / (taille ** 2), 2)

                # Détermination de l'interprétation
                if imc < 18.5:
                    interpretation = "Insuffisance pondérale"
                elif 18.5 <= imc < 25:
                    interpretation = "Poids normal"
                elif 25 <= imc < 30:
                    interpretation = "Surpoids"
                else:
                    interpretation = "Obésité"

                # Sauvegarde uniquement si aucune erreur
                save_result(poids, taille, imc, interpretation)

                # Redirection pour éviter le repost lors du refresh
                return redirect(url_for('index'))

        except ValueError:
            error = "Entrée invalide : veuillez entrer des nombres valides pour le poids et la taille."
        except Exception as e:
            error = f"Erreur inattendue : {str(e)}"

    # Affichage des résultats et éventuelles erreurs
    return render_template("index.html", results=results, error=error)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)