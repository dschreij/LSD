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
import sys, os
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))

import LSD
import sdl2.ext
from LSD.drawing import FrameBuffer
import time

c = LSD.create_window((1280,800), title="Test transparent key", fullscreen=False)

# Print the context information
print(c)

r = 75

xc1 = c.resolution[0]*0.25
xc2 = c.resolution[0]*0.5
xc3 = c.resolution[0]/2*1.5
yc = c.resolution[1]*0.25
yc2 = c.resolution[1]/2*1.5

t1 = time.time()
fb = FrameBuffer(c, background_color="#222222")
print("Framebuffer created in {} ms".format((time.time()-t1)*1000))
t2 = time.time()

## Top row

# Lines
half_ll = 1.5*r
fb.draw_line(xc1-half_ll, yc-half_ll, xc1+half_ll, yc+half_ll, "#333333", width=10)
fb.draw_line(xc2+half_ll, yc-half_ll, xc2-half_ll, yc+half_ll, "#FFFFFF", width=10)
fb.draw_line(xc3-half_ll, yc-half_ll, xc3+half_ll, yc+half_ll, "#FF00FF", width=10)

# Anti aliased circle
fb.draw_circle(xc1, yc, r, color="#FFFF00", fill=False, aa=True, penwidth=1, opacity=0.5)
# Non AA circle
fb.draw_circle(xc2, yc, r, color="#00FFFF", fill=False, aa=False, penwidth=10, opacity=0.5)
# AA ellipse
fb.draw_ellipse(xc3, yc, r, r*2, color="#00FF00", fill=False, aa=True, 
	penwidth=5, opacity=1.0)

## Bottom row

fb.draw_line(xc1-half_ll, yc2-half_ll, xc1+half_ll, yc2+half_ll, "#333333", width=10)
fb.draw_line(xc2-half_ll, yc2-half_ll, xc2+half_ll, yc2+half_ll, "#FFFFFF", width=10)
fb.draw_line(xc3-half_ll, yc2-half_ll, xc3+half_ll, yc2+half_ll, "#FF00FF", width=10)

w, h = r*2, r*2
fb.draw_rect(xc1-w/2, yc2-h/2, w, h, color="#22FFBB", fill=False, penwidth=5)

print("Drawing took {} ms".format((time.time()-t2)*1000))
fb.show()

processor = sdl2.ext.TestEventProcessor()
processor.run(c.window)

sdl2.ext.quit()