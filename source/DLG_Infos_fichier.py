#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB
import FonctionsPerso
import UTILS_Historique

try: import psyco; psyco.full()
except: pass

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


# ---------------------------------------------------------------------------------------------------------------------------

class Informations():
    """ Récupère les informations sur le fichier """
    def __init__(self):
        self.listeDonnees = []
        self.DB = GestionDB.DB()
        
        # Ajout des items par catégorie
        self.listeDonnees.append(self.Categorie_general())
        self.listeDonnees.append(self.Categorie_stats())
        self.listeDonnees.append(self.Categorie_historique())
        
        self.DB.Close()
    
    def GetInformations(self):
        return self.listeDonnees
    
    def Categorie_general(self):
        nomCategorie = _(u"Général")
        listeItems = []
    
        # Récupération du nom du fichier
        nomFichier = self.DB.GetNomFichierDefaut() 
        if "[RESEAU]" in nomFichier :
            nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        listeItems.append((_(u"Nom du fichier"), nomFichier))
        
        # Récupération des paramètres du fichier
        req = """SELECT IDparametre, nom, parametre 
        FROM parametres WHERE categorie='fichier'
        ;"""
        self.DB.ExecuterReq(req)
        listeTemp = self.DB.ResultatReq()
        dictInfos = {}
        for IDparametre, nom, parametre  in listeTemp :
            dictInfos[nom] = parametre
        
        listeItems.append((_(u"Date de création"), FonctionsPerso.DateEngFr(dictInfos["date_creation"])))
        listeItems.append((_(u"Version de fichier"), dictInfos["version"]))
        listeItems.append((_(u"IDfichier"), dictInfos["IDfichier"]))
        
        # Nbre de tables de données
        listeTables = self.DB.GetListeTables()
        listeItems.append((_(u"Nombre de tables de données"), str(len(listeTables)+2)))
        
        return nomCategorie, listeItems
    
    def Categorie_stats(self):
        nomCategorie = _(u"Statistiques")
        listeItems = []
        
        def GetQuantite(label="", champID="", table=""):
            req = """SELECT COUNT(%s) FROM %s;""" % (champID, table)
            self.DB.ExecuterReq(req)
            nbre = self.DB.ResultatReq()[0][0]
            listeItems.append((label, str(nbre)))
        
        # Nbre individus
        GetQuantite(_(u"Nombre d'individus"), "IDindividu", "individus")
        
        # Nbre familles
        GetQuantite(_(u"Nombre de familles"), "IDfamille", "familles")

        # Nbre de consommations
        GetQuantite(_(u"Nombre de consommations"), "IDconso", "consommations")

        # Nbre de prestations
        GetQuantite(_(u"Nombre de prestations"), "IDprestation", "prestations")

        # Nbre de dépôts
        GetQuantite(_(u"Nombre de dépôts bancaires"), "IDdepot", "depots")

        # Nbre de factures
        GetQuantite(_(u"Nombre de factures"), "IDfacture", "factures")

        # Nbre de règlements
        GetQuantite(_(u"Nombre de règlements"), "IDreglement", "reglements")

        # Nbre de pièces
        GetQuantite(_(u"Nombre de pièces"), "IDpiece", "pieces")
        
        # Nbre de photos
        DBTemp = GestionDB.DB(suffixe="PHOTOS")
        req = """SELECT COUNT(IDphoto) FROM photos;"""
        DBTemp.ExecuterReq(req)
        donnees = DBTemp.ResultatReq()
        if len(donnees) > 0 :
            nbre = donnees[0][0]
        else :
            nbre = "Base non installée"
        listeItems.append((_(u"Nombre de photos"), str(nbre)))

        # Nbre de documents scannés
        DBTemp = GestionDB.DB(suffixe="DOCUMENTS")
        req = """SELECT COUNT(IDdocument) FROM documents;"""
        DBTemp.ExecuterReq(req)
        donnees = DBTemp.ResultatReq()
        if len(donnees) > 0 :
            nbre = donnees[0][0]
        else :
            nbre = "Base non installée"
        listeItems.append((_(u"Nombre de documents scannés"), str(nbre)))
        
        return nomCategorie, listeItems


    def Categorie_historique(self):
        nomCategorie = _(u"Historique")
        listeItems = []
        
        req = """SELECT IDcategorie, COUNT(IDaction) 
        FROM historique
        GROUP BY IDcategorie
        ;"""
        self.DB.ExecuterReq(req)
        listeTemp = self.DB.ResultatReq()
        
        for IDcategorie, nbreActions in listeTemp :
            labelCategorie = UTILS_Historique.CATEGORIES[IDcategorie]
            listeItems.append((labelCategorie, str(nbreActions)))
                
        return nomCategorie, listeItems


# --------------------------------------------------------------------------------------------------------------------

class CTRL_Infos(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_COLUMN_LINES | HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.parent = parent
        
        # Adapte taille Police pour Linux
##        import UTILS_Linux
##        UTILS_Linux.AdaptePolice(self)
        
        self.listeDonnees = []
            
    def MAJ(self, listeDonnees=[]): 
        self.listeDonnees = listeDonnees
                      
        # Création des colonnes
        self.AddColumn(_(u"Catégorie"))
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 300)
        self.AddColumn(_(u"Valeur"))
        self.SetColumnWidth(1, 190)
        
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_general = il.Add(wx.Bitmap("Images/16x16/Database.png", wx.BITMAP_TYPE_PNG))
        self.img_stats = il.Add(wx.Bitmap("Images/16x16/Barres.png", wx.BITMAP_TYPE_PNG))
        self.img_historique = il.Add(wx.Bitmap("Images/16x16/Historique.png", wx.BITMAP_TYPE_PNG))
        self.listeImages = [
            self.img_general,
            self.img_stats,
            self.img_historique,
            ]
        self.AssignImageList(il)

        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        # Création des branches
        numCategorie = 0
        for categorie, listeItems in self.listeDonnees :
            
            # Création de la catégorie
            brancheCategorie = self.AppendItem(self.root, categorie)
            self.SetItemBold(brancheCategorie, True)
            self.SetItemBackgroundColour(brancheCategorie, (200, 200, 200) )
            self.SetItemTextColour(brancheCategorie, (100, 100, 100) )
            self.SetItemImage(brancheCategorie, self.listeImages[numCategorie], which=wx.TreeItemIcon_Normal)
            
            for label, valeur in listeItems :

                # Création du label + valeur
                brancheItem = self.AppendItem(brancheCategorie, label)
                self.SetItemText(brancheItem, valeur, 1)
            
            numCategorie+= 1
        
        self.ExpandAllChildren(self.root)
            
    
# -------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter les informations concernant le fichier de données actuellement chargé. Cette liste propose trois catégories de données : les informations générales, les statistiques et l'historique.")
        titre = _(u"Informations sur le fichier")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Information.png")
        
        self.ctrl_informations = CTRL_Infos(self)
                
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        # MAJ liste
        infos = Informations()
        listeDonnees = infos.GetInformations()
        self.ctrl_informations.MAJ(listeDonnees)
        
    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((550, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_informations, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        import UTILS_Aide
        UTILS_Aide.Aide("Informationssurlefichier")




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
