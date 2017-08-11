#!/usr/bin/env python
from direct.showbase.ShowBase import ShowBase
from primitive import Box

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Create a box.
        texture = loader.loadTexture("maps/envir-reeds.png")
        self.box = Box(10., 10., 10., texture=texture)

app = MyApp()
app.run()
