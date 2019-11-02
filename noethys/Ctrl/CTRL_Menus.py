#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
import GestionDB
import calendar
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Dates
import wx.lib.wordwrap as wordwrap

if 'phoenix' in wx.PlatformInfo:
    from wx.grid import GridCellRenderer
else:
    from wx.grid import PyGridCellRenderer as GridCellRenderer

COULEUR_CASES_OUVERTES = wx.Colour(255, 255, 255)
COULEUR_CASES_FERMEES = wx.Colour(240, 240, 240)


def DrawBorder(grid, dc, rect):
    top = rect.top
    bottom = rect.bottom
    left = rect.left
    right = rect.right
    dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
    dc.DrawLine(right, top, right, bottom)
    dc.DrawLine(left, top, left, bottom)
    dc.DrawLine(left, bottom, right, bottom)
    dc.SetPen(wx.WHITE_PEN)
    dc.DrawLine(left + 1, top, left + 1, bottom)
    dc.DrawLine(left + 1, top, right, top)


class LabelColonneRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor=None):
        self._bgcolor = bgcolor

    def Draw(self, grid, dc, rect, col):
        if self._bgcolor != None:
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else:
                dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        texte = grid.GetColLabelValue(col)
        texte = wordwrap.wordwrap(texte, rect.width, dc)
        DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, texte, hAlign, vAlign)



class Case():
    def __init__(self, grid=None, numLigne=None, numColonne=None, IDcategorie=None, date=None, dictMenu=None):
        self.grid = grid
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.IDcategorie = IDcategorie
        self.date = date
        self.IDmenu = None
        self.texte = None

        # Dessin de la case
        self.renderer = CaseRenderer(self)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)

        # Importation des valeurs
        if dictMenu != None and "texte" in dictMenu:
            self.IDmenu = dictMenu["IDmenu"]
            self.SetValeur(dictMenu["texte"])

    def GetRect(self):
        return self.grid.CellToRect(self.numLigne, self.numColonne)

    def Refresh(self):
        rect = self.GetRect()
        x, y = self.grid.CalcScrolledPosition(rect.GetX(), rect.GetY())
        rect = wx.Rect(x, y, rect.GetWidth(), rect.GetHeight())
        self.grid.GetGridWindow().Refresh(False, rect)

    def SetValeur(self, valeur=None):
        self.texte = valeur
        if valeur == None :
            valeur = ""
        self.grid.SetCellValue(self.numLigne, self.numColonne, valeur)
        self.Sauvegarde()

    def Copier(self, event=None):
        self.grid.presse_papiers = self.GetValeur()

    def Coller(self, event=None):
        self.SetValeur(self.grid.presse_papiers)

    def RAZ(self, event=None):
        self.SetValeur(None)

    def GetValeur(self):
        return self.grid.GetCellValue(self.numLigne, self.numColonne)

    def GetTexteToolTip(self):
        if self.texte == None :
            texte = u"Aucune donnée"
        else :
            texte = self.texte
        texte += u"\n\nCOMMANDES :"
        texte += u"\n- Double-cliquez pour modifier une case"
        texte += u"\n- Cliquez sur le bouton droit de la souris pour ouvrir le menu contextuel"
        texte += u"\n- Utilisez le copier-coller (Ctrl+C puis Ctrl+V)"
        return texte

    def Sauvegarde(self):
        DB = GestionDB.DB()

        # Suppression
        if self.texte == None and self.IDmenu != None :
            DB.ReqDEL("menus", "IDmenu", self.IDmenu)
            self.IDmenu = None

        # Ajout ou modification
        if self.texte != None:
            listeDonnees = [
                ("IDrestaurateur", self.grid.IDrestaurateur),
                ("IDcategorie", self.IDcategorie),
                ("date", self.date),
                ("texte", self.texte),
                ]
            if self.IDmenu == None :
                self.IDmenu = DB.ReqInsert("menus", listeDonnees)
            else:
                DB.ReqMAJ("menus", listeDonnees, "IDmenu", self.IDmenu)

        DB.Close()





