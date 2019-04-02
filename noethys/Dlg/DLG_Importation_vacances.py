#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Parametres
import datetime
import GestionDB
from Utils import UTILS_Icalendar
import wx.lib.agw.hyperlink as Hyperlink


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils




def RechercherZone(ville="", cp=""):
    """ Rechercher zone scolaire """
##    url = "http://www.education.gouv.fr/pid25058/le-calendrier-scolaire.html?annee=108&zone=116&search_input=%s+%%28%s%%29" % (ville, str(cp))
##    url = url.replace(' ','%20')
##    f = urllib2.urlopen(url, timeout=5)
##    page = f.read()
##    print url
##    # Recherche dans la page
##    chaine = "appartient &agrave; la Zone "
##    position = page.index(chaine)
##    zone = page[position + len(chaine)][0]
##    return zone
    
##    # Zones par département
##    A = [14, 50, 61, 3, 15, 43, 63, 7, 26, 38, 73, 74, 1, 42, 69, 11, 30, 34, 48, 66, 54, 55, 57, 88, 44, 49, 53, 72, 85, 22, 29, 35, 56, 9, 12, 31, 32, 46, 65, 81, 82]
##    B = [4, 5, 13, 84, 2, 60, 80, 25, 39, 70, 90, 21, 71, 89, 59, 62, 19, 23, 87, 06, 83, 18, 28, 36, 37, 41, 45, 16, 17, 79, 86, 8, 10, 51, 52, 27, 76, 66, 67]
##    C = [24, 33, 40, 47, 64, 77, 93, 94, 75, 78, 91, 92, 95]

    # NOUVELLES Zones par département (à partir de 2015)
    A = [25, 39, 70, 90, 24, 33, 40, 47, 64, 21, 58, 71, 89, 3, 15, 43, 63, 7, 26, 38, 73, 74, 19, 23, 87, 1, 42, 69, 16, 17, 79, 86]
    B = [4, 5, 13, 84, 2, 60, 80, 14, 50, 61, 59, 62, 54, 55, 57, 88, 44, 49, 53, 72, 85, 6, 83, 18, 28, 36, 37, 41, 45, 8, 10, 51, 52, 22, 29, 35, 56, 27, 76, 67, 68]
    C = [77, 93, 94, 75, 11, 30, 34, 48, 66, 9, 12, 31, 32, 46, 65, 81, 82, 78, 91, 92, 95]

    numDep = int(cp[:2])
    if numDep in A : return "A"
    if numDep in B : return "B"
    if numDep in C : return "C"
    return None


