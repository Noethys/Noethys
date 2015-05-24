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
import sys
import FonctionsPerso

import matplotlib
matplotlib.interactive(False)
##matplotlib.use('wxagg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas



class PanelGraph(wx.Panel):
    def __init__(self, parent, figure=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        
        self.figure = figure
        self.figure.set_size_inches(90, 90)
        self.canvas = Canvas(self, -1, figure)
        self.SetColor( (255,255,255) )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.EXPAND|wx.ALL, 0)
        self.SetSizer(sizer)

    def SetColor(self, rgbtuple=None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

    def Save_image(self):
        """ save figure image to file"""
        file_choices = "PNG (*.png)|*.png|" \
                       "PS (*.ps)|*.ps|" \
                       "EPS (*.eps)|*.eps|" \
                       "BMP (*.bmp)|*.bmp"
        
        standardPath = wx.StandardPaths.Get()
        save_destination = standardPath.GetDocumentsDir()

        dlg = wx.FileDialog(self, message=u"Enregistrer le graphe sous...",
                            defaultDir = save_destination, defaultFile="graphe.png",
                            wildcard=file_choices, style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=300)
            message = u"Le graphe a été sauvegardé avec succès"
            dlg = wx.MessageDialog(self, message, u"Sauvegarde", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
                
    def Clipboard_image(self):
        self.canvas.Copy_to_Clipboard()
        message = u"Le graphe a été envoyé dans le presse-papiers."
        dlg = wx.MessageDialog(self, message, u"Presse-papiers", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def Imprimer_image(self):
        # Enregistrement de l'image dans repertoire Temp
        self.canvas.print_figure("Temp/grapheTemp.png", dpi=300)
        # Création du PDF
        from reportlab.pdfgen import canvas as canvasPDF
        from reportlab.lib.pagesizes import A4
        hauteur, largeur = A4
        cheminFichier = "Temp/grapheTemp.pdf"
        if sys.platform.startswith("win") : cheminFichier = cheminFichier.replace("/", "\\")
        c = canvasPDF.Canvas(cheminFichier, pagesize=(largeur, hauteur), pageCompression = 1)
        img = c.drawImage("Temp/grapheTemp.png", 0, 0, width=largeur, height=hauteur, preserveAspectRatio=True)
        c.save()
        FonctionsPerso.LanceFichierExterne(cheminFichier)
        
        


class Dialog(wx.Dialog):
    def __init__(self, parent, figure=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Zoom_graphe", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Graphe
        self.box_graphe_staticbox = wx.StaticBox(self, -1, "Graphe")
        self.ctrl_graphe = PanelGraph(self, figure=figure)
        self.ctrl_graphe.SetMinSize((300, 300))
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_save_image = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Enregistrer_graphe.png", wx.BITMAP_TYPE_ANY))
        self.bouton_clipboard_image = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Clipboard_image.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer_image = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Imprimer_graphe.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSaveImage, self.bouton_save_image)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonClipboardImage, self.bouton_clipboard_image)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimerImage, self.bouton_imprimer_image)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

    def __set_properties(self):
        self.SetTitle(u"Visualisateur de graphe")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.bouton_save_image.SetToolTipString(u"Cliquez ici pour enregistrer le graphe au format image")
        self.bouton_clipboard_image.SetToolTipString(u"Cliquez ici pour envoyer le graphe dans le presse-papiers")
        self.bouton_imprimer_image.SetToolTipString(u"Cliquez ici pour publier le graphe au format PDF")
        self.SetMinSize((900, 650)) 
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        box_graphe = wx.StaticBoxSizer(self.box_graphe_staticbox, wx.VERTICAL)
        box_graphe.Add(self.ctrl_graphe, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_graphe, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_save_image, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_clipboard_image, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer_image, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(4)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Statistiques")

    def OnBoutonFermer(self, event):
        self.EndModal(wx.ID_CANCEL)
    
    def OnBoutonSaveImage(self, event):
        self.ctrl_graphe.Save_image()

    def OnBoutonClipboardImage(self, event):
        self.ctrl_graphe.Clipboard_image()

    def OnBoutonImprimerImage(self, event):
        self.ctrl_graphe.Imprimer_image()





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
    from numpy import arange, sin, pi
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot
    figure = Figure()
    ax = figure.add_subplot(111)
    t = arange(0.0,3.0,0.01)
    s = sin(2*pi*t)
    ax.plot(t,s)
    title = ax.set_title(u"Répartition par activité professionnelle", weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
    matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
    
    dialog_1 = Dialog(None, figure=figure)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