class CaseRenderer(GridCellRenderer):
    def __init__(self, case=None):
        GridCellRenderer.__init__(self)
        self.case = case
        self.grid = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid

        # Dessine le fond
        if self.case.texte == None :
            couleur_fond = COULEUR_CASES_FERMEES
        else :
            couleur_fond = COULEUR_CASES_OUVERTES
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(couleur_fond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else:
            dc.DrawRectangleRect(rect)

        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())

        # Ecrit la valeur
        texte = grid.GetCellValue(row, col)
        texte = texte.replace("\n", ", ")

        dc.SetTextForeground(wx.Colour(0, 0, 0))

        tailleFont = 7
        dc.SetFont(wx.Font(tailleFont, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        texte = wordwrap.wordwrap(texte, rect.width, dc)
        y = rect.y + 2
        hauteurLigne = tailleFont + 3
        listeLignes = texte.split("\n")
        indexLigne = 0
        for ligne in listeLignes:
            dc.DrawText(ligne, rect.x + 3, y)
            y += hauteurLigne
            if (y + hauteurLigne) >= (rect.y + rect.height) :
                if indexLigne < len(listeLignes) - 1 :
                    dc.DrawText("...", rect.x + rect.width - 10, rect.y + rect.height - 12)
                break
            indexLigne += 1

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return CaseRenderer()




# ---------------------------------------------------------------------------------------

class CTRL(gridlib.Grid, glr.GridWithLabelRenderersMixin):
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.parent = parent
        self.periode = None
        self.IDrestaurateur = None

        self.presse_papiers = None
        self.dictCases = {}
        self.last_survol = (None, None)
        self.moveTo = None
        self.CreateGrid(1, 1)
        self.SetRowLabelSize(190)
        self.SetColLabelSize(60)

        # Binds
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDoubleClick)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def OnMouseMotion(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)

        if (numLigne, numColonne) != self.last_survol :
            self.last_survol = (numLigne, numColonne)
            if numLigne < 0 or numColonne < 0 or ((numLigne, numColonne) in self.dictCases) == False :
                self.GetGridWindow().SetToolTip(None)
            else :
                case = self.dictCases[(numLigne, numColonne)]
                texte = case.GetTexteToolTip()
                if self.GetGridWindow().GetToolTip() != texte:
                    tip = wx.ToolTip(texte)
                    tip.SetDelay(800)
                    self.GetGridWindow().SetToolTip(tip)

    def OnChar(self, event):
        numLigne = self.GetGridCursorRow()
        numColonne = self.GetGridCursorCol()
        keycode = event.GetKeyCode()
        if (numLigne, numColonne) in self.dictCases:
            case = self.dictCases[(numLigne, numColonne)]
            # Copier
            if keycode == 3 :
                case.Copier()
            # Coller
            if keycode == 22 :
                case.Coller()
        event.Skip()

    def OnCellRightClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        if (numLigne, numColonne) in self.dictCases:
            case = self.dictCases[(numLigne, numColonne)]

            menuPop = UTILS_Adaptations.Menu()

            # RAZ
            id = wx.Window.NewControlId()
            item = wx.MenuItem(menuPop, id, _(u"Effacer la case"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gomme.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, case.RAZ, id=id)
            if case.texte == None :
                item.Enable(False)

            menuPop.AppendSeparator()

            # Copier
            id = wx.Window.NewControlId()
            item = wx.MenuItem(menuPop, id, _(u"Copier\tCtrl+C"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Copier.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, case.Copier, id=id)

            # Coller
            id = wx.Window.NewControlId()
            item = wx.MenuItem(menuPop, id, _(u"Coller\tCtrl+V"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Coller.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, case.Coller, id=id)
            if self.presse_papiers == None:
                item.Enable(False)

            self.PopupMenu(menuPop)
            menuPop.Destroy()

    def Importation(self):
        """ Importation des données """
        dictDonnees = {}
        if self.periode == None or self.periode == None :
            return dictDonnees

        # Liste des dates du mois
        tmp, nbreJours = calendar.monthrange(self.periode["annee"], self.periode["mois"])
        dictDonnees["dates"] = []
        for numJour in range(1, nbreJours + 1):
            date = datetime.date(self.periode["annee"], self.periode["mois"], numJour)
            dictDonnees["dates"].append(date)

        DB = GestionDB.DB()

        # Catégories de menus
        req = """SELECT IDcategorie, nom
        FROM menus_categories 
        ORDER BY ordre;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictDonnees["categories"] =[]
        for IDcategorie, nom in listeDonnees :
            dictDonnees["categories"].append({"IDcategorie" : IDcategorie, "nom" : nom})

        # Menus
        if self.IDrestaurateur == None :
            self.IDrestaurateur = 0
        req = """SELECT IDmenu, IDcategorie, date, texte
        FROM menus 
        WHERE date>='%s' AND date<='%s' AND IDrestaurateur=%d
        ;""" % (dictDonnees["dates"][0], dictDonnees["dates"][-1], self.IDrestaurateur)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictDonnees["menus"] = {}
        for IDmenu, IDcategorie, date, texte in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if (date in dictDonnees["menus"]) == False :
                dictDonnees["menus"][date] = {}
            dictDonnees["menus"][date][IDcategorie] = {"IDmenu" : IDmenu, "texte" : texte}

        DB.Close()

        return dictDonnees

    def MAJ(self, periode=None, IDrestaurateur=None):
        self.periode = periode
        self.IDrestaurateur = IDrestaurateur

        # RAZ de la grid
        if self.GetNumberRows() > 0:
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0:
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()

        if IDrestaurateur == None :
            return False

        # Importation
        self.dictDonnees = self.Importation()

        if len(self.dictDonnees) == 0 :
            return

        # Création des colonnes
        nbreColonnes = len(self.dictDonnees["categories"])
        self.AppendCols(nbreColonnes)

        numColonne = 0
        for dictCategorie in self.dictDonnees["categories"] :
            nomColonne = dictCategorie["nom"]
            renderer = LabelColonneRenderer()
            self.SetColLabelRenderer(numColonne, renderer)
            self.SetColLabelValue(numColonne, nomColonne)
            self.SetColSize(numColonne, 300)
            numColonne += 1

        # Création des lignes
        nbreLignes = len(self.dictDonnees["dates"])
        self.AppendRows(nbreLignes)

        numLigne = 0
        for date in self.dictDonnees["dates"] :
            if type(date) == datetime.date :
                label = UTILS_Dates.DateComplete(date)
            else :
                label = date
            self.SetRowLabelValue(numLigne, label)
            self.SetRowSize(numLigne, 40)
            numLigne += 1

        # Création des cases
        self.dictCases = {}
        numLigne = 0
        for date in self.dictDonnees["dates"]:
            numColonne = 0

            for dictCategorie in self.dictDonnees["categories"]:
                IDcategorie = dictCategorie["IDcategorie"]

                # Recherche si une valeur existe
                if date in self.dictDonnees["menus"] and IDcategorie in self.dictDonnees["menus"][date]:
                    dictMenu = self.dictDonnees["menus"][date][IDcategorie]
                else :
                    dictMenu = None

                # Création de la case
                case = Case(self, numLigne=numLigne, numColonne=numColonne, IDcategorie=IDcategorie, date=date, dictMenu=dictMenu)
                self.dictCases[(numLigne, numColonne)] = case

                numColonne += 1
            numLigne += 1

    def OnLeftDoubleClick(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        if ((numLigne, numColonne) in self.dictCases) == False :
            return False
        case = self.dictCases[(numLigne, numColonne)]
        dlg = DLG_Saisie_texte(self, texte=case.texte)
        if dlg.ShowModal() == wx.ID_OK :
            case.SetValeur(dlg.GetTexte())
        dlg.Destroy()

    def RAZ(self, event=None):
        for case in list(self.dictCases.values()):
            case.RAZ()

# -------------------------------------------------------------------------------------------------------

class CTRL_Legendes(wx.ListBox):
    def __init__(self, parent, ctrl_texte=None):
        wx.ListBox.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)
        self.parent = parent
        self.ctrl_texte = ctrl_texte
        self.SetBackgroundColour("#F0FBED")
        self.MAJ()
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDoubleClick)

    def OnDoubleClick(self, event):
        index = event.GetSelection()
        IDlegende = self.dictDonnees[index]
        texte = u"{%d}" % IDlegende
        self.ctrl_texte.WriteText(texte)
        self.ctrl_texte.SetFocus()

    def MAJ(self):
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDlegende, nom, couleur
        FROM menus_legendes
        ORDER BY nom
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeLabels = []
        index = 0
        for IDlegende, nom, couleur in listeDonnees:
            self.dictDonnees[index] = IDlegende
            label = u"{%d}  %s" % (IDlegende, nom)
            listeLabels.append(label)
            index += 1
        self.SetItems(listeLabels)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]





class DLG_Saisie_texte(wx.Dialog):
    def __init__(self, parent, texte=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        if texte == None :
            texte = ""

        # Bandeau
        intro = _(u"Saisissez ci-dessous un plat par ligne. Pour insérer une légende dans le texte, double-cliquez sur son nom dans la liste ou tapez directement le numéro correspondant entre accolades (Exemples : {3} ou {14}).")
        titre = _(u"Saisie d'un menu")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Menu.png")

        # Texte
        self.staticbox_texte_staticbox = wx.StaticBox(self, -1, _(u"Texte"))
        self.ctrl_texte = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE )
        self.ctrl_texte.SetMinSize((300, 300))

        # Légendes
        self.staticbox_legendes_staticbox = wx.StaticBox(self, -1, _(u"Légendes disponibles"))
        self.ctrl_legendes = CTRL_Legendes(self, ctrl_texte=self.ctrl_texte)
        self.ctrl_legendes.SetMinSize((200, 200))
        self.bouton_legendes = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_supprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Effacer"), cheminImage="Images/32x32/Gomme.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLegendes, self.bouton_legendes)

        # Init
        self.ctrl_texte.SetValue(texte)
        self.ctrl_texte.SetFocus()

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un menu"))
        self.bouton_legendes.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des légendes")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour effacer le contenu du texte")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider ou tapez sur la touche Entrée du clavier")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Texte
        staticbox_texte = wx.StaticBoxSizer(self.staticbox_texte_staticbox, wx.VERTICAL)
        staticbox_texte.Add(self.ctrl_texte, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(staticbox_texte, 1, wx.EXPAND, 0)

        # Légendes
        staticbox_legendes = wx.StaticBoxSizer(self.staticbox_legendes_staticbox, wx.HORIZONTAL)
        staticbox_legendes.Add(self.ctrl_legendes, 1, wx.ALL|wx.EXPAND, 5)
        staticbox_legendes.Add(self.bouton_legendes, 0, wx.TOP|wx.RIGHT, 5)
        grid_sizer_contenu.Add(staticbox_legendes, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT| wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonLegendes(self, event):
        from Dlg import DLG_Menus_legendes
        dlg = DLG_Menus_legendes.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_legendes.MAJ()

    def OnBoutonSupprimer(self, event=None):
        self.ctrl_texte.SetValue("")
        self.EndModal(wx.ID_OK)

    def OnBoutonOk(self, event=None):
        self.EndModal(wx.ID_OK)

    def GetTexte(self):
        texte = self.ctrl_texte.GetValue()
        texte = texte.strip()
        if texte.endswith("\n"):
            texte = texte[:-1]
        if len(texte) == 0 :
            texte = None
        return texte








# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        # Contrôles
        self.ctrl = CTRL(panel)
        self.ctrl.MAJ(periode={"mois" : 7, "annee" : 2018}, IDrestaurateur=1)

        self.bouton_test = wx.Button(panel, -1, _(u"Bouton de test"))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
    
    def OnBoutonTest(self, event):
        """ Bouton de test """
        self.ctrl.AutoSizeRow(row=2)



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
