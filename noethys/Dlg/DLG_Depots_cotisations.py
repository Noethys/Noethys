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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

from Ctrl import CTRL_Bandeau
from Ol import OL_Depots_cotisations
from Ol import OL_Cotisations_depots

from Utils import UTILS_Divers
from Utils import UTILS_Titulaires
import GestionDB

try: import psyco; psyco.full()
except: pass


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


class Track(object):
    def __init__(self, parent, donnees):
        self.IDcotisation = donnees[0]
        self.IDfamille = donnees[1]
        self.IDindividu = donnees[2]
        self.IDtype_cotisation = donnees[3]
        self.IDunite_cotisation = donnees[4]
        self.date_saisie = DateEngEnDateDD(donnees[5])
        self.IDutilisateur = donnees[6]
        self.date_creation_carte = donnees[7]
        self.numero = donnees[8]
        self.IDdepot_cotisation = donnees[9]
        self.date_debut = DateEngEnDateDD(donnees[10])
        self.date_fin = DateEngEnDateDD(donnees[11])
        self.IDprestation = donnees[12]
        self.nomTypeCotisation = donnees[13]
        self.typeTypeCotisation = donnees[14]
        self.typeHasCarte = donnees[15]
        self.nomUniteCotisation = donnees[16]
        self.observations = donnees[17] 
        self.activites= donnees[18]
        if self.activites == None :
            self.activites = ""

        self.individu_nom = donnees[19]
        if self.individu_nom == None :
            self.individu_nom = ""
        self.individu_prenom = donnees[20]
        if self.individu_prenom == None :
            self.individu_prenom = ""

        # Activites
        texte = ""
        if len(self.activites) > 0 :
            listeTemp = []
            listeIDactivites = UTILS_Divers.ConvertChaineEnListe(self.activites)
            for IDactivite in listeIDactivites :
                if parent.dictActivites.has_key(IDactivite) :
                    nomActivite = parent.dictActivites[IDactivite]["nom"]
                    listeTemp.append(nomActivite)
            if len(listeTemp) > 0 :
                texte = ", ".join(listeTemp)
        self.activitesStr = texte

        if parent.titulaires.has_key(self.IDfamille) :
            self.nomTitulaires = parent.titulaires[self.IDfamille]["titulairesSansCivilite"]
        else:
            self.nomTitulaires = u""
        
        self.nomCotisation = u"%s - %s" % (self.nomTypeCotisation, self.nomUniteCotisation)

        # Individu
        self.individu = ""
        if self.IDindividu != None :
            self.individu = u"%s %s" % (self.individu_nom, self.individu_prenom)

        # Type
        if self.typeTypeCotisation == "famille" :
            self.typeStr = _(u"Cotisation familiale")
        else:
            self.typeStr = _(u"Cotisation individuelle")
        
        # Validité
        dateDuJour = datetime.date.today() 
        if dateDuJour >= self.date_debut and dateDuJour <= self.date_fin :
            self.valide = True
        else:
            self.valide = False
        
        # Dépôt
        if self.IDdepot_cotisation == None :
            self.depotStr = _(u"Non déposée")
        else:
            self.depotStr = _(u"Dépôt n°%d") % self.IDdepot_cotisation
        
        # Etat
        if self.IDdepot_cotisation == None or self.IDdepot_cotisation == 0 :
            self.inclus = False
        else:
            self.inclus = True
        

