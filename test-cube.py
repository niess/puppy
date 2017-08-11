from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

class Box:
    def __init__(self, x, y, z, color):
        # Build the data vector for the faces.
        format = GeomVertexFormat.getV3c4()
        data = GeomVertexData("vertices", format, Geom.UHStatic)
        data.setNumRows(8)
        writer = GeomVertexWriter(data, "vertex")
        for i in xrange(2):
            for j in xrange(2):
                for k in xrange(2):
                    writer.addData3f(
                      (i - 0.5) * x, (j - 0.5) * y, (k - 0.5) * z)
        writer = GeomVertexWriter(data, "color")
        for _ in xrange(8): writer.addData4f(color)

        def connect(object, indices):
            """Connect the vertices of a GeomPrimitive
            """
            for index in indices:
                object.addVertex(index)
            object.closePrimitive()

        # Build the triangles.
        triangles = GeomTriangles(Geom.UHStatic)
        for i, j, k in ((4,1,2),(2,4,1),(1,2,4)):
            connect(triangles, (0, j, k))
            connect(triangles, (j + k, k, j))
            connect(triangles, (i, i + k, i + j))
            connect(triangles, (i + j + k, i + j, i + k))

        # Build the Geom for the faces and initialise the node.
        self.faces = Geom(data)
        self.faces.addPrimitive(triangles)
        node = GeomNode("box")
        node.addGeom(self.faces)

        # Build the data vector for the borders.
        format = GeomVertexFormat.getV3c4()
        data = GeomVertexData("vertices", format, Geom.UHStatic)
        data.setNumRows(8)
        writer = GeomVertexWriter(data, "vertex")
        for i in xrange(2):
            for j in xrange(2):
                for k in xrange(2):
                    writer.addData3f(
                      (i - 0.5) * x, (j - 0.5) * y, (k - 0.5) * z)
        writer = GeomVertexWriter(data, "color")
        for _ in xrange(8): writer.addData4f((0,0,0,1))

        # Build the skeleton.
        lines = GeomLines(Geom.UHStatic)
        connect(lines, (0,1))
        connect(lines, (0,2))
        connect(lines, (0,4))
        connect(lines, (3,1))
        connect(lines, (3,2))
        connect(lines, (3,7))
        connect(lines, (5,1))
        connect(lines, (5,4))
        connect(lines, (5,7))
        connect(lines, (6,2))
        connect(lines, (6,4))
        connect(lines, (6,7))

        # Build the Geom for the borders and add it to the node.
        self.borders = Geom(data)
        self.borders.addPrimitive(lines)
        node.addGeom(self.borders)

        # Render the node.
        self.node = render.attachNewNode(node)

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Create a box.
        self.box = Box(10., 10., 10., (1., 1., 1., 1.))

app = MyApp()
app.run()
