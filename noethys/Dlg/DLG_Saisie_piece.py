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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
import calendar
from dateutil import relativedelta
from Utils import UTILS_Historique
from Ctrl import CTRL_Saisie_date

from Ctrl import CTRL_Pieces_obligatoires
from Ctrl import CTRL_Vignettes_documents
from Utils import UTILS_Dates


class Choix_Piece_autre(wx.Choice):
    def __init__(self, parent, listePiecesObligatoires=[], dictTypesPieces={} ):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeID = []
        self.listeDonnees = []
        self.listePiecesObligatoires = listePiecesObligatoires
        self.dictTypesPieces = dictTypesPieces
        self.SetListeDonnees() 
    
    def SetListeDonnees(self):
        self.listeNoms = []
        self.listeID = []
        self.listeDonnees = []
        
        # Si on vient d'une fiche INDIVIDU :
        if self.parent.IDindividu != None :
            IDindividu = self.parent.IDindividu
            
            if self.parent.dictFamillesRattachees != None :
                
                # S'il y a une seule famille rattachée :
                if len(self.parent.dictFamillesRattachees) == 1 :
                    IDfamille = self.parent.dictFamillesRattachees.keys()[0]
                    for IDtype_piece, dictTypePiece in self.dictTypesPieces.iteritems() :
                        nomPiece = dictTypePiece["nom"]
                        public = dictTypePiece["public"]
                        if public == "famille" : 
                            IDindividuTmp = None
                        else:
                            IDindividuTmp = IDindividu
                        if (IDfamille, IDtype_piece, IDindividuTmp) not in self.listePiecesObligatoires :
                            self.listeNoms.append(nomPiece)
                            self.listeID.append(IDtype_piece)
                            self.listeDonnees.append( {"IDfamille":IDfamille, "IDtype_piece":IDtype_piece, "IDindividu":IDindividuTmp, "nomPiece":nomPiece} )
                        
                else:
                    # S'il y a plusieurs familles rattachées :
                    for IDtype_piece, dictTypePiece in self.dictTypesPieces.iteritems() :
                        nomPiece = dictTypePiece["nom"]
                        public = dictTypePiece["public"]
                        if public == "famille" : 
                            IDindividuTmp = None
                        else:
                            IDindividuTmp = IDindividu
                        for IDfamille, dictFamille in self.parent.dictFamillesRattachees.iteritems() :
                            nomTitulaires = dictFamille["nomsTitulaires"]
                            if (IDfamille, IDtype_piece, IDindividuTmp) not in self.listePiecesObligatoires :
                                self.listeNoms.append( _(u"%s (Famille de %s)") % (nomPiece, nomTitulaires))
                                self.listeID.append(IDtype_piece)
                                self.listeDonnees.append( {"IDfamille":IDfamille, "IDtype_piece":IDtype_piece, "IDindividu":IDindividuTmp, "nomPiece":nomPiece} )
                    
                
        # Si on vient d'une fiche famille
        else:
            
            # Récupération de tous les membres de la famille
            DB = GestionDB.DB()
            req = """SELECT IDrattachement, rattachements.IDindividu, rattachements.IDfamille, IDcategorie, titulaire, nom, prenom
            FROM rattachements 
            LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
            WHERE IDfamille=%d
            ORDER BY nom, prenom;""" % self.parent.IDfamille
            DB.ExecuterReq(req)
            listeMembres = DB.ResultatReq()
            DB.Close()
            
            for IDtype_piece, dictTypePiece in self.dictTypesPieces.iteritems() :
                nomPiece = dictTypePiece["nom"]
                public = dictTypePiece["public"]
                if public == "famille" :
                    if (self.parent.IDfamille, IDtype_piece, None) not in self.listePiecesObligatoires :
                        self.listeNoms.append(nomPiece)
                        self.listeID.append(IDtype_piece)
                        self.listeDonnees.append( {"IDfamille":self.parent.IDfamille, "IDtype_piece":IDtype_piece, "IDindividu":None, "nomPiece":nomPiece} )
                else:
                    for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom in listeMembres :
                        if (IDfamille, IDtype_piece, IDindividu) not in self.listePiecesObligatoires :
                            self.listeNoms.append( _(u"% s de %s") % (nomPiece, prenom) )
                            self.listeID.append(IDtype_piece)
                            self.listeDonnees.append( {"IDfamille":IDfamille, "IDtype_piece":IDtype_piece, "IDindividu":IDindividu, "nomPiece":nomPiece} )
        
        # Remplissage du contrôle
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for IDcompte in self.listeID :
            if IDcompte == ID :
                 self.SetSelection(index)
            index += 1
    
    def SelectPiece(self, IDfamille=None, IDtype_piece=None, IDindividu=None):
        index = 0
        print IDfamille, IDtype_piece, IDindividu
        for dictPiece in self.listeDonnees :
            print dictPiece
            if dictPiece["IDfamille"] == IDfamille and dictPiece["IDtype_piece"] == IDtype_piece and dictPiece["IDindividu"] == IDindividu :
                self.Select(index)
                break
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeID[index]
    
    def GetDonneesSelection(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]

