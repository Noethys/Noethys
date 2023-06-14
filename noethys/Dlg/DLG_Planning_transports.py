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
from Ctrl import CTRL_Bandeau
import six
import GestionDB
import datetime

from Ctrl.CTRL_Saisie_transport import DICT_CATEGORIES
from Data.DATA_Tables import DB_DATA as DICT_TABLES
from Dlg import DLG_Saisie_transport
from Utils import UTILS_Schedule
from Utils import UTILS_Transports

from Outils import wxScheduler
from Outils import wxReportScheduler



def ConvertDateWXenDT(datewx=None):
    """ Convertit une date WX.datetime en datetime """
    jour = datewx.GetDay()
    mois = datewx.GetMonth()+1
    annee = datewx.GetYear()
    heures = datewx.GetHour()
    minutes = datewx.GetMinute()
    dt = datetime.datetime(annee, mois, jour, heures, minutes)
    return dt

def ConvertDateDTenWX(date=None, heure=None):
    """ Convertit une date datetime en WX.datetime """
    if type(date) == six.text_type :
        date = datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))
    hr, mn = 0, 0
    if heure != None :
        hr, mn = heure.split(":")
        hr = int(hr) 
        mn = int(mn)
    datewx = wx.DateTime()
    datewx.Set(date.day, month=date.month-1, year=date.year, hour=hr, minute=mn)
    return datewx



