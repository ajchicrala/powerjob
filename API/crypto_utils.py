import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()


# ==========================================================
# CHAVE SECRETA
# 👉 Gere UMA vez e guarde em local seguro (.env ou variável de ambiente)
# ==========================================================
#
# Para gerar a chave:
# >>> from cryptography.fernet import Fernet
# >>> print(Fernet.generate_key().decode())
#
# Depois coloque no .env:
# CRYPTO_KEY=coloque_a_chave_aqui
#
# ==========================================================

CRYPTO_KEY = os.getenv("CRYPTO_KEY")

if not CRYPTO_KEY:
    raise RuntimeError(
        "❌ CRYPTO_KEY não encontrada. Defina no .env ou variável de ambiente."
    )

fernet = Fernet(CRYPTO_KEY.encode())

# ==========================================================
# 🔐 ENCRIPTAR
# ==========================================================
def Encrypta(texto: str) -> str:
    """
    Recebe uma string e retorna o texto encriptado (base64).
    """
    if texto is None:
        return None

    if not isinstance(texto, str):
        raise TypeError("Encrypta espera uma string")

    token = fernet.encrypt(texto.encode("utf-8"))
    return token.decode("utf-8")

# ==========================================================
# 🔓 DESENCRIPTAR
# ==========================================================
def Decrypta(texto_encriptado: str) -> str:
    """
    Recebe uma string encriptada e retorna o texto original.
    """
    if texto_encriptado is None:
        return None

    if not isinstance(texto_encriptado, str):
        raise TypeError("Decrypta espera uma string")

    texto = fernet.decrypt(texto_encriptado.encode("utf-8"))
    return texto.decode("utf-8")
