#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

try :
    from Crypto.Cipher import AES
    from Crypto import Random
    CRYPTO_IMPORT = True
except :
    CRYPTO_IMPORT = False

import hashlib
import pickle
import base64
import six


class CypherText:
	def __init__(self):
		self.__CypherText = ''
		self.__trailLen = 0

	def getCypherText(self):
		return self.__CypherText
		
	def setCypherText(self, CText):
		self.__CypherText = CText
		
	def setTrail(self, TLen):
		self.__trailLen = TLen
		
	def getTrail(self):
		return self.__trailLen


def hashPassword_MD5(Password):
	m = hashlib.md5()
	if six.PY3:
		Password = str(Password).encode('utf-8')
	m.update(Password)
	return m.hexdigest()


def encrypt(message, key):
	TrailLen = 0
	while (len(message) % 16) != 0:
		message = message + '_'
		# if six.PY2:
		# 	message  = message + '_'
		# else :
		# 	message = message + b'_'
		TrailLen = TrailLen + 1
	
	CypherOut = CypherText()
	CypherOut.setTrail(TrailLen)

	cryptu = AES.new(key, AES.MODE_ECB)

	#Try to delete the key from memory
	key = hashPassword_MD5('PYCRYPT_ERASE_')
	
	CypherOut.setCypherText(cryptu.encrypt(message))
	return CypherOut


def decrypt(ciphertext, key):
	if six.PY3 and not isinstance(key, bytes):
		key = key.encode("utf8")
	cryptu = AES.new(key, AES.MODE_ECB)
	
	#Try to delete the key from memory
	key = hashPassword_MD5('PYCRYPT_ERASE_')
	
	message_n_trail = cryptu.decrypt(ciphertext.getCypherText())
	return message_n_trail[0:len(message_n_trail) - ciphertext.getTrail()]


def cryptFile(filename_in, filename_out, key):
	fr = open(filename_in, 'rb')
	fileContent = fr.read()
	cyphertext = encrypt(fileContent, key )
	fw = open(filename_out, 'wb')
	pickle.dump( cyphertext, fw, -1 )
	
# def decryptFile(filename_in, filename_out, key):
# 	fr = open(filename_in, 'rb')
# 	if six.PY2:
# 		cyphertext = pickle.load(fr)
# 	else:
# 		cyphertext = pickle.load(fr, encoding="bytes")
# 	message = decrypt(cyphertext, key)
# 	fw = open(filename_out, 'wb')
# 	fw.write(message)


# --------------------------------------------------------------------------
# 2ème version qui évite l'utilisation de Pickle pour une compatibilité py3
# --------------------------------------------------------------------------

def pad(s):
	padding_size = AES.block_size - len(s) % AES.block_size
	return s + b"\0" * padding_size, padding_size

def encrypt2(message, key, key_size=256):
	message, padding_size = pad(message)
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(key, AES.MODE_CFB, iv)
	enc_bytes = iv + cipher.encrypt(message)
	if six.PY2:
		enc_bytes += bytearray([padding_size])
	else:
		enc_bytes += bytes([padding_size])
	return enc_bytes

def decrypt2(ciphertext, key):
	iv = ciphertext[:AES.block_size]
	cipher = AES.new(key, AES.MODE_CFB, iv)
	plaintext = cipher.decrypt(ciphertext[AES.block_size:-1])
	if six.PY2:
		ciphertext = bytearray(ciphertext)
	padding_size = ciphertext[-1] * (-1)
	return plaintext[:padding_size]

def cryptFile2(filename_in, filename_out, key):
	if six.PY3:
		key = key.encode("utf8")
	with open(filename_in, 'rb') as fo:
		contenu = fo.read()
	enc = encrypt2(contenu, key)
	enc = b"SV2" + enc
	with open(filename_out, 'wb') as fo:
		fo.write(enc)

# def decryptFile2(filename_in, filename_out, key):
# 	if six.PY3:
# 		key = key.encode("utf8")
# 	with open(filename_in, 'rb') as fo:
# 		ciphertext = fo.read()
# 	ciphertext = ciphertext[2:]
# 	dec = decrypt2(ciphertext, key)
# 	with open(filename_out, 'wb') as fo:
# 		fo.write(dec)


def DecrypterFichier(fichierCrypte="", fichierDecrypte="", motdepasse=""):
	# Formatage du mot de passe
	motdepasse = hashPassword_MD5(motdepasse)
	if six.PY3:
		motdepasse = motdepasse.encode("utf8")

	# Lecture du fichier
	with open(fichierCrypte, 'rb') as fo:
		contenu = fo.read()

	# Analyse du fichier
	if contenu[:3] == b"SV2":
		# Nouvelle version
		contenu = contenu[3:]
		dec = decrypt2(contenu, motdepasse)
	else:
		# Ancienne version
		with open(fichierCrypte, 'rb') as fo:
			if six.PY2:
				contenu2 = pickle.load(fo)
			else:
				contenu2 = pickle.load(fo, encoding="bytes")
			dec = decrypt(contenu2, motdepasse)

	# Enregistrement du fichier décrypté
	with open(fichierDecrypte, 'wb') as fr:
		fr.write(dec)


def CrypterFichier(fichierDecrypte="", fichierCrypte="", motdepasse="", ancienne_methode=False):
	if not ancienne_methode or six.PY3:
		fonction = cryptFile2
	else:
		fonction = cryptFile
	fonction(fichierDecrypte, fichierCrypte, hashPassword_MD5(motdepasse))




# ----------- Cryptage d'un simple texte unicode ------------

class AESCipher(object):
    """
    A classical AES Cipher. Can use any size of data and any size of password thanks to padding.
    Also ensure the coherence and the type of the data with a unicode to byte converter.
    """
    def __init__(self, key, bs=32, prefixe=None):
        self.bs = bs
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()
        self.prefixe = prefixe

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * AESCipher.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        if raw == None :
            return None
        raw = self._pad(AESCipher.str_to_bytes(raw))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        texte = base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')
        if self.prefixe != None :
            texte = self.prefixe + texte
        return texte

    def decrypt(self, enc):
        if enc == None :
            return None
        if self.prefixe != None :
            if enc.startswith(self.prefixe) == False :
                return enc
            else :
                enc = enc[len(self.prefixe):]
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')



if (__name__ == '__main__'):
    cryptage = AESCipher("motdepasse", bs=32, prefixe="#x#")
    data = cryptage.encrypt(u"Ceci est le texte codé")
    print(len(data), data)
    print(cryptage.decrypt(data))
