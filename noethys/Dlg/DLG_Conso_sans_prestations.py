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
            ( _(u"Individu/Date"), 230, wx.ALIGN_LEFT),
            ( _(u"Unité"), 170, wx.ALIGN_LEFT),
            ( _(u"Activité"), 170, wx.ALIGN_LEFT),
            ( _(u"Etat"), 90, wx.ALIGN_LEFT),
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
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_VARIABLE_ROW_HEIGHT | TR_COLUMN_LINES | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds 
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClick)
        
    def Importation(self):
        # Importation des consommations sans prestations
        DB = GestionDB.DB()
        req = """
        SELECT IDconso, consommations.IDindividu, individus.nom, individus.prenom, 
        consommations.IDinscription, consommations.IDactivite, consommations.date, 
        consommations.IDunite, consommations.etat, unites.nom, 
        comptes_payeurs.IDfamille, activites.nom
        FROM consommations
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        WHERE IDprestation IS NULL AND forfait IS NULL
        AND consommations.etat <> 'attente' AND consommations.etat NOT IN ('absentj', 'refus')
        ORDER BY date
        ;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        dictResultats = {}
        for IDconso, IDindividu, nom, prenom, IDinscription, IDactivite, date, IDunite, etat, nomUnite, IDfamille, nomActivite in listeDonnees :
            date = DateEngEnDateDD(date)
            dictTemp = {
                "IDconso" : IDconso, "IDinscription" : IDinscription, "IDactivite" : IDactivite, "date" : date,
                "IDunite" : IDunite, "nomUnite" : nomUnite, "IDfamille" : IDfamille, "IDindividu" : IDindividu,
                "nomActivite" : nomActivite, "etat" : etat,
                }
            if (IDindividu in dictResultats) == False :
                dictResultats[IDindividu] = {"nom":nom, "prenom":prenom, "listeFamilles":[], "listeConso":[]}
            if IDfamille not in dictResultats[IDindividu]["listeFamilles"] :
                dictResultats[IDindividu]["listeFamilles"].append(IDfamille)
            dictResultats[IDindividu]["listeConso"].append(dictTemp)
            
        return dictResultats
    
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()

    def Remplissage(self):
        dictResultats = self.Importation() 
                
        # Tri des individus par ordre alphabétique
        listeNoms = []
        for IDindividu, dictIndividu in dictResultats.items() :
            nomCompletIndividu = u"%s %s" % (dictIndividu["nom"], dictIndividu["prenom"])
            listeNoms.append((nomCompletIndividu, IDindividu, dictIndividu))
        listeNoms.sort() 
        
        # Remplissage
        for nomCompletIndividu, IDindividu, dictIndividu in listeNoms :
            niveauIndividu = self.AppendItem(self.root, nomCompletIndividu)
            self.SetPyData(niveauIndividu, dictIndividu)
            self.SetItemBold(niveauIndividu, True)
                        
            for dictConso in dictIndividu["listeConso"] :
                niveauConso = self.AppendItem(niveauIndividu, DateComplete(dictConso["date"]))
                self.SetPyData(niveauConso, None)
                self.SetItemText(niveauConso, dictConso["nomUnite"], 1)
                self.SetItemText(niveauConso, dictConso["nomActivite"], 2)
                self.SetItemText(niveauConso, dictConso["etat"], 3)
                
        self.ExpandAllChildren(self.root)
        
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
        dictItem = self.GetMainWindow().GetItemPyData(item)
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Double-cliquez sur le nom de l'individu pour accéder à sa fiche famille !"), _(u"Astuce"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        listeFamilles = dictItem["listeFamilles"]
        if len(listeFamilles) == 1 :
            # Si individu rattaché à une seule famille
            self.OuvrirFicheFamille(listeFamilles[0])
        else:
            # Si individu rattaché à plusieurs familles
            dictTitulaires = UTILS_Titulaires.GetTitulaires(listeFamilles)
            listeNoms = []
            for IDfamille in listeFamilles :
                nomsTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
                listeNoms.append(nomsTitulaires)
                
            dlg = wx.SingleChoiceDialog(self, _(u"Cet individu est rattaché à %d familles.\nLa fiche de quelle famille souhaitez-vous ouvrir ?") % len(listeFamilles), _(u"Rattachements multiples"), listeNoms, wx.CHOICEDLG_STYLE)
            IDfamilleSelection = None
            if dlg.ShowModal() == wx.ID_OK:
                indexSelection = dlg.GetSelection()
                IDfamille = listeFamilles[indexSelection]
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            self.OuvrirFicheFamille(IDfamille)

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
        
        intro = _(u"Vous pouvez ici consulter la liste des consommations qui ne possèdent pas de prestations associées. Il s'agit donc de consommations 'gratuites' qui n'ont pas été facturées. Double-cliquez sur une ligne pour ouvrir la fiche famille correspondante.")
        titre = _(u"Consommations sans prestations")
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
        self.SetMinSize((750, 600))

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
