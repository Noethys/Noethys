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
import sys
import datetime

import wx.lib.agw.labelbook as LB
import wx.lib.agw.flatnotebook as FNB
import wx.lib.agw.hyperlink as Hyperlink
import wx.lib.agw.pybusyinfo as PBI

import wx.html as  html
import wx.lib.wxpTag 

##for item in sorted(sys.modules.keys()):
##    if "STATS" in item :
##        print 'delete ' + str(sys.modules[item])
##        del(sys.modules[item])


import CTRL_Bandeau
import CTRL_Stats_objets
import DLG_Stats_parametres

import UTILS_Stats_modeles as MODELES
import UTILS_Stats_individus as INDIVIDUS
import UTILS_Stats_familles as FAMILLES



def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", ID=None, size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.ID = ID
        self.URL = URL
        
        # Construit l'hyperlink
        self.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
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
        if self.URL == "selectionner" : self.parent.Coche(True)
        if self.URL == "deselectionner" : self.parent.Coche(False)
        if self.URL == "parametres" : self.parent.ModificationParametres()
        self.UpdateLink()
        


class HtmlPrintout(wx.html.HtmlPrintout):
    def __init__(self, html=""):
        wx.html.HtmlPrintout.__init__(self)
        self.SetHtmlText(html)
        self.SetMargins(10, 10, 10, 10, spaces=0)


