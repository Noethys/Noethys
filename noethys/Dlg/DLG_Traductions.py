#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_Langues
import wx.lib.agw.hyperlink as Hyperlink
import webbrowser
import os
import FonctionsPerso
import datetime
import GestionDB
from Utils import UTILS_Fichiers



class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)

    def OnLeftLink(self, event):
        if self.URL == "proposer" :
            dlg = DLG_Envoi(self)
            dlg.ShowModal()
            dlg.Destroy()
        if self.URL == "importer" :
            self.parent.Importer()

        self.UpdateLink()
        

    
# ------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, categorie=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_modeles_docs", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        titre = _(u"Traductions")
        intro = _(u"Cette liste présente les langues disponibles sur cet ordinateur. Vous pouvez ici ajouter, modifier ou supprimer des traductions. Il est ensuite possible de partager vos traductions personnalisées avec la communauté en les envoyant au concepteur de Noethys.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Traduction.png")
                
        # Modèles
        self.staticbox_modeles_staticbox = wx.StaticBox(self, -1, _(u"Langues disponibles"))
        self.ctrl_langues = OL_Langues.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
                
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_importer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Document_import.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_exporter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Document_export.png"), wx.BITMAP_TYPE_ANY))
        
        self.hyper_proposer = Hyperlien(self, label=_(u"Partager un fichier de traduction avec la communauté"), infobulle=_(u"Partager un fichier de traduction avec la communauté"), URL="proposer")
        self.label_separation = wx.StaticText(self, -1, "|") 
        self.hyper_importer = Hyperlien(self, label=_(u"Importer/Exporter les textes au format TXT"), infobulle=_(u"Importer/Exporter les textes au format TXT"), URL="importer")
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_langues.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_langues.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_langues.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_langues.Importer, self.bouton_importer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_langues.Exporter, self.bouton_exporter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        # Init contrôles
        self.ctrl_langues.MAJ() 
        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer une nouvelle traduction")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la traduction sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la traduction sélectionnée dans la liste")))
        self.bouton_importer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour importer une traduction (.xlang)")))
        self.bouton_exporter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la traduction personnalisée sélectionnée dans la liste (.xlang)")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((650, 560))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Modèles
        staticbox_modeles = wx.StaticBoxSizer(self.staticbox_modeles_staticbox, wx.VERTICAL)
        grid_sizer_modeles = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_modeles.Add(self.ctrl_langues, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_importer, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_exporter, 0, 0, 0)
        grid_sizer_modeles.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_hyper = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_hyper.Add(self.hyper_importer, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_hyper.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_hyper.Add(self.hyper_proposer, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modeles.Add(grid_sizer_hyper, 1, wx.EXPAND, 0)
        
        grid_sizer_modeles.AddGrowableRow(0)
        grid_sizer_modeles.AddGrowableCol(0)
        staticbox_modeles.Add(grid_sizer_modeles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_modeles, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
            
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Traduirelelogiciel")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)        

    def Importer(self):
        import DLG_Traduction_importer
        dlg = DLG_Traduction_importer.Dialog(self)      
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_langues.MAJ() 
        dlg.Destroy() 






# -------------------------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Envoi(wx.Dialog):
    def __init__(self, parent, texteRapport=u""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.texteRapport = texteRapport
        
        self.SetTitle(_(u"Envoyer un fichier de traduction"))
        self.label_ligne_1 = wx.StaticText(self, wx.ID_ANY, _(u"Vos fichiers seront envoyés pour validation au concepteur de Noethys\npuis intégrés dans la prochaine version du logiciel. En effectuant cette\ndémarche, vous acceptez que votre traduction soit diffusée auprès de\nla communauté sous la licence libre GNU GPL."))
        self.label_ligne_2 = wx.StaticText(self, wx.ID_ANY, _(u"Cochez le ou les fichiers de traduction à envoyer :"))
        
        listeFichiers = os.listdir(UTILS_Fichiers.GetRepLang())
        listeFichiersTemp = []
        for nomFichier in listeFichiers :
            if nomFichier.endswith(".xlang") :
                listeFichiersTemp.append(nomFichier[:-6])
        self.ctrl_fichiers = wx.CheckListBox(self, -1, choices=listeFichiersTemp)
        
        self.label_ligne_3 = wx.StaticText(self, wx.ID_ANY, _(u"Vous pouvez ajouter ci-dessous des commentaires, remarques ou \ncompléments d'informations avant de l'envoyer au concepteur de Noethys."))
        self.ctrl_commentaires = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer l'Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoyer, self.bouton_envoyer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.label_ligne_1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_commentaires.SetToolTip(wx.ToolTip(_(u"Vous pouvez saisir des commentaires ici")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_envoyer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer le rapport et les commentaires à l'auteur")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((460, 450))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(6, 1, 10, 10)
        
        grid_sizer_base.Add(self.label_ligne_1, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        grid_sizer_base.Add(self.label_ligne_2, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        grid_sizer_base.Add(self.ctrl_fichiers, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_base.Add(self.label_ligne_3, 0, wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base.Add(self.ctrl_commentaires, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_envoyer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableRow(4)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Traduirelelogiciel")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)
    
    def GetCommentaires(self):
        return self.ctrl_commentaires.GetValue()

    def GetAdresseExpDefaut(self):
        """ Retourne les paramètres de l'adresse d'expéditeur par défaut """
        dictAdresse = {}
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur
        FROM adresses_mail WHERE defaut=1 ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return None
        IDadresse, adresse, motdepasse, smtp, port, defaut, auth, startTLS, utilisateur = listeDonnees[0]
        dictAdresse = {"adresse":adresse, "motdepasse":motdepasse, "smtp":smtp, "port":port, "auth":auth, "startTLS":startTLS, "utilisateur" : utilisateur}
        return dictAdresse

    def OnBoutonEnvoyer(self, event):  
        # Récupération des commentaires
        commentaires = self.ctrl_commentaires.GetValue() 
        
        # Récupération des fichiers à envoyer
        listeSelections = self.ctrl_fichiers.GetCheckedStrings() 
        listeFichiers = []
        for nomFichier in listeSelections :
            listeFichiers.append(UTILS_Fichiers.GetRepLang(u"%s.xlang" % nomFichier))

        if len(listeFichiers) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher un ou plusieurs fichiers de traduction personnalisés à envoyer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous l'envoi de ce message ?"), _(u"Envoi d'une traduction"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # Envoi de l'email
        resultat = self.EnvoyerEmail(commentaires, listeFichiers)
        if resultat == True :
            self.EndModal(wx.ID_OK)
    
    def EnvoyerEmail(self, commentaires="", listeFichiers=[]):
        """ Envoi d'un mail avec pièce jointe """
        import smtplib
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEBase import MIMEBase
        from email.MIMEText import MIMEText
        from email.MIMEImage import MIMEImage
        from email.MIMEAudio import MIMEAudio
        from email.Utils import COMMASPACE, formatdate
        from email import Encoders
        import mimetypes
        
        IDrapport = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        # texte
        if len(commentaires) == 0 :
            commentaires = _(u"Aucun")
        texteMail = _(u"<u>Envoi de %d fichier(s) de traduction pour Noethys :</u><br/><br/>%s<br/><br/><u>Commentaires :</u><br/><br/>%s") % (len(listeFichiers), ", ".join(listeFichiers), commentaires)
        
        # Destinataire
        listeDestinataires = ["noethys" + "@gmail.com",]
        
        # Expéditeur
        dictExp = self.GetAdresseExpDefaut() 
        if dictExp == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord saisir une adresse d'expéditeur depuis le menu Paramétrage > Adresses d'expédition d'Emails."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        adresseExpediteur = dictExp["adresse"]
        serveur = dictExp["smtp"]
        port = dictExp["port"]
        ssl = dictExp["ssl"]
        motdepasse = dictExp["motdepasse"]
        utilisateur = dictExp["utilisateur"]

        # Création du message
        msg = MIMEMultipart()
        msg['From'] = adresseExpediteur
        msg['To'] = ";".join(listeDestinataires)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = _(u"Envoi de fichiers de traduction Noethys")
            
        msg.attach( MIMEText(texteMail.encode('utf-8'), 'html', 'utf-8') )

        # Attache des pièces jointes
        for fichier in listeFichiers :
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
            nomFichier= os.path.basename(fichier)
            if type(nomFichier) == unicode :
                nomFichier = FonctionsPerso.Supprime_accent(nomFichier)
            part.add_header('Content-Disposition', 'attachment', filename=nomFichier)
            msg.attach(part)

        if ssl == False :
            # Envoi standard
            smtp = smtplib.SMTP(serveur)
        else:
            # Si identification SSL nécessaire :
            smtp = smtplib.SMTP(serveur, port, timeout=150)
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(utilisateur.encode('utf-8'), motdepasse.encode('utf-8'))
        
        try :
            smtp.sendmail(adresseExpediteur, listeDestinataires, msg.as_string())
            smtp.close()
        except Exception, err :
            dlg = wx.MessageDialog(self, _(u"Le message n'a pas pu être envoyé.\n\nErreur : %s !") % err, _(u"Envoi impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Message de confirmation
        dlg = wx.MessageDialog(self, _(u"Le message a été envoyé avec succès."), _(u"Traduction envoyée"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        return True



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
##    dialog_1 = DLG_Envoi(None)
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
