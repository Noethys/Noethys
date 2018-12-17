#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import time
import GestionDB
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Fichiers
from Utils import UTILS_Dialogs
from Ol import OL_Portail_demandes


class CTRL_Regroupement(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, id=-1)
        self.parent = parent

        self.listeValeurs = [
            (_(u"Aucun"), None),
            (_(u"Etat"), "etat"),
            (_(u"Catégorie"), "categorie"),
            (_(u"Famille"), "nom"),
            (_(u"Période"), "periode"),
            ]

        self.listeLabels = []
        self.listeCodes = []
        for label, code in self.listeValeurs :
            self.listeLabels.append(label)
            self.listeCodes.append(code)

        self.SetItems(self.listeLabels)
        # Defaut
        self.SetSelection(0)

    def GetCode(self):
        index = self.GetSelection()
        return self.listeCodes[index]

    def SetCode(self, code=""):
        index = 0
        for label, codeTemp in self.listeValeurs :
            if code == codeTemp :
                self.SetSelection(index)
            index +=1



class CTRL_Log(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, u"", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)

    def EcritLog(self, message=""):
        horodatage = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        if len(self.GetValue()) >0 :
            texte = u"\n"
        else :
            texte = u""
        try :
            texte += u"[%s] %s " % (horodatage, message)
        except :
            texte += u"[%s] %s " % (horodatage, str(message).decode("iso-8859-15"))
        self.AppendText(texte)

        # Surlignage des erreurs
        if "[ERREUR]" in texte :
            self.SetStyle(self.GetInsertionPoint()-len(texte), self.GetInsertionPoint()-1, wx.TextAttr("RED", "YELLOW"))

    def Enregistrer(self, event):
        standardPath = wx.StandardPaths.Get()
        wildcard = _(u"Tous les fichiers (*.*)|*.*")
        dlg = wx.FileDialog(None, message=_(u"Sélectionnez un répertoire et un nom de fichier"), defaultDir=standardPath.GetDocumentsDir(),  defaultFile="journal.txt", wildcard=wildcard, style=wx.FD_SAVE)
        nomFichier = None
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetPath()
        dlg.Destroy()
        if nomFichier == None :
            return
        fichier = open(nomFichier, "w")
        fichier.write(self.GetValue())
        fichier.close()



class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDfamille = IDfamille

        # Bandeau
        intro = _(u"Double-cliquez sur une ligne pour traiter la demande correspondante ou cliquez sur le bouton 'Commencer' pour traiter la première demande de la liste.")
        titre = _(u"Traitement des demandes")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Connecthys.png")

        # Demandes
        self.box_demandes_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Liste des demandes"))
        self.ctrl_demandes = OL_Portail_demandes.ListView(self, id=-1, IDfamille=self.IDfamille, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_demandes.SetMinSize((100, 100))

        self.bouton_traiter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        self.ctrl_recherche = OL_Portail_demandes.CTRL_Outils(self, listview=self.ctrl_demandes, afficherCocher=True)
        self.label_regroupement = wx.StaticText(self, -1, _(u"Regroupement :"))
        self.ctrl_regroupement = CTRL_Regroupement(self)
        self.check_cacher_traitees = wx.CheckBox(self, -1, _(u"Cacher les demandes traitées"))
        self.check_cacher_traitees.SetValue(True)

        # Journal
        self.box_journal_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Journal d'évènements"))
        self.ctrl_log = CTRL_Log(self)
        self.ctrl_log.SetMinSize((100, 80))
        self.ctrl_demandes.log = self.ctrl_log
        self.bouton_enregistrer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Sauvegarder.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Commencer"), cheminImage="Images/32x32/Loupe.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_demandes.Traiter, self.bouton_traiter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_demandes.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_demandes.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_demandes.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_demandes.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_CHOICE, self.OnChoixRegroupement, self.ctrl_regroupement)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCacherTraitees, self.check_cacher_traitees)
        self.Bind(wx.EVT_BUTTON, self.ctrl_log.Enregistrer, self.bouton_enregistrer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonFermer)

        self.VerifierVentilation()

        # Init
        self.ctrl_demandes.MAJ()


    def __set_properties(self):
        self.bouton_traiter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour traiter la demande sélectionnée dans la liste")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.ctrl_regroupement.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner une colonne de regroupement")))
        self.check_cacher_traitees.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour cacher les demandes déjà traitées")))
        self.bouton_enregistrer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour enregistrer le contenu du journal dans un fichier")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour commencer le traitement des demandes")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((900, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        # Demandes
        box_demandes = wx.StaticBoxSizer(self.box_demandes_staticbox, wx.VERTICAL)
        grid_sizer_demandes = wx.FlexGridSizer(2, 2, 5, 5)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_demandes.Add(self.ctrl_demandes, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_demandes = wx.FlexGridSizer(7, 1, 5, 5)
        grid_sizer_boutons_demandes.Add(self.bouton_traiter, 0, 0, 0)
        grid_sizer_boutons_demandes.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_demandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons_demandes.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons_demandes.Add((20, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_demandes.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_boutons_demandes.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_demandes.Add(grid_sizer_boutons_demandes, 1, wx.EXPAND, 0)
        
        grid_sizer_recherche = wx.FlexGridSizer(2, 6, 5, 5)
        grid_sizer_recherche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add( (10, 5), 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add(self.label_regroupement, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_recherche.Add(self.ctrl_regroupement, 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add( (10, 5), 0, wx.EXPAND, 0)
        grid_sizer_recherche.Add(self.check_cacher_traitees, 0, wx.EXPAND, 0)
        grid_sizer_recherche.AddGrowableCol(0)
        grid_sizer_demandes.Add(grid_sizer_recherche, 0, wx.EXPAND, 0)
        
        grid_sizer_demandes.AddGrowableRow(0)
        grid_sizer_demandes.AddGrowableCol(0)
        box_demandes.Add(grid_sizer_demandes, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_demandes, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Journal
        box_journal = wx.StaticBoxSizer(self.box_journal_staticbox, wx.VERTICAL)
        grid_sizer_journal = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_journal.Add(self.ctrl_log, 0, wx.EXPAND, 0)
        
        grid_sizer_boutons_journal = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_boutons_journal.Add(self.bouton_enregistrer, 0, 0, 0)
        grid_sizer_journal.Add(grid_sizer_boutons_journal, 1, wx.EXPAND, 0)
        grid_sizer_journal.AddGrowableRow(0)
        grid_sizer_journal.AddGrowableCol(0)
        box_journal.Add(grid_sizer_journal, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_journal, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        #grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

    def VerifierVentilation(self):
        from Dlg import DLG_Verification_ventilation
        tracks = DLG_Verification_ventilation.Verification()
        if len(tracks) > 0 :
            dlg = wx.MessageDialog(self, _(u"Un ou plusieurs règlements peuvent être ventilés.\n\nSouhaitez-vous le faire maintenant (conseillé) ?"), _(u"Ventilation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                dlg = DLG_Verification_ventilation.Dialog(self) #, tracks=tracks)
                dlg.ShowModal()
                dlg.Destroy()
            if reponse == wx.ID_CANCEL :
                return False
        return True

    def OnCheckCacherTraitees(self, event=None):
        self.ctrl_demandes.cacher_traitees = self.check_cacher_traitees.GetValue()
        self.ctrl_demandes.MAJ()
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)

    def OnChoixRegroupement(self, event):
        code = self.ctrl_regroupement.GetCode()
        self.ctrl_demandes.regroupement = code
        self.ctrl_demandes.MAJ()

    def OnBoutonOk(self, event):  
        self.ctrl_demandes.Commencer()




        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()