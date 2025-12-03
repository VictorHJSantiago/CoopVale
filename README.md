# CoopVale - Cooperativa de Produtores Rurais do Vale Verde

## Descrição
Sistema web completo para gestão de cooperativa rural, com módulos de autenticação, catálogo, pedidos, dashboards, relatórios e páginas institucionais. Desenvolvido em Flask (Python) com SQLAlchemy, Blueprints e Bootstrap.

<div align="center">

<img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
<img src="https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" />

<h1>🌱 CoopVale</h1>
<p><em>Plataforma de e-commerce cooperativo com checkout PIX, cartões, webhooks, seeds e ferramentas de administração.</em></p>

<p>
	<a href="#visao-geral">Visão Geral</a> •
	<a href="#recursos">Recursos</a> •
	<a href="#estrutura-do-projeto">Estrutura</a> •
	<a href="#instalacao-rapida">Instalação Rápida</a> •
	<a href="#configuracao">Configuração</a> •
	<a href="#pagamentos">Pagamentos</a> •
	<a href="#webhooks">Webhooks</a> •
	<a href="#banco-de-dados">Banco de Dados</a> •
	<a href="#cli">CLI</a> •
	<a href="#seeds">Seeds</a> •
	<a href="#testes">Testes</a> •
	<a href="#roadmap">Roadmap</a> •
	<a href="#contribuicao">Contribuição</a>
</p>

## Visão Geral

CoopVale é uma aplicação Flask para gestão de pedidos, produtos e pagamentos em uma cooperativa, com suporte a:
- Cadastro e edição de perfil com CPF e foto de perfil.
- Catálogo de produtos e produtores, com fotos no listing.
- Carrinho, cancelamento e exclusão de pedidos conforme status.
- Checkout com métodos PIX e cartões (débito/crédito), geração de QR Code e código “copia e cola”.
- Integração com Mercado Pago (estrutura pronta), webhooks, criptografia e e-mails transacionais.
- Seeds para categorias, logística (pontos e 27 taxas de entrega), e dados de exemplo.
- Scripts CLI para expiração de PIX, verificação de pagamentos e geração de chave de criptografia.

## Recursos

- Checkout moderno: Seleção de método, máscaras de cartão e alternância dinâmica de campos.
- PIX: QR Code e código EMV para copia/cola (modo simulado). Automatiza confirmação via webhook.
- Cartões: Tokenização planejada (via SDK MP) e armazenamento seguro (Fernet, últimas 4, bandeira).
- Webhooks: Endpoints dedicados para atualizações de pagamento.
- E-mails: Serviço assíncrono para notificações.
- Banco persistente: SQLite em `instance/coopvale.db` com migrações Alembic.
- Seeds: Categorias com mínimos, logística (pontos + 27 taxas), produtos e usuários de exemplo.
- CLI: Expira PIX vencidos, verifica pagamentos, gera chaves.

## Estrutura do Projeto

```
config.py
DOCUMENTACAO_BLUEPRINTS.md
README.md
requirements.txt
routes.py
run.py
app/
	__init__.py
	extensions.py
	forms.py
	models.py
	blueprints/
		produtos/
			__init__.py
			routes.py
	static/
	templates/
		base.html
	viewBP/
		sub_site_01/
			__init__.py
			routes.py
			static/
			templates/
		sub_site_02/
			...
		sub_site_03/
			...
```

## Instalação Rápida

Pré-requisitos:
- Python 3.10+ instalado.
- Bash disponível (Windows: `bash.exe`).

Comandos:

```bash
# 1) Clonar e entrar na pasta do app
git clone https://github.com/VictorHJSantiago/CoopVale.git
cd CoopVale/appBP/appBP

# 2) (Opcional) Criar venv
python -m venv .venv
source .venv/Scripts/activate

# 3) Instalar dependências
pip install -r requirements.txt

# 4) Inicializar banco e seeds (modo completo)
python init_db_completo.py completo

# 5) Executar
python run.py
```

Aplicação acessível em `http://localhost:5000` (a menos que configurado diferente).

## Screenshots

Adicione imagens em `docs/screenshots/` e GIFs em `docs/demos/`.

Exemplos (substitua pelos seus arquivos reais):

<div align="center">

<img src="docs/screenshots/home.png" alt="Home" width="85%" />
<br/>
<img src="docs/screenshots/checkout_pix.png" alt="Checkout PIX" width="85%" />
<br/>
<img src="docs/screenshots/produtores.png" alt="Lista de Produtores" width="85%" />

</div>

### Demo (GIF)

<div align="center">

<img src="docs/demos/checkout_flow.gif" alt="Fluxo de Checkout" width="85%" />

