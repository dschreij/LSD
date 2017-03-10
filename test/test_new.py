# -*- coding: utf-8 -*-
"""
Created on Fri May 22 11:24:53 2015

@author: Daniel
"""

# Make sure LSD from parent folder is imported
import sys, os
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))

import LSD
import LSD.drawing

import sdl2.ext
from LSD.screen import FrameBuffer
import time

c = LSD.create_window((800,600), title="Test transparent key", fullscreen=False)
print(c)

t1 = time.time()
fb = LSD.create_framebuffer(background_color="#222222")

circle = LSD.drawing.circle(100, "#FF0000", x=500, y=200, 
	fill=False, penwidth=5, aa=True, center=True)

ellipse = LSD.drawing.ellipse(200, 100, "#00FF00", fill=False, penwidth=5, aa=True)

# Add all textures to FrameBuffer
fb.add(circle)
fb.add(circle, x=150, y=250)
fb.add(ellipse, x=300, y=250)
fb.show()

print("Operation took {} ms".format((time.time()-t1)*1000))
processor = sdl2.ext.TestEventProcessor()
processor.run(c.window)

sdl2.ext.quit()