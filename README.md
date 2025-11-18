# CoopVale - Cooperativa de Produtores Rurais do Vale Verde

## Descrição
Sistema web completo para gestão de cooperativa rural, com módulos de autenticação, catálogo, pedidos, dashboards, relatórios e páginas institucionais. Desenvolvido em Flask (Python) com SQLAlchemy, Blueprints e Bootstrap.

## Estrutura do Projeto
```
appBP/
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   ├── controllers/
│   ├── templates/
│   ├── static/
│   └── blueprints/
│       ├── auth/
│       ├── produtos/
│       ├── pedidos/
│       ├── produtores/
│       ├── admin/
│       └── main/
├── config.py
├── requirements.txt
├── run.py
├── README.md
```

## Como rodar localmente
1. Clone o repositório
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   pip install -r requirements.txt
   ```
3. Configure variáveis de ambiente se necessário (ex: SECRET_KEY)
4. Execute a aplicação:
   ```bash
   flask run
   ```

## Perfis de Usuário
- **Administrador:** Gestão total do sistema
- **Produtor:** Gerencia seus produtos e pedidos
- **Cliente:** Realiza pedidos e acompanha histórico
- **Visitante:** Visualiza catálogo

## Funcionalidades Principais
- Cadastro/login/logout de usuários
- CRUD de categorias, produtos, produtores, pontos de retirada
- Catálogo público com filtros
- Carrinho de compras e pedidos
- Dashboards para admin, produtor e cliente
- Relatórios e gestão de usuários
- Páginas institucionais (sobre, blog, contato)

## Principais Rotas
- `/auth/login`, `/auth/register`, `/auth/logout`
- `/produtos/`, `/produtos/categorias`, `/produtos/produtos`
- `/pedidos/carrinho`, `/pedidos/finalizar`, `/pedidos/historico`
- `/produtores/`, `/produtores/dashboard`
- `/admin/dashboard`, `/admin/usuarios`, `/admin/relatorios`, `/admin/pontos_retirada`
- `/` (home), `/sobre`, `/produtores`, `/blog`, `/contato`

## Testes Manuais Sugeridos
- [ ] Cadastro de usuário (cliente, produtor)
- [ ] Login/logout
- [ ] CRUD de categorias, produtos, produtores, pontos de retirada
- [ ] Adicionar/remover produtos ao carrinho
- [ ] Finalizar pedido
- [ ] Visualizar histórico de pedidos
- [ ] Acesso a dashboards conforme perfil
- [ ] Ativação/desativação de usuários (admin)
- [ ] Relatórios administrativos
- [ ] Navegação institucional

## Script de Teste Automatizado (pytest)
Crie um arquivo `test_app.py` na raiz do projeto:
```python
import pytest
from app import create_app, db

@pytest.fixture
def app():
	app = create_app()
	app.config['TESTING'] = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
	with app.app_context():
		db.create_all()
	yield app

@pytest.fixture
def client(app):
	return app.test_client()

def test_homepage(client):
	resp = client.get('/')
	assert resp.status_code == 200
	assert b'CoopVale' in resp.data

def test_login_page(client):
	resp = client.get('/auth/login')
	assert resp.status_code == 200
	assert b'Login' in resp.data
# Adicione mais testes para cada rota e fluxo importante
```

## Créditos
Desenvolvido por CoopVale e colaboradores.
"# CoopVale" 
