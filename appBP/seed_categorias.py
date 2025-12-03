from app import create_app
from app.extensions import db
from app.models.core import Categoria

CATEGORIAS = [
    {"nome": "Verduras", "descricao": "Folhas, hortaliças e afins", "icone": "leaf"},
    {"nome": "Frutas", "descricao": "Frutas frescas e sazonais", "icone": "apple"},
    {"nome": "Legumes", "descricao": "Legumes variados", "icone": "carrot"},
    {"nome": "Laticínios", "descricao": "Leite, queijos, iogurtes", "icone": "cheese"},
    {"nome": "Carnes", "descricao": "Carnes e derivados", "icone": "drumstick"},
    {"nome": "Grãos", "descricao": "Arroz, feijão, cereais", "icone": "seedling"},
    {"nome": "Bebidas", "descricao": "Sucos, chás, bebidas naturais", "icone": "cup"},
    {"nome": "Doces", "descricao": "Doces, compotas, sobremesas", "icone": "ice-cream"},
    {"nome": "Pães e Massas", "descricao": "Pães, bolos, massas", "icone": "bread"},
    {"nome": "Outros", "descricao": "Produtos diversos", "icone": "box"},
]

def main():
    app = create_app()
    with app.app_context():
        for cat in CATEGORIAS:
            if not Categoria.query.filter_by(nome=cat["nome"]).first():
                db.session.add(Categoria(**cat))
        db.session.commit()
        print("Categorias inseridas com sucesso!")

if __name__ == "__main__":
    main()