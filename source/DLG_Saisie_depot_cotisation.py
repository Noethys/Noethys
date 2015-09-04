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
import wx.html as html

import CTRL_Saisie_date
import OL_Cotisations_depots
import DLG_Saisie_depot_cotisation_ajouter
import UTILS_Titulaires

import GestionDB

try: import psyco; psyco.full()
except: pass


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))



class CTRL_Infos(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=32,  couleurFond=(255, 255, 255), style=0):
        html.HtmlWindow.__init__(self, parent, -1, style=style)#, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(3)
        self.SetMinSize((-1, hauteur))
        self.couleurFond = couleurFond
        font = self.parent.GetFont()
        self.SetFont(font)
        self.SetLabel(texte)
    
    def SetLabel(self, texte=""):
        self.SetPage(u"""<BODY><FONT SIZE=2 COLOR='#000000'>%s</FONT></BODY>""" % texte)
        self.SetBackgroundColour(self.couleurFond)
    

# ---------------------------------------------------------------------------------------------------------------------------------------



class Track(object):
    def __init__(self, parent, donnees):
        self.IDcotisation = donnees[0]
        self.IDfamille = donnees[1]
        self.IDindividu = donnees[2]
        self.IDtype_cotisation = donnees[3]
        self.IDunite_cotisation = donnees[4]
        self.date_saisie = DateEngEnDateDD(donnees[5])
        self.IDutilisateur = donnees[6]
        self.date_creation_carte = donnees[7]
        self.numero = donnees[8]
        self.IDdepot_cotisation = donnees[9]
        self.date_debut = DateEngEnDateDD(donnees[10])
        self.date_fin = DateEngEnDateDD(donnees[11])
        self.IDprestation = donnees[12]
        self.nomTypeCotisation = donnees[13]
        self.typeTypeCotisation = donnees[14]
        self.typeHasCarte = donnees[15]
        self.nomUniteCotisation = donnees[16]
        
        self.nomCotisation = u"%s - %s" % (self.nomTypeCotisation, self.nomUniteCotisation)
        
        if parent.titulaires.has_key(self.IDfamille) :
            self.nomTitulaires = parent.titulaires[self.IDfamille]["titulairesSansCivilite"]
        else:
            self.nomTitulaires = u""
            
        # Type
        if self.typeTypeCotisation == "famille" :
            self.typeStr = _(u"Cotisation familiale")
        else:
            self.typeStr = _(u"Cotisation individuelle")
        
        # Validit�
        dateDuJour = datetime.date.today() 
        if dateDuJour >= self.date_debut and dateDuJour <= self.date_fin :
            self.valide = True
        else:
            self.valide = False
        
        # D�p�t
        if self.IDdepot_cotisation == None :
            self.depotStr = _(u"Non d�pos�e")
        else:
            self.depotStr = _(u"D�p�t n�%d") % self.IDdepot_cotisation
        
        # Etat
        if self.IDdepot_cotisation == None or self.IDdepot_cotisation == 0 :
            self.inclus = False
        else:
            self.inclus = True



