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
import GestionDB

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass



class Track(object):
    def __init__(self, donnees):
        self.IDgroupe = donnees[0]
        self.IDactivite = donnees[1]
        self.nom = donnees[2]
        self.ordre = donnees[3]
        self.abrege = donnees[4]
    
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.IDactivite = kwds.pop("IDactivite", None)
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
        req = """SELECT IDgroupe, IDactivite, nom, ordre, abrege
        FROM groupes 
        WHERE IDactivite=%d 
        ORDER BY ordre;""" % self.IDactivite
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
                
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDgroupe"),
            ColumnDefn(_(u"Ordre"), "left", 0, "ordre"),
            ColumnDefn(_(u"Nom"), 'left', 300, "nom", isSpaceFilling=True),
            ColumnDefn(_(u"Abr�g�"), 'left', 160, "abrege"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun groupe"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
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
        self._ResizeSpaceFillingColumns() 
    
    def Selection(self):
        return self.GetSelectedObjects() 

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDgroupe
                
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
        
        # Item Deplacer vers le haut
        item = wx.MenuItem(menuPop, 60, _(u"D�placer vers le haut"))
        bmp = wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=60)
        if noSelection == True : item.Enable(False)
        
        # Item D�placer vers le bas
        item = wx.MenuItem(menuPop, 70, _(u"D�placer vers le bas"))
        bmp = wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=70)
        if noSelection == True : item.Enable(False)
        
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des groupes"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des groupes"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        # Recherche num�ro d'ordre � appliquer
        listeTemp = []
        for track in self.donnees :
            listeTemp.append(track.ordre)
        if len(listeTemp) > 0 :
            ordre = max(listeTemp) + 1
        else :
            ordre = 1
        # DLG Saisie
        dlg = Saisie(self)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            abrege = dlg.GetAbrege()
            DB = GestionDB.DB()
            listeDonnees = [ ("IDactivite", self.IDactivite), ("nom", nom), ("ordre", ordre), ("abrege", abrege),]
            IDgroupe = DB.ReqInsert("groupes", listeDonnees)
            DB.Close()
            self.MAJ(IDgroupe)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun groupe � modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDgroupe = self.Selection()[0].IDgroupe
        nom = self.Selection()[0].nom
        abrege = self.Selection()[0].abrege
        
        # DLG Saisie
        dlg = Saisie(self, nom, abrege)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            abrege = dlg.GetAbrege()
            DB = GestionDB.DB()
            listeDonnees = [ ("IDactivite", self.IDactivite), ("nom", nom), ("abrege", abrege)]
            DB.ReqMAJ("groupes", listeDonnees, "IDgroupe", IDgroupe)
            DB.Close()
            self.MAJ(IDgroupe)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun groupe � supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDgroupe = self.Selection()[0].IDgroupe
        
        # V�rifie que le groupe n'est pas d�j� attribu� � une unit� de consommation
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDunite_groupe)
        FROM unites_groupes 
        WHERE IDgroupe=%d
        ;""" % IDgroupe
        DB.ExecuterReq(req)
        nbreUnites = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreUnites > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce groupe a d�j� �t� attribu� � %d unit�(s) de consommation.\n\nVous ne pouvez donc pas le supprimer !") % nbreUnites, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que le groupe n'est pas d�j� attribu� � une ouverture
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDouverture)
        FROM ouvertures 
        WHERE IDgroupe=%d
        ;""" % IDgroupe
        DB.ExecuterReq(req)
        nbreOuvertures = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreOuvertures > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce groupe a d�j� �t� attribu� � %d ouverture(s).\n\nVous ne pouvez donc pas le supprimer !") % nbreOuvertures, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que le groupe n'est pas d�j� attribu� � un remplissage
