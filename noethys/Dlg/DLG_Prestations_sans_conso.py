#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import GestionDB
import datetime
from Ctrl import CTRL_Bandeau
import wx.lib.agw.hypertreelist as HTL
from Utils import UTILS_Titulaires
from Utils import UTILS_Utilisateurs


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
        
def PeriodeComplete(mois, annee):
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete

# ------------------------------------------------------------------------------------------------------------------------

class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
                
        # Création des colonnes
        listeColonnes = [
            ( _(u"Label/Famille"), 400, wx.ALIGN_LEFT),
            ( _(u"Date"), 90, wx.ALIGN_LEFT),
            ( _(u"Individu"), 180, wx.ALIGN_LEFT),
            ( _(u"IDprestation"), 90, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | TR_COLUMN_LINES | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds 
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClick)
        
    def Importation(self):
        # Importation des prestations sans consommations
        DB = GestionDB.DB()
        
        # Récupération des prestations
        req = """SELECT IDprestation, label, date, IDfamille, prestations.IDindividu,
        individus.nom, individus.prenom
        FROM prestations
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        WHERE categorie='consommation' AND IDfacture IS NULL
        ORDER BY prestations.IDfamille, prestations.IDindividu, date
        ;""" 
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        
        # Récupération des consommations
        req = """SELECT IDconso, IDprestation FROM consommations;""" 
        DB.ExecuterReq(req)
        listeConsommations = DB.ResultatReq()
        DB.Close()
        
        # Analyse
        dictPrestations = {}
        for IDconso, IDprestation in listeConsommations :
            if (IDprestation in dictPrestations) == False :
                dictPrestations[IDprestation] = []
            dictPrestations[IDprestation].append(IDconso)
        
        dictResultats = {}
        listeDebug = []
        for IDprestation, label, date, IDfamille, IDindividu, nom, prenom in listePrestations :
            if (IDprestation in dictPrestations) == False :
                # Si aucune prestation :
                if (label in dictResultats) == False :
                    dictResultats[label] = []
                if nom != None and prenom != None :
                    nomIndividu = u"%s %s" % (nom, prenom)
                else :
                    nomIndividu = u""
                dictTemp = {"IDprestation":IDprestation, "date":date, "IDfamille":IDfamille, "IDindividu":IDindividu, "nomIndividu":nomIndividu}
                dictResultats[label].append(dictTemp)
                
                listeDebug.append((IDprestation, date, label, IDfamille, IDindividu, nomIndividu))
                
        listeDonnees = []
        for label, listePrestationsTemp in dictResultats.items() :
            texte = _(u"%s (%d prestations)") % (label, len(listePrestationsTemp))
            listeDonnees.append((texte, label, listePrestationsTemp))
        listeDonnees.sort() 
        
        # Pour debuggage :
##        listeDebug.sort() 
##        for IDprestation, date, label, IDfamille, IDindividu, nomIndividu in listeDebug :
##            print (IDprestation, "-->", date, label, IDfamille, IDindividu, nomIndividu)
##        print "Soit %d prestations au total." % len(listeDebug)
        
        return listeDonnees
    
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()

    def Remplissage(self):
        listeResultats = self.Importation() 
        
        dictTitulaires = UTILS_Titulaires.GetTitulaires()
                
        # Remplissage
        for texte, label, listePrestationsTemp in listeResultats :
            niveauLabel = self.AppendItem(self.root, texte)
            self.SetPyData(niveauLabel, None)
            self.SetItemBold(niveauLabel, True)
                        
            for dictTemp in listePrestationsTemp :
                date = dictTemp["date"]
                IDfamille = dictTemp["IDfamille"]
                nomIndividu = dictTemp["nomIndividu"]
                IDprestation = dictTemp["IDprestation"]
                nomsTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
                
                niveauPrestation = self.AppendItem(niveauLabel, nomsTitulaires)
                self.SetPyData(niveauPrestation, IDfamille)
                self.SetItemText(niveauPrestation, DateEngFr(date), 1)
                self.SetItemText(niveauPrestation, nomIndividu, 2)
                self.SetItemText(niveauPrestation, str(IDprestation), 3)
                
##        self.ExpandAllChildren(self.root)
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Double-cliquez sur le nom de l'individu pour accéder à sa fiche famille !"), _(u"Astuce"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return            
    
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnDoubleClick, id=10)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def OnDoubleClick(self, event):
        item = self.GetSelection()
        IDfamille = self.GetMainWindow().GetItemPyData(item)
        if IDfamille != None :
            self.OuvrirFicheFamille(IDfamille)
        else:
            event.Skip()

    def OuvrirFicheFamille(self, IDfamille=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(None, IDfamille=IDfamille)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ() 
        
    
# -----------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter la liste des prestations qui ne possèdent pas de consommations associées. Double-cliquez sur une ligne pour ouvrir la fiche famille correspondante.")
        titre = _(u"Prestations sans consommations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Configuration2.png")
        
        self.ctrl_liste = CTRL(self)
        self.ctrl_liste.MAJ() 
        
        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_ouvrir_fiche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir la fiche famille sélectionnée dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((860, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_droit = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_liste, 0, wx.EXPAND, 0)
##        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
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
        
    def OuvrirFiche(self, event):
        self.ctrl_liste.OnDoubleClick(None)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
