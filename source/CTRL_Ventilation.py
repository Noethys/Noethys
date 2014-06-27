#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import wx.lib.agw.hypertreelist as HTL
import wx.lib.agw.hyperlink as Hyperlink
import datetime
import decimal
import sys

from UTILS_Decimal import FloatToDecimal as FloatToDecimal

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import GestionDB
import CTRL_Saisie_euros

try: import psyco; psyco.full()
except: pass

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)

COULEUR_NUL = (255, 0, 0)
COULEUR_PARTIEL = (255, 193, 37)
COULEUR_TOTAL = (0, 238, 0)
            
def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
def PeriodeComplete(mois, annee):
    listeMois = (u"Janvier", u"Février", u"Mars", u"Avril", u"Mai", u"Juin", u"Juillet", u"Août", u"Septembre", u"Octobre", u"Novembre", u"Décembre")
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete

    


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", listeChoix=[], size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        
    def OnLeftLink(self, event):
        if self.URL == "automatique" : self.parent.VentilationAuto() 
        if self.URL == "tout" : self.parent.VentilationTout() 
        if self.URL == "rien" : self.parent.VentilationRien() 
        self.UpdateLink()

# -----------------------------------------------------------------------------------------------------------------------


class Track_regroupement(object):
    def __init__(self):
        self.ctrl_checkbox_regroupement = None
        self.ctrl_total_prestations = None
        self.ctrl_total_aVentiler = None
        self.ctrl_total_ventilationActuelle = None
        self.listeTracks = []
        self.IDfacture = None
    
    def Cocher(self, etat=True):
        """ Cocher tous les tracks du regroupement """
        for track in self.listeTracks :
            track.ctrl_checkbox.SetEtat(etat)
            if etat == True :
                track.Ventiler(None)
            else:
                track.Ventiler(0.0)
    
    def MAJ(self):
        # Récupération du total des prestations
        total_prestation = 0.0
        for track in self.listeTracks :
            total_prestation += track.montant
        self.ctrl_total_prestations.SetMontant(total_prestation)
        
        # Récupération du total à ventiler
        total_aVentiler = 0.0
        for track in self.listeTracks :
            total_aVentiler += track.resteAVentiler
        self.ctrl_total_aVentiler.SetMontant(total_aVentiler)

        # Récupération du total des ventilations actuelles
        total_ventilationActuelle = 0.0
        for track in self.listeTracks :
            total_ventilationActuelle += track.ventilationActuelle
        self.ctrl_total_ventilationActuelle.SetMontant(total_ventilationActuelle)



