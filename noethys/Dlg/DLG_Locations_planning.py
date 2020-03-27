#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
import GestionDB
import datetime
import random
import six
from Outils import wxScheduler
from Ctrl import CTRL_Agenda




class CTRL_Produit(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, style=wx.TE_READONLY)
        self.parent = parent
        self.IDproduit = None
        self.IDcategorie = None

    def SetIDproduit(self, IDproduit=None):
        self.IDproduit = IDproduit

        # Recherche des caractéristiques du produit
        db = GestionDB.DB()
        req = """SELECT produits.nom, produits.IDcategorie, produits.observations, produits.image, produits_categories.nom
        FROM produits 
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE IDproduit=%d;""" % self.IDproduit
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 :
            nomProduit, IDcategorie, observations, image, nomCategorie = listeDonnees[0]
            label = u"%s (%s)" % (nomProduit, nomCategorie)
        else :
            IDcategorie = None
            label = ""
            observations = ""
            image = None

        # Nom
        self.SetValue(label)

        # Mémorise IDcategorie (sert pour mesure de la distance)
        self.IDcategorie = IDcategorie

    def GetIDproduit(self):
        return self.IDproduit

    def GetIDcategorie(self):
        return self.IDcategorie




class Track(object):
    def __init__(self, donnees=None):
        self.IDlocation = donnees[0]
        self.IDfamille = donnees[1]
        self.IDproduit = donnees[2]
        self.observations = donnees[3]
        self.date_debut = donnees[4]
        self.date_fin = donnees[5]
        self.quantite = donnees[6]
        self.nomProduit = donnees[7]
        self.nomCategorie = donnees[8]

        if self.quantite == None :
            self.quantite = 1

        # Période
        if isinstance(self.date_debut, str) or isinstance(self.date_debut, six.text_type) :
            self.date_debut = datetime.datetime.strptime(self.date_debut, "%Y-%m-%d %H:%M:%S")

        if isinstance(self.date_fin, str) or isinstance(self.date_fin, six.text_type) :
            self.date_fin = datetime.datetime.strptime(self.date_fin, "%Y-%m-%d %H:%M:%S")



class CTRL_Planning(CTRL_Agenda.CTRL_Planning):
    def __init__(self, parent):
        self.IDproduit = None
        CTRL_Agenda.CTRL_Planning.__init__(self, parent)

        # Règle l'affichage sur SEMAINE + VERTICAL
        self.barre_outils.SetPeriode("semaine")


    def OnLeftClick(self, event):
        schedule = event.schedule
        date = event.date
        self.scheduleMove = schedule
    
    def OnLeftUp(self, event):
        self.scheduleMove = None
        
    def OnMotion(self, event):
        schedule = event.schedule
        date = event.date
        dateExacte = event.dateExacte
        
        if self.scheduleMove != None :
            self.scheduleMove.end = dateExacte
            self.scheduleMove.description = "%s - %s" % (self.scheduleMove.start.Format("%H:%M"), self.scheduleMove.end.Format("%H:%M"))
            self.ctrl_planning.RefreshSchedule(self.scheduleMove)
            
        
    def OnClickDroit(self, event):
        """ Menu contextuel """
        schedule = event.schedule
        date = event.date
        
        def Ajouter(evt):
            self.Ajouter(date)
            
        def Modifier(evt):
            self.Modifier(schedule)
            
        def Supprimer(evt):
            self.Supprimer(schedule)
        
        menuPop = UTILS_Adaptations.Menu()
        
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, Ajouter, id=10)

        if schedule != None:

            item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, Modifier, id=20)

            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, Supprimer, id=30)
            
        self.PopupMenu(menuPop)
        menuPop.Destroy()
        
    def OnDoubleClick(self, event):
        """ Sur un double-clic """
        schedule = event.schedule
        if schedule == None :
            self.Ajouter(date=event.date)
        else :
            self.Modifier(schedule=schedule)
    
    def Ajouter(self, date=None):
        """ Création d'un évènement """
        if self.IDproduit == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un produit !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Création d'une location
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self, IDfamille=None, IDproduit=self.IDproduit)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()

    def Modifier(self, schedule=None):
        """ Modification d'un schedule """
        track = schedule.track
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self, IDlocation=track.IDlocation, IDfamille=track.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_planning.Freeze()
            self.MAJ()
            self.ctrl_planning.Thaw()
        dlg.Destroy()

    def Supprimer(self, schedule=None):
        """ Suppression d'un schedule """
        from Ol.OL_Locations import Supprimer_location
        resultat = Supprimer_location(self, IDlocation=schedule.track.IDlocation)
        if resultat == True :
            self.ctrl_planning.Delete(schedule)
    
    def MAJ(self):
        self.ctrl_planning.DeleteAll()
        self.Importation()

    def SetIDproduit(self, IDproduit):
        self.IDproduit = IDproduit
        self.MAJ()

    def Importation(self):
        """ Importation des events depuis la base de données """
        if self.IDproduit == None :
            IDproduit = 0
        else :
            IDproduit = self.IDproduit

        DB = GestionDB.DB()
        req = """SELECT locations.IDlocation, locations.IDfamille, locations.IDproduit, 
        locations.observations, locations.date_debut, locations.date_fin, locations.quantite,
        produits.nom, 
        produits_categories.nom
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE locations.IDproduit=%d;""" % IDproduit
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeSchedules = []
        index = 0
        for donnees in listeDonnees :
            # Création du track
            track = Track(donnees)

            # Création du schedule
            schedule = wxScheduler.wxSchedule()
            schedule.index = index
            self.RemplitSchedule(track, schedule)
            listeSchedules.append(schedule)
            index += 1

        self.ctrl_planning.Add(listeSchedules)

    def ModificationSchedule(self, dictDonnees={}, schedule=None):
        self.RemplitSchedule(dictDonnees, schedule)
    
    def RemplitSchedule(self, track, schedule=None):
        schedule.track = track

        # Icone
        #schedule.icons = [wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s.png" % dictDonnees["image"]), wx.BITMAP_TYPE_ANY),]
        
        # Date et heure de début
        schedule.start = CTRL_Agenda.ConvertDateDTenWX2(track.date_debut)
        
        # Date et heure de fin
        schedule.end = CTRL_Agenda.ConvertDateDTenWX2(track.date_fin)
        
        # texte
        schedule.description = track.nomProduit

        # Couleur
        schedule.color = self.CreationCouleur(schedule.index)

