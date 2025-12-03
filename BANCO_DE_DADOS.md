# 🗄️ Inicialização do Banco de Dados - AgroFeira CoopVale

## 📍 Localização do Banco de Dados

O banco de dados SQLite está localizado em:
```
C:\Users\Victor\Documents\projetos_flask\appBP\appBP\instance\coopvale.db
```

## ⚠️ IMPORTANTE: Persistência de Dados

O banco de dados é um arquivo físico que **PERMANECE** no disco mesmo após:
- ✅ Desligar o computador
- ✅ Fechar o VS Code
- ✅ Parar a aplicação Flask
- ✅ Reiniciar o sistema

**Se os dados não estão persistindo**, verifique:
1. Se o banco não está sendo deletado por algum script
2. Se você não está usando bancos diferentes (desenvolvimento vs teste)
3. Se a pasta `instance/` não está sendo limpa

## 🚀 Script de Inicialização

Use o script `init_db_completo.py` para gerenciar o banco:

### Inicialização Completa (Recomendado)
```bash
python init_db_completo.py completo
```
ou simplesmente:
```bash
python init_db_completo.py
```

**O que faz:**
- 🗑️ Limpa banco de dados existente
- 🔨 Cria todas as tabelas
- 📦 Insere 10 categorias
- 👥 Cria usuários de teste (admin, cliente, 2 produtores)
- 🥬 Insere 10 produtos
- 🚚 Configura logística (2 pontos de retirada + 27 taxas de entrega)

### Comandos Individuais

#### Limpar banco (cuidado!)
```bash
python init_db_completo.py limpar
```

#### Criar apenas tabelas
```bash
python init_db_completo.py criar
```

#### Inserir apenas categorias
```bash
python init_db_completo.py categorias
```

#### Inserir apenas usuários
```bash
python init_db_completo.py usuarios
```

#### Inserir apenas produtos
```bash
python init_db_completo.py produtos
```

#### Inserir apenas logística
```bash
python init_db_completo.py logistica
```

## 📋 Credenciais de Acesso

Após executar a inicialização completa, use estas credenciais:

| Tipo | Email | Senha |
|------|-------|-------|
| **Admin** | admin@coopvale.com | admin123 |
| **Cliente** | cliente@teste.com | cliente123 |
| **Produtor 1** | produtor1@coopvale.com | produtor123 |
| **Produtor 2** | produtor2@coopvale.com | produtor123 |

## 📦 Dados Criados

### Categorias (10)
- Verduras (valor mínimo: R$ 10,00, quantidade: 2)
- Frutas (valor mínimo: R$ 15,00, quantidade: 2)
- Legumes, Laticínios, Carnes, Grãos, Bebidas, Doces, Pães e Massas, Outros

### Produtos (10)
**Produtor 1 - Fazenda Orgânica São João:**
- Alface Crespa Orgânica (R$ 3,50/un)
- Tomate Cereja Orgânico (R$ 12,00/kg)
- Cenoura Orgânica (R$ 6,50/kg)
- Rúcula Orgânica (R$ 4,00/maço)
- Couve Manteiga (R$ 3,00/maço)

**Produtor 2 - Sítio Frutas do Vale:**
- Banana Prata (R$ 5,50/kg)
- Manga Tommy (R$ 8,00/kg)
- Maracujá (R$ 10,00/kg)
- Laranja Pera (R$ 4,50/kg)
- Abacaxi Pérola (R$ 6,00/un)

### Logística

**Pontos de Retirada (2):**
1. **Sede CoopVale - Centro**
   - Endereço: Av. João Pessoa, 450 - Centro
   - Horário: Segunda a Sexta, 08:00-18:00

2. **Feira Orgânica do Parque**
   - Endereço: Parque Sólon de Lucena - Centro
   - Horário: Sábado, 06:00-13:00

**Taxas de Entrega (27 regiões):**
- Centro: R$ 8,00 (1 dia)
- Tambaú/Manaíra: R$ 12,00 (1 dia)
- Mangabeira: R$ 20,00 (2 dias)
- Cabedelo: R$ 30,00 (3 dias)
- Conde: R$ 35,00 (4 dias)
- Lucena: R$ 40,00 (4 dias)
- ... e mais 21 regiões