class Track(object):
    def __init__(self, donnees):
        self.IDprestation = donnees["IDprestation"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.date = donnees["date"]
        self.date_complete = DateComplete(self.date)
        self.mois = self.date.month
        self.annee = self.date.year
        self.periode = (self.annee, self.mois)
        self.periode_complete = PeriodeComplete(self.mois, self.annee)
        self.categorie = donnees["categorie"]
        self.label = donnees["label"]
        self.montant = donnees["montant"]
        self.IDactivite = donnees["IDactivite"]
        self.nomActivite = donnees["nomActivite"]
        self.IDtarif = donnees["IDtarif"]
        self.nomTarif = donnees["nomTarif"]
        self.nomCategorieTarif = donnees["nomCategorieTarif"]
        self.IDfacture = donnees["IDfacture"]
        if self.IDfacture == None or self.IDfacture == "" :
            self.label_facture = u"Non facturé"
        else:
            num_facture = donnees["num_facture"]
            date_facture = donnees["date_facture"]
            if type(num_facture) == int :
                num_facture = str(num_facture)
            self.label_facture = u"n°%s" % num_facture
        self.IDfamille = donnees["IDfamille"]
        self.IDindividu = donnees["IDindividu"]
        self.nomIndividu = donnees["nomIndividu"]
        self.prenomIndividu = donnees["prenomIndividu"]
        if self.prenomIndividu == None :
            self.prenomIndividu = u""
        if self.nomIndividu != None :
            self.nomCompletIndividu = u"%s %s" % (self.nomIndividu, self.prenomIndividu)
        else:
            self.nomCompletIndividu = u""
        self.ventilationPassee = donnees["ventilationPassee"]
        if self.ventilationPassee == None :
            self.ventilationPassee = 0.0
        self.ventilationActuelle = 0.0
        self.resteAVentiler = self.montant - self.ventilationPassee - self.ventilationActuelle
        
        # Items HyperTreeList
        self.item = None
        self.itemParent = None
        self.track_regroupement = None
        
        # Contrôles
        self.ctrl_checkbox = None
        self.ctrl_ventilation_totale = None
        self.ctrl_ventilation_actuelle  = None
                
    def Ventiler(self, montant=None, importation=False):
        if montant != None :
            # Tout ventiler
            self.ventilationActuelle = montant
        else:
            # Ventiler uniquement le montant donné
            self.ventilationActuelle = self.resteAVentiler
        self.MAJ(importation) 
    
    def MAJ(self, importation=False):
        self.resteAVentiler = self.montant - self.ventilationPassee - self.ventilationActuelle
        self.ctrl_checkbox.MAJ(importation) 
        self.ctrl_ventilation_totale.MAJ() 
        self.ctrl_ventilation_actuelle.MAJ() 
        self.MAJtotal() 
    
    def MAJtotal(self):
        self.track_regroupement.MAJ()
    
    def GetEtat(self):
        """ Retourne si coché ou non """
        return self.ctrl_checkbox.GetEtat() 


# -------------------------------------------------------------------------------------------------------------------


class CTRL_Checkbox_regroupement(wx.Panel):
    def __init__(self, parent, item=None, label=u""):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.item = item
        self.track_regroupement = None

        self.SetBackgroundColour(COULEUR_FOND_REGROUPEMENT)

        # Checkbox
        self.cb = wx.CheckBox(self, id=-1, label=label) 
        self.cb.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.cb, 1, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        # Binds
        self.cb.Bind(wx.EVT_CHECKBOX, self.OnCheck)

    def OnCheck(self, event):
        etat = self.cb.GetValue()
        self.track_regroupement.Cocher(etat)
        self.GetGrandParent().MAJbarreInfos()
       
    def SetEtat(self, etat=False):
        if etat != None :
            self.cb.SetValue(etat)
    
    def GetEtat(self):
        return self.cb.GetValue()

# -------------------------------------------------------------------------------------------------------------------

class CTRL_Total(wx.Panel):
    def __init__(self, parent, item=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.item = item
        self.total = 0.0
        
        self.SetSize((55, -1))
        self.SetMinSize((55, -1))
        self.SetBackgroundColour(COULEUR_FOND_REGROUPEMENT)
        self.SetForegroundColour(COULEUR_TEXTE_REGROUPEMENT)
                
        # Contrôle montant
        self.ctrl_montant = wx.StaticText(self, -1, u"")
##        self.ctrl_montant.SetToolTipString(u"Montant déjà ventilé")
        self.ctrl_montant.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu.Add( (1, 1), 0, wx.EXPAND|wx.ALL, 0)
        grid_sizer_contenu.Add(self.ctrl_montant, 0, wx.TOP, 3)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
        self.grid_sizer_contenu = grid_sizer_contenu
        
        self.MAJ() 
                
    def MAJ(self):
        # Label montant
        self.ctrl_montant.SetLabel(u"%.2f %s " % (self.total, SYMBOLE))
        self.grid_sizer_contenu.Layout()
        self.Refresh() 
    
    def SetMontant(self, montant=0.0):
        self.total = montant
        self.MAJ() 
        
# -------------------------------------------------------------------------------------------------------------------

class CTRL_Checkbox(wx.Panel):
    def __init__(self, parent, IDprestation=None, track=None, label="", infobulle=""):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDprestation = IDprestation
        self.track = track

        self.SetBackgroundColour((255, 255, 255))

        # Image
        self.imgTotal = wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG)
        self.imgAttention = wx.Bitmap("Images/16x16/Attention.png", wx.BITMAP_TYPE_PNG)
        self.imgNul = wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG)
        self.ctrl_image = wx.StaticBitmap(self, -1, self.imgNul)
        self.ctrl_image.SetToolTipString(u"Etat de la ventilation pour cette prestation")

        # Checkbox
        self.cb = wx.CheckBox(self, id=-1, label=label) 
        self.cb.SetToolTipString(infobulle)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_image, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.cb, 1, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        # Binds
        self.cb.Bind(wx.EVT_CHECKBOX, self.OnCheck)

    def MAJ(self, importation=False):
        if importation == True :
            self.SetEtat(True)
        # Couleur du fond et Image
        if self.track.resteAVentiler == 0.0 and self.GetEtat() == True : 
            self.ctrl_image.SetBitmap(self.imgTotal)
        elif self.track.resteAVentiler >= 0.0 : 
            self.ctrl_image.SetBitmap(self.imgNul)
        else: 
            self.ctrl_image.SetBitmap(self.imgAttention)

    def OnCheck(self, event):
        etat = self.cb.GetValue()
        self.Cocher(etat)
    
    def Cocher(self, etat=True):
        if etat == True :
            self.track.Ventiler(montant=None)
        else:
            self.track.Ventiler(montant=0.0)
            self.track.track_regroupement.ctrl_checkbox_regroupement.SetEtat(False)
        # MAJ de la barre d'infos du panel parent
        self.GetGrandParent().MAJbarreInfos()
       
    def SetEtat(self, etat=False):
        if etat != None :
            self.cb.SetValue(etat)
    
    def GetEtat(self):
        return self.cb.GetValue()

