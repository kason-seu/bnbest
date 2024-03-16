from cryptography.fernet import Fernet


# 加密函数
def encrypt_message(message):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message, key


# 解密函数
def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message


if __name__ == '__main__':
    print(encrypt_message(''))