class CTRL_Parametres(wx.html.HtmlWindow):
    def __init__(self, parent):
        wx.html.HtmlWindow.__init__(self, parent, id=-1, style=wx.SUNKEN_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetMinSize((-1, 120))
        self.periode = None
        self.dictParametres = {}
    
    def SetParametres(self, dictParametres={}):
        self.dictParametres = dictParametres

    def MAJ(self):
        """ Cr�ation de la source HTML """
        html = ""
        
        if self.dictParametres.has_key("mode") == False or len(self.dictParametres["listeActivites"]) == 0 :
            return
        
        # P�riode
        if self.dictParametres["mode"] == "inscrits" :
            html += _(u"<U><B>P�riode :</B></U> Aucune")
        else:
            html += _(u"<U><B>P�riode :</B></U> %s") % self.dictParametres["periode"]["label"]
        html += u"<BR><BR>"
        
        # Activit�s
        listeActivites = self.dictParametres["listeActivites"]
        if len(listeActivites) == 0 :
            html += _(u"<U><B>Activit�s :</B></U> Aucune")
        else :
            html += _(u"<U><B>Activit�s : </B></U><UL>")
            for IDactivite in listeActivites :
                nomActivite = self.dictParametres["dictActivites"][IDactivite]
                html += u"<LI>%s</LI>" % nomActivite
            html += u"</UL>"

        # Options
        
        
        
        # Finalisation du html
        html = _(u"<html><head><title>Param�tres</title></head><body><FONT SIZE=-1>%s</FONT></body></html>") % html
        self.SetPage(html)



class MyHtml(html.HtmlWindow):
    def __init__(self, parent):
        html.HtmlWindow.__init__(self, parent, id=-1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, linkinfo):
        code = linkinfo.GetHref()
        figure = self.parent.GetGrandParent().baseHTML.GetFigure(code)
        import DLG_Zoom_graphe
        dlg = DLG_Zoom_graphe.Dialog(self, figure=figure)
        dlg.ShowModal() 
        dlg.Destroy()
        


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Stats", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.couleurFond = wx.SystemSettings.GetColour(30)

        self.dictParametres = {}

####Liste d'objets ici
        self.listeObjets = [

            {"nom" : _(u"Individus"), "code" : "individus", "image" : None, "ctrl_notebook" : None, "visible" : True, "pages" : [
            
                    {"nom" : _(u"Nombre"), "code" : "individus_nombre", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Texte_nombre_individus(),
                            INDIVIDUS.Tableau_nombre_individus(),
                            INDIVIDUS.Graphe_nombre_individus(),
                            ]},

                    {"nom" : _(u"Anciennet�"), "code" : "individus_anciennete", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_nouveaux_individus(),
                            INDIVIDUS.Graphe_nouveaux_individus(),
                            INDIVIDUS.Graphe_arrivee_individus(),
                            ]},

                    {"nom" : _(u"Genre"), "code" : "individus_genre", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_repartition_genre(),
                            INDIVIDUS.Graphe_repartition_genre(),
                            ]},

                    {"nom" : _(u"�ge"), "code" : "individus_age", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_repartition_ages(),
                            INDIVIDUS.Graphe_repartition_ages(),
                            INDIVIDUS.Tableau_repartition_annees_naiss(),
                            INDIVIDUS.Graphe_repartition_annees_naiss(),
                            ]},

                    {"nom" : _(u"Coordonn�es"), "code" : "individus_coordonnees", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_repartition_villes(),
                            INDIVIDUS.Graphe_repartition_villes(),
                            ]},

                    {"nom" : _(u"Scolarit�"), "code" : "individus_scolarite", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_repartition_ecoles(),
                            INDIVIDUS.Graphe_repartition_ecoles(),
                            INDIVIDUS.Tableau_repartition_niveaux_scolaires(),
                            INDIVIDUS.Graphe_repartition_niveaux_scolaires(),
                            ]},

                    {"nom" : _(u"Profession"), "code" : "individus_profession", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_activites_professionnelles(),
                            INDIVIDUS.Graphe_activites_professionnelles(),
                            ]},

                    ]},

            {"nom" : _(u"Familles"), "code" : "familles", "image" : None, "ctrl_notebook" : None, "visible" : True, "pages" : [

                    {"nom" : _(u"Nombre"), "code" : "familles_nombre", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            FAMILLES.Texte_nombre_familles(),
                            FAMILLES.Tableau_nombre_familles(),
                            FAMILLES.Graphe_nombre_familles(),
                            ]},

                    {"nom" : _(u"Caisse"), "code" : "familles_caisse", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            FAMILLES.Tableau_repartition_caisses(),
                            FAMILLES.Graphe_repartition_caisses(),
                            ]},

                    {"nom" : _(u"Composition"), "code" : "familles_composition", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            FAMILLES.Tableau_nombre_membres(),
                            FAMILLES.Graphe_nombre_membres(),
                            ]},

                    {"nom" : _(u"Quotient familial"), "code" : "familles_qf", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            FAMILLES.Tableau_qf_tarifs(),
                            FAMILLES.Graphe_qf_tarifs(),
                            FAMILLES.Tableau_qf_defaut(),
                            FAMILLES.Graphe_qf_defaut(),
                            ]},

                    ]},

            ]


        # Bandeau
        intro = _(u"Vous pouvez ici consulter des statistiques compl�tes sur les activit�s et la p�riode de votre choix. Ces informations sont pr�sent�es sous forme de rubrique, de pages et d'items que vous pouvez choisir d'afficher ou non. Vous pouvez ensuite imprimer ces informations sous forme de rapport hierarchis�. Cliquez sur les graphes pour acc�der aux outils sp�cifiques.")
        titre = _(u"Statistiques")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Barres.png")
        
        # Labelbook
        self.box_informations_staticbox = wx.StaticBox(self, -1, _(u"Informations"))
        self.ctrl_labelbook = LB.LabelBook(self, -1, agwStyle=LB.INB_DRAW_SHADOW | LB.INB_LEFT)

        self.baseHTML = MODELES.HTML(liste_objets=self.listeObjets) 
        self.InitLabelbook() 
        self.ctrl_labelbook.SetSelection(0) 

        # Param�tres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.ctrl_parametres = CTRL_Parametres(self)
        self.ctrl_parametres.MAJ() 
        self.hyper_parametres = Hyperlien(self, label=_(u"Modifier les param�tres"), infobulle=_(u"Modifier les param�tres"), URL="parametres")

        # impression
        self.box_impression_staticbox = wx.StaticBox(self, -1, _(u"Impression"))
        self.ctrl_impression = CTRL_Stats_objets.CTRL_Objets(self, liste_objets=self.listeObjets)
        self.ctrl_impression.MAJ() 
        
        self.hyper_selectionner = Hyperlien(self, label=_(u"Tout s�lectionner"), infobulle=_(u"Tout s�lectionner"), URL="selectionner")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_deselectionner = Hyperlien(self, label=_(u"Tout d�-s�lectionner"), infobulle=_(u"Tout d�-s�lectionner"), URL="deselectionner")
        
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), cheminImage="Images/32x32/Imprimante.png")
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(LB.EVT_IMAGENOTEBOOK_PAGE_CHANGED, self.OnChangeLabelbook, self.ctrl_labelbook)
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
                

    def __set_properties(self):
        self.ctrl_impression.SetMinSize((250, -1))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((950, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Labelbook
        box_informations = wx.StaticBoxSizer(self.box_informations_staticbox, wx.VERTICAL)
        box_informations.Add(self.ctrl_labelbook, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(box_informations, 0, wx.EXPAND, 0)
        
        grid_sizer_droite = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Param�tres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=2, cols=1, vgap=2, hgap=2)
        grid_sizer_parametres.Add(self.ctrl_parametres, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.hyper_parametres, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droite.Add(box_parametres, 1, wx.EXPAND, 0)
        
        # Impression
        box_impression = wx.StaticBoxSizer(self.box_impression_staticbox, wx.VERTICAL)
        grid_sizer_impression = wx.FlexGridSizer(rows=3, cols=1, vgap=2, hgap=2)
        grid_sizer_impression.Add(self.ctrl_impression, 0, wx.EXPAND, 0)
        
        grid_sizer_hyperliens = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_hyperliens.Add( (2, 2), 0, 0, 0)
        grid_sizer_hyperliens.Add(self.hyper_selectionner, 0, 0, 0)
        grid_sizer_hyperliens.Add(self.label_separation, 0, 0, 0)
        grid_sizer_hyperliens.Add(self.hyper_deselectionner, 0, 0, 0)
        grid_sizer_hyperliens.AddGrowableCol(0)
        grid_sizer_impression.Add(grid_sizer_hyperliens, 0, wx.EXPAND, 0)
        
        grid_sizer_impression.Add(self.bouton_imprimer, 0, wx.EXPAND|wx.TOP, 5)
        grid_sizer_impression.AddGrowableRow(0)
        grid_sizer_impression.AddGrowableCol(0)
        box_impression.Add(grid_sizer_impression, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droite.Add(box_impression, 1, wx.EXPAND, 0)
        
        grid_sizer_droite.AddGrowableRow(1)
        grid_sizer_droite.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droite, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Statistiques")

    def OnBoutonImprimer(self, event): 
        # Demande le type d'impression
        menuPop = wx.Menu()

        item = wx.MenuItem(menuPop, 10, _(u"Tout"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=10)
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 20, _(u"La rubrique affich�e"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=20)

        item = wx.MenuItem(menuPop, 30, _(u"La page affich�e"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=30)
            
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Imprimer(self, event=None):
        ID = event.GetId() 
        listeCodes = self.ctrl_impression.GetCoches() 
        
        # Imprimer tout
        dlgAttente = PBI.PyBusyInfo(_(u"Cr�ation du rapport..."), parent=None, title=_(u"Patientez"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        if ID == 10 : 
            html = self.baseHTML.GetHTML(mode="impression", selectionsCodes=listeCodes)
        # Imprimer la rubrique affich�e
        if ID == 20 : 
            indexRubrique = self.ctrl_labelbook.GetSelection()
            codeRubrique = self.RechercherElement(indexRubrique=indexRubrique)[0]
            html = self.baseHTML.GetHTML(mode="impression", rubrique=codeRubrique, selectionsCodes=listeCodes)
        # Imprimer la page affich�e
        if ID == 30 : 
            codeRubrique, codePage = self.RecherchePageAffichee() 
            html = self.baseHTML.GetHTML(mode="impression", rubrique=codeRubrique, page=codePage, selectionsCodes=listeCodes)
        
        if len(listeCodes) == 0 or len(html) <= 50 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune information � imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        del dlgAttente
        
        # Impression
        printout = HtmlPrintout(html)
        printout2 = HtmlPrintout(html)
        preview = wx.PrintPreview(printout, printout2)
        
##        import UTILS_Printer
##        preview_window = UTILS_Printer.PreviewFrame(preview, None, _(u"Aper�u avant impression"))
##        preview_window.Initialize()
##        preview_window.MakeModal(False)
##        preview_window.Show(True)

        preview.SetZoom(100)
        frame = wx.GetApp().GetTopWindow() 
        preview_window = wx.PreviewFrame(preview, None, _(u"Aper�u avant impression"))
        preview_window.Initialize()
        preview_window.MakeModal(False)
        preview_window.SetPosition(frame.GetPosition())
        preview_window.SetSize(frame.GetSize())
        preview_window.Show(True)


    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def InitLabelbook(self):
        self.ctrl_labelbook.SetColour(LB.INB_TAB_AREA_BACKGROUND_COLOUR, self.couleurFond)
        self.ctrl_labelbook.SetColour(LB.INB_ACTIVE_TAB_COLOUR, (255, 255, 255) )

        # Cr�ation de l'ImageList
        self.dictImages = {
            "individus" : {"img" : wx.Bitmap('Images/16x16/Personnes.png', wx.BITMAP_TYPE_PNG), "index" : None},
            "familles" : {"img" : wx.Bitmap('Images/16x16/Famille.png', wx.BITMAP_TYPE_PNG), "index" : None},
            }
        
        il = wx.ImageList(16, 16)
        index =0
        for code, dictImage in self.dictImages.iteritems() :
            il.Add(dictImage["img"])
            dictImage["index"] = index
            index += 1
        self.ctrl_labelbook.AssignImageList(il)

        self.listeContenu = []
        indexRubrique = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique["visible"] == True :
                self.AjouterRubrique(dictRubrique["code"])
                indexRubrique += 1
    
    def AjouterRubrique(self, code=""):
        # Recherche du dictRubrique
        indexRubrique = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique["visible"] == True :
                if dictRubrique["code"] == code :
                    dictRubrique["visible"] = True
                    break
                indexRubrique += 1

        # Cr�ation du notebook
        flatNoteBook = FNB.FlatNotebook(self.ctrl_labelbook, -1, agwStyle=FNB.FNB_BOTTOM 
                                                                                                            | FNB.FNB_NO_TAB_FOCUS
                                                                                                            | FNB.FNB_NO_X_BUTTON
                                                                                                            )
        flatNoteBook.SetTabAreaColour(self.couleurFond)
        
        # M�morise le ctrl flatNoteBook
        self.listeObjets[indexRubrique]["ctrl_notebook"] = flatNoteBook
        
        # Cr�ation des pages
        listePages = []
        indexPage = 0
        for dictPage in dictRubrique["pages"] :
            if dictPage["visible"] == True :
                
                ctrl_html = MyHtml(flatNoteBook)
                flatNoteBook.AddPage(ctrl_html, dictPage["nom"])
                self.listeObjets[indexRubrique]["pages"][indexPage]["ctrl_html"] = ctrl_html
                listePages.append(dictPage["code"])
                indexPage += 1
        
        # Ajoute le notebook au labelbook
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnChangeNotebook, flatNoteBook)
        if self.dictImages.has_key(dictRubrique["code"]):
            indexImage = self.dictImages[dictRubrique["code"]]["index"]
        else:
            indexImage = -1
        self.ctrl_labelbook.AddPage(flatNoteBook, dictRubrique["nom"], imageId=indexImage)
##        self.ctrl_labelbook.InsertPage(indexRubrique, flatNoteBook, dictRubrique["nom"], imageId=-1)
        
        self.listeContenu.append((dictRubrique["code"], listePages))
    
##    def SupprimerRubrique(self, code=""):
##        global self.listeObjets
##        indexRubrique = 0
##        for dictRubrique in self.listeObjets :
##            if dictRubrique["visible"] == True :
##                if dictRubrique["code"] == code :
##                    # Suppression du notebook
##                    del dictRubrique["ctrl_notebook"]
##                    dictRubrique["ctrl_notebook"] = None
##                    dictRubrique["visible"] = False
##                    for page in dictRubrique["pages"] :
##                        page["ctrl_html"] = None
##                    # Suppression de la page du labelbook
##                    self.ctrl_labelbook.DeletePage(indexRubrique)
##                indexRubrique += 1
##        print self.listeObjets

    def MAJpageAffichee(self):
        indexRubrique = self.ctrl_labelbook.GetSelection()
        # Recherche la page � MAJ
        indexR = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique["visible"] == True :
                if indexR == indexRubrique :
                    ctrl_notebook = dictRubrique["ctrl_notebook"]
                    indexPage = ctrl_notebook.GetSelection() 
                    self.MAJpage(indexRubrique, indexPage)
                indexR += 1

    def MAJpage(self, indexRubrique=None, indexPage=None):
        """ Met � jour le contenu d'une page """
        dlgAttente = PBI.PyBusyInfo(_(u"Actualisation des donn�es..."), parent=None, title=_(u"Patientez"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        codeRubrique = None
        codePage = None
        indexR = 0
        # Recherche de la rubrique
        for dictRubrique in self.listeObjets :
            if dictRubrique["visible"] == True :
                if indexR == indexRubrique :
                    codeRubrique = dictRubrique["code"]
                    ctrl_notebook = dictRubrique["ctrl_notebook"]
                    # Recherche de la page
                    indexP = 0
                    for dictPage in dictRubrique["pages"] :
                        if dictPage["visible"] == True :
                            if indexP == indexPage :
                                codePage = dictPage["code"]
                                ctrl_html = dictPage["ctrl_html"]
                            indexP += 1
                indexR += 1
        
        if codeRubrique == None or codePage == None :
            return None
        
        # MAJ du contr�les HTML
        self.baseHTML.MAJ(page=codePage)
        pageHTML = self.baseHTML.GetHTML(page=codePage) 
        ctrl_html.SetPage(pageHTML)
        
        del dlgAttente
    
    def RechercherElement(self, indexRubrique=None, indexPage=None):
        """ retourne le codeRubrique et codePage par rapport aux index """
        codeRubrique = None
        codePage = None
        indexR = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique["visible"] == True :
                if indexR == indexRubrique or indexRubrique == None :
                    codeRubrique = dictRubrique["code"]
                    ctrl_notebook = dictRubrique["ctrl_notebook"]
                    # Recherche de la page
                    indexP = 0
                    for dictPage in dictRubrique["pages"] :
                        if dictPage["visible"] == True :
                            if indexP == indexPage :
                                codePage = dictPage["code"]
                                ctrl_html = dictPage["ctrl_html"]
                            indexP += 1
                indexR += 1
        return codeRubrique, codePage
    
    def RecherchePageAffichee(self):
        indexRubrique = self.ctrl_labelbook.GetSelection()
        codeRubrique = None
        codePage = None
        # Recherche la page � MAJ
        indexR = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique["visible"] == True :
                if indexR == indexRubrique :
                    ctrl_notebook = dictRubrique["ctrl_notebook"]
                    indexPage = ctrl_notebook.GetSelection() 
                    indexP = 0
                    for dictPage in dictRubrique["pages"] :
                        if dictPage["visible"] == True :
                            if indexP == indexPage :
                                codeRubrique = dictRubrique["code"]
                                codePage = dictPage["code"]
                                ctrl_html = dictPage["ctrl_html"]
                                return codeRubrique, codePage
                            indexP += 1
                indexR += 1
        return codeRubrique, codePage
        
    def OnChangeLabelbook(self, event):
        self.MAJpageAffichee() 
##        indexRubrique = self.ctrl_labelbook.GetSelection()
##        # Recherche la page � MAJ
##        indexR = 0
##        for dictRubrique in self.listeObjets :
##            if dictRubrique["visible"] == True :
##                if indexR == indexRubrique :
##                    ctrl_notebook = dictRubrique["ctrl_notebook"]
##                    indexPage = ctrl_notebook.GetSelection() 
##                    self.MAJpage(indexRubrique, indexPage)
##                indexR += 1
        
    def OnChangeNotebook(self, event):
        indexRubrique = self.ctrl_labelbook.GetSelection()
        indexPage = event.GetSelection()
        self.MAJpage(indexRubrique, indexPage)
    
    def AjouterElement(self, code="", afficher=True):
        """ Ajoute une rubrique, une page ou un objet """
        indexR = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique["code"] == code :
                # Affiche la rubrique
                if etat == True and dictRubrique["visible"] == False :
                    pass
    
    def Coche(self, etat=True):
        self.ctrl_impression.Coche(etat)
    
    def ModificationParametres(self, premiere=False):
        if premiere == True :
            dateJour = datetime.date.today() 
            annee = dateJour.year
            self.dictParametres = {"mode":"presents", "periode":{"type":"annee", "annee":annee, "date_debut":datetime.date(annee, 1, 1), "date_fin":datetime.date(annee, 12, 31)}, "listeActivites":[], "dictActivites":{} }
        
        # Demande les param�tres � l'utilisateur
        dlg = DLG_Stats_parametres.Dialog(self)
        dlg.SetParametres(self.dictParametres)
        if dlg.ShowModal() == wx.ID_OK:
            self.dictParametres = dlg.GetDictParametres()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        # Envoi des param�tres � l'afficheur HTML
        self.ctrl_parametres.SetParametres(self.dictParametres)
        self.ctrl_parametres.MAJ() 
        
        # Envoi des param�tres � la baseHTML
        self.baseHTML.SetParametres(self.dictParametres)
        
        # Actualisation de la page affich�e actuellement
        self.MAJpageAffichee()
        return True



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    
    dialog_1.ModificationParametres(premiere=True) 
    
    dialog_1.ShowModal()
    app.MainLoop()
