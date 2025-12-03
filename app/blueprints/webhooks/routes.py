"""
Rotas de webhooks para receber notificações de pagamento
"""
from flask import request, jsonify, current_app
from app.extensions import db
from app.models.core import Pedido
from app.services.pagamento_service import PagamentoService
from app.services.email_service import EmailService
from datetime import datetime
from . import webhooks_bp


@webhooks_bp.route('/mercadopago', methods=['POST'])
def webhook_mercadopago():
    """
    Recebe notificações de pagamento do Mercado Pago
    Documentação: https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks
    """
    try:
        # Obter dados do webhook
        data = request.get_json()
        
        # Log da notificação recebida
        current_app.logger.info(f'Webhook recebido: {data}')
        
        # Validar assinatura (segurança)
        signature = request.headers.get('x-signature', '')
        pagamento_service = PagamentoService()
        
        if not pagamento_service.verificar_assinatura_webhook(str(data), signature):
            current_app.logger.warning('Assinatura do webhook inválida')
            return jsonify({'erro': 'Assinatura inválida'}), 401
        
        # Tipo de notificação
        tipo = data.get('type')
        
        if tipo == 'payment':
            # Notificação de pagamento
            return processar_notificacao_pagamento(data)
        
        # Outros tipos de notificação (opcional)
        return jsonify({'status': 'ok', 'mensagem': 'Tipo de notificação não processado'}), 200
        
    except Exception as e:
        current_app.logger.error(f'Erro ao processar webhook: {e}')
        return jsonify({'erro': str(e)}), 500


def processar_notificacao_pagamento(data):
    """
    Processa notificação de pagamento do Mercado Pago
    
    Args:
        data: Dados do webhook
    """
    try:
        # Extrair informações
        action = data.get('action')  # payment.created, payment.updated
        payment_data = data.get('data', {})
        payment_id = payment_data.get('id')
        
        if not payment_id:
            return jsonify({'erro': 'ID do pagamento não encontrado'}), 400
        
        # Consultar detalhes do pagamento
        pagamento_service = PagamentoService()
        pagamento_info = pagamento_service.consultar_pagamento(payment_id)
        
        if not pagamento_info:
            return jsonify({'erro': 'Pagamento não encontrado'}), 404
        
        # Encontrar pedido pela referência externa
        pedido_id = pagamento_info.get('external_reference')
        if not pedido_id:
            current_app.logger.warning(f'Referência externa não encontrada no pagamento {payment_id}')
            return jsonify({'status': 'ok'}), 200
        
        pedido = db.session.get(Pedido, int(pedido_id))
        if not pedido:
            current_app.logger.warning(f'Pedido {pedido_id} não encontrado')
            return jsonify({'erro': 'Pedido não encontrado'}), 404
        
        # Status do pagamento
        status = pagamento_info.get('status')
        status_detail = pagamento_info.get('status_detail')
        
        current_app.logger.info(f'Processando pagamento {payment_id} - Status: {status} - Pedido: {pedido_id}')
        
        # Atualizar pedido baseado no status
        if status == 'approved':
            # Pagamento aprovado
            if pedido.status_pagamento != 'aprovado':
                pedido.status_pagamento = 'aprovado'
                pedido.status = 'Pagamento confirmado'
                pedido.data_pagamento = datetime.utcnow()
                db.session.commit()
                
                # Enviar email de confirmação
                email_service = EmailService()
                email_service.enviar_confirmacao_pagamento(pedido)
                
                current_app.logger.info(f'Pagamento aprovado para pedido #{pedido.id}')
        
        elif status == 'pending':
            # Pagamento pendente
            pedido.status_pagamento = 'pendente'
            pedido.status = 'Aguardando pagamento'
            db.session.commit()
        
        elif status == 'rejected':
            # Pagamento rejeitado
            pedido.status_pagamento = 'rejeitado'
            pedido.status = 'Pagamento rejeitado'
            pedido.motivo_rejeicao = status_detail
            db.session.commit()
            
            current_app.logger.warning(f'Pagamento rejeitado para pedido #{pedido.id}: {status_detail}')
        
        elif status == 'cancelled':
            # Pagamento cancelado
            pedido.status_pagamento = 'cancelado'
            pedido.status = 'Cancelado'
            pedido.data_cancelamento = datetime.utcnow()
            pedido.motivo_cancelamento = 'Pagamento cancelado'
            
            # Restaurar estoque
            for item in pedido.itens:
                item.produto.estoque += item.quantidade
            
            db.session.commit()
        
        elif status == 'refunded':
            # Pagamento reembolsado
            pedido.status_pagamento = 'reembolsado'
            pedido.status = 'Reembolsado'
            
            # Restaurar estoque
            for item in pedido.itens:
                item.produto.estoque += item.quantidade
            
            db.session.commit()
        
        return jsonify({'status': 'ok', 'mensagem': 'Webhook processado com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f'Erro ao processar notificação de pagamento: {e}')
        return jsonify({'erro': str(e)}), 500


@webhooks_bp.route('/simular-pagamento/<int:pedido_id>', methods=['POST'])
def simular_pagamento(pedido_id):
    """
    APENAS PARA DESENVOLVIMENTO: Simula confirmação de pagamento
    Remover ou proteger em produção!
    """
    if not current_app.debug:
        return jsonify({'erro': 'Disponível apenas em modo debug'}), 403
    
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return jsonify({'erro': 'Pedido não encontrado'}), 404
    
    # Simular aprovação de pagamento
    pedido.status_pagamento = 'aprovado'
    pedido.status = 'Pagamento confirmado'
    pedido.data_pagamento = datetime.utcnow()
    db.session.commit()
    
    # Enviar email
    email_service = EmailService()
    email_service.enviar_confirmacao_pagamento(pedido)
    
    return jsonify({
        'status': 'ok',
        'mensagem': 'Pagamento simulado com sucesso',
        'pedido_id': pedido_id
    }), 200
