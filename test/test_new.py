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

fb = LSD.create_framebuffer(background_color="#222222")

circle = LSD.drawing.circle(150, 150, 100, 
	"#FF0000", fill=False, penwidth=5, aa=True)


fb.add(circle)
fb.add(circle, x=500, y=200)
fb.add(circle, x=200, y=300)

fb.show()
processor = sdl2.ext.TestEventProcessor()
processor.run(c.window)

sdl2.ext.quit()