"""
Serviço de integração com gateway de pagamento (Mercado Pago)
Gerencia criação de pagamentos PIX, processamento de cartões e webhooks
"""
import requests
import hashlib
import hmac
from datetime import datetime, timedelta
from flask import current_app
from app.extensions import db
from app.models.core import Pedido


class PagamentoService:
    """
    Serviço para integração com Mercado Pago
    Documentação: https://www.mercadopago.com.br/developers/pt/docs
    """
    
    def __init__(self):
        self.access_token = current_app.config.get('MERCADOPAGO_ACCESS_TOKEN')
        self.public_key = current_app.config.get('MERCADOPAGO_PUBLIC_KEY')
        self.webhook_secret = current_app.config.get('MERCADOPAGO_WEBHOOK_SECRET')
        self.base_url = 'https://api.mercadopago.com'
        
    def criar_pagamento_pix(self, pedido):
        """
        Cria um pagamento PIX via Mercado Pago
        
        Args:
            pedido: Objeto Pedido do banco de dados
            
        Returns:
            dict: Dados do pagamento incluindo QR Code e código PIX
        """
        if not self.access_token:
            # Modo de desenvolvimento: gerar PIX simulado
            return self._gerar_pix_simulado(pedido)
        
        url = f'{self.base_url}/v1/payments'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Idempotency-Key': f'pedido-{pedido.id}-{int(datetime.utcnow().timestamp())}'
        }
        
        payload = {
            'transaction_amount': float(pedido.total),
            'description': f'Pedido #{pedido.id} - AgroFeira',
            'payment_method_id': 'pix',
            'payer': {
                'email': pedido.cliente.usuario.email,
                'first_name': pedido.cliente.nome.split()[0],
                'last_name': ' '.join(pedido.cliente.nome.split()[1:]) if len(pedido.cliente.nome.split()) > 1 else '-'
            },
            'notification_url': current_app.config.get('WEBHOOK_URL', '') + f'/webhooks/mercadopago',
            'external_reference': str(pedido.id),
            'date_of_expiration': (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Atualizar pedido com dados do pagamento
            pedido.pagamento_id = str(data.get('id'))
            pedido.status_pagamento = 'pendente'
            pedido.expiracao_pagamento = datetime.fromisoformat(data['date_of_expiration'].replace('Z', '+00:00'))
            db.session.commit()
            
            return {
                'qr_code': data['point_of_interaction']['transaction_data']['qr_code_base64'],
                'qr_code_url': f"data:image/png;base64,{data['point_of_interaction']['transaction_data']['qr_code_base64']}",
                'codigo_pix': data['point_of_interaction']['transaction_data']['qr_code'],
                'pagamento_id': data['id'],
                'expiracao': data['date_of_expiration']
            }
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'Erro ao criar pagamento PIX: {e}')
            # Fallback para PIX simulado em caso de erro
            return self._gerar_pix_simulado(pedido)
    
    def _gerar_pix_simulado(self, pedido):
        """Gera PIX simulado para desenvolvimento/teste"""
        import qrcode
        import io
        import base64
        
        chave_pix = "contato@agrofeira.com"
        beneficiario = "AgroFeira - Rede Orgânicos"
        cidade = "João Pessoa"
        valor = float(pedido.total)
        payload_id = f"PEDIDO{pedido.id:08d}"
        
        # Código PIX simplificado (formato EMV básico)
        codigo_pix = f"00020126{len(chave_pix):02d}{chave_pix}52040000530398654{len(str(valor)):02d}{valor:.2f}5802BR59{len(beneficiario):02d}{beneficiario}60{len(cidade):02d}{cidade}62{len(payload_id):02d}{payload_id}6304"
        crc = hashlib.md5(codigo_pix.encode()).hexdigest()[:4].upper()
        codigo_pix += crc
        
        # Gerar QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(codigo_pix)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Atualizar pedido com dados simulados
        pedido.pagamento_id = f"SIM-{pedido.id}-{int(datetime.utcnow().timestamp())}"
        pedido.status_pagamento = 'pendente'
        pedido.expiracao_pagamento = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        
        return {
            'qr_code': img_base64,
            'qr_code_url': f"data:image/png;base64,{img_base64}",
            'codigo_pix': codigo_pix,
            'pagamento_id': pedido.pagamento_id,
            'expiracao': pedido.expiracao_pagamento.isoformat(),
            'simulado': True
        }
    
    def processar_pagamento_cartao(self, pedido, dados_cartao):
        """
        Processa pagamento com cartão de crédito/débito
        
        Args:
            pedido: Objeto Pedido
            dados_cartao: dict com token do cartão (não enviar dados brutos!)
            
        Returns:
            dict: Resultado do processamento
        """
        if not self.access_token:
            # Modo simulado
            return self._simular_pagamento_cartao(pedido)
        
        url = f'{self.base_url}/v1/payments'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Idempotency-Key': f'pedido-{pedido.id}-{int(datetime.utcnow().timestamp())}'
        }
        
        payload = {
            'transaction_amount': float(pedido.total),
            'token': dados_cartao.get('token'),  # Token gerado no frontend via Mercado Pago JS SDK
            'description': f'Pedido #{pedido.id} - AgroFeira',
            'installments': dados_cartao.get('installments', 1),
            'payment_method_id': dados_cartao.get('payment_method_id', 'visa'),
            'payer': {
                'email': pedido.cliente.usuario.email,
            },
            'notification_url': current_app.config.get('WEBHOOK_URL', '') + f'/webhooks/mercadopago',
            'external_reference': str(pedido.id)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Atualizar pedido
            pedido.pagamento_id = str(data.get('id'))
            pedido.status_pagamento = data.get('status')  # approved, pending, rejected
            
            if data.get('status') == 'approved':
                pedido.status = 'Pagamento confirmado'
                pedido.data_pagamento = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'sucesso': data.get('status') == 'approved',
                'status': data.get('status'),
                'pagamento_id': data.get('id'),
                'mensagem': data.get('status_detail')
            }
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'Erro ao processar pagamento com cartão: {e}')
            return {'sucesso': False, 'mensagem': 'Erro ao processar pagamento'}
    
    def _simular_pagamento_cartao(self, pedido):
        """Simula aprovação de pagamento com cartão para desenvolvimento"""
        pedido.pagamento_id = f"SIM-CARD-{pedido.id}-{int(datetime.utcnow().timestamp())}"
        pedido.status_pagamento = 'aprovado'
        pedido.status = 'Pagamento confirmado'
        pedido.data_pagamento = datetime.utcnow()
        db.session.commit()
        
        return {
            'sucesso': True,
            'status': 'aprovado',
            'pagamento_id': pedido.pagamento_id,
            'mensagem': 'Pagamento aprovado (simulado)',
            'simulado': True
        }
    
    def verificar_assinatura_webhook(self, data, signature):
        """
        Verifica autenticidade do webhook do Mercado Pago
        
        Args:
            data: Dados recebidos do webhook
            signature: Assinatura x-signature header
            
        Returns:
            bool: True se assinatura for válida
        """
        if not self.webhook_secret:
            # Em desenvolvimento, aceitar todos os webhooks
            return True
        
        # Criar hash HMAC-SHA256
        message = f"{data}"
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def consultar_pagamento(self, pagamento_id):
        """
        Consulta status de um pagamento no Mercado Pago
        
        Args:
            pagamento_id: ID do pagamento
            
        Returns:
            dict: Dados do pagamento
        """
        if not self.access_token or pagamento_id.startswith('SIM-'):
            return {'status': 'simulado'}
        
        url = f'{self.base_url}/v1/payments/{pagamento_id}'
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'Erro ao consultar pagamento: {e}')
            return None
