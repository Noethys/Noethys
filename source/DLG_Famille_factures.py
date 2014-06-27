#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import OL_Factures 
import GestionDB 
import wx.lib.agw.hyperlink as Hyperlink
import UTILS_Utilisateurs


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        
        if self.parent.GetGrandParent().GetName() == "notebook" :
            self.SetBackgroundColour(self.parent.GetGrandParent().GetThemeBackgroundColour())

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
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_factures_email", "modifier") == False : 
            self.UpdateLink()
            return
        self.parent.OnClic()
        self.UpdateLink()
        

class CTRL_Email(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)        
        self.IDfamille = IDfamille

        self.image_valide = wx.Bitmap(u"Images/16x16/Ok4.png", wx.BITMAP_TYPE_ANY)
        self.image_nonvalide = wx.Bitmap(u"Images/16x16/Interdit2.png", wx.BITMAP_TYPE_ANY)

        self.ctrl_image = wx.StaticBitmap(self, -1, self.image_nonvalide)
        self.hyper_prelevement = Hyperlien(self, label=u"Envoi des factures par Email", infobulle=u"Cliquez ici pour activer l'envoi des factures par Email", URL="email")

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_image, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.hyper_prelevement, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
                
    def OnClic(self):
        import DLG_Selection_email
        intro = u"Sélectionnez ici l'adresse Email à laquelle envoyer les factures."
        titre = u"Activation de l'envoi des factures par Email"
        dlg = DLG_Selection_email.Dialog(self, IDfamille=self.IDfamille, champ="email_factures", intro=intro, titre=titre)
        dlg.ShowModal() 
        dlg.Destroy()
        self.MAJ() 
        
    def MAJ(self):
        DB = GestionDB.DB()
        req = """SELECT IDfamille, email_factures
        FROM familles 
        WHERE IDfamille=%d;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        temp, email_factures = listeDonnees[0]
        if email_factures == None :
            self.ctrl_image.SetBitmap(self.image_nonvalide)
        else :
            self.ctrl_image.SetBitmap(self.image_valide)
        




class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_factures", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.staticbox_factures = wx.StaticBox(self, -1, u"Factures")
        
        # Recherche du IDcompte_payeur
        DB = GestionDB.DB()
        req = """SELECT IDcompte_payeur
        FROM familles
        WHERE IDfamille=%d
        """ % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.IDcompte_payeur = listeDonnees[0][0]
        
        # OL Factures
        codesColonnes = ["IDfacture", "date", "numero", "date_debut", "date_fin", "total", "solde", "solde_actuel", "date_echeance", "nom_lot"]
        checkColonne = True
        triColonne = "date"
        self.ctrl_listview = OL_Factures.ListView(self, id=-1, name="OL_factures", IDcompte_payeur=self.IDcompte_payeur, codesColonnes=codesColonnes, checkColonne=checkColonne, triColonne=triColonne, 
                                                                    style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_recherche = OL_Factures.BarreRecherche(self)
        
        # Commandes boutons
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_email = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_ANY))
        
        # Prélèvement
        self.ctrl_email = CTRL_Email(self, IDfamille)

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        
        # Propriétés
        self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer une facture pour cette famille")
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer la facture sélectionnée")
        self.bouton_imprimer.SetToolTipString(u"Cliquez ici pour rééditer la facture sélectionnée (PDF)")
        self.bouton_email.SetToolTipString(u"Cliquez ici pour envoyer la facture sélectionnée par Email")

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        staticbox_factures = wx.StaticBoxSizer(self.staticbox_factures, wx.VERTICAL)
        grid_sizer_factures = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_factures.Add(self.ctrl_listview, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, wx.ALL, 0)
        grid_sizer_boutons.Add( (5, 5), 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, wx.ALL, 0)
        grid_sizer_factures.Add(grid_sizer_boutons, 1, wx.ALL, 0)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.ctrl_email, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add( (70, 5), 0, wx.ALL, 0)
        grid_sizer_options.Add(self.ctrl_recherche, 0, wx.EXPAND|wx.ALL, 0)
        grid_sizer_options.AddGrowableCol(2)
        
        grid_sizer_factures.Add(grid_sizer_options, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        
        grid_sizer_factures.AddGrowableCol(0)
        grid_sizer_factures.AddGrowableRow(0)
        staticbox_factures.Add(grid_sizer_factures, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_base.Add(staticbox_factures, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
    
    def OnBoutonAjouter(self, event):
        """ Créer une facture """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_factures", "creer") == False : return
        
        import DLG_Verification_ventilation
        tracks = DLG_Verification_ventilation.Verification(self.IDcompte_payeur)
        if len(tracks) > 0 :
            dlg = wx.MessageDialog(self, u"Un ou plusieurs règlements peuvent être ventilés.\n\nSouhaitez-vous le faire maintenant (conseillé) ?", u"Ventilation", wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_YES :
                dlg = DLG_Verification_ventilation.Dialog(self, tracks=tracks, IDcompte_payeur=self.IDcompte_payeur) #, tracks=tracks)
                dlg.ShowModal() 
                dlg.Destroy()
            if reponse == wx.ID_CANCEL :
                return False

        import DLG_Factures_generation
        dlg = DLG_Factures_generation.Dialog(self)
        dlg.SetFamille(self.IDfamille)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_listview.MAJ() 

    def OnBoutonSupprimer(self, event):
        self.ctrl_listview.Supprimer(None)

    def OnBoutonImprimer(self, event):
        if len(self.ctrl_listview.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.ctrl_listview.Selection()[0].IDfacture
                
        # Création du menu contextuel
        menuPop = wx.Menu()
    
        # Item Rééditer facture
        item = wx.MenuItem(menuPop, 10, u"Aperçu PDF de la facture")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ImpressionFacture, id=10)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 20, u"Aperçu avant impression de la liste")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=20)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 30, u"Imprimer la liste")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def ImpressionFacture(self, event):
        self.ctrl_listview.Reedition(None)

    def OnBoutonEmail(self, event):
        self.ctrl_listview.EnvoyerEmail(None)

    def Apercu(self, event):
        self.ctrl_listview.Apercu(None)

    def Imprimer(self, event):
        self.ctrl_listview.Imprimer(None)

    def IsLectureAutorisee(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_factures", "consulter", afficheMessage=False) == False : 
            return False
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.ctrl_listview.MAJ() 
        self.ctrl_listview.DefileDernier() 
        self.ctrl_email.MAJ() 
        self.Refresh()
                
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        pass
        
        


class MyFrame(wx.Frame):  
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDfamille=7)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, u"TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()