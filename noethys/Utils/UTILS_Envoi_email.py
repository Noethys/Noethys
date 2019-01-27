#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import GestionDB
import FonctionsPerso
import re
from Utils import UTILS_Html2text
from Utils import UTILS_Titulaires

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEAudio import MIMEAudio
from email.Utils import COMMASPACE, formatdate
from email.header import Header
from email.utils import formatdate, formataddr
from email import Encoders
import mimetypes

from Outils import mail





def EnvoiEmailFamille(parent=None, IDfamille=None, nomDoc="", categorie="", listeAdresses=[], visible=True, log=None, CreationPDF=None, IDmodele=None):
    # Création du PDF
    if CreationPDF != None :
        temp = CreationPDF
    else :
        temp = parent.CreationPDF
    dictChamps = temp(nomDoc=nomDoc, afficherDoc=False)
    if dictChamps == False :
        return False

    if nomDoc != False :
        liste_pieces = [nomDoc,]
    else :
        liste_pieces = []

    # Recherche adresse famille
    if len(listeAdresses) == 0 :
        listeAdresses = GetAdresseFamille(IDfamille)
        if len(listeAdresses) == 0 :
            return False
    
    # DLG Mailer
    listeDonnees = []
    for adresse in listeAdresses :
        listeDonnees.append({
            "adresse" : adresse, 
            "pieces" : liste_pieces,
            "champs" : dictChamps,
            })
    from Dlg import DLG_Mailer
    dlg = DLG_Mailer.Dialog(parent, categorie=categorie, afficher_confirmation_envoi=visible)
    dlg.SetDonnees(listeDonnees, modificationAutorisee=False)
    if IDmodele == None :
        dlg.ChargerModeleDefaut()
    else :
        dlg.ChargerModele(IDmodele)

    if visible == True :
        # Fenêtre visible
        dlg.ShowModal()

    else :
        # Fenêtre cachée
        dlg.OnBoutonEnvoyer(None)

    if len(dlg.listeSucces) > 0 :
        resultat = True
        if log : log.EcritLog(_(u"L'Email a été envoyé avec succès."))
    else :
        resultat = False
        if log : log.EcritLog(_(u"L'email n'a pas été envoyé."))

    dlg.Destroy()

    # Suppression du PDF temporaire
    if nomDoc != False :
        try :
            os.remove(nomDoc)
        except :
            pass

    return resultat



def ValidationEmail(email):
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
        return True
    else :
        return False


def GetAdresseExpDefaut():
    """ Retourne les paramètres de l'adresse d'expéditeur par défaut """
    return GetAdresseExp(IDadresse=None)

def GetAdresseExp(IDadresse=None):
    """ Si IDadresse = None, retourne l'adresse par défaut"""
    if IDadresse == None :
        condition = "defaut=1"
    else :
        condition = "IDadresse=%d" % IDadresse
    # Récupération des données
    DB = GestionDB.DB()        
    req = """SELECT IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur
    FROM adresses_mail WHERE %s ORDER BY adresse;""" % condition
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return None
    IDadresse, adresse, nom_adresse, motdepasse, smtp, port, defaut, auth, startTLS, utilisateur = listeDonnees[0]
    dictAdresse = {"adresse":adresse, "nom_adresse":nom_adresse, "motdepasse":motdepasse, "smtp":smtp, "port":port, "auth" : auth, "startTLS":startTLS, "utilisateur" : utilisateur}
    return dictAdresse

