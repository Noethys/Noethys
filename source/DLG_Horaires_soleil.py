#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import datetime
import CTRL_Saisie_adresse
import GestionDB
import UTILS_Gps
from UTILS_Astral import City
import calendar

def DateDDEnDateFR(dateDD):
    """ Transforme une datetime.date en date complète FR """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    return listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Horaires_soleil", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        titre = _(u"Horaires du soleil")
        intro = _(u"Cette fonctionnalité permet d'afficher les heures de lever et de coucher du soleil d'une ville sur un mois donné. Cette fonction utilise la géolocalisation GPS de la ville et un agorithme intégré de calcul de la position du soleil.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Soleil.png")
        
        # Paramètres
        self.box_ville_staticbox = wx.StaticBox(self, -1, _(u"Ville"))
        self.radio_ville = wx.RadioButton(self, -1, _(u"Selon une ville :"), style=wx.RB_GROUP)
        self.label_ville = wx.StaticText(self, -1, _(u"CP :"))
        self.ctrl_ville = CTRL_Saisie_adresse.Adresse(self)
        self.radio_gps = wx.RadioButton(self, -1, _(u"Selon une position GPS :"))
        self.label_lat = wx.StaticText(self, -1, _(u"Lat. :"))
        self.ctrl_lat = wx.TextCtrl(self, -1, u"")
        self.label_long = wx.StaticText(self, -1, _(u"Long. :"))
        self.ctrl_long = wx.TextCtrl(self, -1, u"")
        
        self.box_mois_staticbox = wx.StaticBox(self, -1, _(u"Mois"))
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.ctrl_mois = wx.Choice(self, -1, choices=[_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")])
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, u"", min=1970, max=2999)
        
        dateDuJour = datetime.date.today() 
        self.ctrl_mois.SetSelection(dateDuJour.month-1)
        self.ctrl_annee.SetValue(dateDuJour.year)
        
        # Bouton actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        
        # Résultats
        self.ctrl_resultats = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioVille, self.radio_ville)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioVille, self.radio_gps)
        self.Bind(wx.EVT_CHOICE, self.OnChoixMois, self.ctrl_mois)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixAnnee, self.ctrl_annee)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        
        # Init contrôles
        self.OnRadioVille(None)
        self.dictOrganisateur = self.GetOrganisateur() 
        if self.dictOrganisateur != None :
            try :
                self.ctrl_ville.SetValueCP(self.dictOrganisateur["cp"])
                self.ctrl_ville.SetValueVille(self.dictOrganisateur["ville"])
            except :
                pass

    def __set_properties(self):
        self.ctrl_annee.SetMinSize((80, -1))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.bouton_actualiser.SetToolTipString(_(u"Cliquez ici pour actualiser la liste en fonction des paramètres"))
        self.SetMinSize((-1, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        box_mois = wx.StaticBoxSizer(self.box_mois_staticbox, wx.VERTICAL)
        grid_sizer_mois = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        box_ville = wx.StaticBoxSizer(self.box_ville_staticbox, wx.VERTICAL)
        grid_sizer_ville = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_gps = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_ville2 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_ville.Add(self.radio_ville, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ville2.Add(self.label_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ville2.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_ville2.AddGrowableCol(1)
        grid_sizer_ville.Add(grid_sizer_ville2, 1, wx.EXPAND, 0)
        grid_sizer_ville.Add(self.radio_gps, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gps.Add(self.label_lat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gps.Add(self.ctrl_lat, 0, 0, 0)
        grid_sizer_gps.Add(self.label_long, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gps.Add(self.ctrl_long, 0, 0, 0)
        grid_sizer_ville.Add(grid_sizer_gps, 1, wx.EXPAND, 0)
        grid_sizer_ville.AddGrowableCol(1)
        box_ville.Add(grid_sizer_ville, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_parametres.Add(box_ville, 1, wx.EXPAND, 0)
        grid_sizer_mois.Add(self.label_mois, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mois.Add(self.ctrl_mois, 0, 0, 0)
        grid_sizer_mois.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mois.Add(self.ctrl_annee, 0, 0, 0)
        box_mois.Add(grid_sizer_mois, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_parametres.Add(box_mois, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(grid_sizer_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.bouton_actualiser, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_resultats, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnRadioVille(self, event): 
        self.ctrl_ville.Enable(self.radio_ville.GetValue())
        self.ctrl_lat.Enable(self.radio_gps.GetValue())
        self.ctrl_long.Enable(self.radio_gps.GetValue())

    def OnChoixMois(self, event): 
        pass

    def OnChoixAnnee(self, event): 
        pass

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Horairesdusoleil")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)        

    def GetOrganisateur(self):
        """ Récupère les infos sur l'organisateur """
        DB = GestionDB.DB()
        req = """SELECT cp, ville, gps
        FROM organisateur WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return None
        cp, ville, gps = listeDonnees[0]
        if cp == None : cp = ""
        if ville == None : ville = ""
        if gps == None : gps = ""
        if len(gps) > 0 :
            lat, long = gps.split(";") 
        else :
            lat, long = self.GetGPSOrganisateur(cp, ville) 
        dictOrganisateur = {"cp":cp, "ville":ville, "lat":lat, "long":long}
        return dictOrganisateur

    def GetPeriode(self):
        mois = self.ctrl_mois.GetSelection()+1
        annee = self.ctrl_annee.GetValue()
        return mois, annee
    
    def GetGPS(self):
        # VILLE
        if self.radio_ville.GetValue() == True :
            cp = self.ctrl_ville.GetValueCP()
            ville = self.ctrl_ville.GetValueVille()
            if cp == "" or cp == None or ville == "" or ville == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné correctement la ville !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            # recherche GPS
            dictGPS = UTILS_Gps.GPS(cp=cp, ville=ville, pays="France")
            if dictGPS == None : 
                dlg = wx.MessageDialog(self, _(u"Les coordonnées GPS n'ont pas été détectées !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            else :
                return dictGPS["lat"], dictGPS["long"]
        
        # COORDS
        else :
            lat = self.ctrl_lat.GetValue()
            long = self.ctrl_long.GetValue()
            if lat == "" or lat == None or long == "" or long == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné correctement les coordonnées GPS !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            else :
                return lat, long

    def OnBoutonActualiser(self, event): 
        coords = self.GetGPS()
        if coords == None or coords == False :
            return
        # Récupère GPS
        lat, long = coords
        self.AffichageResultats(lat, long)
    
    def AffichageResultats(self, lat, long):
        self.ctrl_resultats.Clear() 
        
        # Récupère période
        mois, annee = self.GetPeriode() 
        tmp, nbreJours = calendar.monthrange(annee, mois)
        
        c = City(("", "France", float(lat), float(long), "Europe/Paris"))
        for jour in range(1, nbreJours+1):
            # Recherche Horaires
            date = datetime.date(annee, mois, jour) 
            try :
                heureLever = c.sunrise(date=date)
                heureCoucher = c.sunset(date=date)
                # Formatage de la ligne
                dateFr = DateDDEnDateFR(date) 
                texte = u"%s : %dh%02d > %dh%02d \n" % (dateFr, heureLever.hour, heureLever.minute, heureCoucher.hour, heureCoucher.minute)
                self.ctrl_resultats.WriteText(texte)
            except :
                pass
                

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
