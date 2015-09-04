#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Utilisateurs



class Track(object):
    def __init__(self, donnees):
        self.IDvacance = donnees[0]
        self.nom = donnees[1]
        self.annee = donnees[2]
        self.date_debut = donnees[3]
        self.date_fin = donnees[4]
    
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        listeID = None
        db = GestionDB.DB()
        req = """SELECT IDvacance, nom, annee, date_debut, date_fin
        FROM vacances ORDER BY date_debut;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()

        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDate(texteDate):
            """ Transforme le format "aaaa-mm-jj" en "mercredi 12 septembre 2008" """
            listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
            listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
            jour = int(texteDate[8:10])
            mois = int(texteDate[5:7])
            annee = int(texteDate[:4])
            jourSemaine = int(datetime.date(annee, mois, jour).strftime("%w"))
            texte = listeJours[jourSemaine-1] + " " + str(jour) + " " + listeMois[mois-1] + " " + str(annee)
            return texte   
            
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDvacance", typeDonnee="entier"),
            ColumnDefn(_(u"Ann�e"), 'left', 50, "annee", typeDonnee="texte"),
            ColumnDefn(_(u"Nom"), "left", 120, "nom", typeDonnee="texte"), 
            ColumnDefn(_(u"Date de d�but"), "left", 190, "date_debut", typeDonnee="date", stringConverter=FormateDate), 
            ColumnDefn(_(u"Date de fin"), "left", 190, "date_fin", typeDonnee="date", stringConverter=FormateDate), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune p�riode de vacances"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[3])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # S�lection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDvacance
                
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()

        # Item Supprimer
        item = wx.MenuItem(menuPop, 70, _(u"Importer depuis Internet"))
        bmp = wx.Bitmap("Images/16x16/Updater.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Importation, id=70)
                
        menuPop.AppendSeparator()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des vacances"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des vacances"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vacances", "creer") == False : return
        dlg = Saisie(self)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            annee = dlg.GetAnnee()
            dateDebut = dlg.GetDateDebut()
            dateFin = dlg.GetDateFin()
            DB = GestionDB.DB()
            listeDonnees = [
                ("nom", nom ),
                ("annee", annee ),
                ("date_debut", dateDebut),
                ("date_fin", dateFin),
                ]
            IDvacance = DB.ReqInsert("vacances", listeDonnees)
            DB.Close()
            self.MAJ(IDvacance)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vacances", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune p�riode de vacances � modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDvacance = self.Selection()[0].IDvacance
        nom = self.Selection()[0].nom
        annee = self.Selection()[0].annee
        date_debut = self.Selection()[0].date_debut
        date_fin = self.Selection()[0].date_fin
        dlg = Saisie(self, IDvacance)
        dlg.SetNom(nom)
        dlg.SetAnnee(annee)
        dlg.SetDateDebut(date_debut)
        dlg.SetDateFin(date_fin)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            annee = dlg.GetAnnee()
            dateDebut = dlg.GetDateDebut()
            dateFin = dlg.GetDateFin()
            DB = GestionDB.DB()
            listeDonnees = [
                ("nom", nom ),
                ("annee", annee ),
                ("date_debut", dateDebut),
                ("date_fin", dateFin),
                ]
            DB.ReqMAJ("vacances", listeDonnees, "IDvacance", IDvacance)
            DB.Close()
            self.MAJ(IDvacance)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vacances", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune p�riode de vacances � supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette p�riode de vacances ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDvacance = self.Selection()[0].IDvacance
            DB = GestionDB.DB()
            DB.ReqDEL("vacances", "IDvacance", IDvacance)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    
    def Importation(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_vacances", "creer") == False : return
        import DLG_Importation_vacances
        dlg = DLG_Importation_vacances.Dialog(self)
        if dlg.ShowModal()  == wx.ID_OK:
            self.MAJ() 
        dlg.Destroy()
        
        
        
# -------------------------------------------------------------------------------------------------------------------------------------------

class DatePickerCtrl(wx.DatePickerCtrl):
    def __init__(self, parent):
        wx.DatePickerCtrl.__init__(self, parent, -1, style=wx.DP_DROPDOWN) 
        self.parent = parent
        
    def SetDate(self, dateTxt=None):
        jour = int(dateTxt[8:10])
        mois = int(dateTxt[5:7])-1
        annee = int(dateTxt[:4])
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        self.SetValue(date)
    
    def GetDate(self):
        date = self.GetValue()
        dateDD = datetime.date(date.GetYear(), date.GetMonth()+1, date.GetDay())
        return str(dateDD)

    
    
class Saisie(wx.Dialog):
    def __init__(self, parent, IDvacance=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent

        self.sizer_periode_staticbox = wx.StaticBox(self, -1, _(u"Nom de la p�riode"))
        choices = [_(u"F�vrier"), _(u"P�ques"), _(u"Et�"), _(u"Toussaint"), _(u"No�l")]
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.Choice(self, -1, choices=choices, size=(100, -1))
        self.label_annee = wx.StaticText(self, -1, _(u"Ann�e :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, "", style=wx.TE_CENTRE, size=(60, -1))
        self.ctrl_annee.SetRange(2000, 2099)
        anneeEnCours = datetime.date.today().year
        self.ctrl_annee.SetValue(anneeEnCours)
        
        self.sizer_dates_staticbox = wx.StaticBox(self, -1, _(u"Dates de la p�riode"))
        self.label_dateDebut = wx.StaticText(self, -1, u"Du")
        self.ctrl_dateDebut = DatePickerCtrl(self)
        self.label_dateFin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_dateFin = DatePickerCtrl(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        # Propri�t�s
        self.ctrl_nom.SetToolTipString(_(u"Choisissez ici le nom de la p�riode"))
        self.ctrl_annee.SetToolTipString(_(u"Saisissez ici l'ann�e de la p�riode. Ex. : '2011'"))
        self.ctrl_dateDebut.SetToolTipString(_(u"Saisissez ici la date de d�but de la p�riode"))
        self.ctrl_dateFin.SetToolTipString(_(u"Saisissez ici la date de fin de la p�riode"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la saisie"))
        if IDvacance == None :
            self.SetTitle(_(u"Saisie d'une p�riode de vacances"))
        else:
            self.SetTitle(_(u"Modification d'une p�riode de vacances"))
        self.SetMinSize((350, -1))
    
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        
        sizer_contenu_1 = wx.StaticBoxSizer(self.sizer_periode_staticbox, wx.VERTICAL)
        grid_sizer_contenu_1 = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_contenu_1.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu_1.Add(self.ctrl_nom, 0, 0, 0)
        grid_sizer_contenu_1.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu_1.Add(self.ctrl_annee, 0, 0, 0)
        sizer_contenu_1.Add(grid_sizer_contenu_1, 1, wx.ALL|wx.EXPAND, 10)
        
        sizer_contenu_2 = wx.StaticBoxSizer(self.sizer_dates_staticbox, wx.VERTICAL)
        grid_sizer_contenu_2 = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_contenu_2.Add(self.label_dateDebut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu_2.Add(self.ctrl_dateDebut, 0, 0, 0)
        grid_sizer_contenu_2.Add(self.label_dateFin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu_2.Add(self.ctrl_dateFin, 0, 0, 0)
        sizer_contenu_2.Add(grid_sizer_contenu_2, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(sizer_contenu_1, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu_2, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
    
    def SetNom(self, nom=None):
        self.ctrl_nom.SetStringSelection(nom)
        
    def GetNom(self):
        return self.ctrl_nom.GetStringSelection()
        
    def SetAnnee(self, annee=None):
        self.ctrl_annee.SetValue(annee)
        
    def GetAnnee(self):
        return self.ctrl_annee.GetValue()
    
    def SetDateDebut(self, date=None):
        self.ctrl_dateDebut.SetDate(date)
        
    def GetDateDebut(self):
        return self.ctrl_dateDebut.GetDate()    

    def SetDateFin(self, date=None):
        self.ctrl_dateFin.SetDate(date)
        
    def GetDateFin(self):
        return self.ctrl_dateFin.GetDate()      
    
    def OnBoutonOk(self, event):
        if self.ctrl_nom.GetSelection == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un nom de p�riode !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        date_debut = self.ctrl_dateDebut.GetDate()
        date_fin = self.ctrl_dateFin.GetDate() 
        # V�rifie que la date de fin est sup�rieure � la date de d�but de contrat
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de fin de vacances doit �tre sup�rieure � la date de d�but !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_dateFin.SetFocus()
            return
        
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Vacances")



# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une p�riode de vacances..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