##        DB = GestionDB.DB()
##        req = """SELECT COUNT(IDremplissage)
##        FROM remplissage
##        WHERE IDgroupe=%d
##        ;""" % IDgroupe
##        DB.ExecuterReq(req)
##        nbreRemplissages = int(DB.ResultatReq()[0][0])
##        DB.Close()
##        if nbreRemplissages > 0 :
##            dlg = wx.MessageDialog(self, _(u"Ce groupe a d�j� �t� attribu� � %d remplissage(s).\n\nVous ne pouvez donc pas le supprimer !") % nbreRemplissages, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return

        # V�rifie que le groupe n'est pas d�j� attribu� � une inscription
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDinscription)
        FROM inscriptions 
        WHERE IDgroupe=%d
        ;""" % IDgroupe
        DB.ExecuterReq(req)
        nbreInscriptions = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreInscriptions > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce groupe a d�j� �t� attribu� � %d inscription(s).\n\nVous ne pouvez donc pas le supprimer !") % nbreInscriptions, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que le groupe n'est pas d�j� attribu� � une consommation
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDconso)
        FROM consommations 
        WHERE IDgroupe=%d
        ;""" % IDgroupe
        DB.ExecuterReq(req)
        nbreConsommations = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreConsommations > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce groupe a d�j� �t� attribu� � %d consommation(s).\n\nVous ne pouvez donc pas le supprimer !") % nbreConsommations, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # V�rifie que le groupe n'est pas d�j� attribu� � un tarif
        DB = GestionDB.DB()
        req = """SELECT IDtarif, groupes
        FROM tarifs 
        ;"""
        DB.ExecuterReq(req)
        listeTarifs = DB.ResultatReq()
        DB.Close()
        nbreTarifs = 0
        for IDtarif, groupesTemp in listeTarifs :
            if groupesTemp != None :
                listeTemp = groupesTemp.split(";")
                for IDgroupeTemp in listeTemp :
                    if int(IDgroupeTemp) == IDgroupe :
                        nbreTarifs += 1
        if nbreTarifs > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce groupe a d�j� �t� attribu� � %d tarif(s).\n\nVous ne pouvez donc pas le supprimer !") % nbreTarifs, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce groupe ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("groupes", "IDgroupe", IDgroupe)
            DB.ReqDEL("remplissage", "IDgroupe", IDgroupe)
            DB.Close() 
            self.MAJordre(IDgroupe)
            self.MAJ()
        dlg.Destroy()


    def MAJordre(self, IDgroupe=None):
        DB = GestionDB.DB()
        ordre = 1
        for index in range(0, len(self.donnees)) :
            objet = self.GetObjectAt(index)
            if objet.IDgroupe != IDgroupe :
                DB.ReqMAJ("groupes", [("ordre", ordre),], "IDgroupe", objet.IDgroupe)
                ordre += 1
        DB.Close()

    def Monter(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun groupe dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDgroupe = self.Selection()[0].IDgroupe
        ordre = self.Selection()[0].ordre
        if ordre == 1 : return
        DB = GestionDB.DB()
        # Modifie groupe actuel
        DB.ReqMAJ("groupes", [("ordre", ordre-1),], "IDgroupe", IDgroupe)
        self.Selection()[0].ordre = ordre-1
        # Modifie groupe a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        groupe2 = self.GetObjectAt(index-1)
        IDgroupe2 = groupe2.IDgroupe
        DB.ReqMAJ("groupes", [("ordre", ordre),], "IDgroupe", IDgroupe2)
        DB.Close()
        self.MAJ(IDgroupe)
    
    def Descendre(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun groupe dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDgroupe = self.Selection()[0].IDgroupe
        ordre = self.Selection()[0].ordre
        if ordre == len(self.donnees) : return
        DB = GestionDB.DB()
        # Modifie groupe actuel
        DB.ReqMAJ("groupes", [("ordre", ordre+1),], "IDgroupe", IDgroupe)
        self.Selection()[0].ordre = ordre+1
        # Modifie groupe a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        groupe2 = self.GetObjectAt(index+1)
        IDgroupe2 = groupe2.IDgroupe
        DB.ReqMAJ("groupes", [("ordre", ordre),], "IDgroupe", IDgroupe2)
        DB.Close()
        self.MAJ(IDgroupe)


# -------------------------------------------------------------------------------------------------------------------------------------------

class Saisie(wx.Dialog):
    def __init__(self, parent, nom=None, abrege=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        if nom != None :
            self.ctrl_nom.SetValue(nom)
            
        self.label_abrege = wx.StaticText(self, -1, _(u"Abr�g� :"))
        self.ctrl_abrege = wx.TextCtrl(self, -1, "")
        if abrege !=None :
            self.ctrl_abrege.SetValue(abrege)
            
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        if nom == None :
            self.SetTitle(_(u"Saisie d'un groupe"))
        else:
            self.SetTitle(_(u"Modification d'un groupe"))
        self.SetMinSize((500, -1))
        
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici l'intitul� du groupe (Ex : '3-6 ans', 'Grands'...)"))
        self.ctrl_abrege.SetToolTipString(_(u"Saisissez ici le nom abr�g� du groupe (Ex : '3-6', 'GRANDS'..."))

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_abrege, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_abrege, 0, 0, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
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
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
    
    def GetNom(self):
        return self.ctrl_nom.GetValue()
    
    def GetAbrege(self):
        return self.ctrl_abrege.GetValue()
        
    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        abrege = self.ctrl_abrege.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de groupe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        if abrege == "" :
            dlg = wx.MessageDialog(self, _(u"Etes-vous s�r de ne pas vouloir saisir de nom abr�g� pour ce groupe ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse !=  wx.ID_YES :
                return
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Groupes")



# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, IDactivite=1, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
