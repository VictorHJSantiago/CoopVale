# 💳 Sistema de Pagamento - AgroFeira

Sistema completo de pagamento integrado com **Mercado Pago**, incluindo PIX, cartões de crédito/débito, webhooks, criptografia e automação.

---

## 🚀 Funcionalidades Implementadas

### 1. **Gateway de Pagamento (Mercado Pago)**
- ✅ Integração completa com API do Mercado Pago
- ✅ Pagamento via PIX com QR Code dinâmico
- ✅ Processamento de cartões (crédito/débito)
- ✅ Modo simulado para desenvolvimento
- ✅ Fallback automático em caso de erro

**Arquivo:** `app/services/pagamento_service.py`

### 2. **Webhooks para Notificações**
- ✅ Rota para receber notificações do Mercado Pago
- ✅ Validação de assinatura (segurança)
- ✅ Processamento automático de pagamentos
- ✅ Atualização de status em tempo real
- ✅ Rota de simulação para testes

**Arquivo:** `app/blueprints/webhooks/routes.py`

### 3. **Criptografia e Tokenização**
- ✅ Criptografia Fernet (AES 128-bit)
- ✅ Tokenização de números de cartão
- ✅ Armazenamento seguro (apenas últimos 4 dígitos + token)
- ✅ Validação com algoritmo de Luhn
- ✅ Detecção automática de bandeira

**Arquivo:** `app/services/criptografia_service.py`

### 4. **Sistema de Email**
- ✅ Envio assíncrono (não bloqueia aplicação)
- ✅ Templates HTML + texto plano
- ✅ Emails implementados:
  - Confirmação de pedido
  - Pagamento confirmado
  - Pedido cancelado
  - Pagamento expirado

**Arquivo:** `app/services/email_service.py`

### 5. **Automação via CLI**
- ✅ Comando para expirar pedidos PIX (30 min)
- ✅ Comando para verificar pagamentos pendentes
- ✅ Gerador de chave de criptografia
- ✅ Restauração automática de estoque

**Arquivo:** `app/cli_commands.py`

### 6. **Modelo de Dados Estendido**
- ✅ Campos para ID de transação
- ✅ Status detalhado de pagamento
- ✅ Data de pagamento/expiração
- ✅ Token de cartão criptografado
- ✅ Bandeira e últimos 4 dígitos

**Arquivo:** `app/models/core.py` (Modelo `Pedido`)

---

## 📦 Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Novas bibliotecas:**
- `Flask-Mail` - Envio de emails
- `cryptography` - Criptografia de dados
- `requests` - Chamadas HTTP para API
- `qrcode[pil]` - Geração de QR Codes

### 2. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:

```env
# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=seu-token-aqui
MERCADOPAGO_PUBLIC_KEY=sua-public-key
MERCADOPAGO_WEBHOOK_SECRET=seu-secret

# Criptografia
ENCRYPTION_KEY=gere-com-comando-abaixo

# Email (opcional)
MAIL_ENABLED=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

### 3. Gerar Chave de Criptografia

```bash
flask gerar-chave-criptografia
```

Copie a chave gerada para `ENCRYPTION_KEY` no `.env`.

### 4. Aplicar Migrações do Banco

```bash
flask db migrate -m "Adiciona campos de pagamento"
flask db upgrade
```

---

## 🔧 Configuração do Mercado Pago

### 1. Criar Conta de Desenvolvedor
1. Acesse: https://www.mercadopago.com.br/developers
2. Crie uma aplicação
3. Obtenha as credenciais (Access Token e Public Key)

### 2. Configurar Webhook
1. No painel do Mercado Pago, vá em **Webhooks**
2. Adicione a URL: `https://seudominio.com/webhooks/mercadopago`
3. Selecione evento: `payments`
4. Copie o **Webhook Secret**

### 3. Modo Teste vs Produção
- **Teste:** Use credenciais de teste (começam com `TEST-`)
- **Produção:** Use credenciais de produção

---

## 💻 Comandos CLI

### Expirar Pedidos PIX (executar via cron)

```bash
flask expirar-pedidos-pix
```

**O que faz:**
- Busca pedidos PIX pendentes há mais de 30 minutos
- Cancela automaticamente
- Restaura estoque
- Envia email de notificação

**Sugestão de cron (executar a cada 5 minutos):**
```cron
*/5 * * * * cd /caminho/app && flask expirar-pedidos-pix
```

### Verificar Pagamentos Pendentes

```bash
flask verificar-pagamentos
```

**O que faz:**
- Consulta status no Mercado Pago
- Atualiza pedidos com pagamento confirmado
- Envia emails de confirmação

### Gerar Chave de Criptografia

```bash
flask gerar-chave-criptografia
```

---

## 🧪 Testes e Desenvolvimento

### Modo Simulado (Desenvolvimento)

