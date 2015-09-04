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
import wx.html as html
import GestionDB

import OL_Vaccins_obligatoires
import OL_Vaccins
import OL_Pb_sante

import UTILS_Utilisateurs


class CTRL_Medecin(html.HtmlWindow):
    def __init__(self, parent, IDindividu=None, hauteur=39):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.SUNKEN_BORDER|wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.IDindividu = IDindividu
        self.IDmedecin = None
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetToolTipString(_(u"Cliquez sur le bouton Modifier pour s�lectionner un m�decin"))
##        couleurFond = wx.SystemSettings.GetColour(30)
##        self.SetBackgroundColour("#F0FBED" )
    
        
    def SetIDmedecin(self, IDmedecin=None):
        """ Recherche dans la base le m�decin de l'individu donn� """
        if self.IDindividu == None : return
        db = GestionDB.DB()
        if IDmedecin == None :
            # Recherche dans la base le m�decin de l'individu
            req = """SELECT IDmedecin FROM individus WHERE IDindividu=%d; """ % self.IDindividu
            db.ExecuterReq(req)
            listeIndividus = db.ResultatReq()
            if len(listeIndividus) > 0 :
                self.IDmedecin = listeIndividus[0][0]
                if self.IDmedecin != None :
                    req = """SELECT IDmedecin, nom, prenom, rue_resid, cp_resid, ville_resid, tel_cabinet, tel_mobile
                    FROM medecins WHERE IDmedecin=%d; """ % self.IDmedecin
                    db.ExecuterReq(req)
                    listeMedecins = db.ResultatReq()
                else:
                    listeMedecins = []
            else:
                listeMedecins = []
                
        else:
            # Attribue un m�decin � l'individu
            req = """SELECT IDmedecin, nom, prenom, rue_resid, cp_resid, ville_resid, tel_cabinet, tel_mobile
            FROM medecins WHERE IDmedecin=%d; """ % IDmedecin
            db.ExecuterReq(req)
            listeMedecins = db.ResultatReq()
            if len(listeMedecins) > 0 :
                self.IDmedecin = IDmedecin
                listeDonnees = [("IDmedecin", IDmedecin ) ]
                db.ReqMAJ("individus", listeDonnees, "IDindividu", self.IDindividu)
        
        db.Close()
        # Cr�ation du texte � afficher
        if len(listeMedecins) > 0 :
            nom = listeMedecins[0][1]
            prenom = listeMedecins[0][2]
            rue = listeMedecins[0][3]
            cp = listeMedecins[0][4]
            ville = listeMedecins[0][5]
            tel = listeMedecins[0][6]
            mobile = listeMedecins[0][7]
            if prenom == None : prenom = ""
            if rue == None : rue = ""
            if cp == None : cp = ""
            if ville == None : ville = ""
            if tel == None : tel = ""
            if mobile == None : mobile = ""
            tel = listeMedecins[0][6]
            if tel == None : tel = ""
            texteMedecin = _(u"Dr %s %s<BR>%s") % (nom, prenom, tel)
            txtToolTip = _(u"Dr %s %s\n\n%s\n%s %s\n\nT�l. Cabinet : %s\nT�l. Mobile : %s") % (nom, prenom, rue, cp, ville, tel, mobile)
            self.SetToolTipString(txtToolTip)
        else:
            texteMedecin = None
            self.SetToolTipString(_(u"Cliquez sur le bouton Modifier pour s�lectionner un m�decin"))
        self.SetTexteMedecin(texteMedecin)
    
    def DetacherMedecin(self):
        db = GestionDB.DB()
        listeDonnees = [("IDmedecin", None ) ]
        db.ReqMAJ("individus", listeDonnees, "IDindividu", self.IDindividu)
        self.IDmedecin = None
        db.Close()
        self.SetTexteMedecin(None)
        self.SetToolTipString(_(u"Cliquez sur le bouton Modifier pour s�lectionner un m�decin"))
        
    def SetTexteMedecin(self, texteMedecin=""):
        if texteMedecin == None or texteMedecin == "" :
            # Si pas de m�decin
            texte = u"""<CENTER><IMG SRC="Images/Special/Medecin_gris.png"></CENTER>"""
        else:
            # Si m�decin s�lectionn�
            texte = u"""
            <CENTER>
            <IMG SRC="Images/48x48/Medecin-avecbords.png"><BR>
            <FONT SIZE=-2>
            %s
            </FONT> 
            </CENTER>
            """ % texteMedecin
        self.SetPage(texte)
    
    def GetIDmedecin(self):
        return self.IDmedecin
        


