# pip install pycryptodome
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes



def encrypt(data: str, key: str, iv: str) -> str:
    '''
    使用CBC模式
    key和iv初始化向量使用 get_key_iv 生成
    '''
    cipher = AES.new(b64decode(key), AES.MODE_CBC, b64decode(iv))
    data = data.encode('utf-8')
    en_bytes = cipher.encrypt(pad(data, AES.block_size))
    return b64encode(en_bytes).decode('utf-8')


def decrypt(cipher_data: str, key: str, iv: str) -> str:
    '''
    使用CBC模式
    key和iv初始化向量使用 get_key_iv 生成
    '''
    cipher = AES.new(b64decode(key), AES.MODE_CBC, b64decode(iv))
    cipher_data = b64decode(cipher_data)
    data = unpad(cipher.decrypt(cipher_data), AES.block_size)
    return data.decode('utf-8')

def get_key_iv():
    '''返回str类型的'''
    key = b64encode(get_random_bytes(16)).decode('utf-8')
    iv = b64encode(get_random_bytes(AES.block_size)).decode('utf-8')
    return key, iv