##        schedule.complete = 0.50
##        schedule.foreground = wx.Color(255, 0, 0)
##        # schedule.foreground.font = wx.Font()
##        # schedule.color = wx.Color(200, 200, 200)
        
    def CreationCouleur(self, index=0):
        listeCouleurs = [
            (77, 133, 255), (155, 255, 105), (255, 148, 82), (255, 133, 255), (149, 131, 255),
            (92, 255, 230), (156, 255, 57), (255, 69, 168), (218, 187, 255), (49, 255, 114),
            (18, 144, 255), (150, 67, 37), (150, 40, 142), (43, 52, 150), (34, 150, 144),
            (30, 150, 63), (132, 150, 43), (93, 35, 87), (79, 66, 93), (0, 93, 31),
            ]
        if index < len(listeCouleurs) -1 :
            return wx.Colour(*listeCouleurs[index])
        else :
            return wx.Colour(random.randint(0, 250), random.randint(0, 250), random.randint(0, 250))

        
# --------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDproduit=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Sélectionnez un produit pour afficher son planning de locations. Faites un clic droit sur le planning pour accéder aux fonctions d'ajout, de modification et de suppression.")
        titre = _(u"Planning des locations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier.png")

        self.label_produit = wx.StaticText(self, -1, _(u"Produit :"))
        self.ctrl_produit = CTRL_Produit(self)
        self.ctrl_produit.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial'))
        self.bouton_produit = wx.Button(self, -1, _(u"Sélectionner"))

        # Planning
        self.ctrl_planning = CTRL_Planning(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
##        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonProduit, self.bouton_produit)

        if IDproduit != None :
            self.ctrl_produit.SetIDproduit(IDproduit)
            self.ctrl_planning.SetIDproduit(IDproduit)


    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_produit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner un produit")))
        self.SetMinSize((950, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Produit
        grid_sizer_produit = wx.FlexGridSizer(1, 3, 5, 5)
        grid_sizer_produit.Add(self.label_produit, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_produit.Add(self.ctrl_produit, 0, wx.EXPAND, 0)
        grid_sizer_produit.Add(self.bouton_produit, 0, 0, 0)
        grid_sizer_produit.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_produit, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Planning
        grid_sizer_base.Add(self.ctrl_planning, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Planningdeslocations")

    def OnBoutonProduit(self, event):
        from Dlg import DLG_Selection_produit
        dlg = DLG_Selection_produit.Dialog(self, IDproduit=self.ctrl_produit.GetIDproduit(), coche_uniquement_disponibles=False)
        if dlg.ShowModal() == wx.ID_OK:
            IDproduit = dlg.GetIDproduit()
            self.ctrl_produit.SetIDproduit(IDproduit)
            self.ctrl_planning.SetIDproduit(IDproduit)
        dlg.Destroy()



        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
