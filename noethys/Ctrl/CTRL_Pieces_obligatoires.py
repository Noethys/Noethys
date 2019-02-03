#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB
from Utils import UTILS_Interface



def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def FormatDuree(duree):
    posM = duree.find("m")
    posA = duree.find("a")
    jours = int(duree[1:posM-1])
    mois = int(duree[posM+1:posA-1])
    annees = int(duree[posA+1:])
    return jours, mois, annees

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, IDfamille=None, IDindividu=None, dictFamillesRattachees={}, size=(-1, -1), largeurColonne=270 ): 
        HTL.HyperTreeList.__init__(self, parent, -1, size=size)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.listePiecesObligatoires = []
        self.dictItems = {}

        # Création des colonnes
        self.AddColumn(_(u"Pièces à fournir"))
        self.SetColumnWidth(0, largeurColonne)
        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
                
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_ok = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.img_attention = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        self.img_pasok = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
                    
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | HTL.TR_NO_HEADER)
        self.SetBackgroundColour(wx.WHITE)
        
        # Binds
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelection)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClick)
    
    def OnSelection(self, event):
        item = event.GetItem()
        donnees = self.GetPyData(item)
        # Si le parent est la fenêtre de saisie d'une pièce :
        if self.GetParent().GetName() == "DLG_Saisie_piece" :
            self.GetParent().OnSelectionPieceObligatoire(donnees)
    
    def OnDoubleClick(self, event):
        item = event.GetItem()
        donnees = self.GetPyData(item)
        if donnees == None : return
        if donnees["type"] != "piece" : return
        # Si la pièce est valide, on annule
        if donnees["valide"] != "pasok" :
            dlg = wx.MessageDialog(self, _(u"Une pièce valide existe déjà !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        # Ouverture de la fenêtre de saisie d'une pièce
        if self.GetParent().GetName() == "DLG_Individu_pieces" or self.GetParent().GetName() == "DLG_Famille_pieces" :
            self.GetParent().OnAjoutExpress(donnees["IDfamille"], donnees["IDtype_piece"], donnees["IDindividu"])
        
        
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.Remplissage()
    
    def GetlistePiecesObligatoires(self):
        return self.listePiecesObligatoires
    
    def GetDonneesSelection(self):
        return self.GetPyData(self.GetSelection())
    
    def Remplissage(self):
        # Récupération des données
        self.listePiecesObligatoires = []
        self.dictItems = {}
        
        # Création des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu
        
        DB = GestionDB.DB()
        
        # Récupération des pièces à fournir pour la famille ou l'individu
        req = """
        SELECT 
        inscriptions.IDfamille, pieces_activites.IDtype_piece, types_pieces.nom, types_pieces.public, types_pieces.valide_rattachement, individus.prenom, individus.IDindividu
        FROM pieces_activites 
        LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces_activites.IDtype_piece
        LEFT JOIN inscriptions ON inscriptions.IDactivite = pieces_activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        WHERE inscriptions.statut='ok' AND activites.date_fin>='%s' %s
        GROUP BY inscriptions.IDfamille, pieces_activites.IDtype_piece, individus.IDindividu;
        """ % (datetime.date.today(), condition)
        DB.ExecuterReq(req)
        listePiecesObligatoires = DB.ResultatReq()
        
        # Récupération des pièces de la famille
        dateDuJour = datetime.date.today()
        
        if self.IDindividu != None :
            # Pour un individu
            if self.dictFamillesRattachees != None :
                listeIDfamille = []
                for IDfamille, dictFamille in self.dictFamillesRattachees.items() :
                    if dictFamille["IDcategorie"] in (1, 2) :
                        listeIDfamille.append(IDfamille)
                if len(listeIDfamille) == 0 : conditionIDfamille = "()"
                if len(listeIDfamille) == 1 : conditionIDfamille = "(%d)" % listeIDfamille[0]
                else : conditionIDfamille = str(tuple(listeIDfamille))
            else:
                conditionIDfamille = "()"
            req = """
            SELECT IDpiece, pieces.IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, public
            FROM pieces 
            LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
            WHERE date_debut <= '%s' AND date_fin >= '%s'
            AND (IDindividu=%d OR (IDfamille IN %s AND IDindividu IS NULL))
            ORDER BY date_fin
            ;""" % (str(dateDuJour), str(dateDuJour), self.IDindividu, conditionIDfamille)
        else:
            # Pour une famille
            req = """
            SELECT IDindividu, IDcategorie
            FROM rattachements 
            WHERE IDfamille=%d AND IDcategorie IN (1, 2);
            """ % self.IDfamille
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            listeIDindividus = []
            for IDindividu, IDcategorie in listeDonnees :
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu) 
            if len(listeIDindividus) == 0 : conditionIndividus = "()"
            if len(listeIDindividus) == 1 : conditionIndividus = "(%d)" % listeIDindividus[0]
            else : conditionIndividus = str(tuple(listeIDindividus))
            req = """
            SELECT IDpiece, pieces.IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, public
            FROM pieces 
            LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
            WHERE date_debut <= '%s' AND date_fin >= '%s'
            AND (IDfamille=%s OR (IDindividu IN %s AND IDfamille IS NULL))
            ORDER BY date_fin
            """ % (str(dateDuJour), str(dateDuJour), self.IDfamille, conditionIndividus)

##        condition = ""
##        # Si pour fiche famille
##        if self.IDfamille != None :
##            condition = " AND IDfamille=%d " % self.IDfamille
##        # Si pour fiche INDIVIDU
##        if self.IDindividu != None :
##            condition = " AND IDindividu=%d " % self.IDindividu
##        req = """
##        SELECT IDpiece, pieces.IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, public
##        FROM pieces 
##        LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
##        WHERE date_debut <= '%s' AND date_fin >= '%s' %s
##        ORDER BY date_fin;
##        """ % (str(dateDuJour), str(dateDuJour), condition)
        
        DB.ExecuterReq(req)
        listePiecesFournies = DB.ResultatReq()
        DB.Close()
        dictPiecesFournies = {}
        for IDpiece, IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, publicPiece in listePiecesFournies :
            # Pour les pièces familiales :
            if publicPiece == "famille" : IDindividu = None
            
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            dictPiecesFournies[ (IDfamille, IDtype_piece, IDindividu) ] = (date_debut, date_fin)
        
        # Comparaison de la liste des pièces à fournir et la liste des pièces fournies
        dictDonnees = {}
        for IDfamille, IDtype_piece, nomPiece, publicPiece, rattachementPiece, prenom, IDindividu in listePiecesObligatoires :
            
            # Pour les pièces familiales :
            if publicPiece == "famille" : IDindividu = None
            # Pour les pièces qui sont indépendantes de la famille
            if rattachementPiece == 1 :
                IDfamille = None
            
            # Mémorise pour la fenêtre de saisie d'une pièce
            self.listePiecesObligatoires.append((IDfamille, IDtype_piece, IDindividu))
            
            if (IDfamille, IDtype_piece, IDindividu) in dictPiecesFournies :
                date_debut, date_fin = dictPiecesFournies[(IDfamille, IDtype_piece, IDindividu)]
                nbreJoursRestants = (date_fin - datetime.date.today()).days
                if nbreJoursRestants > 15 :
                    valide = "ok"
                else:
                    valide = "attention"
            else:
                valide = "pasok"
            dictDonnees[(IDfamille, IDtype_piece, IDindividu)] = (IDfamille, IDtype_piece, nomPiece, publicPiece, prenom, IDindividu, valide)
        
        # Répartition par famille
        dictPieces = {}
        nbreFamilles = 0
        for key, valeurs in dictDonnees.items() :
            IDfamille = valeurs[0]
            if (IDfamille in dictPieces) == False :
                dictPieces[IDfamille] = []
                if IDfamille != None : 
                    nbreFamilles += 1
            dictPieces[IDfamille].append(valeurs)
            dictPieces[IDfamille].sort()
        
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        # Création des branches
        for IDfamille, valeurs in dictPieces.items() :
            
            # Niveau 1 : Titulaires des familles
            if nbreFamilles > 1 :
                if IDfamille == None :
                    label = _(u"Pièces indépendantes")
                else:
                    if self.dictFamillesRattachees != None and len(self.dictFamillesRattachees) > 0 :
                        label = self.dictFamillesRattachees[IDfamille]["nomsTitulaires"]
                    else:
                        label = _(u"IDfamille=%d") % IDfamille
                niveau1 = self.AppendItem(self.root, label)
                self.SetPyData(niveau1, {"type":"famille", "IDfamille":IDfamille} )
                self.SetItemBold(niveau1, True)
            else:
                niveau1 = self.root
            
            # Niveau 2 : Nom des pièces
            for IDfamille, IDtype_piece, nomPiece, publicPiece, prenom, IDindividu, valide in valeurs :
                if publicPiece == "famille" or self.IDindividu != None :
                    label = nomPiece
                else:
                    label = _(u"%s de %s") % (nomPiece, prenom)
                niveau2 = self.AppendItem(niveau1, label)
                self.SetPyData(niveau2, {"type":"piece", "IDtype_piece":IDtype_piece, "IDindividu":IDindividu, "IDfamille":IDfamille, "valide":valide, "nomPiece":nomPiece} )
                self.dictItems[(IDfamille, IDtype_piece, IDindividu)] = niveau2
                if valide == "ok" : self.SetItemImage(niveau2, self.img_ok, which=wx.TreeItemIcon_Normal)
                if valide == "attention" : self.SetItemImage(niveau2, self.img_attention, which=wx.TreeItemIcon_Normal)
                if valide == "pasok" : self.SetItemImage(niveau2, self.img_pasok, which=wx.TreeItemIcon_Normal)
        
        if nbreFamilles < 2 :
            self.SetAGWWindowStyleFlag(wx.TR_NO_LINES | wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | HTL.TR_NO_HEADER)
            
        self.ExpandAllChildren(self.root)
        
    def SelectPiece(self, IDfamille=None, IDtype_piece=None, IDindividu=None):
        if (IDfamille, IDtype_piece, IDindividu) in self.dictItems :
            item = self.dictItems[(IDfamille, IDtype_piece, IDindividu)]
            self.SelectItem(item)
            return True
        return False


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel, IDfamille=None, IDindividu=27)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        
if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
