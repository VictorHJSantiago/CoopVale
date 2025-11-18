from app import create_app

app = create_app()

if __name__ == "__main__":
    # Roda a aplicação na porta 8000 conforme o exemplo
    app.run(debug=True, port=8000)