# ---------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Depots_cotisations", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez ici saisir, modifier ou supprimer des dépôts de cotisations. Ces dépôts sont utiles si, par exemple, votre cotisation se présente sous la forme d'une carte d'adhérent dont vous devez renvoyer un bordereau de création à une fédération ou une maison-mère. Vous pouvez ainsi savoir quels sont les bordereaux qui ont déjà été envoyés...")
        titre = _(u"Gestion des dépôts de cotisations")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Depot_cotisations.png")

        # Importation des activités
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY date_fin DESC;"""
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        self.dictActivites = {}
        for IDactivite, nom, abrege in listeTemp :
            dictTemp = {"IDactivite":IDactivite, "nom":nom, "abrege":abrege}
            self.dictActivites[IDactivite] = dictTemp

        # Cotisations disponibles
        self.staticbox_cotisations = wx.StaticBox(self, -1, _(u"Cotisations disponibles"))
        self.ctrl_cotisations = OL_Cotisations_depots.ListView(self, id=-1, inclus=False, selectionPossible=False, size=(-1, 150), style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_cotisations.SetMinSize((100, 100))
        self.MAJcotisations() 

        # Dépôts
        self.staticbox_depots = wx.StaticBox(self, -1, _(u"Dépôts de cotisations"))
        self.listviewAvecFooter = OL_Depots_cotisations.ListviewAvecFooter(self, kwargs={}) 
        self.ctrl_depots = self.listviewAvecFooter.GetListview()
        self.ctrl_depots.MAJ()
        self.ctrl_recherche = OL_Depots_cotisations.CTRL_Outils(self, listview=self.ctrl_depots)

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des dépôts de cotisations"))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un dépôt")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le dépôt sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le dépôt sélectionné dans la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste des dépôts affichés")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((950, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Règlements
        staticbox_cotisations = wx.StaticBoxSizer(self.staticbox_cotisations, wx.VERTICAL)
        grid_sizer_reglements = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_reglements.Add(self.ctrl_cotisations, 0, wx.EXPAND | wx.ALL, 0)
        
        grid_sizer_reglements.AddGrowableRow(0)
        grid_sizer_reglements.AddGrowableCol(0)
        staticbox_cotisations.Add(grid_sizer_reglements, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_cotisations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Dépôts
        staticbox_depots = wx.StaticBoxSizer(self.staticbox_depots, wx.VERTICAL)
        grid_sizer_depots = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.listviewAvecFooter, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_depots.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_depots.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_depots.AddGrowableRow(0)
        grid_sizer_depots.AddGrowableCol(0)
        staticbox_depots.Add(grid_sizer_depots, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_depots, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def MAJcotisations(self):
        self.titulaires = UTILS_Titulaires.GetTitulaires() 
        tracks = self.GetTracks()
        self.ctrl_cotisations.MAJ(tracks) 

    def GetTracks(self):
        """ Récupération des données """
        db = GestionDB.DB()
        req = """
        SELECT 
        cotisations.IDcotisation, 
        cotisations.IDfamille, cotisations.IDindividu, cotisations.IDtype_cotisation, cotisations.IDunite_cotisation,
        cotisations.date_saisie, cotisations.IDutilisateur, cotisations.date_creation_carte, cotisations.numero,
        cotisations.IDdepot_cotisation, cotisations.date_debut, cotisations.date_fin, cotisations.IDprestation, 
        types_cotisations.nom, types_cotisations.type, types_cotisations.carte,
        unites_cotisations.nom, cotisations.observations, cotisations.activites,
        individus.nom, individus.prenom
        FROM cotisations 
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN unites_cotisations ON unites_cotisations.IDunite_cotisation = cotisations.IDunite_cotisation
        LEFT JOIN individus ON individus.IDindividu = cotisations.IDindividu
        WHERE cotisations.IDdepot_cotisation IS NULL;
        """ 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeListeView = []
        for item in listeDonnees :
            track = Track(self, item)
            listeListeView.append(track)
        return listeListeView

    def Ajouter(self, event):
        self.ctrl_depots.Ajouter(None)
        
    def Modifier(self, event):
        self.ctrl_depots.Modifier(None)

    def Supprimer(self, event):
        self.ctrl_depots.Supprimer(None)
        
    def OnBoutonImprimer(self, event):               
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 20, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=20)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 30, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        self.ctrl_depots.Apercu(None)

    def Imprimer(self, event):
        self.ctrl_depots.Imprimer(None)
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Gestiondesdptsdecotisations")


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
