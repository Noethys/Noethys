#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import decimal


def FloatToDecimal(montant=0.0, plusProche=False):
    """ Transforme un float en decimal """
    if montant == None :
        montant = 0.0
    if type(montant) == str:
        montant = float(montant)
    x = decimal.Decimal(u"%.2f" % montant)
    # Arrondi au centime le plus proche
    if plusProche == True :
        x.quantize(decimal.Decimal('0.01')) # typeArrondi = decimal.ROUND_UP ou decimal.ROUND_DOWN
    return x



if __name__ == "__main__":
    print(FloatToDecimal(3.1359, plusProche=True))
