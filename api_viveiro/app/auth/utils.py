# app/auth/utils.py
from passlib.context import CryptContext

# Configuração da criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_senha(senha_texto, senha_hash):
    """
    Verifica se a senha em texto plano corresponde ao hash armazenado.
    
    Args:
        senha_texto: Senha em texto plano fornecida pelo usuário
        senha_hash: Hash da senha armazenado no banco de dados
        
    Returns:
        bool: True se a senha for válida, False caso contrário
    """
    return pwd_context.verify(senha_texto, senha_hash)

def gerar_senha_hash(senha):
    """
    Gera um hash seguro para uma senha.
    
    Args:
        senha: Senha em texto plano
        
    Returns:
        str: Hash da senha
    """
    return pwd_context.hash(senha)

def validar_requisitos_senha(senha):
    """
    Verifica se a senha atende aos requisitos mínimos de segurança.
    
    Args:
        senha: Senha em texto plano
        
    Returns:
        tuple: (válida, mensagem_erro)
    """
    # Verificar comprimento mínimo
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    
    # Verificar se contém pelo menos uma letra maiúscula
    if not any(c.isupper() for c in senha):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    
    # Verificar se contém pelo menos uma letra minúscula
    if not any(c.islower() for c in senha):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    
    # Verificar se contém pelo menos um número
    if not any(c.isdigit() for c in senha):
        return False, "A senha deve conter pelo menos um número"
    
    # Verificar se contém pelo menos um caractere especial
    especiais = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"
    if not any(c in especiais for c in senha):
        return False, "A senha deve conter pelo menos um caractere especial"
    
    return True, "Senha válida"