# ------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDpiece=None, IDfamille=None, IDindividu=None, dictFamillesRattachees={}):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_piece", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDpiece = IDpiece
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        
        # Récupère les types de pièces existants
        self.dictTypesPieces = self.Importation_types_pieces() 
        
        # Liste des pièces
        self.sizer_type_staticbox = wx.StaticBox(self, -1, _(u"Type de pièce"))
        if IDfamille != None :
            texte = _(u"la famille")
        else:
            texte = _(u"l'individu")
        self.radio_pieces_1 = wx.RadioButton(self, -1, _(u"Dans la liste des pièces que %s doit fournir :") % texte, style = wx.RB_GROUP)
        self.ctrl_pieces_obligatoires = CTRL_Pieces_obligatoires.CTRL(self, IDfamille=IDfamille, IDindividu=IDindividu, dictFamillesRattachees=dictFamillesRattachees, size=(-1, 200))
        self.ctrl_pieces_obligatoires.SetMinSize((-1, 90))
        self.ctrl_pieces_obligatoires.MAJ() 
        self.listePiecesObligatoires = self.ctrl_pieces_obligatoires.GetlistePiecesObligatoires()
        
        # Types de pièces autres
        self.radio_pieces_2 = wx.RadioButton(self, -1, _(u"Dans la liste des autres types de pièces :"))
        self.ctrl_pieces_autres = Choix_Piece_autre(self, self.listePiecesObligatoires, self.dictTypesPieces)
        
        # Date de début
        self.sizer_date_debut_staticbox = wx.StaticBox(self, -1, _(u"Date de début"))
        self.label_date_debut = wx.StaticText(self, -1, "Date :")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        
        # Date de fin
        self.sizer_date_fin_staticbox = wx.StaticBox(self, -1, _(u"Date de fin"))
        self.radio_date_fin_1 = wx.RadioButton(self, -1, _(u"Date :"), style = wx.RB_GROUP)
        self.radio_date_fin_2 = wx.RadioButton(self, -1, _(u"Validité illimitée"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        
        # Pages capturées
        self.sizer_pages_staticbox = wx.StaticBox(self, -1, _(u"Documents associés"))
        self.ctrl_pages = CTRL_Vignettes_documents.CTRL(self, IDpiece=self.IDpiece, style=wx.BORDER_SUNKEN)
        self.bouton_ajouter_page = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_page = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser_page = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_zoom_plus = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/zoom_plus.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_zoom_moins = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/zoom_moins.png"), wx.BITMAP_TYPE_ANY))
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        # Init contrôles
        self.ctrl_pieces_autres.Enable(False)

        # Si Modification -> importation des données
        if IDpiece == None :
            self.SetTitle(_(u"Saisie d'une pièce"))
            self.ctrl_date_debut.SetDate(datetime.date.today())
        else:
            self.SetTitle(_(u"Modification d'une pièce"))
            self.Importation()

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPieces, self.radio_pieces_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPieces, self.radio_pieces_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDateFin, self.radio_date_fin_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDateFin, self.radio_date_fin_2)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_TEXT, self.OnDateDebut, self.ctrl_date_debut)
        self.Bind(wx.EVT_CHOICE, self.OnChoixAutres, self.ctrl_pieces_autres)
        self.Bind(wx.EVT_BUTTON, self.AjouterPage, self.bouton_ajouter_page)
        self.Bind(wx.EVT_BUTTON, self.SupprimerPage, self.bouton_supprimer_page)
        self.Bind(wx.EVT_BUTTON, self.VisualiserPage, self.bouton_visualiser_page)
        self.Bind(wx.EVT_BUTTON, self.ZoomPlus, self.bouton_zoom_plus)
        self.Bind(wx.EVT_BUTTON, self.ZoomMoins, self.bouton_zoom_moins)

    def __set_properties(self):
        self.radio_pieces_1.SetValue(1)
        self.radio_pieces_2.SetToolTipString(_(u"Cliquez ici si la pièce que vous souhaitez enregistrer n'est pas dans la liste des pièces obligatoires à fournir"))
        self.ctrl_pieces_obligatoires.SetToolTipString(_(u"Sélectionnez un type de pièce en cliquant sur son nom"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début de validité.\nRemarque : Il s'agit bien de la date d'emission de la pièce \n(par exemple, la date d'obtention d'un diplôme) et non la date à laquelle vous avez reçue la pièce"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date d'expiration de la pièce"))
        self.radio_date_fin_1.SetToolTipString(_(u"Cliquez ici si la pièce a une durée de validité limitée dans le temps"))
        self.radio_date_fin_2.SetToolTipString(_(u"Cliquez ici si la pièce que vous souhaitez enregistrer a une durée de validité illimitée"))
        self.bouton_ajouter_page.SetToolTipString(_(u"Cliquez ici pour ajouter un document"))
        self.bouton_supprimer_page.SetToolTipString(_(u"Cliquez ici pour supprimer le document sélectionné"))
        self.bouton_visualiser_page.SetToolTipString(_(u"Cliquez ici pour visualiser le document sélectionné"))
        self.bouton_zoom_plus.SetToolTipString(_(u"Cliquez ici pour agrandir les vignettes"))
        self.bouton_zoom_moins.SetToolTipString(_(u"Cliquez ici pour réduire les vignettes"))
        self.SetMinSize((640, 500)) 
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        sizer_type = wx.StaticBoxSizer(self.sizer_type_staticbox, wx.VERTICAL)
        grid_sizer_3 = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_3.Add(self.radio_pieces_1, 0, 0, 0)
        grid_sizer_3.Add(self.ctrl_pieces_obligatoires, 1, wx.LEFT|wx.EXPAND, 17)
        grid_sizer_3.Add(self.radio_pieces_2, 0, 0, 0)
        grid_sizer_3.Add(self.ctrl_pieces_autres, 0, wx.LEFT|wx.EXPAND, 17)
        grid_sizer_3.AddGrowableRow(1)
        grid_sizer_3.AddGrowableCol(0)
        sizer_type.Add(grid_sizer_3, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(sizer_type, 1, wx.EXPAND, 10)
        
        # Dates
        sizer_date_debut = wx.StaticBoxSizer(self.sizer_date_debut_staticbox, wx.VERTICAL)
        grid_sizer_date_debut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        sizer_date_fin = wx.StaticBoxSizer(self.sizer_date_fin_staticbox, wx.VERTICAL)
        grid_sizer_date_fin_1 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_date_fin_2 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_date_debut.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date_debut.Add(self.ctrl_date_debut, 0, 0, 0)
        sizer_date_debut.Add(grid_sizer_date_debut, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_dates.Add(sizer_date_debut, 1, wx.EXPAND, 0)
        grid_sizer_date_fin_2.Add(self.radio_date_fin_1, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date_fin_2.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_date_fin_1.Add(grid_sizer_date_fin_2, 1, wx.EXPAND, 0)
        grid_sizer_date_fin_1.Add(self.radio_date_fin_2, 0, 0, 0)
        sizer_date_fin.Add(grid_sizer_date_fin_1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_dates.Add(sizer_date_fin, 1, wx.EXPAND, 0)
        grid_sizer_dates.AddGrowableCol(0)
        grid_sizer_dates.AddGrowableCol(1)
        grid_sizer_gauche.Add(grid_sizer_dates, 1, wx.EXPAND, 10)
        
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Pages
        sizer_pages = wx.StaticBoxSizer(self.sizer_pages_staticbox, wx.VERTICAL)
        
        grid_sizer_pages = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_pages.Add(self.ctrl_pages, 0, wx.EXPAND, 0)
        grid_sizer_pages.AddGrowableRow(0)
        grid_sizer_pages.AddGrowableCol(0)
        
        grid_sizer_commandes_pages = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes_pages.Add(self.bouton_ajouter_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_supprimer_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add( (10, 10), 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_visualiser_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add( (10, 10), 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_zoom_plus, 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_zoom_moins, 0, 0, 0)
        grid_sizer_pages.Add(grid_sizer_commandes_pages, 1, wx.EXPAND, 0)
        
        sizer_pages.Add(grid_sizer_pages, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_contenu.Add(sizer_pages, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def Importation_types_pieces(self):
        dictTypesPieces = {}
        DB = GestionDB.DB()
        req = """SELECT IDtype_piece, nom, public, duree_validite, valide_rattachement
        FROM types_pieces 
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDtype_piece, nom, public, duree_validite, valide_rattachement in listeDonnees :
            dictTypesPieces[IDtype_piece] = {"nom" : nom, "public" : public, "duree_validite" : duree_validite, "valide_rattachement" : valide_rattachement}
        return dictTypesPieces
    
    def SelectPiece(self, IDfamille=None, IDtype_piece=None, IDindividu=None):
        self.ctrl_pieces_obligatoires.SelectPiece(IDfamille, IDtype_piece, IDindividu)
        if self.CalcValiditeDefaut() == False :
            # Mets le focus sur la date de début
            self.ctrl_date_debut.SetFocus()
    
    def OnSelectionPieceObligatoire(self, donnees):
        # Si une date de début a déjà été saisie, on procède à la recherche de la date de fin par défaut
        if self.CalcValiditeDefaut() == False :
            # Mets le focus sur la date de début
            self.ctrl_date_debut.SetFocus()
        
    def OnChoixAutres(self, event):
        IDtype_piece = self.ctrl_pieces_autres.GetID()
        if IDtype_piece == None : return
        # Si une date de début a déjà été saisie, on procède à la recherche de la date de fin par défaut
        if self.CalcValiditeDefaut() == False :
            # Mets le focus sur la date de début
            self.ctrl_date_debut.SetFocus()
        self.ctrl_pieces_obligatoires.Unselect() 

    def OnRadioPieces(self, event):
        if self.radio_pieces_1.GetValue() == True:
            self.ctrl_pieces_autres.Enable(False)
            self.ctrl_pieces_obligatoires.Enable(True)
        else:
            self.ctrl_pieces_autres.Enable(True)
            self.ctrl_pieces_obligatoires.Enable(False)
            self.ctrl_pieces_obligatoires.Unselect() 

    def OnRadioDateFin(self, event):
        if self.radio_date_fin_1.GetValue() == True:
            self.ctrl_date_fin.Enable(True)
        else:
            self.ctrl_date_fin.Enable(False)
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Pices")
    
    def GetSelectionPiece(self):
        if self.radio_pieces_1.GetValue() == True :
            donnees = self.ctrl_pieces_obligatoires.GetDonneesSelection() 
            if donnees == None :
                return None
            if donnees["type"] == "famille" :
                return
            if donnees["type"] == "piece" :
                IDtype_piece = donnees["IDtype_piece"]
                IDindividu = donnees["IDindividu"]
                IDfamille = donnees["IDfamille"]
                nomPiece = donnees["nomPiece"]
        else:
            donnees = self.ctrl_pieces_autres.GetDonneesSelection() 
            if donnees == None :
                return None
            IDtype_piece = donnees["IDtype_piece"]
            IDindividu = donnees["IDindividu"]
            IDfamille = donnees["IDfamille"]
            nomPiece = donnees["nomPiece"]
        return { "IDfamille":IDfamille, "IDtype_piece":IDtype_piece, "IDindividu":IDindividu, "nomPiece":nomPiece}
            

    def OnDateDebut(self, event):
        texte = self.ctrl_date_debut.GetValue()
        for caract in texte:
            if caract == " ":
                return
        self.CalcValiditeDefaut()
        event.Skip()

    def CalcValiditeDefaut(self):
        dateDebut = self.ctrl_date_debut.GetValue()

        if dateDebut == "  /  /    ":
            return False

        # Récupération des données sur la pièces
        selection = self.GetSelectionPiece()
        if selection == None : return
        
        # Validation de la date de début
        validation = self.ctrl_date_debut.FonctionValiderDate()
        if validation == False:
            self.ctrl_date_debut.SetFocus()
            return

        # Recherche de la durée de validité par défaut de la pièce
        IDtype_piece = selection["IDtype_piece"]
        validite = self.dictTypesPieces[IDtype_piece]["duree_validite"]
        
        # Si illimité
        if validite == None or validite == "j0-m0-a0" : 
            dateFin = "2999-01-01"
            self.radio_date_fin_2.SetValue(1)
            self.ctrl_date_fin.Enable(False)
            self.bouton_ok.SetFocus()
        
        # Si durée limitée
        elif validite != None and validite.startswith("j") :
            posM = validite.find("m")
            posA = validite.find("a")
            jours = int(validite[1:posM-1])
            mois = int(validite[posM+1:posA-1])
            annees = int(validite[posA+1:])
        
            dateJour = int(dateDebut[:2])
            dateMois = int(dateDebut[3:5])
            dateAnnee = int(dateDebut[6:10])
            dateDebut = datetime.date(dateAnnee, dateMois, dateJour)

##            # Calcul des jours
##            if jours != 0:
##                dateFin = dateDebut + (datetime.timedelta(days = jours))
##                dateJour = dateFin.day
##                dateMois = dateFin.month
##                dateAnnee = dateFin.year
##
##            # Calcul des mois
##            if mois != 0:
##                dateMois = dateMois + mois
##                if dateMois > 12:
##                    division = divmod(dateMois, 12)
##                    dateAnnee = dateAnnee + division[0]
##                    dateMois = division[1]
##                nbreJoursMois = calendar.monthrange(dateAnnee, dateMois)[1]
##                if dateJour > nbreJoursMois :
##                    dateJour = nbreJoursMois
##                dateFin = datetime.date(dateAnnee, dateMois, dateJour)
##                dateJour = dateFin.day
##                dateMois = dateFin.month
##                dateAnnee = dateFin.year
##
##            # Calcul des années
##            if annees != 0:
##                dateAnnee = dateAnnee + annees
##                nbreJoursMois = calendar.monthrange(dateAnnee, dateMois)[1]
##                if dateJour > nbreJoursMois :
##                    dateJour = nbreJoursMois
##                dateFin = datetime.date(dateAnnee, dateMois, dateJour)

            # Calcul de la date de fin de validité
            dateFin = dateDebut
            if jours != 0 : dateFin = dateFin + relativedelta.relativedelta(days=+jours)
            if mois != 0 : dateFin = dateFin + relativedelta.relativedelta(months=+mois)
            if annees != 0 : dateFin = dateFin + relativedelta.relativedelta(years=+annees)

            # Insertion de la date dans la case Date_Fin
            dateFinale = str(dateFin)
            dateFinale = dateFinale[8:10] + "/" + dateFinale[5:7] + "/" + dateFinale[:4]
            self.ctrl_date_fin.SetValue(dateFinale)

            # Mets le focus sur la date de fin
            self.radio_date_fin_1.SetValue(1)
            self.ctrl_date_fin.Enable(True)
            self.bouton_ok.SetFocus()
        
        # Date Max
        elif validite != None and validite.startswith("d") :
            date_fin = UTILS_Dates.DateEngFr(validite[1:])
            self.ctrl_date_fin.SetValue(date_fin)
            self.radio_date_fin_1.SetValue(1)
            self.ctrl_date_fin.Enable(True)
            self.bouton_ok.SetFocus()

        
    
    def GetIDpiece(self):
        return self.IDpiece

    def Importation(self):
        """ Importation des donnees de la base """
        DB = GestionDB.DB()
        req = """SELECT pieces.IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, public
        FROM pieces 
        LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
        WHERE IDpiece=%d;""" % self.IDpiece
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, public = listeDonnees[0]
        if public == "famille" : IDindividu = None
        
        # Sélection de la pièce dans les pièces obligatoires
        resultat = self.ctrl_pieces_obligatoires.SelectPiece(IDfamille, IDtype_piece, IDindividu)
        self.radio_pieces_1.SetValue(True)
        
        # Sélection de la pièce dans les pièces autres
        if resultat == False :
            self.ctrl_pieces_autres.SelectPiece(IDfamille, IDtype_piece, IDindividu)
            self.radio_pieces_2.SetValue(True)
        
        self.OnRadioPieces(None) 
        
        # Insertion de la date de début
        self.ctrl_date_debut.SetDate(date_debut)

        # Insertion de la date de fin
        if date_fin == "2999-01-01":
            self.radio_date_fin_2.SetValue(True)
            self.ctrl_date_fin.Enable(False)
        else:
            self.radio_date_fin_1.SetValue(True)
            self.ctrl_date_fin.Enable(True)
            self.ctrl_date_fin.SetDate(date_fin)

        
                
    def OnBoutonOk(self, event):
        """ Bouton Ok """
        # Vérification des données saisies
        selection = self.GetSelectionPiece() 
        if selection == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun type de pièce !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
            
        # Validation de la date de début
        if self.ctrl_date_debut.FonctionValiderDate() == False or self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        
        if self.radio_date_fin_1.GetValue() == True :
            if self.ctrl_date_fin.FonctionValiderDate() == False or self.ctrl_date_fin.GetDate() == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
        
        # Vérifie que la date de fin est supérieure à la date de début
        if self.radio_date_fin_1.GetValue() == True :
            if self.ctrl_date_debut.GetDate() > self.ctrl_date_fin.GetDate() :
                dlg = wx.MessageDialog(self, _(u"Attention, la date de début est supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False

        # Sauvegarde
        IDtype_piece = selection["IDtype_piece"]
        IDindividu = selection["IDindividu"]
        IDfamille = selection["IDfamille"]
        date_debut = str(self.ctrl_date_debut.GetDate())
        if self.radio_date_fin_1.GetValue() == True :
            date_fin = str(self.ctrl_date_fin.GetDate())
        else:
            date_fin = "2999-01-01"

        DB = GestionDB.DB()
        listeDonnees = [    
                ("IDtype_piece", IDtype_piece),
                ("IDindividu", IDindividu),
                ("IDfamille", IDfamille),
                ("date_debut", date_debut),
                ("date_fin", date_fin),
            ]
        if self.IDpiece == None :
            nouvellePiece = True
            self.IDpiece = DB.ReqInsert("pieces", listeDonnees)
        else:
            nouvellePiece = False
            DB.ReqMAJ("pieces", listeDonnees, "IDpiece", self.IDpiece)
        DB.Close()
        
        # Mémorise l'action dans l'historique
        if nouvellePiece == True :
            type = _(u"Saisie")
            IDcategorie = 15 
        else:
            type = _(u"Modification")
            IDcategorie = 16
        if IDindividu != None and IDfamille !=None :
            texteDetail = _(u"pour l'individu ID%d et la famille ID%d") % (IDindividu, IDfamille)
        elif IDindividu == None and IDfamille !=None :
            texteDetail = _(u"pour la famille ID%d") % IDfamille
        elif IDindividu != None and IDfamille == None :
            texteDetail = _(u"pour l'individu ID%d") % IDindividu 
        else:
            texteDetail = u""
        nomPiece = selection["nomPiece"]
        UTILS_Historique.InsertActions([{
                "IDindividu" : IDindividu,
                "IDfamille" : self.IDfamille,
                "IDcategorie" : IDcategorie, 
                "action" : _(u"%s de la pièce ID%d '%s' %s") % (type, self.IDpiece, nomPiece, texteDetail),
                },])
        
        # Sauvegarde des pages scannées
        self.ctrl_pages.Sauvegarde(self.IDpiece) 
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def AjouterPage(self, event):
        self.ctrl_pages.AjouterPage()

    def SupprimerPage(self, event):
        self.ctrl_pages.SupprimerPage(None)
    
    def VisualiserPage(self, event):
        self.ctrl_pages.VisualiserPage(None)
    
    def ZoomPlus(self, event):
        self.ctrl_pages.ZoomPlus()

    def ZoomMoins(self, event):
        self.ctrl_pages.ZoomMoins()


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDpiece=18, IDindividu=None, IDfamille=7)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
