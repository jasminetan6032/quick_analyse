#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 14:27:43 2023

@author: jwt30
"""

from sty import bg, fg, rs

a = fg(34) + "I have a green foreground." + rs.fg
b = bg(133) + "I have a pink background" + rs.bg
c = fg(226) + bg(19) + "I have a light yellow fg and dark blue bg." + rs.all

print(a, b, c, sep="\n")