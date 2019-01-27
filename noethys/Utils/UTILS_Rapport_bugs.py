#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import sys
import platform
import traceback
import datetime
import GestionDB
import webbrowser
import wx.lib.dialogs
import UTILS_Config
import UTILS_Customize
import UTILS_Fichiers



def Activer_rapport_erreurs(version=""):
    def my_excepthook(exctype, value, tb):
        dateDuJour = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        systeme = u"%s %s %s %s" % (sys.platform, platform.system(), platform.release(), platform.machine())
        infos = u"## %s | %s | wxPython %s | %s ##" % (dateDuJour, version, wx.version(), systeme)
        bug = ''.join(traceback.format_exception(exctype, value, tb))

        # Affichage dans le journal
        print bug

        # Affichage dans une DLG
        try :
            if UTILS_Config.GetParametre("rapports_bugs", True) == False :
                return
        except :
            pass
        try :
            texte = u"%s\n%s" % (infos, bug.decode("iso-8859-15"))
            dlg = DLG_Rapport(None, texte)
            dlg.ShowModal()
            dlg.Destroy()
        except :
            pass

    sys.excepthook = my_excepthook



# ------------------------------------------- BOITE DE DIALOGUE ----------------------------------------------------------------------------------------

class DLG_Rapport(wx.Dialog):
    def __init__(self, parent, texte=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        self.ctrl_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(Chemins.GetStaticPath(u"Images/48x48/Erreur.png"), wx.BITMAP_TYPE_ANY))
        self.label_ligne_1 = wx.StaticText(self, wx.ID_ANY, _(u"Noethys a rencontré un problème !"))
        self.label_ligne_2 = wx.StaticText(self, wx.ID_ANY, _(u"Le rapport d'erreur ci-dessous peut servir à la résolution de ce bug.\nMerci de bien vouloir le communiquer à l'auteur par Email ou depuis le forum."))
        self.ctrl_rapport = wx.TextCtrl(self, wx.ID_ANY, texte, style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer à l'auteur"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_forum = CTRL_Bouton_image.CTRL(self, texte=_(u"Accéder au forum"), cheminImage="Images/32x32/Forum.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoyer, self.bouton_envoyer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonForum, self.bouton_forum)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

        # Envoi dans le presse-papiers
        clipdata = wx.TextDataObject()
        clipdata.SetText(texte)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

        self.bouton_fermer.SetFocus()


    def __set_properties(self):
        self.SetTitle(_(u"Rapport d'erreurs"))
        self.label_ligne_1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_rapport.SetToolTip(wx.ToolTip(_(u"Ce rapport d'erreur a été copié dans le presse-papiers")))
        self.bouton_envoyer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer ce rapport d'erreur à l'auteur par Email")))
        self.bouton_forum.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir votre navigateur internet et accéder au forum de Noethys. Vous pourrez ainsi signaler ce bug dans la rubrique dédiée.")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((650, 450))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        grid_sizer_bas = wx.FlexGridSizer(1, 5, 10, 10)
        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)
        grid_sizer_droit = wx.FlexGridSizer(3, 1, 10, 10)
        grid_sizer_haut.Add(self.ctrl_image, 0, wx.ALL, 10)
        grid_sizer_droit.Add(self.label_ligne_1, 0, 0, 0)
        grid_sizer_droit.Add(self.label_ligne_2, 0, 0, 0)
        grid_sizer_droit.Add(self.ctrl_rapport, 0, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableRow(2)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_droit, 1, wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        grid_sizer_bas.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.bouton_envoyer, 0, 0, 0)
        grid_sizer_bas.Add(self.bouton_forum, 0, 0, 0)
        grid_sizer_bas.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonFermer(self, event):  
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonEnvoyer(self, event):
        # DLG Commentaires
        texteRapport = self.ctrl_rapport.GetValue()
        dlg = DLG_Envoi(self, texteRapport)
        reponse = dlg.ShowModal()
        commentaires = dlg.GetCommentaires()
        joindre_journal = dlg.GetJoindreJournal()
        dlg.Destroy()

        if reponse == wx.ID_OK :
            self.Envoyer_mail(commentaires, joindre_journal)

    def OnBoutonForum(self, event):
        dlg = wx.MessageDialog(self, _(u"Noethys va ouvrir votre navigateur internet à la page du forum de Noethys. Vous n'aurez plus qu'à vous connecter avec vos identifiants Noethys et poster un nouveau message dans la rubrique dédiée aux bugs."), _(u"Forum Noethys"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        webbrowser.open("https://www.noethys.com/index.php/forum-34/6-signaler-un-bug")

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
        IDadresse, adresse, motdepasse, smtp, port, defaut, connexionAuthentifiee, startTLS, utilisateur = listeDonnees[0]
        dictAdresse = {"adresse":adresse, "motdepasse":motdepasse, "smtp":smtp, "port":port, "auth":connexionAuthentifiee, "startTLS":startTLS, "utilisateur" : utilisateur}
        return dictAdresse

    def Envoyer_mail(self, commentaires="", joindre_journal=False):
        """ Envoi d'un mail avec pièce jointe """
        from Utils import UTILS_Envoi_email

        # Expéditeur
        dictExp = self.GetAdresseExpDefaut()
        if dictExp == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord saisir une adresse d'expéditeur depuis le menu Paramétrage > Adresses d'expédition d'Emails. Sinon, postez votre rapport de bug dans le forum de Noethys."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        moteur = dictExp["moteur"]
        adresseExpediteur = dictExp["adresse"]
        serveur = dictExp["smtp"]
        port = dictExp["port"]
        auth = dictExp["auth"]
        startTLS = dictExp["startTLS"]
        motdepasse = dictExp["motdepasse"]
        utilisateur = dictExp["utilisateur"]
        parametres = dictExp["parametres"]

        if adresseExpediteur == None :
            dlg = wx.MessageDialog(self, _(u"L'adresse d'expédition ne semble pas valide. Veuillez la vérifier."), _(u"Envoi impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Attacher le journal d'erreurs
        fichiers = []
        if joindre_journal == True :
            customize = UTILS_Customize.Customize()
            nom_journal = UTILS_Fichiers.GetRepUtilisateur(customize.GetValeur("journal", "nom", "journal.log"))
            fichiers.append(nom_journal)

        # Préparation du message
        IDrapport = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        texteRapport = self.ctrl_rapport.GetValue().replace("\n","<br/>")
        if len(commentaires) == 0 :
            commentaires = _(u"Aucun")
        texte_html = _(u"<u>Rapport de bug %s :</u><br/><br/>%s<br/><u>Commentaires :</u><br/><br/>%s") % (IDrapport, texteRapport, commentaires)

        sujet = _(u"Rapport de bug Noethys n°%s") % IDrapport
        message = UTILS_Envoi_email.Message(destinataires=["noe" + "thys" + "@" + "gm" + "ail" + ".com",], sujet=sujet, texte_html=texte_html, fichiers=fichiers)

        # Envoi du mail
        try :
            messagerie = UTILS_Envoi_email.Messagerie(backend=moteur, hote=serveur, port=port, utilisateur=utilisateur, motdepasse=motdepasse, email_exp=adresseExpediteur, use_tls=startTLS, parametres=parametres)
            messagerie.Connecter()
            messagerie.Envoyer(message)
            messagerie.Fermer()
        except Exception, err :
            dlg = wx.MessageDialog(self, _(u"Le message n'a pas pu être envoyé. Merci de poster votre rapport de bug sur le forum de Noethys.\n\nErreur : %s !") % err, _(u"Envoi impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Message de confirmation
        dlg = wx.MessageDialog(self, _(u"Le rapport d'erreur a été envoyé avec succès."), _(u"Rapport envoyé"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        return True


# -------------------------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Envoi(wx.Dialog):
    def __init__(self, parent, texteRapport=u""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.texteRapport = texteRapport

        self.label_ligne_1 = wx.StaticText(self, wx.ID_ANY, _(u"Le rapport est prêt à être envoyé..."))
        self.label_ligne_2 = wx.StaticText(self, wx.ID_ANY, _(u"Vous pouvez ajouter ci-dessous des commentaires, remarques ou compléments d'informations\navant de l'envoyer à l'auteur. Il est également possible de joindre le rapport complet."))

        self.ctrl_commentaires = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE)

        self.check_journal = wx.CheckBox(self, -1, _(u"Joindre le journal des erreurs (Recommandé)"))

        self.bouton_apercu = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer l'Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoyer, self.bouton_envoyer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Envoyer le rapport à l'auteur"))
        self.label_ligne_1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_commentaires.SetToolTip(wx.ToolTip(_(u"Vous pouvez saisir des commentaires ici")))
        self.check_journal.SetToolTip(wx.ToolTip(_(u"Pour faciliter la résolution du bug, vous pouvez joindre votre rapport d'erreurs")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser le contenu du message qui sera envoyé à l'auteur")))
        self.bouton_envoyer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer le rapport et les commentaires à l'auteur")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((550, 350))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(5, 1, 10, 10)
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_base.Add(self.label_ligne_1, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        grid_sizer_base.Add(self.label_ligne_2, 0, wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base.Add(self.ctrl_commentaires, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_base.Add(self.check_journal, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_envoyer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonApercu(self, event):
        """ Visualisation du message à envoyer """
        commentaires = self.ctrl_commentaires.GetValue()
        if len(commentaires) == 0 :
            commentaires = _(u"Aucun")
        message = _(u"Rapport : \n\n%s\nCommentaires : \n\n%s") % (self.texteRapport, commentaires)
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, message, _(u"Visualisation du contenu du message"))
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonEnvoyer(self, event):
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def GetCommentaires(self):
        return self.ctrl_commentaires.GetValue()

    def GetJoindreJournal(self):
        return self.check_journal.GetValue()


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = DLG_Rapport(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
