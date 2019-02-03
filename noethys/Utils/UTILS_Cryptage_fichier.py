#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
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
import sys, getopt
import getpass
import base64
import six


class CypherText:

	__doc__ = """
	This in an encrypted file. It uses PyCrypt: 
	http://reachme.web.googlepages.com/pycrypt 
	"""
	def __init__(self):
		self.__ProjectWebpage = ' http://reachme.web.googlepages.com/pycrypt '
		self.__ProgramVersion = ' 0.2 '
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
	
def read_keys_from_file():
	f = open('./keys.txt','r')
	key = ''

	for line in f.readlines():
		if line.find('PUBLIC_KEY = ') != -1:
			key = line.strip('PUBLIC_KEY = ')
	
	if key == '' or len(key) != 32: 
		return -1
	else:
		return key	
	
def encrypt(message, key):

	TrailLen = 0
	#AES requires blocks of 16
	while (len(message) % 16) != 0:
		if six.PY2:
			message  = message + '_'
		else :
			message = message + b'_'
		TrailLen = TrailLen + 1
	
	CypherOut = CypherText()
	CypherOut.setTrail(TrailLen)

	if six.PY3:
		key = key.encode("utf8")
	cryptu = AES.new(key, AES.MODE_ECB)

	#Try to delete the key from memory
	key = hashPassword_MD5('PYCRYPT_ERASE_')
	
	CypherOut.setCypherText( cryptu.encrypt(message) )
	return CypherOut
	
def decrypt(ciphertext, key):
	if six.PY3:
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
	
def decryptFile(filename_in, filename_out, key):
	fr = open(filename_in, 'rb')
	cyphertext = pickle.load(fr)
	message = decrypt(cyphertext, key)
	fw = open(filename_out, 'wb')
	fw.write(message)

def getManual():
	man = """-- PyCrypt V0.2 --
Usage:
	PyCrypt [mode= -e or -d] [filename_in] [filename_out] [password]
	-e : Encrypt a file
	-d : Decrypt a file
	The user will be prompted to provide missing information if any.
	
Examples:
	PyCrypt
	PyCrypt -e
	PyCrypt --encrypt Filename_in Filename_out Password
	PyCrypt --decrypt Filename_in Filename_out Password
	
For more info, please visit the project's homepage at:
	http://reachme.web.googlepages.com/pycrypt
	"""
	return man

__doc__ = """
System exit code:
2 : Argument parsing error
-1: Error/Crash, please report
"""

#Returns the parameters of execution of the program
def parseCommandLine():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hed", ["help","encrypt","decrypt"])
	except getopt.error as msg:
		print('Cannot parse arguments:')
		print(msg)
		print('\n' + getManual())
		sys.exit(2)
	
	method = ''
	
	#Process options
	for o, a in opts:
		if o in ("-h", "--help"):
			print(getManual())
			sys.exit(0)
			
		elif o in ("-d", "--decrypt"):
			method = 'decrypt'
		elif o in ("-e", "--encrypt"):
			method = 'encrypt'
		else:
			print('Invalid option.')
			print(getManual())
			sys.exit(2)
	
	if len(opts) > 1:
		print('Too many options')
		print(getManual())
		sys.exit(2)
		
	if len(args) > 3:
		print('Too many arguments')
		print(getManual())
		sys.exit(2)
	
	#If -e -d?
	#If not specified, ask for the operation mode		
	if len(opts) == 0:
		menu = "Please select one of the following options:\n"
		menu +="1: Encrypt a file\n"
		menu +="2: Decrypt a file\n"
		menu +="(1,2)?"
		print(menu)
		choice = raw_input()
		
		while (choice != '1') and (choice != '2'):
			print(menu)
			choice = raw_input()
		
		if choice == '1':
			method = 'encrypt'
		if choice == '2':
			method = 'decrypt'

	#If not present, ask for the arguments interactively
	if len(args) == 0:
		filename_in = raw_input("Please enter the input filename\n")
		filename_out = raw_input("Please enter the output filename\n")
		password = getpass.getpass()
	
	if len(args) == 1:
		filename_in = args[0]
		filename_out = raw_input("Please enter the output filename\n")
		password = getpass.getpass()
	
	if len(args) == 2:
		#If the password is not specified, ask for one
		filename_in = args[0]
		filename_out = args[1]
		password = getpass.getpass()
		
	if len(args) == 3:
		filename_in = args[0]
		filename_out = args[1]
		password = args[2]
		
	return (method, filename_in, filename_out, password)

def checkProgArgs(method, filename_in, filename_out, password):
	if (method != 'encrypt') and (method != 'decrypt'):
		print('ERROR: invalid method: ' + method)
		sys.exit(-1)
	
	#Should it be allowed?
	"""
	if filename_in == filename_out:
		print 'ERROR: filename_in == filename_out.'
		sys.exit(-1)
	"""
	
	#++check the existense of filename_in and inexistence of filename_out
	return 0

def CrypterFichier(fichierDecrypte="", fichierCrypte="", motdepasse=""):
	cryptFile(fichierDecrypte, fichierCrypte, hashPassword_MD5(motdepasse))

def DecrypterFichier(fichierCrypte="", fichierDecrypte="", motdepasse=""):
	decryptFile(fichierCrypte, fichierDecrypte, hashPassword_MD5(motdepasse))

def CrypterTexte(texte, motdepasse=""):
	return encrypt(texte, hashPassword_MD5(motdepasse)).getCypherText()

def DecrypterTexte(texte, motdepasse=""):
	texte = pickle.load(texte)
	return decrypt(texte, hashPassword_MD5(motdepasse))



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
##	#Parse command line options
##	(method, filename_in, filename_out, password) = parseCommandLine()
##	checkProgArgs(method, filename_in, filename_out, password)
##	#print (method, filename_in, filename_out, password)
##	
##	if method == 'encrypt':
##		cryptFile(filename_in, filename_out, hashPassword_MD5(password))
##	elif method == 'decrypt':
##		decryptFile(filename_in, filename_out, hashPassword_MD5(password))
##	
##	getpass.getpass('\nProgram successfully ended, press any key to exit.') 

##Use example:
    #PublicKey = read_keys_from_file()
    #cyphertext = encrypt( 'truc!', PublicKey )
    #print decrypt( cyphertext, PublicKey )

    cryptage = AESCipher("motdepasse", bs=32, prefixe="#x#")
    data = cryptage.encrypt(u"Ceci est le texte codé")
    print(len(data), data)
    print(cryptage.decrypt(data))