class Track(object):
    def __init__(self, donnees):
        self.nom = donnees["nom"]
        self.annee = donnees["annee"]
        self.date_debut = donnees["date_debut"]
        self.date_fin = donnees["date_fin"]
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.zone = None
        
        # Récupère Vacances déjà enregistrées
        DB = GestionDB.DB()
        req = """SELECT IDvacance, nom, annee, date_debut, date_fin
        FROM vacances ORDER BY date_debut;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        self.dictVacances = {}
        for IDvacance, nom, annee, date_debut, date_fin in listeDonnees :
            self.dictVacances[(annee, nom)] = (date_debut, date_fin)
        
        # Init
        FastObjectListView.__init__(self, *args, **kwds)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        if self.zone == None :
            return []
        
        cal = UTILS_Icalendar.Calendrier(url="http://media.education.gouv.fr/ics/Calendrier_Scolaire_Zone_%s.ics" % self.zone)
        titre = cal.GetTitre()
        if titre == None :
            return []
        listePeriodes = cal.GetVacances()

        listeListeView = []
        for item in listePeriodes :
            track = Track(item)
            if ((track.annee, track.nom) in self.dictVacances) == False :
                listeListeView.append(track)
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDate(date):
            """ Transforme le format "aaaa-mm-jj" en "mercredi 12 septembre 2008" """
            listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
            listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
            jour = date.day
            mois = date.month
            annee = date.year
            jourSemaine = int(date.strftime("%w"))
            texte = listeJours[jourSemaine-1] + " " + str(jour) + " " + listeMois[mois-1] + " " + str(annee)
            return texte   
            
        liste_Colonnes = [
            ColumnDefn(_(u"Année"), 'left', 50, "annee"),
            ColumnDefn(_(u"Nom"), "left", 120, "nom"), 
            ColumnDefn(_(u"Date de début"), "left", 190, "date_debut", stringConverter=FormateDate), 
            ColumnDefn(_(u"Date de fin"), "left", 190, "date_fin", stringConverter=FormateDate), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        
        self.SetEmptyListMsg(_(u"Aucune période de vacances"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[3])
        self.SetObjects(self.donnees)
       
    def MAJ(self, zone="A"):
        self.zone = zone
        self.InitModel()
        self.InitObjectListView()
        self.CocheSuggestions() 
        self.DefileDernier() 
    
    def CocheTout(self, event=None):
        for track in self.donnees :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)
    
    def CocheSuggestions(self):
        anneeActuelle = datetime.date.today().year
        nbre = 0
        for track in self.donnees :
            if ((track.annee, track.nom) in self.dictVacances) == False and track.annee >= anneeActuelle :
                self.Check(track)
                self.RefreshObject(track)
                nbre += 1
        
        # Texte de label
        if nbre == 0 : texte = _(u"Noethys n'a aucune suggestion d'importation...")
        elif nbre == 1 : texte = _(u"Noethys vous suggère d'importer 1 période de vacances...")
        else : texte = _(u"Noethys vous suggère d'importer %d périodes de vacances...") % nbre
        self.SetLabelPeriodes(texte)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
##    def GetInfosCoches(self):
##        listeDonnees = []
##        for track in self.GetTracksCoches() :
##            dictTemp = track.GetDict()
##            for code, valeur in self.dictOrganisme.iteritems() :
##                dictTemp[code] = valeur
##            listeDonnees.append(dictTemp)
##        return listeDonnees

    
    def SetLabelPeriodes(self, texte=""):
        self.GetParent().SetLabelPeriodes(texte)


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
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
        if self.URL == "tout" :
            self.parent.ctrl_periodes.CocheTout()
        if self.URL == "rien" :
            self.parent.ctrl_periodes.CocheRien()
        if self.URL == "suggestions" :
            self.parent.ctrl_periodes.CocheSuggestions()
        if self.URL == "zone" :
            self.parent.ImportationZone()
        self.UpdateLink()
        
        

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici importer des périodes de vacances depuis le site internet de l'Education Nationale. Sélectionnez votre zone géographique et cochez les périodes à importer.")
        titre = _(u"Importation de périodes de vacances")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Telecharger.png")
        
        # Zone
        self.box_zone_staticbox = wx.StaticBox(self, -1, _(u"1. Sélectionnez votre zone"))
        self.label_zone = wx.StaticText(self, -1, _(u"Zone géographique :"))
        self.ctrl_zone = wx.Choice(self, -1, choices=[u"Zone A", u"Zone B", u"Zone C"])
        self.hyper_zone = Hyperlien(self, label=_(u"Rechercher la zone de l'organisateur sur internet"), infobulle=_(u"Cliquez ici pour rechercher la zone de l'organisateur sur internet"), URL="zone")
        
        # Périodes
        self.box_periodes_staticbox = wx.StaticBox(self, -1, _(u"2. Cochez les périodes à importer"))
        self.label_periodes = wx.StaticText(self, -1, _(u"Sélectionnez une zone..."))
        self.label_periodes.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD))
                
        self.ctrl_periodes = ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        self.hyper_tout = Hyperlien(self, label=_(u"Tout sélectionner"), infobulle=_(u"Cliquez ici pour tout sélectionner"), URL="tout")
        self.label_separation_1 = wx.StaticText(self, -1, u" | ")
        self.hyper_rien = Hyperlien(self, label=_(u"Tout désélectionner"), infobulle=_(u"Cliquez ici pour tout désélectionner"), URL="rien")
        self.label_separation_2 = wx.StaticText(self, -1, u" | ")
        self.hyper_suggestions = Hyperlien(self, label=_(u"Sélectionner les suggestions"), infobulle=_(u"Cliquez ici pour sélectionner uniquement les suggestions"), URL="suggestions")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Importer"), cheminImage="Images/32x32/Fleche_bas.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixZone, self.ctrl_zone)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init
        zone = UTILS_Parametres.Parametres(mode="get", categorie="vacances", nom="zone", valeur="A")
        self.SetZone(zone)
        self.OnChoixZone(None)
        

    def __set_properties(self):
        self.ctrl_zone.SetToolTip(wx.ToolTip(_(u"Sélectionnez une zone")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour importer les périodes sélectionnées")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((670, 680))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Zone
        box_zone = wx.StaticBoxSizer(self.box_zone_staticbox, wx.VERTICAL)
        grid_sizer_zone = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_zone.Add(self.label_zone, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_zone.Add(self.ctrl_zone, 0, wx.EXPAND, 0)
        grid_sizer_zone.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_zone.Add(self.hyper_zone, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_zone.AddGrowableCol(1)
        box_zone.Add(grid_sizer_zone, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_zone, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Périodes
        box_periodes = wx.StaticBoxSizer(self.box_periodes_staticbox, wx.VERTICAL)
        grid_sizer_periodes = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_periodes.Add(self.label_periodes, 1, wx.EXPAND, 0)
        grid_sizer_periodes.Add(self.ctrl_periodes, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=8, vgap=0, hgap=0)
        grid_sizer_commandes.Add(self.hyper_tout, 0, 0, 0)
        grid_sizer_commandes.Add(self.label_separation_1, 0, 0, 0)
        grid_sizer_commandes.Add(self.hyper_rien, 0, 0, 0)
        grid_sizer_commandes.Add(self.label_separation_2, 0, 0, 0)
        grid_sizer_commandes.Add(self.hyper_suggestions, 0, 0, 0)
        grid_sizer_periodes.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_periodes.AddGrowableRow(1)
        grid_sizer_periodes.AddGrowableCol(0)
        box_periodes.Add(grid_sizer_periodes, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_periodes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnChoixZone(self, event=None):
        zone = self.GetZone() 
        self.ctrl_periodes.MAJ(zone)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Vacances")

    def OnBoutonOk(self, event): 
        tracks = self.ctrl_periodes.GetTracksCoches() 
        
        # Validation
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune période à importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Sauvegarde
        listeDonnees = []
        for track in tracks :
            listeDonnees.append((track.nom, track.annee, str(track.date_debut), str(track.date_fin)))
        
        DB = GestionDB.DB()
        DB.Executermany("INSERT INTO vacances (nom, annee, date_debut, date_fin) VALUES (?, ?, ?, ?)", listeDonnees, commit=True)
        DB.Close() 
        
        # Fermeture
        self.MemoriseZone() 
        self.EndModal(wx.ID_OK)   

    def OnBoutonAnnuler(self, event): 
        self.MemoriseZone() 
        self.EndModal(wx.ID_CANCEL)   
    
    def SetZone(self, zone="A"):
        if zone == "A" : self.ctrl_zone.SetSelection(0)
        if zone == "B" : self.ctrl_zone.SetSelection(1)
        if zone == "C" : self.ctrl_zone.SetSelection(2)
        self.OnChoixZone()
    
    def GetZone(self):
        if self.ctrl_zone.GetSelection() == 0 : return "A"
        if self.ctrl_zone.GetSelection() == 1 : return "B"
        if self.ctrl_zone.GetSelection() == 2 : return "C"
        
    def MemoriseZone(self):
        zone = self.GetZone() 
        UTILS_Parametres.Parametres(mode="set", categorie="vacances", nom="zone", valeur=zone)
    
    def SetLabelPeriodes(self, texte=u""):
        self.label_periodes.SetLabel(texte)
    
    def ImportationZone(self):
        """ Récupération de la zone sur internet """
        # Récupération de la ville de l'organisateur
        DB = GestionDB.DB()
        req = """SELECT cp, ville
        FROM organisateur
        WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        cp, ville = DB.ResultatReq()[0]
        DB.Close()
        
        # Recherche sur internet
        try :
            zone = RechercherZone(ville, cp)
        except :
            zone = None
        if zone == None :
            dlg = wx.MessageDialog(self, _(u"Désolé, Noethys n'a pas réussi à trouver la zone scolaire de l'organisateur sur internet !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.SetZone(zone) 
        dlg = wx.MessageDialog(self, _(u"La ville de l'organisateur (%s) est située dans la zone %s.") % (ville, zone), _(u"Zone scolaire"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
