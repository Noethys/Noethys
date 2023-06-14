#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------



def ModifierLuminosite(couleurRGB, coeff=-50) :
    """ Modifie la luminosité d'une couleur : + éclaircit / - assombrit """
    couleurHSV = RGBToHSV(couleurRGB) 
    couleurRGB = HSVToRGB((couleurHSV[0], couleurHSV[1], couleurHSV[2] + coeff))
    return couleurRGB

    
def HSVToRGB(couleurHSV):
    """ Converts a HSV triplet into a RGB triplet. """
    h = couleurHSV[0]
    s = couleurHSV[1]
    v = couleurHSV[2]
    maxVal = v
    delta = (maxVal*s)/255.0
    minVal = maxVal - delta
    hue = float(h)

    if h > 300 or h <= 60:
        r = maxVal
        if h > 300:
            g = int(minVal)
            hue = (hue - 360.0)/60.0
            b = int(-(hue*delta - minVal))
        else:
            b = int(minVal)
            hue = hue/60.0
            g = int(hue*delta + minVal)
    elif h > 60 and h < 180:
        g = int(maxVal)
        if h < 120:
            b = int(minVal)
            hue = (hue/60.0 - 2.0)*delta
            r = int(minVal - hue)
        else:
            r = int(minVal)
            hue = (hue/60.0 - 2.0)*delta
            b = int(minVal + hue)
    else:
        b = int(maxVal)
        if h < 240:
            r = int(minVal)
            hue = (hue/60.0 - 4.0)*delta
            g = int(minVal - hue)
        else:
            g = int(minVal)
            hue = (hue/60.0 - 4.0)*delta
            r = int(minVal + hue)
    return (r, g, b)



def RGBToHSV(couleurRGB=(255, 255, 255)):
    """ Converts a RGB triplet into a HSV triplet. """
    r = couleurRGB[0]
    g = couleurRGB[1]
    b = couleurRGB[2]
    minVal = float(min(r, min(g, b)))
    maxVal = float(max(r, max(g, b)))
    delta = maxVal - minVal
    v = int(maxVal)
    
    if abs(delta) < 1e-6:
        h = s = 0
    else:
        temp = delta/maxVal
        s = int(temp*255.0)
        if r == int(maxVal):
            temp = float(g-b)/delta
        elif g == int(maxVal):
            temp = 2.0 + (float(b-r)/delta)
        else:
            temp = 4.0 + (float(r-g)/delta)
        temp *= 60
        if temp < 0:
            temp += 360
        elif temp >= 360.0:
            temp = 0
        h = int(temp)
    return (h, s, v)