# -------------------------------------------------------------------------------------------------------------------


class CTRL_Montant_prestation(wx.Panel):
    def __init__(self, parent, IDprestation=None, track=None, montantPrestation=0.0):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDprestation = IDprestation
        self.track = track
        
        self.SetSize((55, -1))
        self.SetMinSize((55, -1))
        self.SetBackgroundColour((255, 255, 255))
                
        # Contrôle montant
        self.ctrl_montant = wx.StaticText(self, -1, u"%.2f %s " % (montantPrestation, SYMBOLE))
        self.ctrl_montant.SetToolTipString(u"Montant de la prestation")
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu.Add( (1, 1), 0, wx.EXPAND|wx.ALL, 0)
        grid_sizer_contenu.Add(self.ctrl_montant, 0, wx.TOP, 1)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
        self.grid_sizer_contenu = grid_sizer_contenu
        
        
# -------------------------------------------------------------------------------------------------------------------


class CTRL_Ventilation_totale(wx.Panel):
    def __init__(self, parent, IDprestation=None, track=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDprestation = IDprestation
        self.track = track
        
        self.SetSize((55, -1))
        self.SetMinSize((55, -1))
                
        # Contrôle montant
        self.ctrl_montant = wx.StaticText(self, -1, u"0.00 %s" % SYMBOLE)
        self.ctrl_montant.SetToolTipString(u"Montant déjà ventilé")
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu.Add( (1, 1), 0, wx.EXPAND|wx.ALL, 0)
        grid_sizer_contenu.Add(self.ctrl_montant, 0, wx.TOP, 1)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
        self.grid_sizer_contenu = grid_sizer_contenu
        
        self.MAJ() 
                
    def MAJ(self):
        # Label montant
        self.ctrl_montant.SetLabel(u"%.2f %s " % (self.track.resteAVentiler, SYMBOLE))
        # Couleur du fond et Image
        if self.track.resteAVentiler == 0.0 and self.track.ctrl_checkbox.GetEtat() : 
            self.SetBackgroundColour(COULEUR_TOTAL)
        elif self.track.resteAVentiler == self.track.montant : 
            self.SetBackgroundColour(COULEUR_NUL)
        else: 
            self.SetBackgroundColour(COULEUR_PARTIEL)
        self.grid_sizer_contenu.Layout()
        self.Refresh() 

        
# -------------------------------------------------------------------------------------------------------------------

class CTRL_Ventilation_actuelle(wx.Panel):
    def __init__(self, parent, IDprestation=None, track=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDprestation = IDprestation
        self.track = track
                        
        # Contrôle montant
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self, size=(55, -1))
        self.ctrl_montant.SetValue("")
        self.ctrl_montant.SetToolTipString(u"Cliquez ici pour modifier manuellement le montant ventilé")
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
##        grid_sizer_base.Add(self.ctrl_image, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.ctrl_montant, 1, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        
        self.ctrl_montant.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def OnKillFocus(self, event):
        # Vérification de la saisie du montant
        valide, messageErreur = self.ctrl_montant.Validation()
        if valide == False :
            wx.MessageBox(messageErreur, "Erreur de saisie")
            self.GetGrandParent().MAJbarreInfos(erreur=True)
        else:
            montant = float(self.ctrl_montant.GetValue())
            self.ctrl_montant.SetValue(u"%.2f" % montant)
            # Met à jour le track
            self.track.ventilationActuelle = montant
            self.track.MAJ() 
            self.GetGrandParent().MAJbarreInfos()
        event.Skip() 
    
    def MAJ(self):
        if self.track.ctrl_checkbox.cb.GetValue() == True :
            self.Enable(True)
            self.ctrl_montant.SetMontant(self.track.ventilationActuelle)
        else:
            self.Enable(False)
            self.ctrl_montant.SetValue("")
            
        

# -------------------------------------------------------------------------------------------------------------------
            
class CTRL_Ventilation(HTL.HyperTreeList):
    def __init__(self, parent, IDcompte_payeur=None, IDreglement=None): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.IDcompte_payeur = IDcompte_payeur
        self.IDreglement = IDreglement
        self.listeTracks = []
        self.dictVentilation = {}
        self.dictVentilationInitiale = {}
        self.ventilationValide = True
        
        if "linux" in sys.platform :
            defaultFont = self.GetFont()
            defaultFont.SetPointSize(8)
            self.SetFont(defaultFont)

        # Key de regroupement
        self.KeyRegroupement = "periode" # individu, facture, date, periode
        
        # Création des colonnes
        listeColonnes = [
            ( u"Date", 225, wx.ALIGN_LEFT),
            ( u"Individu", 95, wx.ALIGN_LEFT),
            ( u"Intitulé", 185, wx.ALIGN_LEFT),
            ( u"N° Facture", 75, wx.ALIGN_CENTRE),
            ( u"Montant", 60, wx.ALIGN_LEFT),
            ( u"A ventiler", 62, wx.ALIGN_LEFT),
            ( u"Ventilé", 60, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_VIRTUAL|wx.TR_ROW_LINES |  wx.TR_COLUMN_LINES |wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)
                    
    def Importation(self):
        if self.IDreglement == None :
            IDreglement = 0
        else:
            IDreglement = self.IDreglement
        
        # Importation des ventilations de ce règlement
        DB = GestionDB.DB()
        req = """SELECT IDventilation, IDprestation, montant
        FROM ventilation
        WHERE IDreglement=%d
        ;""" % IDreglement
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        self.dictVentilation = {}
        self.dictVentilationInitiale
        for IDventilation, IDprestation, montant in listeDonnees :
            self.dictVentilation[IDprestation] = montant
            self.dictVentilationInitiale[IDprestation] = IDventilation
        
        # Importation des données
        req = """
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, date, categorie, label, prestations.montant, 
        prestations.IDactivite, activites.nom,
        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom, 
        prestations.IDfacture, factures.numero, factures.date_edition,
        IDfamille, prestations.IDindividu, 
        individus.nom, individus.prenom,
        SUM(ventilation.montant) AS montant_ventilation
        FROM prestations
        LEFT JOIN ventilation ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON tarifs.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        LEFT JOIN factures ON prestations.IDfacture = factures.IDfacture
        WHERE prestations.IDcompte_payeur = %d 
        GROUP BY prestations.IDprestation
        ORDER BY date
        ;""" % self.IDcompte_payeur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        listeTracks = []
        for IDprestation, IDcompte_payeur, date, categorie, label, montant, IDactivite, nomActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, num_facture, date_facture, IDfamille, IDindividu, nomIndividu, prenomIndividu, montantVentilation in listeDonnees :
            if num_facture == None : num_facture = 0
            if montantVentilation < montant or IDprestation in self.dictVentilation.keys() :
                date = DateEngEnDateDD(date)
                if self.dictVentilation.has_key(IDprestation) :
                    montantVentilation = montantVentilation - self.dictVentilation[IDprestation] 
                dictTemp = {
                    "IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur, "date" : date, "categorie" : categorie,
                    "label" : label, "montant" : montant, "IDactivite" : IDactivite, "nomActivite" : nomActivite, "IDtarif" : IDtarif, "nomTarif" : nomTarif, 
                    "nomCategorieTarif" : nomCategorieTarif, "IDfacture" : IDfacture, "num_facture" : num_facture, "date_facture" : date_facture, 
                    "IDfamille" : IDfamille, "IDindividu" : IDindividu, "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu,
                    "ventilationPassee" : montantVentilation,
                    }
                track = Track(dictTemp)
                listeTracks.append(track)
        
        # Si trop de prestations impayées à afficher dans le contrôle
##        print "nbre prestations =", len(listeTracks)
        maxPrestationsAffichables = 300
        if len(listeTracks) > maxPrestationsAffichables :
            message = u"Avertissement\n\nCette famille a %d prestations impayées alors que cette fonctionnalité peut actuellement planter lorsqu'elle en affiche plus de %d (Un correctif sera proposé ultérieurement). \n\nSouhaitez-vous afficher uniquement les %d premières prestations de la liste ?" % (len(listeTracks), maxPrestationsAffichables, maxPrestationsAffichables)
            dlg = wx.MessageDialog(None, message, u"Avertissement", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_YES :
                listeTracks = listeTracks[:maxPrestationsAffichables]
            dlg.Destroy()

        return listeTracks

    def Sauvegarde(self, IDreglement=None):
        # --------------- Sauvegarde -----------------------
        DB = GestionDB.DB()
        
        for track in self.listeTracks :
            IDprestation = track.IDprestation
            montant = track.ventilationActuelle
            
            if self.dictVentilationInitiale.has_key(IDprestation) :
                IDventilation = self.dictVentilationInitiale[IDprestation]
            else:
                IDventilation = None
            
            if track.GetEtat() == True :
                # Ajout ou modification
                listeDonnees = [    
                        ("IDreglement", IDreglement),
                        ("IDcompte_payeur", self.IDcompte_payeur),
                        ("IDprestation", IDprestation),
                        ("montant", montant),
                    ]
                if IDventilation == None :
                    IDventilation = DB.ReqInsert("ventilation", listeDonnees)
                else:
                    DB.ReqMAJ("ventilation", listeDonnees, "IDventilation", IDventilation)
            else :
                # Suppression
                if IDventilation != None :
                    DB.ReqDEL("ventilation", "IDventilation", IDventilation)
        
        DB.Close()
        
        return True
    
    def SetRegroupement(self, key):
        self.KeyRegroupement = key
        self.MAJ() 

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.Freeze()
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(u"Racine")
        self.Remplissage()
        self.Thaw() 
        self.MAJbarreInfos()

    def Remplissage(self):
        listeTracks = self.Importation()
        self.dictControles = {} 
        
        # Regroupement
        dictTracks = {}
        listeKeys = []
        for track in listeTracks :
            if self.KeyRegroupement == "individu" : 
                key = track.IDindividu
                if key == 0 or key == None :
                    label = u"Prestations familiales"
                else:
                    label = track.nomCompletIndividu
            if self.KeyRegroupement == "facture" : 
                key = track.IDfacture
                label = track.label_facture
            if self.KeyRegroupement == "date" : 
                key = track.date
                label = track.date_complete
            if self.KeyRegroupement == "periode" : 
                key = track.periode
                label = track.periode_complete
            
            if dictTracks.has_key(key) == False :
                dictTracks[key] = { "label" : label, "total" : 0.0, "prestations" : [] }
                listeKeys.append(key)
            dictTracks[key]["prestations"].append(track)
            dictTracks[key]["total"] += track.montant
        
        # Tri des Keys
        listeKeys.sort()
        
        # Création des branches
        self.dictTracksRegroupement = {}
        for key in listeKeys :
            
            # Niveau 1
            label = dictTracks[key]["label"]
            
            regroupement = self.AppendItem(self.root, "")
##            regroupement = self.AppendItem(self.root, label, ct_type=1)
            self.SetPyData(regroupement, None)
            self.SetItemBold(regroupement, True)
            self.SetItemBackgroundColour(regroupement, COULEUR_FOND_REGROUPEMENT)
            
            # Checkbox Regroupement
            ctrl_checkbox_regroupement = CTRL_Checkbox_regroupement(self.GetMainWindow(), item=regroupement, label=label)
            self.SetItemWindow(regroupement, ctrl_checkbox_regroupement, 0)
            
            # Total des montants des prestations
            ctrl_total_prestations = CTRL_Total(self.GetMainWindow(), item=regroupement)
            self.SetItemWindow(regroupement, ctrl_total_prestations, 4)
            
            # Total déjà ventilé
            ctrl_total_aVentiler = CTRL_Total(self.GetMainWindow(), item=regroupement)
            self.SetItemWindow(regroupement, ctrl_total_aVentiler, 5)

            # Total ventilation actuelle
            ctrl_total_ventilationActuelle = CTRL_Total(self.GetMainWindow(), item=regroupement)
            self.SetItemWindow(regroupement, ctrl_total_ventilationActuelle, 6)

            # Mémorisation des contrôles et données du regroupement
            trackRegroupement = Track_regroupement()
            trackRegroupement.ctrl_checkbox_regroupement = ctrl_checkbox_regroupement
            trackRegroupement.ctrl_total_prestations = ctrl_total_prestations
            trackRegroupement.ctrl_total_aVentiler = ctrl_total_aVentiler
            trackRegroupement.ctrl_total_ventilationActuelle = ctrl_total_ventilationActuelle
            trackRegroupement.listeTracks = dictTracks[key]["prestations"]
            if self.KeyRegroupement == "facture" : 
                trackRegroupement.IDfacture = key
            self.dictTracksRegroupement[regroupement] = trackRegroupement
            
            ctrl_checkbox_regroupement.track_regroupement = trackRegroupement

            # Niveau 2
            for track in dictTracks[key]["prestations"] :
                
                label = DateComplete(track.date)
                prestation = self.AppendItem(regroupement, "")
                self.SetPyData(prestation, track.IDprestation)
                
                # Mémorisation des items dans le track
                track.item = prestation
                track.itemParent = regroupement
                track.track_regroupement = trackRegroupement
                
                # Case à cocher + Date
                ctrl_checkbox = CTRL_Checkbox(self.GetMainWindow(), IDprestation=track.IDprestation, track=track, label=label, infobulle=u"")
                self.SetItemWindow(prestation, ctrl_checkbox, 0)
                track.ctrl_checkbox = ctrl_checkbox
                
                self.SetItemText(prestation, track.prenomIndividu, 1)
                self.SetItemText(prestation, track.label, 2)
                self.SetItemText(prestation, track.label_facture, 3)
                
                # Montant de la prestation
                ctrl_montant_prestation = CTRL_Montant_prestation(self.GetMainWindow(), track=track, montantPrestation=track.montant)
                self.SetItemWindow(prestation, ctrl_montant_prestation, 4)              
                
                # Montant déjà ventilé
                ctrl_ventilation_totale = CTRL_Ventilation_totale(self.GetMainWindow(), track=track)
                self.SetItemWindow(prestation, ctrl_ventilation_totale, 5)
                track.ctrl_ventilation_totale = ctrl_ventilation_totale
                
                # Montant ventilé
                ctrl_ventilation_actuelle = CTRL_Ventilation_actuelle(self.GetMainWindow(), track=track)
                self.SetItemWindow(prestation, ctrl_ventilation_actuelle, 6)
                ctrl_ventilation_actuelle.Enable(False)
                track.ctrl_ventilation_actuelle = ctrl_ventilation_actuelle
            
            # Met à jour les totaux du niveau de regroupement
            trackRegroupement.MAJ() 
        
        self.ExpandAllChildren(self.root)
        
        # Pour éviter le bus de positionnement des contrôles
        self.GetMainWindow().CalculatePositions() 
        
        self.listeTracks = listeTracks
        
        # Importation des ventilations déjà définies
        for track in listeTracks :
            if self.dictVentilation.has_key(track.IDprestation) :
                montant = self.dictVentilation[track.IDprestation]
                track.Ventiler(montant, importation=True)
                

    
    def OnCompareItems(self, item1, item2):
        if self.GetPyData(item1) > self.GetPyData(item2) :
            return 1
        elif self.GetPyData(item1) < self.GetPyData(item2) :
            return -1
        else:
            return 0
                        
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
    
    def MAJbarreInfos(self, erreur=None):
        self.dictVentilation = {}
        total = 0.0
        for track in self.listeTracks :
            total += track.ventilationActuelle
            self.dictVentilation[track.IDprestation] = track.ventilationActuelle
        self.parent.MAJbarreInfos(total, erreur)

    def SelectionneFacture(self, IDfacture=None):
        # Afficher par facture
        self.SetRegroupement("facture")
        # Coche les prestations liées à la facture données
        for treeItemList, trackRegroupement in self.dictTracksRegroupement.iteritems():
            if trackRegroupement.IDfacture == IDfacture :
                checkBox = trackRegroupement.ctrl_checkbox_regroupement
                checkBox.SetEtat(True)
                checkBox.OnCheck(None)
                
    def GetTotalVentile(self):
        total = 0.0
        for track in self.listeTracks :
            total += track.ventilationActuelle
        return total

    def GetTotalRestePrestationsAVentiler(self):
        total = 0.0
        for track in self.listeTracks :
            total += track.resteAVentiler
        return total
    
    
    

# -----------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, IDcompte_payeur=None, IDreglement=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDcompte_payeur = IDcompte_payeur
        self.IDreglement = IDreglement
        self.montant_reglement = FloatToDecimal(0.0)
        self.total_ventilation = FloatToDecimal(0.0)
        self.validation = True
        
        if "linux" in sys.platform :
            defaultFont = self.GetFont()
            defaultFont.SetPointSize(8)
            self.SetFont(defaultFont)

        # Regroupement
        self.label_regroupement = wx.StaticText(self, -1, u"Regrouper par :")
        self.radio_periode = wx.RadioButton(self, -1, u"Mois", style = wx.RB_GROUP)
        self.radio_facture = wx.RadioButton(self, -1, u"Facture")
        self.radio_individu = wx.RadioButton(self, -1, u"Individu")
        self.radio_date = wx.RadioButton(self, -1, u"Date")
        
        # Commandes rapides
        self.label_hyperliens_1 = wx.StaticText(self, -1, u"Ventiler ")
        self.hyper_automatique = Hyperlien(self, label=u"automatiquement", infobulle=u"Cliquez ici pour ventiler automatiquement le crédit restant", URL="automatique")
        self.label_hyperliens_2 = wx.StaticText(self, -1, u" | ")
        self.hyper_tout = Hyperlien(self, label=u"tout", infobulle=u"Cliquez ici pour tout ventiler", URL="tout")
        self.label_hyperliens_3 = wx.StaticText(self, -1, u" | ")
        self.hyper_rien = Hyperlien(self, label=u"rien", infobulle=u"Cliquez ici pour ne rien ventiler", URL="rien")
        
        # Liste de la ventilation
        self.ctrl_ventilation = CTRL_Ventilation(self, IDcompte_payeur, IDreglement)
        
        # Etat de la ventilation
        self.imgOk = wx.Bitmap("Images/16x16/Ok4.png", wx.BITMAP_TYPE_PNG)
        self.imgErreur = wx.Bitmap("Images/16x16/Interdit2.png", wx.BITMAP_TYPE_PNG)
        self.imgAddition = wx.Bitmap("Images/16x16/Addition.png", wx.BITMAP_TYPE_PNG)
        self.ctrl_image = wx.StaticBitmap(self, -1, self.imgAddition)
        
        self.ctrl_info = wx.StaticText(self, -1, u"Vous pouvez encore ventiler 30.90 €")
        self.ctrl_info.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioRegroupement, self.radio_periode)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioRegroupement, self.radio_facture)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioRegroupement, self.radio_individu)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioRegroupement, self.radio_date)
                
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        grid_sizer_barre_haut = wx.FlexGridSizer(rows=1, cols=12, vgap=5, hgap=1)
        grid_sizer_barre_haut.Add(self.label_regroupement, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_barre_haut.Add(self.radio_periode, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_barre_haut.Add(self.radio_facture, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_barre_haut.Add(self.radio_individu, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_barre_haut.Add(self.radio_date, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_barre_haut.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_barre_haut.Add(self.label_hyperliens_1, 0, 0, 0)
        grid_sizer_barre_haut.Add(self.hyper_automatique, 0, 0, 0)
        grid_sizer_barre_haut.Add(self.label_hyperliens_2, 0, 0, 0)
        grid_sizer_barre_haut.Add(self.hyper_tout, 0, 0, 0)
        grid_sizer_barre_haut.Add(self.label_hyperliens_3, 0, 0, 0)
        grid_sizer_barre_haut.Add(self.hyper_rien, 0, 0, 0)
        grid_sizer_barre_haut.AddGrowableCol(5)
        grid_sizer_base.Add(grid_sizer_barre_haut, 1, wx.EXPAND|wx.BOTTOM, 5)

        grid_sizer_base.Add(self.ctrl_ventilation, 1, wx.EXPAND, 0)
        
        grid_sizer_barre_bas = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_barre_bas.Add( (400, 5), 0, 0, 0)
        grid_sizer_barre_bas.Add(self.ctrl_image, 0, 0, 0)
        grid_sizer_barre_bas.Add(self.ctrl_info, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(grid_sizer_barre_bas, 1, wx.EXPAND|wx.TOP, 2)
        
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
    
    def OnRadioRegroupement(self, event):
        if self.radio_periode.GetValue() == True : key = "periode"
        if self.radio_facture.GetValue() == True : key = "facture"
        if self.radio_individu.GetValue() == True : key = "individu"
        if self.radio_date.GetValue() == True : key = "date"
        self.ctrl_ventilation.SetRegroupement(key)
    
    def MAJ(self):
        self.ctrl_ventilation.MAJ() 
        self.MAJinfos() 
    
    def SetMontantReglement(self, montant=FloatToDecimal(0.0)):
        if montant == None : return
        if type(montant) != decimal.Decimal :
            montant = FloatToDecimal(montant)
        self.montant_reglement = montant
        self.MAJinfos() 
    
    def MAJbarreInfos(self, total=FloatToDecimal(0.0), erreur=None):
        self.total_ventilation = total
        self.MAJinfos(erreur) 
    
    def MAJinfos(self, erreur=None):
        """ Recherche l'état """
        if self.montant_reglement == FloatToDecimal(0.0) :
            self.validation = "erreur"
            self.ctrl_image.SetBitmap(self.imgErreur)
            self.ctrl_info.SetLabel(u"Vous devez déjà saisir un montant pour ce règlement !")
            return

##        if self.montant_reglement < FloatToDecimal(0.0) :
##            self.validation = "ok"
##            self.ctrl_image.SetBitmap(self.imgOk)
##            self.ctrl_info.SetLabel(u"Ventilation non obligatoire")
##            return

        if erreur == True :
            self.validation = "erreur"
            self.ctrl_image.SetBitmap(self.imgErreur)
            self.ctrl_info.SetLabel(u"Vous avez saisi un montant non valide !")
            return
        
        creditAVentiler = FloatToDecimal(self.montant_reglement) - FloatToDecimal(self.total_ventilation)
        
        totalRestePrestationsAVentiler = FloatToDecimal(self.ctrl_ventilation.GetTotalRestePrestationsAVentiler())
        if creditAVentiler > totalRestePrestationsAVentiler :
            creditAVentiler = totalRestePrestationsAVentiler
        
        # Recherche de l'état
        if creditAVentiler == FloatToDecimal(0.0) :
            self.validation = "ok"
            label = u"Le règlement a été correctement ventilé !"
        elif creditAVentiler > FloatToDecimal(0.0) :
            self.validation = "addition"
            label = u"Vous devez encore ventiler %.2f %s !" % (creditAVentiler, SYMBOLE)
        elif creditAVentiler < FloatToDecimal(0.0) :
            self.validation = "trop"
            label = u"Vous avez ventilé %.2f %s en trop !" % (-creditAVentiler, SYMBOLE)
        # Affiche l'image
        if self.validation == "ok" : self.ctrl_image.SetBitmap(self.imgOk)
        if self.validation == "addition" : self.ctrl_image.SetBitmap(self.imgAddition)
        if self.validation == "trop" : self.ctrl_image.SetBitmap(self.imgErreur)
        # MAJ le label d'infos
        self.ctrl_info.SetLabel(label)
        # Colore Label Ventilation Auto
        self.ColoreLabelVentilationAuto() 
        
    def Validation(self):
        creditAVentiler = FloatToDecimal(self.montant_reglement) - FloatToDecimal(self.total_ventilation)
        if self.validation == "ok" :
            return True
        if self.validation == "addition" :
            totalRestePrestationsAVentiler = FloatToDecimal(self.ctrl_ventilation.GetTotalRestePrestationsAVentiler())
            if creditAVentiler > totalRestePrestationsAVentiler :
                creditAVentiler = totalRestePrestationsAVentiler
            if creditAVentiler > FloatToDecimal(0.0) :
                dlg = wx.MessageDialog(self, u"Vous devez encore ventiler %.2f %s.\n\nEtes-vous sûr de quand même vouloir valider et fermer ?" % (creditAVentiler, SYMBOLE), u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse !=  wx.ID_YES :
                    return False
        if self.validation == "trop" :
            dlg = wx.MessageDialog(self, u"Vous avez ventilé %.2f %s en trop !" % (-creditAVentiler, SYMBOLE), u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if self.validation == "erreur" :
            dlg = wx.MessageDialog(self, u"La ventilation n'est pas valide. Veuillez la vérifier...", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True
        
    def Sauvegarde(self, IDreglement=None):
        self.ctrl_ventilation.Sauvegarde(IDreglement) 
        # Si le montant du règlement est négatif :
##        if self.montant_reglement < 0.0 : 
##            DB = GestionDB.DB() 
##            DB.ReqDEL("ventilation", "IDreglement", IDreglement)
##            DB.Close() 
        
    def SelectionneFacture(self, IDfacture=None):
        self.radio_facture.SetValue(True)
        self.ctrl_ventilation.SelectionneFacture(IDfacture)
    
    def ColoreLabelVentilationAuto(self):
        aVentiler = FloatToDecimal(0.0)
        for track in self.ctrl_ventilation.listeTracks :
             aVentiler += FloatToDecimal(track.montant) - FloatToDecimal(track.ventilationPassee)
        if self.montant_reglement == aVentiler :
            couleur = wx.Colour(0, 200, 0)
        else :
            couleur = "BLUE"
        self.hyper_automatique.SetColours(couleur, couleur, couleur)
        self.hyper_automatique.UpdateLink()

    def VentilationAuto(self):
        """ Procédure de ventilation automatique """
        # Vérifie qu'il n'y a pas de prestations négatives
        for track in self.ctrl_ventilation.listeTracks :
            if FloatToDecimal(track.montant) < FloatToDecimal(0.0) :
                dlg = wx.MessageDialog(None, u"Ventilation automatique impossible !\n\nLa ventilation automatique n'est pas compatible avec les prestations comportant un montant négatif ! Vous devez donc effectuer une ventilation manuelle.", u"Information", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        # Ventilation automatique
        totalVentilation = FloatToDecimal(self.ctrl_ventilation.GetTotalVentile())
        resteVentilation = self.montant_reglement - totalVentilation
        if self.montant_reglement == FloatToDecimal(0.0) :
            dlg = wx.MessageDialog(self, u"Vous avez déjà saisir un montant pour ce règlement !", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if resteVentilation <= FloatToDecimal(0.0) :
            dlg = wx.MessageDialog(self, u"Vous avez déjà ventilé tout le crédit disponible !", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        for track in self.ctrl_ventilation.listeTracks :
            aVentiler = resteVentilation
            if aVentiler > FloatToDecimal(track.resteAVentiler) : 
                aVentiler = FloatToDecimal(track.resteAVentiler)
            if aVentiler > FloatToDecimal(0.0) :
                track.Ventiler(float(aVentiler + FloatToDecimal(track.ventilationActuelle)), importation=True)
                resteVentilation -= FloatToDecimal(aVentiler)
        self.ctrl_ventilation.MAJbarreInfos()
        
    def VentilationTout(self):
        for track in self.ctrl_ventilation.listeTracks :
            aVentiler = track.montant - track.ventilationPassee
            track.Ventiler(aVentiler, importation=True)
        self.ctrl_ventilation.MAJbarreInfos()
        
    def VentilationRien(self):
        for track in self.ctrl_ventilation.listeTracks :
            track.Ventiler(0)
            track.ctrl_checkbox.SetEtat(False)
            track.ctrl_ventilation_actuelle.MAJ() 
            track.track_regroupement.ctrl_checkbox_regroupement.SetEtat(False)
        self.ctrl_ventilation.MAJbarreInfos()

        
# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.ctrl = CTRL(panel, IDcompte_payeur=11, IDreglement=None)
        self.ctrl.SetMontantReglement(8.00)
        self.ctrl.MAJ() 
    
        self.bouton_test = wx.Button(panel, -1, u"Bouton de test")
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
    
    def OnBoutonTest(self, event):
        """ Bouton de test """
        self.ctrl.VentilationAuto()
                    
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
