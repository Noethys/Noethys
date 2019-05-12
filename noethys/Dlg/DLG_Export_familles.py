#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import os
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Fichiers
from Utils import UTILS_Export_familles
import FonctionsPerso
import datetime



class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Export_familles", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDfamille = IDfamille

        if self.IDfamille == None :
            texte = _(u"des familles")
        else :
            texte = _(u"de la famille")

        # Bandeau
        intro = _(u"Vous pouvez ici exporter les données %s au format XML. Vous pouvez enregistrer le fichier généré dans le répertoire souhaité ou l'envoyer par email.") % texte
        titre = _(u"Exporter les données %s") % texte
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Document_export.png")

        self.bouton_enregistrer = CTRL_Bouton_image.CTRL(self, texte=_(u"Enregistrer sous"), cheminImage="Images/48x48/Sauvegarder.png", tailleImage=(48, 48), margesImage=(40, 20, 40, 0), positionImage=wx.TOP, margesTexte=(10, 10))
        self.bouton_enregistrer.SetToolTip(wx.ToolTip(_(u"Enregistrer le fichier XML")))

        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer par Email"), cheminImage="Images/48x48/Email.png", tailleImage=(48, 48), margesImage=(40, 20, 40, 0), positionImage=wx.TOP, margesTexte=(10, 10))
        self.bouton_email.SetToolTip(wx.ToolTip(_(u"Envoyer le fichier XML par Email")))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnregistrer, self.bouton_enregistrer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Annuler")))
        self.SetMinSize((430, 300))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.bouton_enregistrer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_contenu.Add(self.bouton_email, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def GetNomFichier(self):
        if self.IDfamille == None :
            IDfamilleTxt = "s"
        else :
            IDfamilleTxt = "_id%d" % self.IDfamille
        nomFichier = "Export_famille%s_%s.xml" % (IDfamilleTxt, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        return nomFichier

    def GenerationFichier(self, cheminFichier=""):
        """ Génération du fichier XML """
        export = UTILS_Export_familles.Export(IDfamille=self.IDfamille)
        export.Enregistrer(cheminFichier)

    def OnBoutonEnregistrer(self, event):
        nomFichier = self.GetNomFichier()

        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier XML (*.xml)|*.xml| Tous les fichiers (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut,
            defaultFile = nomFichier,
            wildcard = wildcard,
            style = wx.FD_SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_NO :
                return False

        # Génération du fichier XML
        self.GenerationFichier(cheminFichier)

        # Propose l'ouverture du fichier XML
        txtMessage = _(u"Le fichier XML a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)

    def OnBoutonEmail(self, event):
        nomFichier = self.GetNomFichier()

        # Définit le chemin de stockage du fichier
        cheminFichier = UTILS_Fichiers.GetRepTemp(fichier=nomFichier)

        # Génération du fichier XML
        self.GenerationFichier(cheminFichier)

        # Ouverture de l'envoi d'email
        listeAdresses = []
        if self.IDfamille != None :
            from Utils import UTILS_Envoi_email
            listeAdresses = UTILS_Envoi_email.GetAdresseFamille(self.IDfamille)
            if listeAdresses == False or len(listeAdresses) == 0 :
                return

        from Dlg import DLG_Mailer
        dlg = DLG_Mailer.Dialog(None)
        # dlg.ChargerModeleDefaut()

        # Chargement de l'adresse de la famille
        if len(listeAdresses) > 0 :
            listeDonnees = []
            for adresse in listeAdresses:
                listeDonnees.append({"adresse": adresse, "pieces": [], "champs": {}, })
            dlg.SetDonnees(listeDonnees, modificationAutorisee=True)

        # Ajout du fichier en pièce jointe
        dlg.SetPiecesJointes([cheminFichier,])
        dlg.ShowModal()
        dlg.Destroy()



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
