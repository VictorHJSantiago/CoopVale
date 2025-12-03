"""
Serviço de envio de emails
Suporta Flask-Mail e SMTP direto
"""
from flask import current_app, render_template
from flask_mail import Message, Mail
from threading import Thread


mail = Mail()


def enviar_email_async(app, msg):
    """Envia email em thread separada para não bloquear a aplicação"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f'Erro ao enviar email: {e}')


class EmailService:
    """
    Serviço para envio de emails transacionais
    """
    
    def __init__(self):
        self.remetente = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@agrofeira.com')
        self.habilitado = current_app.config.get('MAIL_ENABLED', False)
    
    def enviar_confirmacao_pedido(self, pedido):
        """
        Envia email de confirmação de pedido
        
        Args:
            pedido: Objeto Pedido
        """
        if not self.habilitado:
            current_app.logger.info(f'Email desabilitado. Confirmação do pedido #{pedido.id} não enviada.')
            return
        
        destinatario = pedido.cliente.usuario.email
        assunto = f'Pedido #{pedido.id} Confirmado - AgroFeira'
        
        # Renderizar template HTML
        html = render_template('emails/confirmacao_pedido.html', pedido=pedido)
        texto = render_template('emails/confirmacao_pedido.txt', pedido=pedido)
        
        self._enviar(destinatario, assunto, html, texto)
    
    def enviar_confirmacao_pagamento(self, pedido):
        """
        Envia email de confirmação de pagamento
        
        Args:
            pedido: Objeto Pedido com pagamento confirmado
        """
        if not self.habilitado:
            current_app.logger.info(f'Email desabilitado. Confirmação de pagamento do pedido #{pedido.id} não enviada.')
            return
        
        destinatario = pedido.cliente.usuario.email
        assunto = f'Pagamento Confirmado - Pedido #{pedido.id}'
        
        html = render_template('emails/pagamento_confirmado.html', pedido=pedido)
        texto = render_template('emails/pagamento_confirmado.txt', pedido=pedido)
        
        self._enviar(destinatario, assunto, html, texto)
    
    def enviar_pedido_cancelado(self, pedido):
        """
        Envia email de notificação de cancelamento
        
        Args:
            pedido: Objeto Pedido cancelado
        """
        if not self.habilitado:
            return
        
        destinatario = pedido.cliente.usuario.email
        assunto = f'Pedido #{pedido.id} Cancelado'
        
        html = render_template('emails/pedido_cancelado.html', pedido=pedido)
        texto = render_template('emails/pedido_cancelado.txt', pedido=pedido)
        
        self._enviar(destinatario, assunto, html, texto)
    
    def enviar_pedido_expirado(self, pedido):
        """
        Envia email notificando expiração de pagamento PIX
        
        Args:
            pedido: Objeto Pedido com pagamento expirado
        """
        if not self.habilitado:
            return
        
        destinatario = pedido.cliente.usuario.email
        assunto = f'Pagamento Expirado - Pedido #{pedido.id}'
        
        html = render_template('emails/pagamento_expirado.html', pedido=pedido)
        texto = render_template('emails/pagamento_expirado.txt', pedido=pedido)
        
        self._enviar(destinatario, assunto, html, texto)
    
    def _enviar(self, destinatario, assunto, html, texto):
        """
        Método interno para envio de email
        
        Args:
            destinatario: Email do destinatário
            assunto: Assunto do email
            html: Corpo em HTML
            texto: Corpo em texto plano
        """
        try:
            msg = Message(
                subject=assunto,
                sender=self.remetente,
                recipients=[destinatario]
            )
            msg.body = texto
            msg.html = html
            
            # Enviar de forma assíncrona
            Thread(
                target=enviar_email_async,
                args=(current_app._get_current_object(), msg)
            ).start()
            
            current_app.logger.info(f'Email enviado para {destinatario}: {assunto}')
            
        except Exception as e:
            current_app.logger.error(f'Erro ao preparar email: {e}')