## 🔄 Migrações do Banco

Se precisar aplicar migrações (após mudanças no modelo):

```bash
# Criar migração
flask db migrate -m "Descrição da mudança"

# Aplicar migração
flask db upgrade

# Reverter última migração
flask db downgrade
```

## 🧪 Verificar Banco

### Ver estrutura de tabelas
```bash
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); print(db.metadata.tables.keys())"
```

### Contar registros
```bash
python -c "from app import create_app; from app.models.core import Usuario, Produto, Categoria; from app.extensions import db; app = create_app(); app.app_context().push(); print(f'Usuários: {Usuario.query.count()}'); print(f'Produtos: {Produto.query.count()}'); print(f'Categorias: {Categoria.query.count()}')"
```

### Ver caminho e tamanho do banco
```bash
python -c "from config import Config; import os; print('Caminho:', Config.DB_PATH); print('Existe:', os.path.exists(Config.DB_PATH)); print('Tamanho:', os.path.getsize(Config.DB_PATH) if os.path.exists(Config.DB_PATH) else 0, 'bytes')"
```

## 📁 Estrutura do Banco

```
instance/
└── coopvale.db        # Arquivo SQLite (persiste no disco)
```

## 🔒 Backup do Banco

### Criar backup
```bash
# Windows
copy instance\coopvale.db instance\coopvale_backup.db

# Linux/Mac
cp instance/coopvale.db instance/coopvale_backup.db
```

### Restaurar backup
```bash
# Windows
copy instance\coopvale_backup.db instance\coopvale.db

# Linux/Mac
cp instance/coopvale_backup.db instance/coopvale.db
```

## 🐛 Troubleshooting

### Problema: Dados não persistem

**Causa possível:** Banco de teste sendo usado
```bash
# Verifique qual banco está sendo usado
python -c "from config import Config; print(Config.SQLALCHEMY_DATABASE_URI)"
```

**Solução:** Certifique-se de que não há variável `DATABASE_URL` no `.env` apontando para outro local.

### Problema: Erro "no such table"

**Causa:** Tabelas não criadas
**Solução:**
```bash
python init_db_completo.py completo
```

### Problema: Banco vazio após reiniciar

**Causas possíveis:**
1. Script de limpeza sendo executado
2. Pasta instance/ sendo deletada
3. `.gitignore` deletando o banco (verifique!)

**Solução:**
1. Verifique se `instance/coopvale.db` existe
2. Execute `python init_db_completo.py completo`
3. NÃO execute comandos de limpeza automaticamente

## 📝 .gitignore

O banco **NÃO está** no `.gitignore` por padrão, para facilitar desenvolvimento.

Se quiser ignorar o banco no Git, adicione ao `.gitignore`:
```
instance/*.db
```

## ✅ Checklist de Inicialização

Use este checklist após clonar o projeto ou resetar o ambiente:

- [ ] 1. Ativar ambiente virtual: `source venv/bin/activate` ou `venv\Scripts\activate`
- [ ] 2. Instalar dependências: `pip install -r requirements.txt`
- [ ] 3. Inicializar banco: `python init_db_completo.py completo`
- [ ] 4. Verificar dados: Acessar http://localhost:8000 e fazer login
- [ ] 5. Testar aplicação: `python -m pytest tests/ -v`

## 🎯 Próximos Passos

Após inicializar o banco, você pode:

1. **Rodar a aplicação:**
   ```bash
   python run.py
   ```
   Acesse: http://localhost:8000

2. **Fazer login:**
   - Use as credenciais acima
   - Explore o sistema

3. **Executar testes:**
   ```bash
   python -m pytest tests/ -v
   ```

4. **Testar pagamentos:**
   ```bash
   # Ver documentação em SISTEMA_PAGAMENTO.md
   ```

---

**Desenvolvido para AgroFeira - CoopVale** 🌱