</div>

Como gerar um GIF rapidamente no Windows:

```bash
# Use ShareX ou ScreenToGif
# Exporte para docs/demos/checkout_flow.gif
```

## Configuração

Arquivo principal: `config.py`
- `SQLALCHEMY_DATABASE_URI`: caminho para `instance/coopvale.db`.
- `MAIL_*`: configuração de e-mail para envio transacional.
- `MERCADO_PAGO_*`: credenciais e URLs para gateway.
- `ENCRYPTION_KEY`: chave Fernet para criptografia.
- `WEBHOOK_URL`: URL pública para recebimento de eventos.

Sugestão: use um `.env` (há um `.env.example` se presente) para credenciais.

## Pagamentos

- PIX:
	- Página `pagamento_pix.html` exibe QR Code e código “copia e cola”.
	- Modo atual simulado; na produção, configure credenciais do Mercado Pago e CRC16/EMV adequados.

- Cartões:
	- UI de cartão em `finalizar.html` (
		máscaras, bandeira e últimas 4 capturadas quando aplicável).
	- Planejado: tokenização via SDK JS do Mercado Pago (front-end) e processamento com token.

Serviços:
- `app/services/pagamento_service.py`: integração com gateway, geração de PIX e consulta.
- `app/services/criptografia_service.py`: Fernet, Luhn, detecção de bandeira, tokenização.
- `app/services/email_service.py`: envio de e-mails.

## Webhooks

- Blueprint: `app/blueprints/webhooks/routes.py`.
- Objetivo: receber eventos do gateway, validar assinatura, atualizar pedidos e notificar.
- Produção: configure `WEBHOOK_URL` público e credenciais reais.

## Banco de Dados

- SQLite em `instance/coopvale.db`. Persiste após reiniciar app/PC.
- Migrações via Alembic/Flask-Migrate.

Verificar conteúdo:

```bash
python verificar_banco.py
```

Reinicialização completa com seeds:

```bash
python init_db_completo.py completo
```

Observação: isso apaga e recria tabelas (use com cuidado).

## CLI

Comandos administrativos (registrados em `app/cli_commands.py`):
- `expirar-pedidos-pix`: marca como vencidos pedidos PIX expirados.
- `verificar-pagamentos`: consulta gateway e atualiza status.
- `gerar-chave-criptografia`: cria/joga chave Fernet em arquivo seguro.

Execução típica:

```bash
python -m flask expirar-pedidos-pix
python -m flask verificar-pagamentos
python -m flask gerar-chave-criptografia
```

## Seeds

- `run.py`: seeds básicos (categorias com mínimos, incluindo Verduras `quantidade_minima=2`).
- `init_db_completo.py`: cria BD e insere categorias, usuários, produtores, produtos, pontos e 27 taxas de entrega.

## Testes

Suite de testes baseada em `pytest`.

```bash
pytest -q
```

Status atual: 27 testes passando (com um aviso de depreciação do `Query.get`).

## CI & Badges

Badges de status (exemplos com Shields.io):

<div align="center">

<img src="https://img.shields.io/github/actions/workflow/status/VictorHJSantiago/CoopVale/.github/workflows/tests.yml?label=CI%20Tests&logo=github" alt="CI Tests" />
<img src="https://img.shields.io/github/actions/workflow/status/VictorHJSantiago/CoopVale/.github/workflows/lint.yml?label=Lint%20%26%20Style&logo=github" alt="Lint & Style" />
<img src="https://codecov.io/gh/VictorHJSantiago/CoopVale/branch/main/graph/badge.svg" alt="Coverage" />

</div>

Workflows:
- `tests.yml`: roda `pytest`.
- `lint.yml`: verifica formatação com Black e lint com Flake8.
- `coverage.yml`: gera `coverage.xml` e publica como artifact.

Cobertura:
- Badge acima usa Codecov. Para repositório privado, cadastre o projeto no Codecov e defina `CODECOV_TOKEN` nos segredos do repositório.
- Workflow `coverage.yml` já envia `coverage.xml` para o Codecov.

## Roadmap

- Integração completa com Mercado Pago em produção.
- Tokenização de cartões via SDK JS (front-end).
- PIX com geração EMV e CRC-16 oficiais.
- Mais casos de teste e hardening de segurança.

## Contribuição

Contribuições são bem-vindas! Por favor:
- Abra uma issue descrevendo a proposta.
- Mantenha o estilo e padrões existentes.
- Inclua testes sempre que possível.

## Licença

Este projeto é proprietário do autor do repositório. Não inclua headers de licença automaticamente.

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