class Panel(wx.Panel):
    def __init__(self, parent, IDindividu=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_medical", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        
        # Vaccinations
        self.staticbox_vaccinations_staticbox = wx.StaticBox(self, -1, _(u"Vaccinations"))
        self.ctrl_maladies = OL_Vaccins_obligatoires.ListView(self, IDindividu=IDindividu, id=-1, name="OL_maladies", style=wx.LC_NO_HEADER|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_maladies.SetMinSize((150, 20))
        self.ctrl_maladies.SetBackgroundColour("#F0FBED")
        
        self.ctrl_vaccins = OL_Vaccins.ListView(self, IDindividu=IDindividu, id=-1, name="OL_vaccins", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_vaccins.SetMinSize((150, 20))
        self.bouton_ajouter_vaccin = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_vaccin = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_vaccin = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Problemes de sant�
        self.staticbox_problemes_staticbox = wx.StaticBox(self, -1, _(u"Informations m�dicales"))
        self.ctrl_problemes = OL_Pb_sante.ListView(self, IDindividu=IDindividu, id=-1, name="OL_problemes", style=wx.LC_NO_HEADER|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_problemes.SetMinSize((150, 20))
        self.bouton_ajouter_probleme = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_probleme = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_probleme = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
       
        # M�decin traitant
        self.staticbox_medecin_staticbox = wx.StaticBox(self, -1, _(u"M�decin traitant"))
        self.bouton_medecin = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY)) #wx.BitmapButton(self, -1, wx.Bitmap(u"Images/32x32/Medecin.png", wx.BITMAP_TYPE_ANY))
        self.bouton_detacher_medecin = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        self.ctrl_medecin = CTRL_Medecin(self, IDindividu=self.IDindividu)
        self.ctrl_medecin.SetIDmedecin(IDmedecin=None) 
        
        self.__set_properties()
        self.__do_layout()
        
##        # Initialisation des contr�les
##        self.ctrl_maladies.MAJ()
##        self.ctrl_vaccins.MAJ()
##        self.ctrl_problemes.MAJ()
##        self.SetEtatBoutonDetacherMedecin()
        
        self.Bind(wx.EVT_BUTTON, self.Selectionner_medecin, self.bouton_medecin)
        self.Bind(wx.EVT_BUTTON, self.Detacher_medecin, self.bouton_detacher_medecin)
        self.Bind(wx.EVT_BUTTON, self.OnAjouter_vaccin, self.bouton_ajouter_vaccin)
        self.Bind(wx.EVT_BUTTON, self.OnModifier_vaccin, self.bouton_modifier_vaccin)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimer_vaccin, self.bouton_supprimer_vaccin)
        self.Bind(wx.EVT_BUTTON, self.OnAjouter_probleme, self.bouton_ajouter_probleme)
        self.Bind(wx.EVT_BUTTON, self.OnModifier_probleme, self.bouton_modifier_probleme)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimer_probleme, self.bouton_supprimer_probleme)

    def __set_properties(self):
        self.ctrl_maladies.SetToolTipString(_(u"Liste des maladies dont le vaccin est obligatoire"))
        self.bouton_ajouter_vaccin.SetToolTipString(_(u"Cliquez ici pour ajouter un vaccin"))
        self.bouton_modifier_vaccin.SetToolTipString(_(u"Cliquez ici pour modifier le vaccin s�lectionn�"))
        self.bouton_supprimer_vaccin.SetToolTipString(_(u"Cliquez ici pour supprimer le vaccin s�lectionn�"))
        self.bouton_ajouter_probleme.SetToolTipString(_(u"Cliquez ici pour ajouter une information m�dicale"))
        self.bouton_modifier_probleme.SetToolTipString(_(u"Cliquez ici pour modifier l'information m�dicale s�lectionn�e dans la liste"))
        self.bouton_supprimer_probleme.SetToolTipString(_(u"Cliquez ici pour supprimer l'information m�dicale s�lectionn�e dans la liste"))
        self.bouton_medecin.SetToolTipString(_(u"Cliquez ici pour s�lectionner un m�decin traitant"))
        self.bouton_detacher_medecin.SetToolTipString(_(u"Cliquez ici pour d�tacher le m�decin de cette fiche individuelle"))
