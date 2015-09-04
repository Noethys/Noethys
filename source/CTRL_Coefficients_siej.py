#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB
import CTRL_Saisie_heure

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)



class Track(object):
    def __init__(self, donnees):
        self.IDunite = donnees[0]
        self.IDactivite = donnees[1]
        self.nomUnite = donnees[2]
        self.typeUnite = donnees[3]
        self.coeffUnite = donnees[4]
        self.nomActivite = donnees[5]
        
        # Items HyperTreeList
        self.item = None
        self.itemParent = None
        
        # Contr�les
        self.ctrl_type = None
        self.ctrl_coeff  = None
        self.ctrl_arrondi  = None
        self.ctrl_plafond  = None
    
    def GetType(self):
        """ Retourne le type de calcul s�lectionn� """
        return self.ctrl_type.GetSelection() 
    
    def ValidationCoeff(self):
        return self.ctrl_coeff.Validation()
    
    def GetCoeff(self):
        return self.ctrl_coeff.GetValeur() 

    def GetCoeffStr(self):
        return self.ctrl_coeff.GetValeurStr() 

    def SetCoeff(self, valeur=None):
        self.ctrl_coeff.SetValeur(valeur)
    
    def GetArrondi(self):
        return self.ctrl_arrondi.GetValeur() 

    def ValidationPlafond(self):
        if self.ctrl_plafond.GetHeure() != None and self.ctrl_plafond.Validation() == False :
            return False
        else:
            return True

    def GetPlafond(self):
        return self.ctrl_plafond.GetValeur() 

# --------------------------------------------------------------------------------------------------------------------------------

