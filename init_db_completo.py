#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Inicialização Completa do Banco de Dados
Cria todas as tabelas e popula com dados iniciais
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models.core import (
    Usuario, Cliente, Produtor, Categoria, Produto,
    PontoRetirada, TaxaEntrega, Pedido, ItemPedido
)
from datetime import datetime, timedelta

app = create_app()

def limpar_banco():
    """Remove todas as tabelas"""
    print("🗑️  Limpando banco de dados...")
    with app.app_context():
        db.drop_all()
        print("✅ Banco limpo!")

def criar_tabelas():
    """Cria todas as tabelas"""
    print("🔨 Criando tabelas...")
    with app.app_context():
        db.create_all()
        print("✅ Tabelas criadas!")

def seed_categorias():
    """Popula categorias"""
    print("📦 Inserindo categorias...")
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
        
        for cat_data in categorias:
            cat = Categoria.query.filter_by(nome=cat_data['nome']).first()
            if not cat:
                cat = Categoria(**cat_data)
                db.session.add(cat)
        
        db.session.commit()
        print(f"✅ {len(categorias)} categorias inseridas!")

def seed_usuarios():
    """Cria usuários de teste"""
    print("👥 Criando usuários de teste...")
    with app.app_context():
        # Admin
        admin = Usuario.query.filter_by(email='admin@coopvale.com').first()
        if not admin:
            admin = Usuario(
                email='admin@coopvale.com',
                tipo_usuario='admin',
                ativo=True
            )
            admin.set_senha('admin123')
            db.session.add(admin)
        
        # Cliente
        cliente_user = Usuario.query.filter_by(email='cliente@teste.com').first()
        if not cliente_user:
            cliente_user = Usuario(
                email='cliente@teste.com',
                tipo_usuario='cliente',
                ativo=True,
                cpf='123.456.789-00'
            )
            cliente_user.set_senha('cliente123')
            db.session.add(cliente_user)
            db.session.flush()
            
            cliente = Cliente(
                usuario_id=cliente_user.id,
                nome='João Silva',
                cpf='12345678900',
                telefone='(83) 98765-4321'
            )
            db.session.add(cliente)
        
        # Produtor 1
        prod1_user = Usuario.query.filter_by(email='produtor1@coopvale.com').first()
        if not prod1_user:
            prod1_user = Usuario(
                email='produtor1@coopvale.com',
                tipo_usuario='produtor',
                ativo=True,
                cpf='987.654.321-00'
            )
            prod1_user.set_senha('produtor123')
            db.session.add(prod1_user)
            db.session.flush()
            
            produtor1 = Produtor(
                usuario_id=prod1_user.id,
                nome='Fazenda Orgânica São João',
                cpf='98765432100',
                telefone='(83) 99876-5432',
                endereco='Zona Rural, João Pessoa - PB',
                certificacoes='Certificação Orgânica Brasil',
                descricao='Produzimos verduras e legumes orgânicos há 15 anos'
            )
            db.session.add(produtor1)
        
        # Produtor 2
        prod2_user = Usuario.query.filter_by(email='produtor2@coopvale.com').first()
        if not prod2_user:
            prod2_user = Usuario(
                email='produtor2@coopvale.com',
                tipo_usuario='produtor',
                ativo=True,
                cpf='111.222.333-44'
            )
            prod2_user.set_senha('produtor123')
            db.session.add(prod2_user)
            db.session.flush()
            
            produtor2 = Produtor(
                usuario_id=prod2_user.id,
                nome='Sítio Frutas do Vale',
                cpf='11122233344',
                telefone='(83) 99111-2222',
                endereco='Zona Rural, Conde - PB',
                certificacoes='Agricultura Familiar',
                descricao='Especialistas em frutas tropicais e cítricas'
            )
            db.session.add(produtor2)
        
        db.session.commit()
        print("✅ Usuários criados!")

