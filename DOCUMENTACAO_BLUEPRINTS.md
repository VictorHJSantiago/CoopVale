# 📘 Documentação: Estrutura de Projeto Flask com Blueprints

## 📋 Índice
1. [O que são Blueprints?](#o-que-são-blueprints)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Arquitetura e Fluxo de Execução](#arquitetura-e-fluxo-de-execução)
4. [Implementação Passo a Passo](#implementação-passo-a-passo)
5. [Como Funciona o Sistema de Rotas](#como-funciona-o-sistema-de-rotas)
6. [Testando a Aplicação](#testando-a-aplicação)

---

## 🎯 O que são Blueprints?

**Blueprints** são uma funcionalidade do Flask que permite **modularizar** uma aplicação web, dividindo-a em componentes independentes e reutilizáveis.

### Por que usar Blueprints?

✅ **Organização**: Separa diferentes seções do site (blog, admin, api, etc.)  
✅ **Manutenibilidade**: Facilita encontrar e editar código específico  
✅ **Reutilização**: Um blueprint pode ser usado em múltiplos projetos  
✅ **Trabalho em equipe**: Cada desenvolvedor pode trabalhar em um blueprint diferente  
✅ **Escalabilidade**: Adicionar novas funcionalidades sem bagunçar o código existente

### Analogia

Imagine que você está construindo uma **casa**:
- A casa inteira = Aplicação Flask completa
- Cada cômodo (sala, cozinha, quarto) = Um Blueprint diferente
- Cada cômodo tem sua decoração e móveis próprios = Templates e arquivos estáticos específicos

---

## 📁 Estrutura do Projeto

```
appBP/
│
├── run.py                          # Arquivo principal - inicia a aplicação
│
├── app/                            # Pacote principal da aplicação
│   ├── __init__.py                 # Factory function (create_app)
│   ├── routes.py                   # Rotas globais/comuns (opcional)
│   │
│   ├── templates/                  # Templates globais
│   │   └── home.html              # Página inicial geral
│   │
│   ├── static/                     # Arquivos estáticos globais
│   │
│   └── viewBP/                     # Diretório dos Blueprints
│       │
│       ├── sub_site_01/            # Blueprint 1
│       │   ├── __init__.py         # Criação do blueprint
│       │   ├── routes.py           # Rotas específicas
│       │   ├── templates/          # HTMLs específicos
│       │   └── static/             # CSS/JS/imagens específicos
│       │
│       ├── sub_site_02/            # Blueprint 2
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   ├── templates/
│       │   └── static/
│       │
│       └── sub_site_03/            # Blueprint 3
│           ├── __init__.py
│           ├── routes.py
│           ├── templates/
│           └── static/
│
└── venv/                           # Ambiente virtual Python
```

---

## 🏗️ Arquitetura e Fluxo de Execução

### Fluxo de Inicialização

```
1. run.py é executado
   ↓
2. Chama create_app() de app/__init__.py
   ↓
3. create_app() cria a instância Flask
   ↓
4. Importa os blueprints de cada sub_site
   ↓
5. Registra cada blueprint na aplicação
   ↓
6. Retorna a aplicação configurada
   ↓
7. run.py define rotas globais (opcional)
   ↓
8. Inicia o servidor Flask
```

### Diagrama Visual

```
┌─────────────────────────────────────────────────┐
│                   run.py                        │
│  - Cria app via create_app()                    │
│  - Define rotas globais                         │
│  - Inicia servidor (app.run())                  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│            app/__init__.py                      │
│  - create_app() - Factory Pattern               │
│  - Importa blueprints                           │
│  - Registra blueprints                          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           Blueprints Registrados                │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ sub_site_01  │  │ sub_site_02  │  ...      │
│  │ /site_01/*   │  │ /site_02/*   │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ Implementação Passo a Passo

### **PASSO 1: Arquivo Principal (run.py)**

Este é o **ponto de entrada** da aplicação.

```python
# Arquivo principal para rodar a aplicação Flask
from app import create_app
from flask import render_template

# Criação da aplicação Flask usando o padrão Factory
app = create_app()

# área de rotas comuns (rotas globais da aplicação)
@app.route("/")
def home():
    return render_template("home.html", titulo="Site de Exemplo")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
```

**O que acontece aqui:**
- Importa a função `create_app()` do pacote `app`
- Chama `create_app()` para criar e configurar a aplicação
- Define rotas globais que não pertencem a nenhum blueprint específico
- Inicia o servidor na porta 8000 com modo debug ativado

---

### **PASSO 2: Factory Function (app/__init__.py)**

O **padrão Factory** é usado para criar a aplicação de forma organizada.

```python
from flask import Flask

def create_app():
    # Método de fábrica para criar a aplicação Flask

    # Criação da aplicação
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        SECRET_KEY="algumasecretkey",  # para uso futuro em sessions e cookies
    )

    # Registro de blueprints
    from app.viewBP.sub_site_01 import pagina01BP
    from app.viewBP.sub_site_02 import pagina02BP
    from app.viewBP.sub_site_03 import pagina03BP

    app.register_blueprint(pagina01BP)
    app.register_blueprint(pagina02BP)
    app.register_blueprint(pagina03BP)

    return app
```

**O que acontece aqui:**
1. Cria a instância do Flask
2. Configura a aplicação (SECRET_KEY, etc.)
3. **Importa** os blueprints (objetos Blueprint de cada módulo)
4. **Registra** cada blueprint na aplicação usando `app.register_blueprint()`
5. Retorna a aplicação configurada

**⚠️ IMPORTANTE:** Os imports dos blueprints ficam **dentro** da função `create_app()` para evitar problemas de importação circular.

---

### **PASSO 3: Criando um Blueprint (app/viewBP/sub_site_01/__init__.py)**

Cada blueprint é **criado** no arquivo `__init__.py` da sua pasta.

```python
from flask import Blueprint

# Criação do objeto Blueprint
pagina01BP = Blueprint(
    "site_01",                      # Nome interno do blueprint
    __name__,                       # Módulo atual
    template_folder="templates",    # Onde estão os HTMLs deste blueprint
    static_folder="static",         # Onde estão css/js/imagens específicos
    url_prefix="/site_01",          # Prefixo de todas as rotas
)

# Importa as rotas após criar o blueprint
from . import routes
```

**Parâmetros do Blueprint:**

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `name` | Identificador único do blueprint | `"site_01"` |
| `__name__` | Nome do módulo Python (automático) | - |
| `template_folder` | Pasta dos templates HTML | `"templates"` |
| `static_folder` | Pasta dos arquivos estáticos | `"static"` |
| `url_prefix` | Prefixo adicionado a todas as rotas | `"/site_01"` |

**⚠️ ORDEM IMPORTANTE:** O blueprint deve ser criado **ANTES** de importar as rotas!

---

### **PASSO 4: Definindo Rotas do Blueprint (app/viewBP/sub_site_01/routes.py)**

Após criar o blueprint, definimos suas rotas.

```python
from . import pagina01BP

@pagina01BP.route("/")
def index():
    return "Exemplo de site com BP - 01 - Home"

@pagina01BP.route("/cadastro")
def cadastro():
    return "Exemplo de site com BP - 01 - Cadastro"

@pagina01BP.route("/login")
def login():
    return "Exemplo de site com BP - 01 - Login"
```

**O que acontece aqui:**
- Importa o objeto `pagina01BP` criado no `__init__.py`
- Define rotas usando o decorador `@pagina01BP.route()`
- Cada função retorna uma resposta (texto, HTML, template, etc.)

---

## 🛣️ Como Funciona o Sistema de Rotas

### URL Prefix: O Segredo da Organização

O `url_prefix` definido na criação do blueprint é **automaticamente adicionado** a todas as rotas.

#### Exemplo com sub_site_01:

```python
# No __init__.py
pagina01BP = Blueprint("site_01", __name__, url_prefix="/site_01")

# No routes.py
@pagina01BP.route("/")          # URL final: /site_01/
@pagina01BP.route("/cadastro")  # URL final: /site_01/cadastro
@pagina01BP.route("/login")     # URL final: /site_01/login
```

### Mapa Completo de URLs do Projeto

| Blueprint | Rota Definida | URL Final Completa | Função |
|-----------|---------------|-------------------|--------|
| **Global** | `/` | `http://localhost:8000/` | `home()` |
| **sub_site_01** | `/` | `http://localhost:8000/site_01/` | `index()` |
| **sub_site_01** | `/cadastro` | `http://localhost:8000/site_01/cadastro` | `cadastro()` |
| **sub_site_01** | `/login` | `http://localhost:8000/site_01/login` | `login()` |
| **sub_site_02** | `/` | `http://localhost:8000/site_02/` | `index()` |
| **sub_site_03** | `/` | `http://localhost:8000/site_03/` | `index()` |
| **sub_site_03** | `/cadastro` | `http://localhost:8000/site_03/cadastro` | `cadastro()` |

### Por que isso é útil?

✅ **Organização clara**: Cada seção tem seu próprio "namespace" de URLs  
✅ **Evita conflitos**: Dois blueprints podem ter rotas com o mesmo nome  
✅ **Fácil refatoração**: Mudar o `url_prefix` altera todas as URLs de uma vez

---

## 🔄 Fluxo de uma Requisição HTTP

Vamos entender o que acontece quando um usuário acessa `http://localhost:8000/site_01/login`:

```
1. Navegador faz requisição GET para /site_01/login
   ↓
2. Flask recebe a requisição
   ↓
3. Flask verifica os blueprints registrados
   ↓
4. Encontra que /site_01/* pertence ao pagina01BP
   ↓
5. Remove o prefixo /site_01 → sobra /login
   ↓
6. Procura a rota /login no pagina01BP
   ↓
7. Encontra a função login()
   ↓
8. Executa a função login()
   ↓
9. Retorna a resposta ao navegador
```

---

## 🧪 Testando a Aplicação

### 1. Ativar o Ambiente Virtual

```bash
# Windows (Git Bash)
source venv/Scripts/activate

# Windows (CMD)
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install flask
```

### 3. Executar a Aplicação

```bash
python run.py
```

### 4. Acessar no Navegador

Abra o navegador e teste todas as rotas:

**Rotas Globais:**
- http://localhost:8000/

**Rotas do sub_site_01:**
- http://localhost:8000/site_01/
- http://localhost:8000/site_01/cadastro
- http://localhost:8000/site_01/login

**Rotas do sub_site_02:**
- http://localhost:8000/site_02/

**Rotas do sub_site_03:**
- http://localhost:8000/site_03/
- http://localhost:8000/site_03/cadastro

---

## ✨ Boas Práticas e Dicas

### 1. Nomenclatura Consistente

```python
# ✅ BOM: Nomes claros e relacionados
pasta: sub_site_01
variável: pagina01BP
nome blueprint: "site_01"
url_prefix: "/site_01"

# ❌ RUIM: Nomes inconsistentes
pasta: site1
variável: meuBP
nome blueprint: "pagina"
url_prefix: "/teste"
```

### 2. Organização de Arquivos

Cada blueprint deve ter sua **própria pasta** com estrutura completa:

```
sub_site_01/
├── __init__.py      # Cria o blueprint
├── routes.py        # Define as rotas
├── templates/       # HTML específicos
│   ├── index.html
│   └── login.html
└── static/          # CSS/JS/imagens específicos
    ├── css/
    ├── js/
    └── img/
```

### 3. Quando Criar um Novo Blueprint?

Crie um blueprint separado quando:
- ✅ A seção tem funcionalidade **distinta** (ex: blog, admin, api)
- ✅ Vai ter seus **próprios templates e estilos**
- ✅ Pode ser **reutilizado** em outros projetos
- ✅ Tem um **contexto específico** (ex: dashboard de usuário)

**NÃO** crie um blueprint para:
- ❌ Cada página individual
- ❌ Rotas muito simples
- ❌ Quando não há benefício de modularização

### 4. Import Circular - Como Evitar

**Problema:** Blueprints e app se importando mutuamente.

**Solução:** Sempre importe blueprints **dentro** da função `create_app()`:

```python
# ✅ CORRETO
def create_app():
    app = Flask(__name__)
    from app.viewBP.sub_site_01 import pagina01BP  # Import local
    app.register_blueprint(pagina01BP)
    return app

# ❌ ERRADO
from app.viewBP.sub_site_01 import pagina01BP  # Import global

def create_app():
    app = Flask(__name__)
    app.register_blueprint(pagina01BP)
    return app
```

---

## 🎓 Exercícios Práticos para os Alunos

### Exercício 1: Criar um Novo Blueprint

Crie um blueprint chamado `sub_site_04` com:
- URL prefix: `/produtos`
- Rotas:
  - `/` - lista de produtos
  - `/adicionar` - formulário de adicionar produto
  - `/detalhes/<int:id>` - detalhes de um produto

### Exercício 2: Adicionar Templates

Modifique o `sub_site_01` para usar templates HTML em vez de retornar strings.

### Exercício 3: Compartilhar Arquivos Estáticos

Crie um arquivo CSS global em `app/static/` e use-o em um template de um blueprint.

### Exercício 4: API Blueprint

Crie um blueprint `api` que retorne JSON em vez de HTML:
- `/api/usuarios` - lista de usuários em JSON
- `/api/produtos` - lista de produtos em JSON

---

## 📚 Resumo dos Conceitos-Chave

| Conceito | Descrição | Onde Fica |
|----------|-----------|-----------|
| **Blueprint** | Módulo independente da aplicação | `app/viewBP/sub_site_XX/` |
| **Factory Pattern** | Função que cria e configura a app | `app/__init__.py → create_app()` |
| **URL Prefix** | Prefixo automático das rotas | Parâmetro do Blueprint |
| **Registro** | Conectar blueprint à aplicação | `app.register_blueprint()` |
| **Rotas Globais** | Rotas fora de qualquer blueprint | `run.py` ou `app/routes.py` |

---

## 🔗 Referências e Materiais Complementares

- [Documentação Oficial Flask - Blueprints](https://flask.palletsprojects.com/en/latest/blueprints/)
- [Tutorial Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- [Padrão Application Factory](https://flask.palletsprojects.com/en/latest/patterns/appfactories/)

---

## ❓ Perguntas Frequentes (FAQ)

**P: Posso ter blueprints dentro de blueprints?**  
R: Tecnicamente sim, mas não é recomendado. Mantenha uma estrutura plana para facilitar a manutenção.

**P: Preciso criar templates e static para cada blueprint?**  
R: Não é obrigatório. Blueprints podem usar templates e arquivos estáticos globais também.

**P: Quantos blueprints posso ter?**  
R: Quantos precisar! Aplicações grandes podem ter dezenas de blueprints.

**P: Blueprints podem compartilhar código?**  
R: Sim! Crie funções utilitárias em arquivos separados e importe onde precisar.

**P: O que acontece se dois blueprints tiverem o mesmo url_prefix?**  
R: As rotas de ambos ficarão acessíveis, mas pode gerar conflitos. Evite isso!

---

**Criado para:** IFPR 2025 - Frameworks  
**Professor:** [Seu Nome]  
**Data:** Novembro/2025
