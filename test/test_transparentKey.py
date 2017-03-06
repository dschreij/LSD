# -*- coding: utf-8 -*-
"""
Created on Fri May 22 11:24:53 2015

@author: Daniel
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May  6 22:52:13 2015

@author: daniel
"""
# Make sure LSD from parent folder is imported
import sys
sys.path.insert(0,'..')

import LSD
import sdl2.ext
from LSD.drawing import FrameBuffer
from random import randint
from math import pi, cos, sin

c = LSD.create_window((1024,768))

print(c)

r = 100
fb = FrameBuffer(c, background_color="#222222")
xc1 = c.resolution[0]/2-2*r
xc2 = c.resolution[0]/2+2*r
yc = c.resolution[1]/2

# Lines
half_ll = 1.5*r
fb.draw_line(xc1-half_ll, yc-half_ll, xc1+half_ll, yc+half_ll, "#FFFFFF", width=15)
fb.draw_line(xc2+half_ll, yc-half_ll, xc2-half_ll, yc+half_ll, "#FFFFFF", width=15)

# Anti aliased circle
fb.draw_circle(xc1, yc, r, color="#FFFF00", fill=False, aa=True, penwidth=1)
# Non AA circle
fb.draw_circle(xc2, yc, r, color="#00FFFF", fill=False, aa=True, penwidth=10)
fb.show()

processor = sdl2.ext.TestEventProcessor()
processor.run(c.window)

sdl2.ext.quit()