class CTRL_Type(wx.Choice):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Type de calcul : Par unit� ou par avec coefficient """
        wx.Choice.__init__(self, parent, id=id, size=(200, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetItems([_(u"Nombre d'unit�s consomm�es"), _(u"Temps r��l de pr�sence"), _(u"Temps de pr�sence factur�")])
        self.SetToolTipString(_(u"S�lectionnez le type de calcul � appliquer � cette unit� de consommation"))
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        # Defaut
        if self.track.typeUnite == "Horaire" :
            self.SetSelection(1)
        else:
            self.SetSelection(0)

    def OnChoice(self, event):
        if self.GetSelection() == 0 :
            self.track.ctrl_coeff.Enable(True)
            self.track.ctrl_arrondi.Enable(False)
            self.track.ctrl_plafond.Enable(False)
        elif self.GetSelection() == 1 :
            self.track.ctrl_coeff.Enable(False)
            self.track.ctrl_arrondi.Enable(True)
            self.track.ctrl_plafond.Enable(True)
        else:
            self.track.ctrl_coeff.Enable(False)
            self.track.ctrl_arrondi.Enable(False)
            self.track.ctrl_plafond.Enable(False)
        
# -------------------------------------------------------------------------------------------------------------------

class CTRL_Arrondi(wx.Choice):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Arrondi � appliquer. Ex : Au quart d'heures sup�rieur """
        wx.Choice.__init__(self, parent, id=id, size=(85, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.listeLabels = [_(u"Aucun"), _(u"5 min. sup."), _(u"10 min. sup."), _(u"15 min. sup."), _(u"30 min. sup."), _(u"45 min. sup."), _(u"60 min. sup.")]
        self.listeArrondis=[None, 5, 10, 15, 30, 45, 60]
        self.SetItems(self.listeLabels)
        self.SetToolTipString(_(u"S�lectionnez un arrondi � appliquer � chaque consommation. Ex : Arrondir au quart d'heure sup�rieur."))
        # Defaut
        self.SetSelection(0)
    
    def GetValeur(self):
        index = self.GetSelection() 
        return self.listeArrondis[index]

# -------------------------------------------------------------------------------------------------------------------

class CTRL_Coeff(wx.TextCtrl):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Coefficient � appliquer"""
        wx.TextCtrl.__init__(self, parent, id=id, value="", size=(70, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetToolTipString(_(u"Saisissez le coefficient multiplicateur � appliquer"))
    
    def Validation(self):
        valeur = self.GetValue() 
        if valeur == "" : return True
        try :
            test = float(valeur)
        except :
            return False
        return True
    
    def GetValeurStr(self):
        return self.GetValue() 
        
    def GetValeur(self):
        valeur = self.GetValue() 
        if self.Validation() == True :
            if valeur == "" : 
                return 0
            else:
                return float(valeur)
        else:
            return None
    
    def SetValeur(self, valeur=None):
        if valeur in (None, 0, 0.0) : 
            valeur = ""
        try :
            self.SetValue(str(valeur))
        except :
            pass
                    
# -------------------------------------------------------------------------------------------------------------------

class CTRL_Plafond(CTRL_Saisie_heure.Heure):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Plafond � appliquer sur heures r�elles """
        CTRL_Saisie_heure.Heure.__init__(self, parent) 
        self.parent = parent
        self.SetSize((70, -1))
        self.item = item
        self.track = track
        self.SetToolTipString(_(u"Saisissez le nombre d'heures plafond"))
    
    def GetValeur(self):
        valeur = self.GetHeure() 
        if self.Validation() == True :
            return valeur
        else:
            return None
                    

# -------------------------------------------------------------------------------------------------------------------

class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        
        self.listeTracks = []
        self.listeActivites = []
        self.dictCoeff = {}
        self.periode = (None, None)
                
        # Cr�ation des colonnes
        listeColonnes = [
            ( _(u"Unit� de consommation"), 225, wx.ALIGN_LEFT),
            ( _(u"Type de calcul"), 210, wx.ALIGN_LEFT),
            ( _(u"Coefficient"), 80, wx.ALIGN_LEFT),
            ( _(u"Arrondi"), 92, wx.ALIGN_LEFT),
            ( _(u"Plafond"), 80, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_ROW_LINES |  wx.TR_COLUMN_LINES |wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)
                    
    def Importation(self):
        # V�rifie les dates de la p�riode
        date_debut, date_fin = self.periode
        if date_debut == None or date_fin == None :
            return []
        
        # Importation des unit�s de consommations
        if len(self.listeActivites) == 0 : return []
        elif len(self.listeActivites) == 1 : conditionActivites = "unites.IDactivite=%d" % self.listeActivites[0]
        else : conditionActivites = "unites.IDactivite IN %s" % str(tuple(self.listeActivites))
        DB = GestionDB.DB()
        req = """SELECT 
        unites.IDunite, unites.IDactivite, unites.nom, unites.type, unites.coeff,
        activites.nom
        FROM unites
        LEFT JOIN activites ON activites.IDactivite = unites.IDactivite
        WHERE %s
        AND (activites.date_debut<='%s' AND activites.date_fin>='%s')
        ORDER BY ordre
        ;""" % (conditionActivites, date_fin, date_debut)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        listeTracks = []
        for item in listeDonnees :
            track = Track(item)
            listeTracks.append(track)
            
            # M�morisation du coeff initial
            if self.dictCoeff.has_key(track.IDunite) == False :
                self.dictCoeff[track.IDunite] = track.coeffUnite
        
        return listeTracks

    def MAJ(self):
        """ Met � jour (redessine) tout le contr�le """
        # M�morise les coeff d�j� saisis
        self.GetDictCoeff() 
        # MAJ
        self.Freeze()
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
        self.Thaw() 

    def Remplissage(self):        
        # Importation des donn�es
        listeTracks = self.Importation() 

        # Regroupement
        listeKeys = []
        for track in listeTracks :
            key = (track.nomActivite, track.IDactivite)
            if key not in listeKeys :
                listeKeys.append(key)
                    
        # Tri des Keys
        listeKeys.sort()
        
        # Cr�ation des branches
        for nomActivite, IDactivite in listeKeys :
            
            # Niveau Nom de l'activit�
            brancheActivite = self.AppendItem(self.root, nomActivite)
            self.SetPyData(brancheActivite, IDactivite)
            self.SetItemBold(brancheActivite, True)
            self.SetItemBackgroundColour(brancheActivite, COULEUR_FOND_REGROUPEMENT)
            
            # Niveau Unit�s de consommation
            for track in listeTracks :
                
                if track.IDactivite == IDactivite :
                
                    brancheUnite = self.AppendItem(brancheActivite, track.nomUnite, ct_type=1)
                    self.SetPyData(brancheUnite, track.IDunite)
                    self.CheckItem(brancheUnite, True)
                    
                    # M�morisation des items dans le track
                    track.item = brancheUnite
                    track.itemParent = brancheActivite
                                        
                    # CTRL du type de calcul
                    ctrl_type = CTRL_Type(self.GetMainWindow(), item=brancheUnite, track=track)
                    self.SetItemWindow(brancheUnite, ctrl_type, 1)        
                    track.ctrl_type = ctrl_type      
                                        
                    # CTRL du Coeff
                    ctrl_coeff = CTRL_Coeff(self.GetMainWindow(), item=brancheUnite, track=track)
                    self.SetItemWindow(brancheUnite, ctrl_coeff, 2)        
                    track.ctrl_coeff = ctrl_coeff      
                    if track.ctrl_type.GetSelection() == 1 :
                        ctrl_coeff.Enable(False)
                    
                    if self.dictCoeff.has_key(track.IDunite) :
                        track.SetCoeff(self.dictCoeff[track.IDunite])

                    # CTRL de l'Arrondi
                    ctrl_arrondi = CTRL_Arrondi(self.GetMainWindow(), item=brancheUnite, track=track)
                    self.SetItemWindow(brancheUnite, ctrl_arrondi, 3)        
                    track.ctrl_arrondi = ctrl_arrondi      
                    if track.ctrl_type.GetSelection() == 0 :
                        ctrl_arrondi.Enable(False)

                    # CTRL du plafond
                    ctrl_plafond = CTRL_Plafond(self.GetMainWindow(), item=brancheUnite, track=track)
                    self.SetItemWindow(brancheUnite, ctrl_plafond, 4)        
                    track.ctrl_plafond = ctrl_plafond      
                    if track.ctrl_type.GetSelection() == 0 :
                        ctrl_plafond.Enable(False)
        
        self.ExpandAllChildren(self.root)
        
        # Pour �viter le bus de positionnement des contr�les
        self.GetMainWindow().CalculatePositions() 
        
        self.listeTracks = listeTracks
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
    
    def GetDictCoeff(self):
        # M�morise les coeff d�j� saisis
        for track in self.listeTracks :
            if self.IsItemChecked(track.item) :
                if track.GetType() == 0 :
                    if track.ValidationCoeff() == True :
                        self.dictCoeff[track.IDunite] = track.GetCoeffStr()
        return self.dictCoeff
    
    def GetDonnees(self):
        """ R�cup�re les r�sultats des donn�es saisies """
        dictDonnees = {}
        for track in self.listeTracks :
            
            if self.IsItemChecked(track.item) :
                
                typeCalcul = track.GetType()
                if typeCalcul == 0 :
                    # Heure selon coeff
                    if track.ValidationCoeff() == False :
                        dlg = wx.MessageDialog(self, _(u"Le coefficient de l'unit� '%s' semble incorrecte !") % track.nomUnite, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False
                    coeff = track.GetCoeff() 
                    arrondi = None
                    plafond = None
                    
                elif typeCalcul == 1 :
                    # heures r�elles
                    if track.ValidationPlafond() == False :
                        dlg = wx.MessageDialog(self, _(u"Le plafond de l'unit� '%s' semble incorrecte !") % track.nomUnite, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return False
                    coeff = None
                    arrondi = track.GetArrondi() 
                    plafond = track.GetPlafond()
                    
                else :
                    # Heures factur�es
                    coeff = None
                    arrondi = None
                    plafond = None
                    
                # M�morisation des valeurs
                dictValeurs = {
                    "IDunite" : track.IDunite,
                    "IDactivite" : track.IDactivite,
                    "nomUnite" : track.nomUnite,
                    "nomActivite" : track.nomActivite,
                    "typeCalcul" : typeCalcul,
                    "coeff" : coeff,
                    "arrondi" : arrondi,
                    "plafond" : plafond,
                    }
                dictDonnees[track.IDunite] = dictValeurs
        
        return dictDonnees
                
    def SauvegardeCoeff(self):
        """ Sauvegarde des coeff sasis dans la table unit�s """
        self.GetDictCoeff() 
        DB = GestionDB.DB() 
        for IDunite, coeff in self.dictCoeff.iteritems() :
            DB.ReqMAJ("unites", [("coeff", coeff),], "IDunite", IDunite)
        DB.Close() 

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.ctrl.MAJ() 
        self.boutonTest = wx.Button(panel, -1, _(u"Test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
    
    def OnBoutonTest(self, event):
        print self.ctrl.GetDonnees()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
