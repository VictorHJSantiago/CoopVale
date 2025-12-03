"""
Serviço de criptografia para dados sensíveis
Usa Fernet (criptografia simétrica) para proteger dados de cartão
"""
from cryptography.fernet import Fernet
from flask import current_app
import base64
import hashlib


class CriptografiaService:
    """
    Serviço para criptografar/descriptografar dados sensíveis
    Usa a biblioteca cryptography com Fernet (AES 128-bit)
    """
    
    def __init__(self):
        # Chave de criptografia da configuração
        chave = current_app.config.get('ENCRYPTION_KEY')
        
        if not chave:
            # Gerar chave temporária para desenvolvimento (NÃO USAR EM PRODUÇÃO!)
            current_app.logger.warning('ENCRYPTION_KEY não configurada! Usando chave temporária.')
            chave = Fernet.generate_key()
        elif isinstance(chave, str):
            # Converter string para bytes se necessário
            chave = chave.encode()
        
        self.cipher = Fernet(chave)
    
    def criptografar(self, dados):
        """
        Criptografa dados sensíveis
        
        Args:
            dados (str): Dados em texto plano
            
        Returns:
            str: Dados criptografados em base64
        """
        if not dados:
            return None
        
        dados_bytes = dados.encode('utf-8')
        criptografado = self.cipher.encrypt(dados_bytes)
        return base64.urlsafe_b64encode(criptografado).decode('utf-8')
    
    def descriptografar(self, dados_criptografados):
        """
        Descriptografa dados
        
        Args:
            dados_criptografados (str): Dados criptografados em base64
            
        Returns:
            str: Dados em texto plano
        """
        if not dados_criptografados:
            return None
        
        try:
            dados_bytes = base64.urlsafe_b64decode(dados_criptografados.encode('utf-8'))
            descriptografado = self.cipher.decrypt(dados_bytes)
            return descriptografado.decode('utf-8')
        except Exception as e:
            current_app.logger.error(f'Erro ao descriptografar dados: {e}')
            return None
    
    def tokenizar_cartao(self, numero_cartao):
        """
        Cria um token seguro para número de cartão
        Armazena apenas os últimos 4 dígitos e um hash
        
        Args:
            numero_cartao (str): Número do cartão completo
            
        Returns:
            dict: Token com últimos 4 dígitos e hash
        """
        if not numero_cartao:
            return None
        
        # Remover espaços e caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, numero_cartao))
        
        if len(numero_limpo) < 13 or len(numero_limpo) > 19:
            raise ValueError('Número de cartão inválido')
        
        # Últimos 4 dígitos
        ultimos_4 = numero_limpo[-4:]
        
        # Hash SHA256 do número completo (para validação futura)
        hash_cartao = hashlib.sha256(numero_limpo.encode()).hexdigest()
        
        # Criptografar número completo (caso precise ser recuperado - use com cautela!)
        numero_criptografado = self.criptografar(numero_limpo)
        
        return {
            'ultimos_4': ultimos_4,
            'hash': hash_cartao,
            'token': numero_criptografado,
            'bandeira': self._detectar_bandeira(numero_limpo)
        }
    
    def _detectar_bandeira(self, numero):
        """
        Detecta a bandeira do cartão pelo número
        
        Args:
            numero (str): Número do cartão
            
        Returns:
            str: Nome da bandeira
        """
        if numero.startswith('4'):
            return 'Visa'
        elif numero.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        elif numero.startswith(('34', '37')):
            return 'Amex'
        elif numero.startswith('6011') or numero.startswith('65'):
            return 'Discover'
        elif numero.startswith('35'):
            return 'JCB'
        elif numero.startswith('6062'):
            return 'Hipercard'
        elif numero.startswith('5067') or numero.startswith('4576'):
            return 'Elo'
        else:
            return 'Desconhecida'
    
    def validar_numero_cartao(self, numero):
        """
        Valida número de cartão usando algoritmo de Luhn
        
        Args:
            numero (str): Número do cartão
            
        Returns:
            bool: True se válido
        """
        # Remover espaços e caracteres não numéricos
        numero_limpo = ''.join(filter(str.isdigit, numero))
        
        if not numero_limpo or len(numero_limpo) < 13 or len(numero_limpo) > 19:
            return False
        
        # Algoritmo de Luhn
        soma = 0
        alternado = False
        
        for i in range(len(numero_limpo) - 1, -1, -1):
            digito = int(numero_limpo[i])
            
            if alternado:
                digito *= 2
                if digito > 9:
                    digito -= 9
            
            soma += digito
            alternado = not alternado
        
        return soma % 10 == 0
    
    @staticmethod
    def gerar_chave():
        """
        Gera uma nova chave de criptografia Fernet
        Use este método para gerar a chave ENCRYPTION_KEY
        
        Returns:
            str: Chave em base64
        """
        return Fernet.generate_key().decode('utf-8')
