"""
Comandos CLI personalizados para tarefas administrativas
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from datetime import datetime
from app.extensions import db
from app.models.core import Pedido
from app.services.email_service import EmailService


@click.group()
def cli():
    """Comandos administrativos da AgroFeira"""
    pass


@cli.command('expirar-pedidos-pix')
@with_appcontext
def expirar_pedidos_pix():
    """
    Cancela pedidos PIX com pagamento expirado (mais de 30 minutos)
    e restaura o estoque dos produtos.
    
    Execute este comando periodicamente via cron/scheduler:
    flask expirar-pedidos-pix
    """
    click.echo('🔍 Buscando pedidos PIX expirados...')
    
    # Buscar pedidos PIX pendentes
    pedidos_pendentes = Pedido.query.filter(
        Pedido.forma_pagamento == 'pix',
        Pedido.status_pagamento == 'pendente',
        Pedido.expiracao_pagamento.isnot(None)
    ).all()
    
    agora = datetime.utcnow()
    contador_expirados = 0
    
    for pedido in pedidos_pendentes:
        # Verificar se expirou
        if pedido.expiracao_pagamento and agora > pedido.expiracao_pagamento:
            click.echo(f'⏰ Expirando pedido #{pedido.id} (expirou em {pedido.expiracao_pagamento})')
            
            # Cancelar pedido
            pedido.status = 'Cancelado'
            pedido.status_pagamento = 'expirado'
            pedido.data_cancelamento = agora
            pedido.motivo_cancelamento = 'Pagamento PIX expirado (30 minutos)'
            pedido.cancelado_por = 'sistema'
            
            # Restaurar estoque
            for item in pedido.itens:
                produto = item.produto
                produto.estoque += item.quantidade
                click.echo(f'  ↩️ Restaurando {item.quantidade}x {produto.nome} ao estoque')
            
            # Enviar email de notificação
            try:
                email_service = EmailService()
                email_service.enviar_pedido_expirado(pedido)
                click.echo(f'  📧 Email de expiração enviado para {pedido.cliente.usuario.email}')
            except Exception as e:
                click.echo(f'  ⚠️ Erro ao enviar email: {e}', err=True)
            
            contador_expirados += 1
    
    # Salvar alterações
    if contador_expirados > 0:
        db.session.commit()
        click.echo(f'✅ {contador_expirados} pedido(s) PIX expirado(s) cancelado(s)')
    else:
        click.echo('✅ Nenhum pedido PIX expirado encontrado')


@cli.command('verificar-pagamentos')
@with_appcontext
def verificar_pagamentos():
    """
    Consulta status de pagamentos pendentes no gateway
    e atualiza o banco de dados.
    
    flask verificar-pagamentos
    """
    from app.services.pagamento_service import PagamentoService
    
    click.echo('🔍 Verificando status de pagamentos pendentes...')
    
    # Buscar pedidos com pagamento pendente
    pedidos_pendentes = Pedido.query.filter(
        Pedido.status_pagamento == 'pendente',
        Pedido.pagamento_id.isnot(None)
    ).all()
    
    if not pedidos_pendentes:
        click.echo('✅ Nenhum pagamento pendente')
        return
    
    pagamento_service = PagamentoService()
    contador_atualizados = 0
    
    for pedido in pedidos_pendentes:
        click.echo(f'🔎 Consultando pagamento #{pedido.pagamento_id} (Pedido #{pedido.id})')
        
        # Consultar status no gateway
        info = pagamento_service.consultar_pagamento(pedido.pagamento_id)
        
        if not info:
            click.echo(f'  ⚠️ Não foi possível consultar o pagamento', err=True)
            continue
        
        status = info.get('status')
        
        if status == 'approved':
            click.echo(f'  ✅ Pagamento aprovado!')
            pedido.status_pagamento = 'aprovado'
            pedido.status = 'Pagamento confirmado'
            pedido.data_pagamento = datetime.utcnow()
            
            # Enviar email
            try:
                email_service = EmailService()
                email_service.enviar_confirmacao_pagamento(pedido)
            except Exception as e:
                click.echo(f'  ⚠️ Erro ao enviar email: {e}', err=True)
            
            contador_atualizados += 1
        
        elif status == 'rejected':
            click.echo(f'  ❌ Pagamento rejeitado')
            pedido.status_pagamento = 'rejeitado'
            pedido.status = 'Pagamento rejeitado'
            pedido.motivo_rejeicao = info.get('status_detail')
            contador_atualizados += 1
        
        elif status == 'cancelled':
            click.echo(f'  🚫 Pagamento cancelado')
            pedido.status_pagamento = 'cancelado'
            pedido.status = 'Cancelado'
            pedido.data_cancelamento = datetime.utcnow()
            
            # Restaurar estoque
            for item in pedido.itens:
                item.produto.estoque += item.quantidade
            
            contador_atualizados += 1
        
        else:
            click.echo(f'  ⏳ Status: {status}')
    
    # Salvar alterações
    if contador_atualizados > 0:
        db.session.commit()
        click.echo(f'✅ {contador_atualizados} pagamento(s) atualizado(s)')
    else:
        click.echo('✅ Nenhuma atualização necessária')


@cli.command('gerar-chave-criptografia')
def gerar_chave_criptografia():
    """
    Gera uma nova chave de criptografia Fernet
    Use esta chave na variável ENCRYPTION_KEY do .env
    
    flask gerar-chave-criptografia
    """
    from app.services.criptografia_service import CriptografiaService
    
    chave = CriptografiaService.gerar_chave()
    
    click.echo('🔐 Nova chave de criptografia gerada:')
    click.echo('')
    click.echo(f'ENCRYPTION_KEY={chave}')
    click.echo('')
    click.echo('⚠️ IMPORTANTE:')
    click.echo('1. Adicione esta chave ao seu arquivo .env')
    click.echo('2. NUNCA compartilhe ou versione esta chave')
    click.echo('3. Use a mesma chave em produção para descriptografar dados')