def GetAdresseFamille(IDfamille=None, choixMultiple=True, muet=False, nomTitulaires=None):
    """ Récupère l'adresse email de la famille """
    # Récupération du nom de la famille
    if nomTitulaires == None :
        dictTitulaires = UTILS_Titulaires.GetTitulaires([IDfamille,])
        if dictTitulaires.has_key(IDfamille):
            nomTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
        else :
            nomTitulaires = _(u"Famille inconnue")
    # Récupération des adresses mails de chaque membre de la famille
    DB = GestionDB.DB()
    req = """
    SELECT 
    rattachements.IDindividu, IDcategorie,
    individus.nom, individus.prenom, individus.mail, individus.travail_mail
    FROM rattachements 
    LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
    WHERE IDcategorie IN (1, 2) AND IDfamille=%d
    ;""" % IDfamille
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    listeAdresses = []
    listeTemp = []
    for IDindividu,  IDcategorie, nom, prenom, mailPerso, mailTravail in listeDonnees :
        if mailPerso != None and mailPerso != "" and mailPerso not in listeTemp :
            listeAdresses.append((_(u"%s (Adresse perso de %s)") % (mailPerso, prenom), mailPerso))
            listeTemp.append(mailPerso)
        if mailTravail != None and mailTravail != "" and mailTravail not in listeTemp :
            listeAdresses.append((_(u"%s (Adresse pro de %s)") % (mailTravail, prenom), mailTravail))
            listeTemp.append(mailTravail)
    if len(listeAdresses) == 0 :
        if muet == False :
            dlg = wx.MessageDialog(None, _(u"Aucun membre de la famille de %s ne dispose d'adresse mail !") % nomTitulaires, "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
        return []
    elif len(listeAdresses) == 1 :
        listeMails = [listeAdresses[0][1],]
    else:
        listeLabels = []
        listeMails = []
        for label, adresse in listeAdresses :
            listeLabels.append(label)
        if choixMultiple == True :
            dlg = wx.MultiChoiceDialog(None, _(u"%d adresses internet sont disponibles pour la famille de %s.\nSélectionnez celles que vous souhaitez utiliser puis cliquez sur le bouton 'Ok' :") % (len(listeAdresses), nomTitulaires), _(u"Choix d'adresses Emails"), listeLabels)
        else :
            dlg = wx.SingleChoiceDialog(None, _(u"%d adresses internet sont disponibles pour la famille de %s.\nSélectionnez celle que vous souhaitez utiliser puis cliquez sur le bouton 'Ok' :") % (len(listeAdresses), nomTitulaires), _(u"Choix d'une adresse Email"), listeLabels)
        dlg.SetSize((450, -1))
        dlg.CenterOnScreen() 
        if dlg.ShowModal() == wx.ID_OK :
            if choixMultiple == True :
                selections = dlg.GetSelections()
            else :
                selections = [dlg.GetSelection(),]
            dlg.Destroy()
            if len(selections) == 0 :
                dlg = wx.MessageDialog(None, _(u"Vous n'avez sélectionné aucune adresse mail !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return []
            for index in selections :
                listeMails.append(listeAdresses[index][1])
        else:
            dlg.Destroy()
            return []
    
    if choixMultiple == True :
        return listeMails
    else :
        return listeMails[0]





class Message():
    def __init__(self, destinataires=[], sujet="", texte_html="", fichiers=[], images=[]):
        self.destinataires = destinataires
        self.sujet = sujet
        self.fichiers = fichiers
        self.images = images
        self.texte_html = texte_html

        # Corrige le pb des images embarquées
        index = 0
        for img in images:
            img = img.replace(u"\\", u"/")
            img = img.replace(u":", u"%3a")
            self.texte_html = self.texte_html.replace(_(u"file:/%s") % img, u"cid:image%d" % index)
            index += 1

        # Conversion du html en texte plain
        self.texte_plain = UTILS_Html2text.html2text(self.texte_html)

    def AttacheImagesIncluses(self, email=None):
        index = 0
        for img in self.images:
            fp = open(img, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            msgImage.add_header('Content-ID', '<image%d>' % index)
            msgImage.add_header('Content-Disposition', 'inline', filename=img)
            email.attach(msgImage)
            index += 1

    def AttacheFichiersJoints(self, email=None):
        for fichier in self.fichiers:
            """Guess the content type based on the file's extension. Encoding
            will be ignored, altough we should check for simple things like
            gzip'd or compressed files."""
            ctype, encoding = mimetypes.guess_type(fichier)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compresses), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                fp = open(fichier)
                # Note : we should handle calculating the charset
                part = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'image':
                fp = open(fichier, 'rb')
                part = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(fichier, 'rb')
                part = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(fichier, 'rb')
                part = MIMEBase(maintype, subtype)
                part.set_payload(fp.read())
                fp.close()
                # Encode the payload using Base64
                Encoders.encode_base64(part)
            # Set the filename parameter
            nomFichier = os.path.basename(fichier)
            if type(nomFichier) == unicode:
                nomFichier = FonctionsPerso.Supprime_accent(nomFichier)
            # changement cosmetique pour ajouter les guillements autour du filename
            part.add_header('Content-Disposition', "attachment; filename=\"%s\"" % nomFichier)
            email.attach(part)




def Messagerie(backend='SmtpV2', **kwds):
    # Ancien moteur SMTP
    if backend == "SmtpV1":
        klass = SmtpV1(**kwds)
    # Nouveau moteur SMTP
    if backend == "SmtpV2":
        klass = SmtpV2(**kwds)
    return klass




class Base_messagerie():
    def __init__(self, hote=None, port=None, utilisateur=None, motdepasse=None, email_exp=None, nom_exp=None, timeout=None, use_tls=False, fail_silently=False):
        self.hote = hote
        self.port = port
        self.utilisateur = utilisateur
        self.motdepasse = motdepasse
        self.email_exp = email_exp
        self.nom_exp = nom_exp
        self.timeout = timeout
        self.use_tls = use_tls
        self.fail_silently = fail_silently

        if self.utilisateur == "" : self.utilisateur = None
        if self.motdepasse == "" : self.motdepasse = None

        # Préparation de l'adresse d'expédition
        if self.nom_exp not in ("", None):
            self.from_email = u"%s <%s>" % (self.nom_exp, self.email_exp)
        else :
            self.from_email = self.email_exp

    def Connecter(self):
        pass

    def Envoyer(self, message=None):
        pass

    def Fermer(self):
        pass





class SmtpV1(Base_messagerie):
    def __init__(self, **kwds):
        Base_messagerie.__init__(self, **kwds)

    def Connecter(self):
        try :
            if self.motdepasse == None: self.motdepasse = ""
            if self.utilisateur == None: self.utilisateur = ""

            if self.utilisateur == None and self.motdepasse == None:
                # Envoi standard
                self.connection = smtplib.SMTP(self.hote, timeout=self.timeout)
            else:
                # Si identification SSL nécessaire :
                self.connection = smtplib.SMTP(self.hote, self.port, timeout=self.timeout)
                self.connection.ehlo()
                if self.use_tls == True:
                    self.connection.starttls()
                    self.connection.ehlo()
                self.connection.login(self.utilisateur.encode('utf-8'), self.motdepasse.encode('utf-8'))
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise

    def Envoyer(self, message=None):
        # Création du message
        email = MIMEMultipart('alternative')
        # msg['Message-ID'] = make_msgid()

        # if accuseReception == True:
        #     msg['Disposition-Notification-To'] = adresseExpediteur

        email.attach(MIMEText(message.texte_plain.encode('utf-8'), 'plain', 'utf-8'))
        email.attach(MIMEText(message.texte_html.encode('utf-8'), 'html', 'utf-8'))

        tmpmsg = email
        email = MIMEMultipart('mixed')
        email.attach(tmpmsg)

        # Ajout des headers Ã  ce Multipart
        if self.nom_exp in ("", None):
            email['From'] = self.email_exp
        else:
            sender = Header(self.nom_exp, "utf-8")
            sender.append(self.email_exp, "ascii")
            email['From'] = sender  # formataddr((nomadresseExpediteur, adresseExpediteur))
        email['To'] = ";".join(message.destinataires)
        email['Date'] = formatdate(localtime=True)
        email['Subject'] = message.sujet

        message.AttacheImagesIncluses(email)
        message.AttacheFichiersJoints(email)

        try:
            self.connection.sendmail(self.email_exp, message.destinataires, email.as_string())
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True

    def Fermer(self):
        self.connection.close()





class SmtpV2(Base_messagerie):
    def __init__(self, **kwds):
        Base_messagerie.__init__(self, **kwds)

    def Connecter(self):
        try :
            self.connection = mail.get_connection(backend='Outils.mail.smtp.EmailBackend', fail_silently=self.fail_silently,
                                             host=self.hote, port=self.port, username=self.utilisateur, password=self.motdepasse,
                                             use_tls=self.use_tls, use_ssl=False, timeout=self.timeout, ssl_keyfile=None, ssl_certfile=None)
            self.connection.open()
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise


    def Envoyer(self, message=None):
        email = mail.EmailMultiAlternatives(
            subject=message.sujet,
            body=message.texte_plain,
            from_email=self.from_email,
            to=message.destinataires,
            connection=self.connection,
        )
        email.attach_alternative(message.texte_html, "text/html")

        message.AttacheImagesIncluses(email)
        message.AttacheFichiersJoints(email)

        resultat = email.send()
        return resultat

    def Fermer(self):
        self.connection.close()





if __name__ == u"__main__":
    # Préparation du message
    message = Message(destinataires=[""], sujet=u"Sujet du mail", texte_html="<p>Ceci est le <b>texte</b> html</p>", fichiers=[], images=[])

    # Envoi du message
    messagerie = Messagerie(hote="", port=None, utilisateur="", motdepasse="", email_exp="", nom_exp=u"", timeout=None, use_tls=False)
    messagerie.Connecter()
    print messagerie.Envoyer(message)
    messagerie.Fermer()

