#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import OL_Etat_nomin_resultats


class Dialog(wx.Dialog):
    def __init__(self, parent, dictParametres={}):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        self.label_intro = wx.StaticText(self, -1, _(u"Voici la liste des résultats. Vous pouvez maintenant imprimer cette liste ou l'exporter au format texte ou Ms Excel."))
        
        self.ctrl_listview = OL_Etat_nomin_resultats.ListView(self, id=-1, dictParametres=dictParametres, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_texte = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Facture.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_excel = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        
        self.ctrl_recherche = OL_Etat_nomin_resultats.CTRL_Outils(self, listview=self.ctrl_listview)
        self.ctrl_totaux = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.ctrl_totaux.SetMinSize((-1, 80)) 
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTexte, self.bouton_export_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_export_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        self.ctrl_listview.MAJ() 

    def __set_properties(self):
        self.SetTitle(_(u"Aperçu des résultats"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour créer un aperçu de la liste"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.bouton_export_texte.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format texte"))
        self.bouton_export_excel.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format MS Excel"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((800, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_commandes = wx.FlexGridSizer(rows=8, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_contenu.Add(self.ctrl_listview, 1, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_export_texte, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_export_excel, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add( (5, 5), 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_totaux, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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

    def OnBoutonApercu(self, event): 
        self.ctrl_listview.Apercu(None)

    def OnBoutonImprimer(self, event): 
        self.ctrl_listview.Imprimer(None)

    def OnBoutonTexte(self, event): 
        self.ctrl_listview.ExportTexte(None)

    def OnBoutonExcel(self, event): 
        self.ctrl_listview.ExportExcel(None)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Etatnominatif")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import datetime
    import GestionDB
    # Paramètres de tests
    IDprofil = 3
    listeActivites = [1, 2, 3, 4]
    dateMin = datetime.date(2012, 1, 1)
    dateMax = datetime.date(2012, 12, 31)
    
    # Récupération de tous les champs disponibles
    import OL_Etat_nomin_champs
    champs = OL_Etat_nomin_champs.Champs(listeActivites=listeActivites, dateMin=dateMin, dateMax=dateMax)
    dictChamps = champs.GetDictChamps() 
    listeChampsDispo = champs.GetChamps() 
    
    # Récupération des champs sélectionnés du profil
    DB = GestionDB.DB()
    req = """SELECT IDselection, IDprofil, code, ordre
    FROM etat_nomin_selections
    WHERE IDprofil=%d
    ORDER BY ordre
    ;""" % IDprofil
    DB.ExecuterReq(req)
    listeSelectionChamps = DB.ResultatReq()     
    DB.Close() 
    listeChamps = []
    import OL_Etat_nomin_selections
    for IDselection, IDprofil, code, ordre in listeSelectionChamps :
        if dictChamps.has_key(code) :
            # Champ disponible
            trackInfo = dictChamps[code]
            dictTemp = {"IDselection":IDselection, "IDprofil":IDprofil, "code":code, "ordre":ordre, "label":trackInfo.label, "type":trackInfo.type, "categorie":trackInfo.categorie, "formule":trackInfo.formule, "titre":trackInfo.titre, "largeur":trackInfo.largeur}
        else :
            # Champ indisponible
            dictTemp = {"IDselection":IDselection, "IDprofil":IDprofil, "code":code, "ordre":ordre, "label":_(u"Non disponible"), "type":None, "categorie":None, "titre":None, "formule":None}
        listeChamps.append(OL_Etat_nomin_selections.Track(dictTemp))
        
    # Création des paramètres
    dictParametres = {
        "caisses" : [1, 2],
        "champs" : listeChamps,
        "champsDispo" : listeChampsDispo,
        "groupes" : [1, 2, 6, 7, 8, 9, 5, 3, 4, 10],
        "age" : None,
        "date_debut" : dateMin,
        "date_fin" : dateMax,
        "activites" : [1, 2, 3, 4],
        "qf" : None,
        "categories" : [6, 5, 1, 3, 2, 4],
        }

    dialog_1 = Dialog(None, dictParametres=dictParametres)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
