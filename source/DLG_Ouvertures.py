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
import sys
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
import datetime
import calendar
import traceback
import GestionDB
import CTRL_Bandeau
import wx.lib.agw.pybusyinfo as PBI

try: import psyco; psyco.full()
except: pass

COULEUR_DATE = "#C0C0C0"
COULEUR_OUVERTURE = "#FFE900" #(0, 230, 0)
COULEUR_FERMETURE = "#8EA0AA" #"#F7ACB2"
COULEUR_VACANCES = "#F3FD89"
COULEUR_FERIE = "#828282"


def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

def CreationImage(largeur, hauteur, couleur=None):
    """ couleur peut être RGB ou HEXA """
    if type(couleur) == str : r, v, b = hex_to_rgb(couleur)
    if type(couleur) == tuple : r, v, b = couleur
    bmp = wx.EmptyImage(largeur, hauteur, True)
    bmp.SetRGBRect((0, 0, largeur, hauteur), r, v, b)
    return bmp.ConvertToBitmap()


class MyRowLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, row):
        dc.SetBrush(wx.Brush(self._bgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetRowLabelAlignment()
        text = grid.GetRowLabelValue(row)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

class MyColLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor):
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, col):
        dc.SetBrush(wx.Brush(self._bgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)



class Calendrier(gridlib.Grid, glr.GridWithLabelRenderersMixin): 
    def __init__(self, parent, IDactivite=None):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.parent = parent
        self.moveTo = None
        self.IDactivite = IDactivite
        self.CreateGrid(1, 1)
        self.SetRowLabelSize(180)
        self.DisableDragColSize()
        self.DisableDragRowSize()
        
        self.listeVacances = self.GetListeVacances()
        self.listeFeries = self.GetListeFeries() 
        self.dictOuvertures = {}
        self.dictRemplissage = {}
        self.dictConso = {}
        self.datesValiditeActivite = self.GetValiditeActivite() 
        self.dictUnitesGroupes = self.GetDictUnitesGroupes() 
        self.clipboard = None # Date à copier pour  la fonction copier-coller
        self.annee = None
        self.mois = None
        self.afficherTousGroupes = None

        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
    
    def Sauvegarde(self):
        # ---- Nouvelle version optimisée ----

        DB = GestionDB.DB()
        
        # Ouvertures
        listeAjouts = []
        listeSuppressions = []
        for dateDD, dictGroupes in self.dictOuvertures.iteritems() :
            for IDgroupe, dictUnites in dictGroupes.iteritems() :
                for IDunite, dictValeurs in dictUnites.iteritems() :
                    etat = dictValeurs["etat"]
                    initial = dictValeurs["initial"]
                    IDouverture = dictValeurs["IDouverture"]
                    
                    if etat != initial :
                        # Si la valeur a été modifiée :
                        if IDouverture == None and etat == True :
                            listeAjouts.append((self.IDactivite, IDunite, IDgroupe, str(dateDD)))
                        elif IDouverture != None and etat == False :
                            listeSuppressions.append(IDouverture)
                        else:
                            pass
        
        # Ajouts
        if len(listeAjouts) > 0 :
            DB.Executermany("INSERT INTO ouvertures (IDactivite, IDunite, IDgroupe, date) VALUES (?, ?, ?, ?)", listeAjouts, commit=False)
        # Suppression
        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 : 
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else : 
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM ouvertures WHERE IDouverture IN %s" % conditionSuppression)
        # Confirmation
        DB.Commit() 
        
        # Remplissage
        listeAjouts = []
        listeModifications = []
        listeSuppressions = []
        for dateDD, dictGroupes in self.dictRemplissage.iteritems() :
            for IDgroupe, dictUnites in dictGroupes.iteritems() :
                for IDunite_remplissage, dictValeurs in dictUnites.iteritems() :
                    places = dictValeurs["places"]
                    initial = dictValeurs["initial"]
                    IDremplissage = dictValeurs["IDremplissage"]
                    if places != initial :
                        # Si la valeur a été modifiée :
                        if IDremplissage == None and places != 0 :
                            listeAjouts.append((self.IDactivite, IDunite_remplissage, IDgroupe, str(dateDD), places))
                        elif IDremplissage != None and places != 0 :
                            listeModifications.append((self.IDactivite, IDunite_remplissage, IDgroupe, str(dateDD), places, IDremplissage))
                        elif IDremplissage != None and places == 0 :
                            listeSuppressions.append(IDremplissage)
                        else:
                            pass

        # Ajouts
        if len(listeAjouts) > 0 :
            DB.Executermany("INSERT INTO remplissage (IDactivite, IDunite_remplissage, IDgroupe, date, places) VALUES (?, ?, ?, ?, ?)", listeAjouts, commit=False)
        # Modifications
        if len(listeModifications) > 0 :
            DB.Executermany("UPDATE remplissage SET IDactivite=?, IDunite_remplissage=?, IDgroupe=?, date=?, places=? WHERE IDremplissage=?", listeModifications, commit=False)
        # Suppression
        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 : 
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else : 
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM remplissage WHERE IDremplissage IN %s" % conditionSuppression)
        # Confirmation
        DB.Commit() 
        
        DB.Close() 

        
    def MAJ(self, annee=None, mois=None):
        self.annee = annee
        self.mois = mois
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        self.InitGrid(annee, mois)
        self.Refresh()
        
    def InitGrid(self, annee, mois):
        self.listeDates = self.GetListeDates(annee, mois)
        self.listeUnites = self.GetListeUnites(self.listeDates[0], self.listeDates[-1])
        self.listeUnitesRemplissage = self.GetListeUnitesRemplissage(self.listeDates[0], self.listeDates[-1])
        self.GetDictOuvertures(self.listeDates[0], self.listeDates[-1])
        self.GetDictRemplissage(self.listeDates[0], self.listeDates[-1])
        self.GetDictConso(self.listeDates[0], self.listeDates[-1])
        self.listeGroupes = self.GetListeGroupes() 
        
        nbreColonnes = len(self.listeUnites) + len(self.listeUnitesRemplissage) + 1
        self.AppendCols(nbreColonnes)
        
        dictCases = {}
        
        # ----------------- Création des colonnes -------------------------------------------------------
        largeurColonneOuverture = 50
        largeurColonneRemplissage = 60
        numColonne = 0
        
        # Colonnes Unités
        for dictUnite in self.listeUnites :
            self.SetColLabelValue(numColonne, dictUnite["abrege"])
            self.SetColSize(numColonne, largeurColonneOuverture)
            numColonne += 1
        # Colonne de séparation
        self.SetColLabelValue(numColonne, "")
        self.SetColSize(numColonne, 15)
        numColonne += 1
        # Colonnes Unités de remplissage
        for dictUniteRemplissage in self.listeUnitesRemplissage :
            self.SetColLabelValue(numColonne, dictUniteRemplissage["abrege"])
            self.SetColSize(numColonne, largeurColonneRemplissage)
            numColonne += 1
        
        
        # ------------------ Création des lignes -------------------------------------------------------
        
        nbreLignes = (len(self.listeGroupes)+1) * len(self.listeDates)
        self.AppendRows(nbreLignes)
        
        self.listeLignesDates = {}
        numLigne = 0
        for dateDD in self.listeDates :
            
            # Ligne DATE
            hauteurLigne = 20
            self.SetRowLabelValue(numLigne, DateComplete(dateDD))
            self.SetRowSize(numLigne, hauteurLigne)
            self.SetRowLabelRenderer(numLigne, MyRowLabelRenderer(COULEUR_DATE))
            self.listeLignesDates[numLigne] = dateDD
            
            numColonne = 0
            for dictUnite in self.listeUnites :
                self.SetReadOnly(numLigne, numColonne, True)
                self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                numColonne += 1
            self.SetReadOnly(numLigne, numColonne, True)
            self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
            numColonne += 1
            for dictUniteRemplissage in self.listeUnitesRemplissage :
                self.SetReadOnly(numLigne, numColonne, True)
                self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                numColonne += 1
                        
            numLigne += 1
            
            # Lignes GROUPES
            hauteurLigne = 25
            for dictGroupe in self.listeGroupes :
                IDgroupe = dictGroupe["IDgroupe"]
                self.SetRowLabelValue(numLigne, dictGroupe["nom"])
                self.SetRowSize(numLigne, hauteurLigne)
                self.SetRowLabelRenderer(numLigne, None)
                # Si vacances : entete en jaune
                if self.EstEnVacances(dateDD) == True :
                    self.SetRowLabelRenderer(numLigne, MyRowLabelRenderer(COULEUR_VACANCES))
                # Si vacances : entete en gris foncé
                if self.EstFerie(dateDD) == True :
                    self.SetRowLabelRenderer(numLigne, MyRowLabelRenderer(COULEUR_FERIE))

                numColonne = 0
                for dictUnite in self.listeUnites :
                    self.SetReadOnly(numLigne, numColonne, True)
                    self.SetCellFont(numLigne, numColonne, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL)) 
                    self.SetCellTextColour(numLigne, numColonne, (100, 100, 100) )
                    self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_RIGHT, wx.ALIGN_TOP)
                    
                    # Recherche une ouverture
                    IDunite = dictUnite["IDunite"]
                    date_debut = dictUnite["date_debut"]
                    date_fin = dictUnite["date_fin"]
                    if self.dictUnitesGroupes.has_key(IDunite) == False :
                        self.dictUnitesGroupes[IDunite] = []
                    if (IDgroupe in self.dictUnitesGroupes[IDunite] or len(self.dictUnitesGroupes[IDunite]) == 0) and(str(dateDD) >= date_debut and str(dateDD) <= date_fin) and (str(dateDD) >= self.datesValiditeActivite[0] and str(dateDD) <= self.datesValiditeActivite[1]) :
                        # Si date valide pour cette unité 
                        ouverture = self.RechercheOuverture(dateDD, IDgroupe, IDunite)
                        if ouverture == True :
                            self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_OUVERTURE)
                        else:
                            self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_FERMETURE)
                        actif = True
                    else:
                        # Hors période de validité
                        self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                        actif = False
                    
                    # Si c'est une ligne 'Tous les groupes'
                    if IDgroupe == None :
                        self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                        actif = False
                        
                    dictCases[(numLigne, numColonne)] = { "type" : "ouverture", "date" : dateDD, "actif" : actif, "IDgroupe" : IDgroupe, "IDunite" : IDunite }

                    # Ecrit le nombre de consommations dans la case
                    if self.dictConso.has_key(dateDD) :
                        if self.dictConso[dateDD].has_key(IDgroupe) :
                            if self.dictConso[dateDD][IDgroupe].has_key(IDunite) :
                                nbreConso = self.dictConso[dateDD][IDgroupe][IDunite]
                                self.SetCellValue(numLigne, numColonne, str(nbreConso))

                    numColonne += 1
                    
                self.SetReadOnly(numLigne, numColonne, True)
                self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                numColonne += 1
                
                for dictUniteRemplissage in self.listeUnitesRemplissage :
                    self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetCellEditor(numLigne, numColonne, gridlib.GridCellNumberEditor(0, 999))
                    
                    # Recherche un remplissage
                    IDunite_remplissage = dictUniteRemplissage["IDunite_remplissage"]
                    date_debut = dictUniteRemplissage["date_debut"]
                    date_fin = dictUniteRemplissage["date_fin"]
                    if str(dateDD) >= date_debut and str(dateDD) <= date_fin and (str(dateDD) >= self.datesValiditeActivite[0] and str(dateDD) <= self.datesValiditeActivite[1]) :
                        # Si date valide pour cette unité de remplissage
                        nbrePlaces = self.RechercheRemplissage(dateDD, IDgroupe, IDunite_remplissage)
                        if nbrePlaces > 0 :
                            self.SetCellValue(numLigne, numColonne, str(nbrePlaces))
                        else:
                            self.SetCellValue(numLigne, numColonne, "")
                        actif = True
                    else:
                        # Hors période de validité
                        self.SetReadOnly(numLigne, numColonne, True)
                        self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_DATE)
                        actif = False
                        
                    dictCases[(numLigne, numColonne)] = { "type" : "remplissage", "actif" : actif, "date" : dateDD, "IDgroupe" : IDgroupe, "IDunite_remplissage" : IDunite_remplissage }
                        
                    numColonne += 1
                    
                numLigne += 1
                
                self.dictCases = dictCases
    
    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False
    
    def EstFerie(self, dateDD):
        jour = dateDD.day
        mois = dateDD.month
        annee = dateDD.year        
        for type, nom, jourTmp, moisTmp, anneeTmp in self.listeFeries :
            jourTmp = int(jourTmp)
            moisTmp = int(moisTmp)
            anneeTmp = int(anneeTmp)
            if type == "fixe" :
                if jourTmp == jour and moisTmp == mois :
                    return True
            else:
                if jourTmp == jour and moisTmp == mois and anneeTmp == annee :
                    return True
        return False

    def OnLabelRightClick(self, event):
        numLigne = event.GetRow()
        if numLigne == -1 or self.listeLignesDates.has_key(numLigne) == False : return
        dateDD = self.listeLignesDates[numLigne]
        
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        item = wx.MenuItem(menuPop, 10, self.GetRowLabelValue(numLigne))
        menuPop.AppendItem(item)
        item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Copier
        item = wx.MenuItem(menuPop, 2000+numLigne, _(u"Copier"))
        bmp = wx.Bitmap("Images/16x16/Copier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Copier, id=2000+numLigne)
        
        # Item Coller
        item = wx.MenuItem(menuPop, 3000+numLigne, _(u"Coller"))
        bmp = wx.Bitmap("Images/16x16/Coller.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Coller, id=3000+numLigne)
        if self.clipboard == None or self.clipboard == dateDD : 
            item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Reinitialiser
        item = wx.MenuItem(menuPop, 4000+numLigne, _(u"Réinitialiser cette date"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ReInitDate, id=4000+numLigne)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Copier(self, event):
        numLigne = event.GetId() - 2000
        dateDD = self.listeLignesDates[numLigne]
        self.clipboard = dateDD
    
    def Coller(self, event):
        numLigne = event.GetId() - 3000
        dateDD = self.listeLignesDates[numLigne]
        numLigne += 1
        
        # Parcours les groupes
        for dictGroupe in self.listeGroupes :
            IDgroupe = dictGroupe["IDgroupe"]
            numColonne = 0
            
            # Parcours les unités
            for dictUnite in self.listeUnites :
                IDunite = dictUnite["IDunite"]
                try :
                    etat = self.dictOuvertures[self.clipboard][IDgroupe][IDunite]["etat"]
                except :
                    etat = False
                self.OnChangeOuverture(numLigne, numColonne, etat)
                numColonne += 1
            
            # Parcours les unités de remplissage
            numColonne += 1
            for dictUniteRemplissage in self.listeUnitesRemplissage :
                IDunite_remplissage = dictUniteRemplissage["IDunite_remplissage"]
                try :
                    nbrePlaces = self.dictRemplissage[self.clipboard][IDgroupe][IDunite_remplissage]["places"]
                    self.SetCellValue(numLigne, numColonne, str(nbrePlaces))
                    self.OnChangeRemplissage(numLigne, numColonne, nbrePlaces)
                except : 
                    pass
                numColonne += 1
                
            numLigne += 1
    
    def SaisieLot(self):
        import DLG_Saisie_lot_ouvertures
        dlg = DLG_Saisie_lot_ouvertures.Dialog(self)
        if self.clipboard != None :
            dlg.SetDate(self.clipboard)
        if dlg.ShowModal() == wx.ID_OK:
            mode = dlg.GetMode() 
            date = dlg.GetDate() 
            elements = dlg.GetElements() 
            date_debut, date_fin = dlg.GetPeriode() 
            jours_scolaires, jours_vacances = dlg.GetJours() 
            feries = dlg.GetFeries()
            try :
                dlgAttente = PBI.PyBusyInfo(_(u"Veuillez patienter durant l'opération..."), parent=None, title=_(u"Patientez..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
                wx.Yield() 
                self.TraitementLot(mode, date, elements, date_debut, date_fin, jours_scolaires, jours_vacances, feries)
                del dlgAttente
            except Exception, err:
                del dlgAttente
                traceback.print_exc(file=sys.stdout)
                dlg2 = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans le traitement par lot des ouvertures : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg2.ShowModal()
                dlg2.Destroy()
        dlg.Destroy()
    
    def TraitementLot(self, mode="date", date=None, elements=[], date_debut=None, date_fin=None, jours_scolaires=[], jours_vacances=[], feries=False):
        """ Test de duplication """
        dateModele = date
    
        # Init calendrier
        date_debut_temp = date_debut
        date_fin_temp = date_fin
        if date < date_debut_temp :
            date_debut_temp = date
        if date > date_fin_temp :
            date_fin_temp = date
        self.GetDictOuvertures(date_debut_temp, date_fin_temp)
        self.GetDictRemplissage(date_debut_temp, date_fin_temp)
        self.GetDictConso(date_debut_temp, date_fin_temp)
        
        # Liste dates
        listeDates = [date_debut,]
        tmp = date_debut
        while tmp < date_fin:
            tmp += datetime.timedelta(days=1)
            listeDates.append(tmp)
            
        for date in listeDates :
            
            # Vérifie période et jour
            valide = False
            if self.EstEnVacances(date) :
                if date.weekday() in jours_vacances :
                    valide = True
            else :
                if date.weekday() in jours_scolaires :
                    valide = True
            
            # Vérifie si férié
            if feries == False and self.EstFerie(date) == True :
                valide = False
                
            # Application
            if valide == True :
                
                for dictGroupe in self.listeGroupes :
                    IDgroupe = dictGroupe["IDgroupe"]
                    
                    # Ouvertures
                    if "ouvertures" in elements :
                        
                        for dictUnite in self.listeUnites :
                            IDunite = dictUnite["IDunite"]
                            if mode == "date" :
                                try :
                                    etat = self.dictOuvertures[dateModele][IDgroupe][IDunite]["etat"]
                                except :
                                    etat = False
                            else :
                                etat = False
                            
                            # Vérifie si pas de conso
                            if etat == False :
                                try :
                                    nbreConso = self.dictConso[date][IDgroupe][IDunite]
                                except :
                                    nbreConso = 0
                                if nbreConso > 0 :
                                    etat = True
                            
                            # Mémorise ouverture
                            dictTemp = self.GetOuverture(date, IDgroupe, IDunite)
                            if dictTemp == None :
                                IDouverture = None
                                initial = None
                            else :
                                IDouverture = dictTemp["IDouverture"]
                                initial = dictTemp["initial"]
                            self.MemoriseOuverture(date, IDouverture, IDunite, IDgroupe, etat, initial, True)
                
                    # Remplissage
                    if "places" in elements :

                        for dictUniteRemplissage in self.listeUnitesRemplissage :
                            IDunite_remplissage = dictUniteRemplissage["IDunite_remplissage"]
                            if mode == "date" :
                                try :
                                    nbrePlaces = self.dictRemplissage[dateModele][IDgroupe][IDunite_remplissage]["places"]
                                except : 
                                    nbrePlaces = 0
                            else :
                                nbrePlaces = 0
                            
                            # Mémorise remplissage
                            dictTemp = self.GetRemplissage(date, IDgroupe, IDunite_remplissage)
                            if dictTemp == None :
                                IDremplissage = None
                                initial = None
                            else :
                                IDremplissage = dictTemp["IDremplissage"]
                                initial = dictTemp["initial"]
                            self.MemoriseRemplissage(date, IDremplissage, IDunite_remplissage, IDgroupe, nbrePlaces, initial, True)

        # MAJ grille
        self.MAJ(self.annee, self.mois)

    def ReInitDate(self, event):
        numLigne = event.GetId() - 4000
        dateDD = self.listeLignesDates[numLigne]
        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment réinitialiser les paramètres de la date du %s ?") % DateComplete(dateDD), _(u"Réinitialisation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return
        dlg.Destroy()

        numLigne += 1
        
        # Parcours les groupes
        for dictGroupe in self.listeGroupes :
            IDgroupe = dictGroupe["IDgroupe"]
            numColonne = 0
            
            # Parcours les unités
            for dictUnite in self.listeUnites :
                IDunite = dictUnite["IDunite"]
                etat = False
                self.OnChangeOuverture(numLigne, numColonne, etat)
                numColonne += 1
            
            # Parcours les unités de remplissage
            numColonne += 1
            for dictUniteRemplissage in self.listeUnitesRemplissage :
                IDunite_remplissage = dictUniteRemplissage["IDunite_remplissage"]
                self.SetCellValue(numLigne, numColonne, "")
                self.OnChangeRemplissage(numLigne, numColonne, 0)
                numColonne += 1
                
            numLigne += 1

    def OnCellChange(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        nbrePlaces = self.GetCellValue(numLigne, numColonne)
        self.OnChangeRemplissage(numLigne, numColonne, nbrePlaces)
        event.Skip()
    
    def OnChangeRemplissage(self, numLigne, numColonne, nbrePlaces) :
        if self.dictCases.has_key((numLigne, numColonne)) :
            infoCase = self.dictCases[(numLigne, numColonne)]
            if infoCase["type"] == "remplissage" and infoCase["actif"] == True :
                nbrePlaces = int(nbrePlaces)
                self.ModifieRemplissage(numLigne, numColonne, infoCase["date"], infoCase["IDgroupe"], infoCase["IDunite_remplissage"], nbrePlaces)
                if nbrePlaces == 0 :
                    self.SetCellValue(numLigne, numColonne, "")

    def ModifieRemplissage(self, numLigne, numColonne, dateDD, IDgroupe, IDunite_remplissage, nbrePlaces):        
        # Modifie le dictionnaire de données
        if self.dictRemplissage.has_key(dateDD) == False :
            self.dictRemplissage[dateDD] = {}
        if self.dictRemplissage[dateDD].has_key(IDgroupe) == False :
            self.dictRemplissage[dateDD][IDgroupe] = {}
        if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) == False :
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] = { "IDremplissage" : None, "places" : nbrePlaces, "initial" : None}
        else:
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage]["places"] = nbrePlaces

    def OnCellLeftClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        self.OnChangeOuverture(numLigne, numColonne)
        event.Skip()
        
    def OnChangeOuverture(self, numLigne, numColonne, etat=None):
        nbreConso = self.GetCellValue(numLigne, numColonne) 
        if self.dictCases.has_key((numLigne, numColonne)) :
            infoCase = self.dictCases[(numLigne, numColonne)]
            if infoCase["type"] == "ouverture" and infoCase["actif"] == True :
                dateDD = infoCase["date"]
                IDgroupe = infoCase["IDgroupe"]
                IDunite = infoCase["IDunite"]
                if nbreConso != "" : 
                    # Interdit la modification si des conso existent
                    dlg = wx.MessageDialog(self, _(u"Impossible de supprimer cette ouverture !\n\n%s consommation(s) existent déjà...") % nbreConso, "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                # Recherche la valeur actuelle
                if etat == None :
                    etat = self.RechercheOuverture(dateDD, IDgroupe, IDunite)
                    if etat == True :
                        etat = False
                    else:
                        etat = True
                # Modification
                self.ModifieOuverture(numLigne, numColonne, dateDD, IDgroupe, IDunite, etat)
                self.ClearSelection()
                self.Refresh() 
                return
    
    def ModifieOuverture(self, numLigne, numColonne, dateDD, IDgroupe, IDunite, etat):
        # Modifie le dictionnaire de données
        if self.dictOuvertures.has_key(dateDD) == False :
            self.dictOuvertures[dateDD] = {}
        if self.dictOuvertures[dateDD].has_key(IDgroupe) == False :
            self.dictOuvertures[dateDD][IDgroupe] = {}
        if self.dictOuvertures[dateDD][IDgroupe].has_key(IDunite) == False :
            self.dictOuvertures[dateDD][IDgroupe][IDunite] = {}
        if self.dictOuvertures[dateDD][IDgroupe][IDunite].has_key("etat") == False :
            self.dictOuvertures[dateDD][IDgroupe][IDunite] = { "IDouverture" : None, "etat" : etat, "initial" : None}
        else:
            self.dictOuvertures[dateDD][IDgroupe][IDunite]["etat"] = etat
        # Modifie case du tableau
        if etat == True :
            self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_OUVERTURE)
        else:
            self.SetCellBackgroundColour(numLigne, numColonne, COULEUR_FERMETURE)
            
    def RechercheOuverture(self, dateDD, IDgroupe, IDunite):
        if self.dictOuvertures.has_key(dateDD) :
            if self.dictOuvertures[dateDD].has_key(IDgroupe) :
                if self.dictOuvertures[dateDD][IDgroupe].has_key(IDunite) :
                    if self.dictOuvertures[dateDD][IDgroupe][IDunite]["etat"] == True :
                        return True
        return False

    def GetOuverture(self, dateDD, IDgroupe, IDunite):
        if self.dictOuvertures.has_key(dateDD) :
            if self.dictOuvertures[dateDD].has_key(IDgroupe) :
                if self.dictOuvertures[dateDD][IDgroupe].has_key(IDunite) :
                    return self.dictOuvertures[dateDD][IDgroupe][IDunite]
        return None

    def RechercheRemplissage(self, dateDD, IDgroupe, IDunite_remplissage):
        if self.dictRemplissage.has_key(dateDD) :
            if self.dictRemplissage[dateDD].has_key(IDgroupe) :
                if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) :
                    if self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage]["places"] > 0 :
                        return self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage]["places"]
        return 0

    def GetRemplissage(self, dateDD, IDgroupe, IDunite_remplissage):
        if self.dictRemplissage.has_key(dateDD) :
            if self.dictRemplissage[dateDD].has_key(IDgroupe) :
                if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) :
                    return self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage]
        return None

    def GetListeDates(self, annee, mois) :
        tmp, nbreJours = calendar.monthrange(annee, mois)
        listeDates = []
        for numJour in range(1, nbreJours+1):
            date = datetime.date(annee, mois, numJour)
            listeDates.append(date)
        return listeDates
        
    def GetListeUnites(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, date_debut, date_fin, ordre
        FROM unites 
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeUnites = []
        for IDunite, nom, abrege, type, date_debut, date_fin, ordre in listeDonnees :
            dictTemp = { "IDunite" : IDunite, "nom" : nom, "abrege" : abrege, "type" : type, "date_debut" : date_debut, "date_fin" : date_fin, "ordre" : ordre }
            listeUnites.append(dictTemp)
        return listeUnites

    def GetDictUnitesGroupes(self):
        db = GestionDB.DB()
        req = """SELECT IDunite_groupe, IDunite, IDgroupe
        FROM unites_groupes; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        dictDonnees = {}
        for IDunite_groupe, IDunite, IDgroupe in listeDonnees :
            if dictDonnees.has_key(IDunite) == False :
                dictDonnees[IDunite] = [IDgroupe,]
            else:
                dictDonnees[IDunite].append(IDgroupe)
        return dictDonnees

    def GetListeUnitesRemplissage(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT IDunite_remplissage, nom, abrege, date_debut, date_fin, seuil_alerte
        FROM unites_remplissage
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeUnites = []
        for IDunite_remplissage, nom, abrege, date_debut, date_fin, seuil_alerte in listeDonnees :
            dictTemp = { "IDunite_remplissage" : IDunite_remplissage, "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "seuil_alerte" : seuil_alerte }
            listeUnites.append(dictTemp)
        return listeUnites
    
    def GetListeGroupes(self):
        db = GestionDB.DB()
        req = """SELECT IDgroupe, nom
        FROM groupes 
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeGroupes = []
        for IDgroupe, nom in listeDonnees :
            listeGroupes.append({ "IDgroupe" : IDgroupe, "nom" : nom })
        # Si aucun groupe :
        if len(listeGroupes) == 0 :
            listeGroupes.append({ "IDgroupe" : 0, "nom" : _(u"Sans groupe") })
        # Tous les groupes
        if self.afficherTousGroupes == True :
            listeGroupes.append({ "IDgroupe" : None, "nom" : _(u"Total max.") })
        return listeGroupes
    
    def GetListeVacances(self):
        db = GestionDB.DB()
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

    def GetListeFeries(self):
        db = GestionDB.DB()
        req = """SELECT type, nom, jour, mois, annee
        FROM jours_feries 
        ; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

    def GetDictOuvertures(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT IDouverture, IDunite, IDgroupe, date
        FROM ouvertures 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        ORDER BY date; """ % (self.IDactivite, date_debut, date_fin)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        for IDouverture, IDunite, IDgroupe, date in listeDonnees :
            dateDD = DateEngEnDateDD(date)
            self.MemoriseOuverture(dateDD, IDouverture, IDunite, IDgroupe, True, True)
            
    def MemoriseOuverture(self, dateDD=None, IDouverture=None, IDunite=None, IDgroupe=None, etat=True, initial=True, forcer=False) :
            dictValeurs = { "IDouverture" : IDouverture, "etat" : etat, "initial" : initial}
            if self.dictOuvertures.has_key(dateDD) == False :
                self.dictOuvertures[dateDD] = {}
            if self.dictOuvertures[dateDD].has_key(IDgroupe) == False :
                self.dictOuvertures[dateDD][IDgroupe] = {}
            if self.dictOuvertures[dateDD][IDgroupe].has_key(IDunite) == False :
                self.dictOuvertures[dateDD][IDgroupe][IDunite] = {}
            if self.dictOuvertures[dateDD][IDgroupe][IDunite] == {} or forcer == True :
                self.dictOuvertures[dateDD][IDgroupe][IDunite] = dictValeurs

    def GetDictRemplissage(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT IDremplissage, IDunite_remplissage, IDgroupe, date, places
        FROM remplissage 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        ORDER BY date; """ % (self.IDactivite, date_debut, date_fin)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        for IDremplissage, IDunite_remplissage, IDgroupe, date, places in listeDonnees :
            dateDD = DateEngEnDateDD(date)
            self.MemoriseRemplissage(dateDD, IDremplissage, IDunite_remplissage, IDgroupe, places, places)
            if IDgroupe == None and self.afficherTousGroupes == None :
                self.parent.SetAfficherTousGroupes(True) 
    
    def MemoriseRemplissage(self, dateDD=None, IDremplissage=None, IDunite_remplissage=None, IDgroupe=None, places=None, initial=None, forcer=False):
        dictValeurs = { "IDremplissage" : IDremplissage, "places" : places, "initial" : initial}
        if self.dictRemplissage.has_key(dateDD) == False :
            self.dictRemplissage[dateDD] = {}
        if self.dictRemplissage[dateDD].has_key(IDgroupe) == False :
            self.dictRemplissage[dateDD][IDgroupe] = {}
        if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) == False :
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] = {}
        if self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] == {} or forcer == True :
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] = dictValeurs
        
    def GetDictConso(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT date, IDgroupe, IDunite, COUNT(IDconso)
        FROM consommations 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        GROUP BY date, IDgroupe, IDunite
        ORDER BY date; """ % (self.IDactivite, date_debut, date_fin)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        for date, IDgroupe, IDunite, nbreConso in listeDonnees :
            date = DateEngEnDateDD(date)
            if self.dictConso.has_key(date) == False :
                self.dictConso[date] = {}
            if self.dictConso[date].has_key(IDgroupe) == False :
                self.dictConso[date][IDgroupe] = {}
            if self.dictConso[date][IDgroupe].has_key(IDunite) == False :
                self.dictConso[date][IDgroupe][IDunite] = {}
            self.dictConso[date][IDgroupe][IDunite] = nbreConso

    def GetValiditeActivite(self):
        db = GestionDB.DB()
        req = """SELECT date_debut, date_fin
        FROM activites 
        WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return (None, None)
        return (listeDonnees[0][0], listeDonnees[0][1])










class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDactivite = IDactivite
        
        intro = _(u"Ce calendrier vous permet de définir les jours d'ouverture de l'activité et le nombre maximal de places. Cliquez sur les cases pour indiquer que l'unité est fonctionnelle et saisissez directement les effectifs maximals en double-cliquant sur les cases blanches. <U>Important :</U> Cliquez avec le bouton droit de la souris sur les cases Dates pour utiliser le Copier-Coller.")
        titre = _(u"Calendrier des ouvertures")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Calendrier.png")
        
        # Selection Mois
        self.staticbox_mois_staticbox = wx.StaticBox(self, -1, _(u"Sélection du mois"))
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.ctrl_mois = wx.Choice(self, -1, choices=[_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")])
        self.spin_mois = wx.SpinButton(self, -1, size=(18, 20),  style=wx.SP_VERTICAL)
        self.spin_mois.SetRange(-1, 1)
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, "", min=1977, max=2999)
        dateDuJour = datetime.date.today()
        self.ctrl_annee.SetValue(dateDuJour.year)
        self.ctrl_mois.SetSelection(dateDuJour.month-1)
        
        # Légende
        self.staticbox_legende_staticbox = wx.StaticBox(self, -1, _(u"Légende"))
        self.listeLegende = [
            { "label" : _(u"Ouvert"), "couleur" : COULEUR_OUVERTURE, "ctrl_label" : None, "ctrl_img" : None },
            { "label" : _(u"Fermé"), "couleur" : COULEUR_FERMETURE, "ctrl_label" : None, "ctrl_img" : None },
            { "label" : _(u"Vacances"), "couleur" : COULEUR_VACANCES, "ctrl_label" : None, "ctrl_img" : None },
            { "label" : _(u"Férié"), "couleur" : COULEUR_FERIE, "ctrl_label" : None, "ctrl_img" : None },
            { "label" : _(u"Effectifs max."), "couleur" : (255, 255, 255), "ctrl_label" : None, "ctrl_img" : None },
            ]
        index = 0
        for dictTemp in self.listeLegende :
            img = wx.StaticBitmap(self, -1, CreationImage(12, 12, dictTemp["couleur"]))
            label = wx.StaticText(self, -1, dictTemp["label"]) 
            self.listeLegende[index]["ctrl_img"] = img
            self.listeLegende[index]["ctrl_label"] = label
            index += 1

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.check_tous_groupes = wx.CheckBox(self, -1, _(u"Afficher Total max."))

        # Calendrier
        self.staticbox_calendrier_staticbox = wx.StaticBox(self, -1, _(u"Calendrier"))
        self.ctrl_calendrier = Calendrier(self, self.IDactivite)
                
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_saisie_lot = CTRL_Bouton_image.CTRL(self, texte=_(u"Saisie et suppression par lot"), cheminImage="Images/32x32/Magique.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_SPIN, self.OnSpinMois, self.spin_mois)
        self.Bind(wx.EVT_CHOICE, self.OnMois, self.ctrl_mois)
        self.Bind(wx.EVT_SPINCTRL, self.OnAnnee, self.ctrl_annee)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSaisieLot, self.bouton_saisie_lot)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAfficherTousGroupes, self.check_tous_groupes)
        
        self.MAJCalendrier()

    def __set_properties(self):
        self.SetTitle(_(u"Calendrier des ouvertures"))
        self.ctrl_mois.SetToolTipString(_(u"Sélectionnez un mois"))
        self.ctrl_annee.SetMinSize((70, -1))
        self.ctrl_annee.SetToolTipString(_(u"Sélectionnez une année"))
        self.check_tous_groupes.SetToolTipString(_(u"Cochez cette case pour afficher les lignes 'Total max.' afin de saisir des limitations d'effectifs globales"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_saisie_lot.SetToolTipString(_(u"Cliquez ici saisir ou supprimer un lot d'ouvertures"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.ctrl_calendrier.SetMinSize((100, 100))
        self.SetMinSize((890, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        
        # Selection Mois
        staticbox_mois = wx.StaticBoxSizer(self.staticbox_mois_staticbox, wx.VERTICAL)
        grid_sizer_mois = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=0)
        grid_sizer_mois.Add(self.label_mois, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mois.Add(self.ctrl_mois, 0, wx.LEFT, 5)
        grid_sizer_mois.Add(self.spin_mois, 0, wx.EXPAND, 0)
        grid_sizer_mois.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        grid_sizer_mois.Add(self.ctrl_annee, 0, wx.LEFT, 5)
        staticbox_mois.Add(grid_sizer_mois, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(staticbox_mois, 1, wx.EXPAND, 0)
        
        # Légende
        staticbox_legende = wx.StaticBoxSizer(self.staticbox_legende_staticbox, wx.VERTICAL)
        grid_sizer_legende = wx.FlexGridSizer(rows=1, cols=len(self.listeLegende)*3, vgap=4, hgap=4)
        for dictTemp in self.listeLegende :
            grid_sizer_legende.Add(dictTemp["ctrl_img"], 0, wx.ALIGN_CENTER_VERTICAL, 0)
            grid_sizer_legende.Add(dictTemp["ctrl_label"], 0, wx.ALIGN_CENTER_VERTICAL, 0)
            grid_sizer_legende.Add( (5, 5), 0, 0, 0)
        staticbox_legende.Add(grid_sizer_legende, 1, wx.ALL|wx.EXPAND, 6)
        grid_sizer_haut.Add(staticbox_legende, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        staticbox_options.Add(self.check_tous_groupes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(staticbox_options, 1, wx.EXPAND, 0)


        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
    
        # Calendrier
        staticbox_calendrier = wx.StaticBoxSizer(self.staticbox_calendrier_staticbox, wx.VERTICAL)
        staticbox_calendrier.Add(self.ctrl_calendrier, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_calendrier, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_saisie_lot, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnSpinMois(self, event):
        x = event.GetPosition()
        mois = self.ctrl_mois.GetSelection()+x
        if mois != -1 and mois < 12 :
            self.ctrl_mois.SetSelection(mois)
            self.MAJCalendrier()
        self.spin_mois.SetValue(0)

    def OnMois(self, event): 
        self.MAJCalendrier()

    def OnAnnee(self, event):
        self.MAJCalendrier()

    def MAJCalendrier(self):
        annee = int(self.ctrl_annee.GetValue())
        mois = self.ctrl_mois.GetSelection()+1
        self.Freeze()
        self.ctrl_calendrier.MAJ(annee, mois)
        self.Thaw() 
    
    def OnCheckAfficherTousGroupes(self, event):
        self.ctrl_calendrier.afficherTousGroupes = self.check_tous_groupes.GetValue() 
        self.MAJCalendrier()
    
    def SetAfficherTousGroupes(self, etat=True):
        self.check_tous_groupes.SetValue(etat) 
        self.ctrl_calendrier.afficherTousGroupes = etat
        
    def OnBoutonOk(self, event):
        try :
            dlgAttente = PBI.PyBusyInfo(_(u"Veuillez patienter durant la sauvegarde des données..."), parent=None, title=_(u"Enregistrement"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            self.ctrl_calendrier.Sauvegarde()
            del dlgAttente
        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la sauvegarde des ouvertures : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Calendrier")

    def OnBoutonSaisieLot(self, event): 
        self.ctrl_calendrier.SaisieLot() 
        
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDactivite=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