def seed_produtos():
    """Cria produtos de exemplo"""
    print("🥬 Inserindo produtos...")
    with app.app_context():
        produtor1 = Produtor.query.filter_by(cpf='98765432100').first()
        produtor2 = Produtor.query.filter_by(cpf='11122233344').first()
        
        if not produtor1 or not produtor2:
            print("❌ Produtores não encontrados. Execute seed_usuarios() primeiro.")
            return
        
        produtos = [
            # Produtor 1 - Verduras e Legumes
            {
                "nome": "Alface Crespa Orgânica",
                "descricao": "Alface crespa fresca, cultivada sem agrotóxicos",
                "preco": 3.50,
                "unidade": "unidade",
                "estoque": 50,
                "categoria": "Verduras",
                "produtor": produtor1,
                "origem": "João Pessoa - PB"
            },
            {
                "nome": "Tomate Cereja Orgânico",
                "descricao": "Tomate cereja doce e suculento",
                "preco": 12.00,
                "unidade": "kg",
                "estoque": 30,
                "categoria": "Legumes",
                "produtor": produtor1,
                "origem": "João Pessoa - PB"
            },
            {
                "nome": "Cenoura Orgânica",
                "descricao": "Cenoura fresca e crocante",
                "preco": 6.50,
                "unidade": "kg",
                "estoque": 40,
                "categoria": "Legumes",
                "produtor": produtor1,
                "origem": "João Pessoa - PB"
            },
            {
                "nome": "Rúcula Orgânica",
                "descricao": "Rúcula fresca com sabor marcante",
                "preco": 4.00,
                "unidade": "maço",
                "estoque": 35,
                "categoria": "Verduras",
                "produtor": produtor1,
                "origem": "João Pessoa - PB"
            },
            {
                "nome": "Couve Manteiga",
                "descricao": "Couve manteiga fresca e nutritiva",
                "preco": 3.00,
                "unidade": "maço",
                "estoque": 45,
                "categoria": "Verduras",
                "produtor": produtor1,
                "origem": "João Pessoa - PB"
            },
            # Produtor 2 - Frutas
            {
                "nome": "Banana Prata",
                "descricao": "Banana prata madura e doce",
                "preco": 5.50,
                "unidade": "kg",
                "estoque": 60,
                "categoria": "Frutas",
                "produtor": produtor2,
                "origem": "Conde - PB"
            },
            {
                "nome": "Manga Tommy",
                "descricao": "Manga tommy suculenta e aromática",
                "preco": 8.00,
                "unidade": "kg",
                "estoque": 25,
                "categoria": "Frutas",
                "produtor": produtor2,
                "origem": "Conde - PB"
            },
            {
                "nome": "Maracujá",
                "descricao": "Maracujá azedo para suco",
                "preco": 10.00,
                "unidade": "kg",
                "estoque": 20,
                "categoria": "Frutas",
                "produtor": produtor2,
                "origem": "Conde - PB"
            },
            {
                "nome": "Laranja Pera",
                "descricao": "Laranja pera para suco",
                "preco": 4.50,
                "unidade": "kg",
                "estoque": 50,
                "categoria": "Frutas",
                "produtor": produtor2,
                "origem": "Conde - PB"
            },
            {
                "nome": "Abacaxi Pérola",
                "descricao": "Abacaxi pérola doce e perfumado",
                "preco": 6.00,
                "unidade": "unidade",
                "estoque": 30,
                "categoria": "Frutas",
                "produtor": produtor2,
                "origem": "Conde - PB"
            },
        ]
        
        for prod_data in produtos:
            categoria = Categoria.query.filter_by(nome=prod_data['categoria']).first()
            if not categoria:
                continue
            
            produto = Produto.query.filter_by(
                nome=prod_data['nome'],
                produtor_id=prod_data['produtor'].id
            ).first()
            
            if not produto:
                produto = Produto(
                    nome=prod_data['nome'],
                    descricao=prod_data['descricao'],
                    preco=prod_data['preco'],
                    unidade=prod_data['unidade'],
                    estoque=prod_data['estoque'],
                    origem=prod_data['origem'],
                    produtor_id=prod_data['produtor'].id,
                    categoria_id=categoria.id
                )
                db.session.add(produto)
        
        db.session.commit()
        print(f"✅ {len(produtos)} produtos inseridos!")

def seed_logistica():
    """Cria pontos de retirada e taxas de entrega"""
    print("🚚 Configurando logística...")
    with app.app_context():
        # Pontos de Retirada
        pontos = [
            {
                "nome": "Sede CoopVale - Centro",
                "endereco": "Av. João Pessoa, 450 - Centro",
                "cidade": "João Pessoa",
                "cep": "58013-420",
                "dias_funcionamento": "Segunda a Sexta",
                "horario_abertura": "08:00",
                "horario_fechamento": "18:00",
                "ativo": True
            },
            {
                "nome": "Feira Orgânica do Parque",
                "endereco": "Parque Sólon de Lucena - Centro",
                "cidade": "João Pessoa",
                "cep": "58013-120",
                "dias_funcionamento": "Sábado",
                "horario_abertura": "06:00",
                "horario_fechamento": "13:00",
                "ativo": True
            },
        ]
        
        for p in pontos:
            ponto = PontoRetirada.query.filter_by(nome=p['nome']).first()
            if not ponto:
                ponto = PontoRetirada(**p)
                db.session.add(ponto)
        
        # Taxas de Entrega
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
            taxa = TaxaEntrega.query.filter_by(regiao=t['regiao']).first()
            if not taxa:
                taxa = TaxaEntrega(**t)
                db.session.add(taxa)
        
        db.session.commit()
        print(f"✅ {len(pontos)} pontos de retirada e {len(taxas)} taxas de entrega inseridos!")

def inicializar_completo():
    """Executa todos os seeds em ordem"""
    print("\n" + "="*60)
    print("🌱 INICIALIZAÇÃO COMPLETA DO BANCO DE DADOS")
    print("="*60 + "\n")
    
    limpar_banco()
    criar_tabelas()
    seed_categorias()
    seed_usuarios()
    seed_produtos()
    seed_logistica()
    
    print("\n" + "="*60)
    print("✅ BANCO DE DADOS INICIALIZADO COM SUCESSO!")
    print("="*60)
    print("\n📋 Credenciais de Acesso:")
    print("   Admin:    admin@coopvale.com / admin123")
    print("   Cliente:  cliente@teste.com / cliente123")
    print("   Produtor: produtor1@coopvale.com / produtor123")
    print("             produtor2@coopvale.com / produtor123")
    print("="*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "limpar":
            limpar_banco()
        elif comando == "criar":
            criar_tabelas()
        elif comando == "categorias":
            seed_categorias()
        elif comando == "usuarios":
            seed_usuarios()
        elif comando == "produtos":
            seed_produtos()
        elif comando == "logistica":
            seed_logistica()
        elif comando == "completo":
            inicializar_completo()
        else:
            print("Comando desconhecido!")
            print("Uso: python init_db_completo.py [limpar|criar|categorias|usuarios|produtos|logistica|completo]")
    else:
        # Por padrão, executa inicialização completa
        inicializar_completo()
