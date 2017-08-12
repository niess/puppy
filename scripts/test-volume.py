#!/usr/bin/env python
from direct.showbase.ShowBase import ShowBase
import puppy

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        texture = loader.loadTexture("maps/envir-reeds.png")

        # Create a box.
        self.box = puppy.Box(10., 10., 10.).render()
        self.box.setTexture(texture)
        self.box.setPos(0., 0., 20.)

        # Create a tube with a triangular section.
        section = ((0., 0.), (0., 10.), (10., 0.))
        self.tube = puppy.TriangularTube(section, 10.).render()
        self.tube.setTexture(texture)
        self.box.setPos(0., 0., -20.)

app = MyApp()
app.run()
