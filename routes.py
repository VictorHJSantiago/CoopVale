# Arquivo principal para rodar a aplicação Flask
from app import create_app


from flask import render_template, flash


# Criação da aplicação Flask
app = create_app()


# área de rotas
@app.route("/")
def home():
    return render_template("home.html", titulo="App de Exemplo - Blueprints")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