##        self.ctrl_maladies.SetMinSize((130, -1))
        self.ctrl_medecin.SetMinSize((90, 100))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_problemes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Vaccinations
        staticbox_vaccinations = wx.StaticBoxSizer(self.staticbox_vaccinations_staticbox, wx.VERTICAL)
        grid_sizer_vaccinations = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_com_vaccins = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_vaccinations.Add(self.ctrl_maladies, 1, wx.RIGHT|wx.EXPAND, 5)
        grid_sizer_vaccinations.Add(self.ctrl_vaccins, 1, wx.EXPAND, 0)
        grid_sizer_com_problemes = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_com_vaccins.Add(self.bouton_ajouter_vaccin, 0, 0, 0)
        grid_sizer_com_vaccins.Add(self.bouton_modifier_vaccin, 0, 0, 0)
        grid_sizer_com_vaccins.Add(self.bouton_supprimer_vaccin, 0, 0, 0)
        grid_sizer_vaccinations.Add(grid_sizer_com_vaccins, 1, wx.EXPAND, 0)
        grid_sizer_vaccinations.AddGrowableRow(0)
        grid_sizer_vaccinations.AddGrowableCol(1)
        staticbox_vaccinations.Add(grid_sizer_vaccinations, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_vaccinations, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        
        # Probl�mes
        staticbox_problemes = wx.StaticBoxSizer(self.staticbox_problemes_staticbox, wx.VERTICAL)
        grid_sizer_problemes.Add(self.ctrl_problemes, 1, wx.EXPAND, 0)
        grid_sizer_com_problemes.Add(self.bouton_ajouter_probleme, 0, 0, 0)
        grid_sizer_com_problemes.Add(self.bouton_modifier_probleme, 0, 0, 0)
        grid_sizer_com_problemes.Add(self.bouton_supprimer_probleme, 0, 0, 0)
        grid_sizer_problemes.Add(grid_sizer_com_problemes, 1, wx.EXPAND, 0)
        grid_sizer_problemes.AddGrowableRow(0)
        grid_sizer_problemes.AddGrowableCol(0)
        staticbox_problemes.Add(grid_sizer_problemes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_bas.Add(staticbox_problemes, 1, wx.EXPAND, 0)
        
        # M�decin
        staticbox_medecin = wx.StaticBoxSizer(self.staticbox_medecin_staticbox, wx.VERTICAL)
        grid_sizer_medecin = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_medecin.Add(self.ctrl_medecin, 1, wx.EXPAND, 0)
        grid_sizer_medecin_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_medecin_boutons.Add(self.bouton_medecin, 1, wx.EXPAND, 0)
        grid_sizer_medecin_boutons.Add(self.bouton_detacher_medecin, 1, wx.EXPAND, 0)
        grid_sizer_medecin.Add(grid_sizer_medecin_boutons, 1, wx.EXPAND, 0)
        grid_sizer_medecin.AddGrowableCol(0)
        grid_sizer_medecin.AddGrowableRow(0)
        staticbox_medecin.Add(grid_sizer_medecin, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_bas.Add(staticbox_medecin, 1, wx.EXPAND, 0)
        
        grid_sizer_bas.AddGrowableRow(0)
        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
##        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0) 
    
    def MAJ(self):
        # Initialisation des contr�les
        self.IDindividu = self.GetGrandParent().IDindividu
        if self.IDindividu == None :
            print "Pas de IDindividu"
            return
        self.ctrl_maladies.MAJ()
        self.ctrl_vaccins.MAJ()
        self.ctrl_problemes.MAJ()
        self.SetEtatBoutonDetacherMedecin()
        
    def SetEtatBoutonDetacherMedecin(self):
        if self.ctrl_medecin.GetIDmedecin() == None :
            self.bouton_detacher_medecin.Enable(False)
        else:
            self.bouton_detacher_medecin.Enable(True)
        
    def Selectionner_medecin(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_medecin", "modifier") == False : return
        import DLG_Medecins
        dlg = DLG_Medecins.Dialog(self, mode="selection")
        etat = dlg.ShowModal() 
        if etat == wx.ID_OK :
            IDmedecin = dlg.GetIDmedecin()
            self.ctrl_medecin.SetIDmedecin(IDmedecin=IDmedecin)
        if etat == wx.ID_CANCEL :
            self.ctrl_medecin.SetIDmedecin()
        dlg.Destroy()
        self.SetEtatBoutonDetacherMedecin()
    
    def Detacher_medecin(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_medecin", "modifier") == False : return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment d�tacher ce m�decin ?"), _(u"D�tacher un m�decin"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.ctrl_medecin.DetacherMedecin() 
        dlg.Destroy()
        self.SetEtatBoutonDetacherMedecin()
        
    def OnAjouter_vaccin(self, event):
        self.ctrl_vaccins.Ajouter(None)

    def OnModifier_vaccin(self, event):
        self.ctrl_vaccins.Modifier(None)

    def OnSupprimer_vaccin(self, event):
        self.ctrl_vaccins.Supprimer(None)

    def OnAjouter_probleme(self, event):
        self.ctrl_problemes.Ajouter(None)

    def OnModifier_probleme(self, event):
        self.ctrl_problemes.Modifier(None)

    def OnSupprimer_probleme(self, event):
        self.ctrl_problemes.Supprimer(None)


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDindividu=27)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()