Quando `MERCADOPAGO_ACCESS_TOKEN` não está configurado:
- PIX é gerado localmente (sem API)
- Pagamentos com cartão são aprovados automaticamente
- Funciona offline

### Simular Confirmação de Pagamento

Rota disponível apenas em modo debug:

```bash
curl -X POST http://localhost:5000/webhooks/simular-pagamento/1
```

Onde `1` é o ID do pedido.

---

## 📧 Configuração de Email

### Gmail

1. Ative **2FA** na sua conta Google
2. Crie uma **Senha de App**: https://myaccount.google.com/apppasswords
3. Configure no `.env`:

```env
MAIL_ENABLED=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=senha-de-app-gerada
```

### Outros Provedores

- **SendGrid:** `MAIL_SERVER=smtp.sendgrid.net`, porta 587
- **Mailgun:** `MAIL_SERVER=smtp.mailgun.org`, porta 587
- **AWS SES:** Configure com SMTP da AWS

---

## 🔐 Segurança

### Dados Criptografados
- Números de cartão são tokenizados
- Apenas últimos 4 dígitos + hash armazenados
- Token criptografado com Fernet (AES)

### Webhooks
- Validação de assinatura HMAC-SHA256
- Apenas requisições autênticas são processadas

### Boas Práticas
- ⚠️ **NUNCA** versione `.env` ou chaves
- ⚠️ Use HTTPS em produção
- ⚠️ Rotacione `ENCRYPTION_KEY` periodicamente
- ⚠️ Configure firewall para webhooks (apenas IPs do Mercado Pago)

---

## 📊 Fluxos Implementados

### Fluxo PIX

1. Cliente finaliza pedido e seleciona PIX
2. `PagamentoService` cria pagamento no Mercado Pago
3. QR Code e código copia-e-cola são exibidos
4. Cliente paga no app do banco
5. Mercado Pago envia notificação via webhook
6. Sistema atualiza pedido e envia email
7. Se não pagar em 30 min → cancelamento automático

### Fluxo Cartão

1. Cliente finaliza pedido e seleciona cartão
2. Dados do cartão são tokenizados no frontend (JS SDK do MP)
3. Token é enviado para backend
4. `PagamentoService` processa pagamento
5. Se aprovado → atualiza pedido e envia email
6. Se rejeitado → notifica cliente

### Webhook de Pagamento

```
Mercado Pago → POST /webhooks/mercadopago
    ↓
Validar assinatura
    ↓
Consultar detalhes do pagamento
    ↓
Atualizar status do pedido
    ↓
Enviar email ao cliente
```

---

## 🐛 Troubleshooting

### Webhook não está funcionando

1. Verifique URL no painel do Mercado Pago
2. Confirme que aplicação está acessível publicamente
3. Use **ngrok** para testes locais:
   ```bash
   ngrok http 5000
   ```
4. Configure URL temporária no Mercado Pago

### Emails não estão sendo enviados

1. Verifique `MAIL_ENABLED=true`
2. Teste credenciais SMTP
3. Veja logs: `app.logger` registra erros
4. Gmail: confirme senha de app (não senha normal)

### Erro de criptografia

1. Gere nova chave: `flask gerar-chave-criptografia`
2. Adicione ao `.env`
3. **Atenção:** mudar chave invalida dados criptografados anteriormente

### QR Code não aparece

1. Confirme instalação: `pip install qrcode[pil]`
2. Biblioteca Pillow deve estar instalada
3. Fallback: usa API externa (qrserver.com)

---

## 📝 Variáveis de Status

### `status_pagamento` (Pedido)
- `pendente` - Aguardando pagamento
- `aprovado` - Pagamento confirmado
- `rejeitado` - Pagamento negado
- `expirado` - Prazo PIX expirou
- `cancelado` - Pagamento cancelado
- `reembolsado` - Pagamento devolvido

### `status` (Pedido)
- `Aguardando confirmação`
- `Aguardando pagamento`
- `Pagamento confirmado`
- `Pagamento rejeitado`
- `Em preparo`
- `Enviado`
- `Cancelado`

---

## 🎯 Próximas Melhorias (Opcional)

- [ ] Parcelamento de cartões
- [ ] Boleto bancário
- [ ] Link de pagamento por email
- [ ] Reembolso automático
- [ ] Dashboard de transações
- [ ] Relatório financeiro
- [ ] Múltiplos gateways (PagSeguro, Stripe)

---

## 📚 Documentação Oficial

- **Mercado Pago API:** https://www.mercadopago.com.br/developers/pt/docs
- **Flask-Mail:** https://flask-mail.readthedocs.io
- **Cryptography:** https://cryptography.io/en/latest/

---

## 👨‍💻 Suporte

Para dúvidas ou problemas:
1. Verifique logs da aplicação
2. Consulte documentação do Mercado Pago
3. Revise configurações do `.env`

**Sistema desenvolvido para AgroFeira - CoopVale** 🌱