class ToolBar(wx.ToolBar):
    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, style=wx.TB_FLAT|wx.TB_TEXT)
        self.parent = parent
        self.periodCount = 1

        ID_OUTIL_JOUR = wx.Window.NewControlId()
        ID_OUTIL_SEMAINE = wx.Window.NewControlId()
        ID_OUTIL_MOIS = wx.Window.NewControlId()
        ID_OUTIL_HORIZONTAL = wx.Window.NewControlId()
        ID_OUTIL_VERTICAL = wx.Window.NewControlId()
        ID_OUTIL_RECULER = wx.Window.NewControlId()
        ID_OUTIL_AVANCER = wx.Window.NewControlId()
        ID_OUTIL_MOINS = wx.Window.NewControlId()
        ID_OUTIL_PLUS = wx.Window.NewControlId()
        ID_OUTIL_AUJOURDHUI = wx.Window.NewControlId()
        ID_OUTIL_CHERCHER = wx.Window.NewControlId()
        ID_OUTIL_APERCU = wx.Window.NewControlId()

        # Boutons
        self.AddLabelTool(ID_OUTIL_JOUR, _(u"Jour"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calendrier_jour.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Affichage quotidien"), "")
        self.AddLabelTool(ID_OUTIL_SEMAINE, _(u"Semaine"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calendrier_semaine.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Affichage hebdomadaire"), "")
        self.AddLabelTool(ID_OUTIL_MOIS, _(u"Mois"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calendrier_mois.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Affichage mensuel"), "")
        self.AddSeparator()
        self.AddLabelTool(ID_OUTIL_HORIZONTAL, _(u"Horizontal"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calendrier_horizontal.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Affichage horizontal"), "")
        self.AddLabelTool(ID_OUTIL_VERTICAL, _(u"Vertical"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calendrier_vertical.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, _(u"Affichage vertical"), "")
        self.ToggleTool(ID_OUTIL_VERTICAL, True)
        self.AddSeparator()
        self.AddLabelTool(ID_OUTIL_RECULER, _(u"Reculer"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Precedent.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Reculer"), "")
        self.AddLabelTool(ID_OUTIL_AVANCER, _(u"Avancer"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Suivant.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Avancer"), "")
        self.AddSeparator()
        self.AddLabelTool(ID_OUTIL_MOINS, _(u"Moins"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_moins.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Afficher moins"), "")
        self.EnableTool(ID_OUTIL_MOINS, False)
        self.AddLabelTool(ID_OUTIL_PLUS, _(u"Plus"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/zoom_plus.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Afficher plus"), "")
        self.AddSeparator()
        self.AddLabelTool(ID_OUTIL_AUJOURDHUI, _(u"Aujourd'hui"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Jour.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Aujourd'hui"), "")
        self.AddLabelTool(ID_OUTIL_CHERCHER, _(u"Chercher"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Calendrier_zoom.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Chercher une date"), "")
        self.AddLabelTool(ID_OUTIL_APERCU, _(u"Aperçu"), wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Apercu.png"), wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Aperçu avant impression"), "")

        # Binds
        self.Bind(wx.EVT_TOOL, self.OnAffichageJour, id=ID_OUTIL_JOUR)
        self.Bind(wx.EVT_TOOL, self.OnAffichageSemaine, id=ID_OUTIL_SEMAINE)
        self.Bind(wx.EVT_TOOL, self.OnAffichageMois, id=ID_OUTIL_MOIS)
        self.Bind(wx.EVT_TOOL, self.OnAffichageVertical, id=ID_OUTIL_VERTICAL)
        self.Bind(wx.EVT_TOOL, self.OnAffichageHorizontal, id=ID_OUTIL_HORIZONTAL)
        self.Bind(wx.EVT_TOOL, self.OnReculer, id=ID_OUTIL_RECULER)
        self.Bind(wx.EVT_TOOL, self.OnAvancer, id=ID_OUTIL_AVANCER)
        self.Bind(wx.EVT_TOOL, self.OnMoins, id=ID_OUTIL_MOINS)
        self.Bind(wx.EVT_TOOL, self.OnPlus, id=ID_OUTIL_PLUS)
        self.Bind(wx.EVT_TOOL, self.OnAujourdhui, id=ID_OUTIL_AUJOURDHUI)
        self.Bind(wx.EVT_TOOL, self.OnChercherDate, id=ID_OUTIL_CHERCHER)
        self.Bind(wx.EVT_TOOL, self.OnApercu, id=ID_OUTIL_APERCU)

        self.SetToolBitmapSize((32, 32))
        self.Realize()
    
    def OnAffichageJour(self, event):
        self.parent.ctrl_planning.SetViewType(wxScheduler.wxSCHEDULER_DAILY)
        self.MAJAffichagePlusMoins() 

    def OnAffichageSemaine(self, event):
        self.parent.ctrl_planning.SetViewType(wxScheduler.wxSCHEDULER_WEEKLY)
        self.MAJAffichagePlusMoins() 

    def OnAffichageMois(self, event):
        self.parent.ctrl_planning.SetViewType(wxScheduler.wxSCHEDULER_MONTHLY)
        self.MAJAffichagePlusMoins() 

    def OnAffichageHorizontal(self, event):
        self.parent.ctrl_planning.Freeze()
        self.parent.ctrl_planning.SetStyle(wxScheduler.wxSCHEDULER_HORIZONTAL)
        self.parent.ctrl_planning.Thaw()

    def OnAffichageVertical(self, event):
        self.parent.ctrl_planning.Freeze()
        self.parent.ctrl_planning.SetStyle(wxScheduler.wxSCHEDULER_VERTICAL)
        self.parent.ctrl_planning.Thaw()

    def OnReculer(self, event):
        self.parent.ctrl_planning.SetViewType(wxScheduler.wxSCHEDULER_PREV)

    def OnAvancer(self, event):
        self.parent.ctrl_planning.SetViewType(wxScheduler.wxSCHEDULER_NEXT)

    def MAJAffichagePlusMoins(self):
        if self.parent.ctrl_planning.GetViewType() == wxScheduler.wxSCHEDULER_MONTHLY :
            self.EnableTool(ID_OUTIL_PLUS, False)
        else :
            self.EnableTool(ID_OUTIL_PLUS, True)
        if self.parent.ctrl_planning.GetViewType() == wxScheduler.wxSCHEDULER_MONTHLY or self.periodCount < 2 :
            self.EnableTool(ID_OUTIL_MOINS, False)
        else :
            self.EnableTool(ID_OUTIL_MOINS, True)
        
    def OnMoins(self, event):
        self.periodCount -= 1
        if self.periodCount == 1 :
            self.EnableTool(ID_OUTIL_MOINS, False)
        else :
            self.EnableTool(ID_OUTIL_MOINS, True)
        self.parent.ctrl_planning.SetPeriodCount(self.periodCount)

    def OnPlus(self, event):
        self.periodCount += 1
        if self.periodCount > 1 :
            self.EnableTool(ID_OUTIL_MOINS, True)
        self.parent.ctrl_planning.SetPeriodCount(self.periodCount)

    def OnAujourdhui(self, event):
        self.parent.ctrl_planning.SetViewType(wxScheduler.wxSCHEDULER_TODAY)

    def OnChercherDate(self, event):
        dlg = DLG_Recherche_date(self)
        if dlg.ShowModal():
            newDate = dlg.GetDate()
        dlg.Destroy()
        self.parent.ctrl_planning.SetDate(newDate)

    def OnApercu(self, event):
        """ Aperçu avant impression """
        # Demande à l'utilisateur la mise en page
        reglages = self.parent.reglagesImpression
        
        data = wx.PrintData()
        data.SetOrientation(reglages["orientation"])
        data.SetPaperId(reglages["papier"])
        pageData = wx.PageSetupDialogData(data)
        pageData.SetMarginTopLeft(wx.Point(reglages["marge_haut"], reglages["marge_gauche"]))
        pageData.SetMarginBottomRight(wx.Point(reglages["marge_bas"], reglages["marge_droite"]))

        dlg = wx.PageSetupDialog(self, pageData)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetPageSetupData()
            reglages["papier"] = data.GetPrintData().GetPaperId()
            reglages["orientation"] = data.GetPrintData().GetOrientation()
            reglages["marge_haut"] = data.GetMarginTopLeft()[0]
            reglages["marge_gauche"] = data.GetMarginTopLeft()[1]
            reglages["marge_bas"] = data.GetMarginBottomRight()[0]
            reglages["marge_droite"] = data.GetMarginBottomRight()[1]
            dlg.Destroy()
        else :
            dlg.Destroy()
            return

        format = self.parent.ctrl_planning.GetViewType()
        style = self.parent.ctrl_planning.GetStyle()
        drawer = self.parent.ctrl_planning.GetDrawer()
        weekstart = self.parent.ctrl_planning.GetWeekStart()
        periodCount = self.parent.ctrl_planning.GetPeriodCount()
        day	 = self.parent.ctrl_planning.GetDate()
        rpt1	 = wxReportScheduler.wxReportScheduler( format, style, drawer, day, weekstart, periodCount, self.parent.ctrl_planning.GetSchedules(), self.parent.ctrl_planning.joursSpeciaux, reglages )
        rpt2	 = wxReportScheduler.wxReportScheduler( format, style, drawer, day, weekstart, periodCount, self.parent.ctrl_planning.GetSchedules(), self.parent.ctrl_planning.joursSpeciaux, reglages )

        data = wx.PrintData()
        data.SetOrientation(reglages["orientation"])
        data.SetPaperId(reglages["papier"])

        preview = wx.PrintPreview(rpt1, rpt2, data)
##        preview.SetZoom( 100 )
##        if preview.Ok():
##            frame = wx.PreviewFrame(preview, None, _(u"Aperçu avant impression"), size=wx.Size( 700, 500 ) )
##            frame.Initialize()
##            frame.Show( True )
        
##        from Utils import UTILS_Printer
##        preview_window = UTILS_Printer.PreviewFrame(preview, None, _(u"Aperçu avant impression"), reglages["orientation"])
##        preview_window.Initialize()
##        preview_window.MakeModal(False)
##        preview_window.Show(True)
        
        preview.SetZoom(100)
        frame = wx.GetApp().GetTopWindow() 
        preview_window = wx.PreviewFrame(preview, None, _(u"Aperçu avant impression"))
        preview_window.Initialize()
        preview_window.MakeModal(False)
        preview_window.SetPosition(frame.GetPosition())
        preview_window.SetSize(frame.GetSize())
        preview_window.Show(True)


# --------------------------------------------------------------------------------------------------------------------------

class DLG_Recherche_date(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        # Contrôles
        if 'phoenix' in wx.PlatformInfo:
            self._date = wx.adv.DatePickerCtrl(self, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY )
        else :
            self._date = wx.DatePickerCtrl(self, style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY )
        btOk = wx.Button( self, wx.ID_OK, _(u"Ok") )
        btCancel = wx.Button( self, wx.ID_CANCEL, _(u"Annuler") )
        # Layout
        szAll = wx.BoxSizer( wx.VERTICAL )
        szDate = wx.BoxSizer( wx.HORIZONTAL )
        szDate.Add( wx.StaticText( self, label=_(u"Sélectionnez une date :")), wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )
        szDate.Add( self._date, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5 )
        btSizer = wx.StdDialogButtonSizer()
        btSizer.Add( btOk, 0, wx.RIGHT, 5 )
        btSizer.Add( btCancel, 0, wx.LEFT, 5 )
        btSizer.Realize()
        szAll.Add( szDate, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5 )
        szAll.Add( btSizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5 )
        self.SetSizerAndFit(szAll)
        
    def GetDate(self):
        return self._date.GetValue()


# --------------------------------------------------------------------------------------------------------------------------

class CTRL_Planning(wx.Panel):
    """ Contrôle Scheduler """
    def __init__(self, parent, IDindividu=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        
        # Barre d'outils
        self.barre_outils = ToolBar(self)
        
        # Insertion des vacances et jours fériés dans le schedule
        self.joursSpeciaux = UTILS_Schedule.JoursSpeciaux()
        
        # Réglage de l'impression
        self.reglagesImpression = {
            "orientation" : wx.PORTRAIT,
            "papier" : wx.PAPER_A4,            
            "marge_haut" : 30,
            "marge_bas" : 30,
            "marge_gauche" : 30,
            "marge_droite" : 30,
            }
        
        # Création du scheduler
        self.ctrl_planning = wxScheduler.wxScheduler(self, joursSpeciaux=self.joursSpeciaux)
        self.ctrl_planning.SetResizable(True)
        self.ctrl_planning.SetShowWorkHour(False)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.barre_outils, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_planning, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

        # Binds
        self.ctrl_planning.Bind(wxScheduler.EVT_SCHEDULE_DCLICK, self.OnDoubleClick)
        self.ctrl_planning.Bind(wxScheduler.EVT_SCHEDULE_RIGHT_CLICK, self.OnClickDroit)
        
        # Importation
        self.Importation() 
        
    
    def OnClickDroit(self, event):
        """ Menu contextuel """
        schedule = event.schedule
        date = event.date
        
        def Ajouter(evt):
            self.Ajouter(date)
            
        def Modifier(evt):
            self.Modifier(schedule)
            
        def Supprimer(evt):
            self.Supprimer(schedule)
        
        menuPop = UTILS_Adaptations.Menu()
        
        if schedule == None :
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, Ajouter, id=10)
        else :
            item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, Modifier, id=20)
            
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, Supprimer, id=30)
            
        self.PopupMenu(menuPop)
        menuPop.Destroy()
        
    def OnDoubleClick(self, event):
        """ Sur un double-clic """
        schedule = event.schedule
        if schedule == None :
            self.Ajouter(date=event.date)
        else :
            self.Modifier(schedule=schedule)
    
    def Ajouter(self, date=None):
        """ Création d'un transport """
        datedt = ConvertDateWXenDT(date)
        dlg = DLG_Saisie_transport.Dialog(self, IDtransport=None, IDindividu=self.IDindividu)
        dlg.SetDateHeure(datedt)
        if dlg.ShowModal() == wx.ID_OK:
##            dictTransport = dlg.GetDictDonnees()
##            dictTransport = self.AnalyseTransport(dictTransport)
##            self.CreationSchedule(dictTransport) 
            self.MAJ() 
        dlg.Destroy()

    def AjouterLot(self):
        """ Création d'un lot de transports """
        dlg = DLG_Saisie_transport.Dialog_multiple(self, IDindividu=self.IDindividu)
        if dlg.ShowModal() == wx.ID_OK:
##            listeDictDonnees = dlg.GetListeDictDonnees()
##            for dictTransport in listeDictDonnees :
##                dictTransport = self.AnalyseTransport(dictTransport)
##                self.CreationSchedule(dictTransport) 
            self.MAJ() 
        dlg.Destroy()

##        print date
##        schedule = wxScheduler.wxSchedule()
##        schedule.description = _(u"Ceci est un test sur 3 jours")
##        schedule.start = wx.DateTimeFromHMS(15, 0, 0)
##        end = wx.DateTimeFromHMS(16, 0, 0)
##        end.AddDS(wx.DateSpan(days=2))
##        schedule.end = end
##        schedule.complete = 0.50
##        schedule.foreground = wx.Color(255, 0, 0)
##        # schedule.foreground.font = wx.Font()
##        # schedule.color = wx.Color(200, 200, 200)
##        schedule.icons = [wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Avion.png"), wx.BITMAP_TYPE_ANY),]
##        self.ctrl_planning.Add(schedule)
        
    def Modifier(self, schedule=None):
        """ Modification d'un schedule """
        self.ctrl_planning.Freeze()
        dlg = DLG_Saisie_transport.Dialog(self, IDtransport=schedule.IDtransport, IDindividu=self.IDindividu)
        if dlg.ShowModal() == wx.ID_OK:
##            dictTransport = dlg.GetDictDonnees()
##            dictTransport = self.AnalyseTransport(dictTransport)
##            self.ModificationSchedule(dictTransport, schedule)
            self.MAJ() 
        dlg.Destroy()
        self.ctrl_planning.Thaw()
        
    def Supprimer(self, schedule=None):
        """ Suppression d'un schedule """
        DB = GestionDB.DB()
        DB.ReqDEL("transports", "IDtransport", schedule.IDtransport)
        DB.Close() 
        self.ctrl_planning.Delete(schedule)
    
    def MAJ(self):
        self.ctrl_planning.DeleteAll()
        self.Importation()
        
    def Importation(self):
        """ Importation des transports depuis la base de données """
        # Récupération des champs de la table
        listeChamps = []
        for nom, type, info in DICT_TABLES["transports"] :
            listeChamps.append(nom)
        
        # Importation
        DB = GestionDB.DB()
        req = """SELECT %s
        FROM transports 
        WHERE mode="TRANSP" AND IDindividu=%d;""" % (", ".join(listeChamps), self.IDindividu)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        # Stockage des données sous forme de dictionnaires dans une liste
        listeTransports = []
        for donnees in listeDonnees :
            dictTemp = {}
            index = 0
            for valeur in donnees :
                dictTemp[listeChamps[index]] = valeur
                index += 1
            listeTransports.append(dictTemp)
        
        # Récupération des données tierces
        modLocalisation = UTILS_Transports.AnalyseLocalisation() 
        
        # Création des schedules
        for dictTransport in listeTransports :
            dictTransport = self.AnalyseTransport(dictTransport, modLocalisation)
            self.CreationSchedule(dictTransport) 
    
    def AnalyseTransport(self, dictTransport={}, modLocalisation=None):
        """ Analyse les données et les convertit en donnée texte pour le futur schedule """        
        # catégorie
        categorie = dictTransport["categorie"]
        dictTransport["labelCategorie"] = DICT_CATEGORIES[categorie]["label"]
        
        # Image
        dictTransport["image"] = DICT_CATEGORIES[categorie]["image"]
        
        # Analyse des localisations
        depart_nom = modLocalisation.Analyse(dictTransport["depart_IDarret"], dictTransport["depart_IDlieu"], dictTransport["depart_localisation"])
        arrivee_nom = modLocalisation.Analyse(dictTransport["arrivee_IDarret"], dictTransport["arrivee_IDlieu"], dictTransport["arrivee_localisation"])
        
        # Création du label du schedule
        dictTransport["label"] = u"%s > %s" % (depart_nom, arrivee_nom)
        
        return dictTransport
        
    def CreationSchedule(self, dictDonnees={}):
        """ Création d'un schedule """
        schedule = wxScheduler.wxSchedule()
        schedule.IDtransport = dictDonnees["IDtransport"]
        self.RemplitSchedule(dictDonnees, schedule)
        self.ctrl_planning.Add(schedule)
    
    def ModificationSchedule(self, dictDonnees={}, schedule=None):
        self.RemplitSchedule(dictDonnees, schedule)
    
    def RemplitSchedule(self, dictDonnees={}, schedule=None):
        # Icone
        schedule.icons = [wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s.png" % dictDonnees["image"]), wx.BITMAP_TYPE_ANY),]
        
        # Date et heure de début
        schedule.start = ConvertDateDTenWX(date=dictDonnees["depart_date"], heure=dictDonnees["depart_heure"])
        
        # Date et heure de fin
        schedule.end = ConvertDateDTenWX(date=dictDonnees["arrivee_date"], heure=dictDonnees["arrivee_heure"])
        
        # texte
        schedule.description = dictDonnees["label"]
        
##        schedule.complete = 0.50
##        schedule.foreground = wx.Color(255, 0, 0)
##        # schedule.foreground.font = wx.Font()
##        # schedule.color = wx.Color(200, 200, 200)
        
        
        
        
# --------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDindividu=None):
        """ Affiche un planning des transports pour un individu"""
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez consulter ici le planning complet des transports enregistrés pour un individu. Pour saisir un transport, double-cliquez sur le jour et l'heure souhaités dans ce planning. Double-cliquez sur un transport pour le modifier ou utilisez le bouton droit de la souris pour accéder au menu contextuel.")
        titre = _(u"Planning des transports")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Transport.png")
        
        # Planning
        self.ctrl_planning = CTRL_Planning(self, IDindividu=IDindividu)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_saisie_lot = CTRL_Bouton_image.CTRL(self, texte=_(u"Saisir un lot de transports"), cheminImage="Images/32x32/Magique.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
##        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSaisieLot, self.bouton_saisie_lot)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_saisie_lot.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir un lot de transports")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
##        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))
        self.SetMinSize((950, 850))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Planning
        grid_sizer_base.Add(self.ctrl_planning, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_saisie_lot, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
##        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)
    
    def OnBoutonSaisieLot(self, event):
        self.ctrl_planning.AjouterLot() 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Transports1")


        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDindividu=46)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
