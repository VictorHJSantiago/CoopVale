from app import create_app
from app.extensions import db
from app.models.core import Categoria

app = create_app()

if __name__ == "__main__":
    # Permite seed rápido via argumento: python run.py seed-categorias
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'seed-categorias':
        with app.app_context():
            categorias = [
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
            for cat in categorias:
                if not Categoria.query.filter_by(nome=cat['nome']).first():
                    db.session.add(Categoria(**cat))
            db.session.commit()
            print('Categorias inseridas com sucesso!')
    elif len(sys.argv) > 1 and sys.argv[1] == 'seed-logistica':
        # Insere pontos de retirada e taxas de entrega básicas
        from app.models.core import PontoRetirada, TaxaEntrega
        with app.app_context():
            pontos = [
                {"nome": "Sede CoopVale", "endereco": "Rua Central, 100", "cidade": "Cidade A", "cep": "84000-000", "dias_funcionamento": "Seg-Sex", "horario_abertura": "08:00", "horario_fechamento": "18:00", "ativo": True},
                {"nome": "Feira Livre", "endereco": "Praça das Flores", "cidade": "Cidade B", "cep": "84010-000", "dias_funcionamento": "Sábado", "horario_abertura": "07:00", "horario_fechamento": "12:00", "ativo": True},
            ]
            for p in pontos:
                if not PontoRetirada.query.filter_by(nome=p['nome']).first():
                    db.session.add(PontoRetirada(**p))
            taxas = [
                {"regiao": "Centro", "valor": 10.0, "prazo_dias": 1, "ativo": True},
                {"regiao": "Zona Norte", "valor": 15.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Zona Sul", "valor": 18.0, "prazo_dias": 2, "ativo": True},
            ]
            for t in taxas:
                if not TaxaEntrega.query.filter_by(regiao=t['regiao']).first():
                    db.session.add(TaxaEntrega(**t))
            db.session.commit()
            print('Logística semeada com sucesso! (pontos e taxas)')
    else:
        # Roda a aplicação na porta 8000 conforme o exemplo
        app.run(debug=True, port=8000)