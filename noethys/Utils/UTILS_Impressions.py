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

def AjouterPolicesPDF():
    """ Ajouter une police dans Reportlab """
    import reportlab.rl_config
    reportlab.rl_config.warnOnMissingFontGlyphs = 0
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    
    pdfmetrics.registerFont(TTFont("Arial", Chemins.GetStaticPath("Polices/arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", Chemins.GetStaticPath("Polices/arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Oblique", Chemins.GetStaticPath("Polices/ariali.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-BoldOblique", Chemins.GetStaticPath("Polices/arialbi.ttf")))
    
    registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Oblique', boldItalic='Arial-BoldOblique')






if __name__ == u"__main__":
    AjouterPolicePDF()
