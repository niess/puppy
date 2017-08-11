#!/usr/bin/env python
from direct.showbase.ShowBase import ShowBase
import puppy

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Create a box.
        self.box = puppy.Box(10., 10., 10.).render()
        texture = loader.loadTexture("maps/envir-reeds.png")
        self.box.setTexture(texture)

app = MyApp()
app.run()