# ---------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDdepot_cotisation=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_depot_cotisation", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDdepot_cotisation = IDdepot_cotisation
        
        # Param�tres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom du d�p�t :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"", size=(300, -1))
        self.label_date = wx.StaticText(self, -1, _(u"Date du d�p�t :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.label_verrouillage = wx.StaticText(self, -1, _(u"Verrouillage :"))
        self.ctrl_verrouillage = wx.CheckBox(self, -1, u"")
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", size=(300, -1), style=wx.TE_MULTILINE)
        
        # Cotisations
        self.staticbox_cotisations_staticbox = wx.StaticBox(self, -1, _(u"Cotisations"))
        self.ctrl_cotisations = OL_Cotisations_depots.ListView(self, id=-1, inclus=True, selectionPossible=False, name="OL_cotisations_depot", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_infos = CTRL_Infos(self, hauteur=32, couleurFond="#F0FBED" , style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.SUNKEN_BORDER)
        self.bouton_ajouter = CTRL_Bouton_image.CTRL(self, texte=_(u"Ajouter ou retirer des cotisations"), cheminImage="Images/32x32/Cotisation_ajouter.png")
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckVerrouillage, self.ctrl_verrouillage)
        
        # Importation lors d'une modification
        if self.IDdepot_cotisation != None :
            self.SetTitle(_(u"Modification d'un d�p�t de cotisations"))
            self.Importation() 
            self.OnCheckVerrouillage(None)
        else:
            self.SetTitle(_(u"Saisie d'un d�p�t de cotisations"))
            self.ctrl_date.SetDate(datetime.date.today())
        
        # Importation des r�glements
        self.tracks = self.GetTracks()
        self.ctrl_cotisations.MAJ(tracks=self.tracks, labelParametres=self.GetLabelParametres()) 
        self.MAJinfos() 


    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici un nom"))
        self.ctrl_date.SetToolTipString(_(u"Saisissez la date de d�p�t"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste des cotisations du d�p�t"))
        self.ctrl_verrouillage.SetToolTipString(_(u"Cochez cette case si le d�p�t doit �tre verrouill�. Dans ce cas, il devient impossible de modifier la liste des cotisations qui le contient !"))
        self.ctrl_observations.SetToolTipString(_(u"[Optionnel] Saisissez des commentaires"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter ou retirer des cotisations de ce d�p�t"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((890, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        staticbox_reglements = wx.StaticBoxSizer(self.staticbox_cotisations_staticbox, wx.VERTICAL)
        grid_sizer_reglements = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_bas_reglements = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=100)
        grid_sizer_haut_droit = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_haut_gauche = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_haut_gauche.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut_gauche.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_haut_gauche.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_haut_2 = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_haut_2.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_haut_2.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_haut_2.Add(self.label_verrouillage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut_2.Add(self.ctrl_verrouillage, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut_2.AddGrowableCol(1)
        grid_sizer_haut_gauche.Add(grid_sizer_haut_2, 0, wx.EXPAND, 0)
        
        grid_sizer_haut_gauche.AddGrowableCol(1)
        grid_sizer_parametres.Add(grid_sizer_haut_gauche, 1, wx.EXPAND, 0)
        grid_sizer_haut_droit.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut_droit.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_haut_droit.AddGrowableRow(0)
        grid_sizer_haut_droit.AddGrowableCol(1)
        grid_sizer_parametres.Add(grid_sizer_haut_droit, 1, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableCol(0)
        grid_sizer_parametres.AddGrowableCol(1)
        staticbox_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_parametres, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_reglements.Add(self.ctrl_cotisations, 1, wx.EXPAND, 0)
        grid_sizer_bas_reglements.Add(self.ctrl_infos, 0, wx.EXPAND, 0)
        grid_sizer_bas_reglements.Add(self.bouton_ajouter, 0, wx.EXPAND, 0)
        grid_sizer_bas_reglements.AddGrowableCol(0)
        grid_sizer_reglements.Add(grid_sizer_bas_reglements, 1, wx.EXPAND, 0)
        grid_sizer_reglements.AddGrowableRow(0)
        grid_sizer_reglements.AddGrowableCol(0)
        staticbox_reglements.Add(grid_sizer_reglements, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_reglements, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        self.titulaires = UTILS_Titulaires.GetTitulaires() 
        if self.IDdepot_cotisation == None : 
            IDdepot_cotisation = 0
        else:
            IDdepot_cotisation = self.IDdepot_cotisation
            
        db = GestionDB.DB()
        req = """
        SELECT 
        cotisations.IDcotisation, 
        cotisations.IDfamille, cotisations.IDindividu, cotisations.IDtype_cotisation, cotisations.IDunite_cotisation,
        cotisations.date_saisie, cotisations.IDutilisateur, cotisations.date_creation_carte, cotisations.numero,
        cotisations.IDdepot_cotisation, cotisations.date_debut, cotisations.date_fin, cotisations.IDprestation, 
        types_cotisations.nom, types_cotisations.type, types_cotisations.carte, 
        unites_cotisations.nom
        FROM cotisations 
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN unites_cotisations ON unites_cotisations.IDunite_cotisation = cotisations.IDunite_cotisation
        WHERE cotisations.IDdepot_cotisation IS NULL OR cotisations.IDdepot_cotisation=%d;
        """ % IDdepot_cotisation
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        
        listeListeView = []
        for item in listeDonnees :
            track = Track(self, item)
            listeListeView.append(track)
        return listeListeView


    def Importation(self):
        """ Importation des donn�es """
        DB = GestionDB.DB()
        req = """SELECT IDdepot_cotisation, date, nom, verrouillage, observations
        FROM depots_cotisations
        WHERE IDdepot_cotisation=%d;""" % self.IDdepot_cotisation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDdepot, date, nom, verrouillage, observations = listeDonnees[0]
        
        # Date
        self.ctrl_date.SetDate(date)
        # Nom
        self.ctrl_nom.SetValue(nom)
        # Verrouillage
        if verrouillage == 1 :
            self.ctrl_verrouillage.SetValue(True)
        # Observations
        if observations != None :
            self.ctrl_observations.SetValue(observations)

    def OnBoutonAjouter(self, event): 
        dlg = DLG_Saisie_depot_cotisation_ajouter.Dialog(self, tracks=self.tracks)      
        if dlg.ShowModal() == wx.ID_OK:
            self.tracks = dlg.GetTracks()
            self.ctrl_cotisations.MAJ(self.tracks, labelParametres=self.GetLabelParametres())
            self.MAJinfos()
        dlg.Destroy() 
        
    def OnCheckVerrouillage(self, event):
        if self.ctrl_verrouillage.GetValue() == True :
            self.bouton_ajouter.Enable(False)
        else:
            self.bouton_ajouter.Enable(True)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Gestiondesdptsdecotisations")

    def OnBoutonOk(self, event): 
        # Sauvegarde des param�tres
        etat = self.Sauvegarde_depot() 
        if etat == False :
            return
        # Sauvegarde des r�glements
        self.Sauvegarde_cotisations()
        # Fermeture
        self.EndModal(wx.ID_OK)
    
    def Sauvegarde_depot(self):
        # Nom
        nom = self.ctrl_nom.GetValue() 
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom. Exemple : 'Cotisations de Juillet 2010'... !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False
        
        # Date
        date = self.ctrl_date.GetDate()
        if date == None :
            dlg = wx.MessageDialog(self, _(u"Etes-vous s�r de ne pas vouloir saisir de date de d�p�t ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse !=  wx.ID_YES :
                return False
        
        # Verrouillage
        verrouillage = self.ctrl_verrouillage.GetValue()
        if verrouillage == True :
            verrouillage = 1
        else:
            verrouillage = 0
                
        # Observations
        observations = self.ctrl_observations.GetValue()
        
        DB = GestionDB.DB()
        listeDonnees = [    
                ("nom", nom),
                ("date", date),
                ("verrouillage", verrouillage),
                ("observations", observations),
            ]
        if self.IDdepot_cotisation == None :
            self.IDdepot_cotisation = DB.ReqInsert("depots_cotisations", listeDonnees)
        else:
            DB.ReqMAJ("depots_cotisations", listeDonnees, "IDdepot_cotisation", self.IDdepot_cotisation)
        DB.Close()
        
        return True
        
    def Sauvegarde_cotisations(self):
        DB = GestionDB.DB()
        for track in self.tracks :
            # Ajout
            if track.IDdepot_cotisation == None and track.inclus == True :
                DB.ReqMAJ("cotisations", [("IDdepot_cotisation", self.IDdepot_cotisation),], "IDcotisation", track.IDcotisation)
            # Retrait
            if track.IDdepot_cotisation != None and track.inclus == False :
                DB.ReqMAJ("cotisations", [("IDdepot_cotisation", None),], "IDcotisation", track.IDcotisation)
        DB.Close() 

    def GetIDdepotCotisation(self):
        return self.IDdepot_cotisation
    
    def MAJinfos(self):
        """ Cr�� le texte infos avec les stats du d�p�t """
        # R�cup�ration des chiffres
        nbreTotal = 0
        for track in self.tracks :
            if track.inclus == True :
                nbreTotal += 1
        if nbreTotal == 0 : 
            texte = _(u"Aucune cotisation")
        elif nbreTotal == 1 : 
            texte = _(u"1 cotisation")
        else:
            texte = _(u"%d cotisations") % nbreTotal
        self.ctrl_infos.SetLabel(texte)
    
    def OnBoutonImprimer(self, event):               
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()
        
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 20, _(u"Aper�u avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=20)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 30, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        self.ctrl_cotisations.labelParametres = self.GetLabelParametres()
        self.ctrl_cotisations.Apercu(None)

    def Imprimer(self, event):
        self.ctrl_cotisations.labelParametres = self.GetLabelParametres()
        self.ctrl_cotisations.Imprimer(None)
    
    def GetLabelParametres(self):
        listeParametres = []

        nom = self.ctrl_nom.GetValue()
        listeParametres.append(_(u"Nom du d�p�t : %s") % nom)
        
        date = self.ctrl_date.GetDate() 
        if date == None : 
            date = _(u"Non sp�cifi�e")
        else :
            date = DateEngFr(str(date))
        listeParametres.append(_(u"Date : %s") % date)
        
        if self.ctrl_verrouillage.GetValue() == True :
            listeParametres.append(_(u"D�p�t verrouill�"))
        else :
            listeParametres.append(_(u"D�p�t d�verrouill�"))
        
        labelParametres = " | ".join(listeParametres)
        return labelParametres


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDdepot_cotisation=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
