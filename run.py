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
                {"nome": "Verduras", "descricao": "Folhas, hortaliças e afins", "icone": "leaf", "valor_minimo": 10.0, "quantidade_minima": 2.0},
                {"nome": "Frutas", "descricao": "Frutas frescas e sazonais", "icone": "apple", "valor_minimo": 15.0, "quantidade_minima": 2.0},
                {"nome": "Legumes", "descricao": "Legumes variados", "icone": "carrot", "valor_minimo": 12.0, "quantidade_minima": 1.0},
                {"nome": "Laticínios", "descricao": "Leite, queijos, iogurtes", "icone": "cheese", "valor_minimo": 20.0, "quantidade_minima": 1.0},
                {"nome": "Carnes", "descricao": "Carnes e derivados", "icone": "drumstick", "valor_minimo": 30.0, "quantidade_minima": 1.0},
                {"nome": "Grãos", "descricao": "Arroz, feijão, cereais", "icone": "seedling", "valor_minimo": 25.0, "quantidade_minima": 2.0},
                {"nome": "Bebidas", "descricao": "Sucos, chás, bebidas naturais", "icone": "cup", "valor_minimo": 10.0, "quantidade_minima": 1.0},
                {"nome": "Doces", "descricao": "Doces, compotas, sobremesas", "icone": "ice-cream", "valor_minimo": 15.0, "quantidade_minima": 1.0},
                {"nome": "Pães e Massas", "descricao": "Pães, bolos, massas", "icone": "bread", "valor_minimo": 12.0, "quantidade_minima": 1.0},
                {"nome": "Outros", "descricao": "Produtos diversos", "icone": "box", "valor_minimo": 5.0, "quantidade_minima": 1.0},
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
                # Regiões Centrais
                {"regiao": "Centro", "valor": 8.0, "prazo_dias": 1, "ativo": True},
                {"regiao": "Centro Histórico", "valor": 10.0, "prazo_dias": 1, "ativo": True},
                {"regiao": "Tambaú", "valor": 12.0, "prazo_dias": 1, "ativo": True},
                {"regiao": "Manaíra", "valor": 12.0, "prazo_dias": 1, "ativo": True},
                {"regiao": "Bessa", "valor": 15.0, "prazo_dias": 1, "ativo": True},
                
                # Zona Norte
                {"regiao": "Zona Norte", "valor": 18.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Mangabeira", "valor": 20.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Valentina", "valor": 22.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Bancários", "valor": 18.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Cristo Redentor", "valor": 25.0, "prazo_dias": 2, "ativo": True},
                
                # Zona Sul
                {"regiao": "Zona Sul", "valor": 20.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Torre", "valor": 12.0, "prazo_dias": 1, "ativo": True},
                {"regiao": "Jaguaribe", "valor": 15.0, "prazo_dias": 1, "ativo": True},
                {"regiao": "Altiplano", "valor": 18.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Cabo Branco", "valor": 15.0, "prazo_dias": 1, "ativo": True},
                
                # Zona Leste
                {"regiao": "Zona Leste", "valor": 22.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Ernesto Geisel", "valor": 25.0, "prazo_dias": 3, "ativo": True},
                {"regiao": "José Américo", "valor": 28.0, "prazo_dias": 3, "ativo": True},
                {"regiao": "Grotão", "valor": 30.0, "prazo_dias": 3, "ativo": True},
                
                # Zona Oeste
                {"regiao": "Zona Oeste", "valor": 25.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Cruz das Armas", "valor": 22.0, "prazo_dias": 2, "ativo": True},
                {"regiao": "Jardim Cidade Universitária", "valor": 20.0, "prazo_dias": 2, "ativo": True},
                
                # Regiões Metropolitanas
                {"regiao": "Cabedelo", "valor": 30.0, "prazo_dias": 3, "ativo": True},
                {"regiao": "Bayeux", "valor": 28.0, "prazo_dias": 3, "ativo": True},
                {"regiao": "Santa Rita", "valor": 32.0, "prazo_dias": 3, "ativo": True},
                {"regiao": "Conde", "valor": 35.0, "prazo_dias": 4, "ativo": True},
                {"regiao": "Lucena", "valor": 40.0, "prazo_dias": 4, "ativo": True},
            ]
            for t in taxas:
                if not TaxaEntrega.query.filter_by(regiao=t['regiao']).first():
                    db.session.add(TaxaEntrega(**t))
            db.session.commit()
            print('Logística semeada com sucesso! (pontos e taxas)')
    else:
        # Roda a aplicação na porta 8000 conforme o exemplo
        app.run(debug=True, port=8000)