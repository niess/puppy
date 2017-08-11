from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

class Box:
    def __init__(self, dx, dy, dz, face_color=(1,1,1,1), line_color=(0,0,0,1),
      texture=None):
        # Build the data vector for the faces.
        format = GeomVertexFormat.getV3c4t2()
        data = GeomVertexData("vertices", format, Geom.UHStatic)
        data.setNumRows(24)
        writer = GeomVertexWriter(data, "vertex")
        for axis in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
            for c in ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)):
                writer.addData3f((c[axis[0]] - 0.5) * dx,
                                 (c[axis[1]] - 0.5) * dy,
                                 (c[axis[2]] - 0.5) * dz)
            for c in ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)):
                writer.addData3f((c[axis[0]] - 0.5) * dx,
                                 (c[axis[1]] - 0.5) * dy,
                                 (c[axis[2]] - 0.5) * dz)
        writer = GeomVertexWriter(data, "color")
        n = len(face_color)
        if n == 4:
            for _ in xrange(24): writer.addData4f(face_color)
        elif n == 6:
            for i in xrange(6):
                for _ in xrange(4): writer.addData4f(face_color[i])
        else:
            raise ValueError("Invalid face color")
        writer = GeomVertexWriter(data, "texcoord")
        for _ in xrange(6):
            writer.addData2f(0, 0)
            writer.addData2f(1, 0)
            writer.addData2f(1, 1)
            writer.addData2f(0, 1)

        def connect(object, indices):
            """Connect the vertices of a GeomPrimitive
            """
            for index in indices:
                object.addVertex(index)
            object.closePrimitive()

        # Build the triangles.
        triangles = GeomTriangles(Geom.UHStatic)
        for i in xrange(6):
            connect(triangles, (4 * i + 1, 4 * i + 2, 4 * i))
            connect(triangles, (4 * i + 2, 4 * i + 3, 4 * i))

        # Build the Geom for the faces and initialise the node.
        self.faces = Geom(data)
        self.faces.addPrimitive(triangles)
        node = GeomNode("box")
        node.addGeom(self.faces)

        # Build the data vector for the border lines.
        if line_color is not None:
            format = GeomVertexFormat.getV3c4()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(8)
            writer = GeomVertexWriter(data, "vertex")
            for i in xrange(2):
                for j in xrange(2):
                    for k in xrange(2):
                        writer.addData3f(
                          (i - 0.5) * dx, (j - 0.5) * dy, (k - 0.5) * dz)
            writer = GeomVertexWriter(data, "color")
            for _ in xrange(8): writer.addData4f(line_color)

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
        if texture is not None:
            self.node.setTexture(texture)

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Create a box.
        texture = loader.loadTexture("maps/envir-reeds.png")
        self.box = Box(10., 10., 10., texture=texture)

app = MyApp()
app.run()
