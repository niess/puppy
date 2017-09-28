# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 Université Clermont Auvergne, CNRS/IN2P3, LPC
#  Author: Valentin NIESS (niess@in2p3.fr)
#
#  This software is a Python library whose purpose is to provide procedural
#  builders for the Panda3D engine.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from panda3d.core import *

def _connect(object, indices, offset=0):
    """connect the vertices of a GeomPrimitive
    """
    for index in indices:
        object.addVertex(index + offset)
    object.closePrimitive()

def multiply(s, v):
    """Multiply a vector with a scalar."""
    return (s * v[0], s * v[1], s * v[2])

def dot(i,j):
    """Dot product of 2 vectors."""
    return i[0] * j[0] + i[1] * j[1] + i[2] * j[2]

def cross(i,j):
    """Cross product of 2 vectors."""
    return ( i[2] * j[1] - i[1] * j[2], i[0] * j[2] - i[2] * j[0],
             i[1] * j[0] - i[0] * j[1] )

def det(i,j,k):
    """Triple product (determinant) of 3 vectors.
    """
    return dot(i, cross(j, k))

class Builder:
    """Base geometry builder from primitives.
    """
    def __init__(self):
        self.name = None
        self.node = None
        self.path = None

    def render(self):
        """Render the GeomNode.

        Return: a NodePath to the rendered object.
        """
        if self.node is None:
            raise ValueError("empty GeomNode")
        if self.path is None:
            self.path = render.attachNewNode(self.node)
        return self.path

class PolyTube(Builder):
    """Builder for a tube with a polygonal section.
    """
    def __init__(self, *args, **kwargs):
        Builder.__init__(self)

        # Unpack the arguments.
        try:
            frame, vertices, length = args
        except ValueError:
            vertices, length = args
            frame = ((0., 0., 0.), ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.)))
        opts = { "name" : "polytube", "face_color" : (1,1,1,1),
          "line_color" : (0,0,0,1), "texture_scale" : None }
        for k, v in kwargs.items():
            if k not in opts: raise ValueError("unknown option {:}".format(k))
            opts[k] = v
        self.name = opts["name"]
        n_vx = len(vertices)

        # Build the 3D section.
        origin, (v0, v1, v2) = frame
        section = []
        bary = [0., 0., 0.]
        for vertex in vertices:
            v = [origin[i] + vertex[0] * v0[i] + vertex[1] * v1[i] -
                 0.5 * length * v2[i]  for i in xrange(3)]
            for i in xrange(3): bary[i] += v[i]
            section.append(v)
        nrm = 1. / n_vx
        for i in xrange(3): bary[i] *= nrm

        # Check the orientation of the section.
        u0 = [section[1][i] - section[0][i] for i in xrange(3)]
        u1 = [section[-1][i] - section[0][i] for i in xrange(3)]
        n = cross(u0, u1)
        if dot(v2, n) < 0.:
            v0, v1 = v1, v0
            vertices = vertices[::-1]
            section = section[::-1]
        v2 = multiply(length, v2)

        # Build and export the vertices representation.
        self._vertices = section + [[v[0] + v2[0], v[1] + v2[1], v[2] + v2[2]]
                                    for v in section]

        # Build and export the faces representation.
        n0 = cross(v0, v1)
        n0 = multiply(1. / dot(n0, n0)**0.5, n0)
        n1 = multiply(-1., n0)
        self._faces = [(self._vertices[0], n0), (self._vertices[n_vx], n1)]
        for i in xrange(n_vx):
            j = (i + 1) % n_vx
            k = (i + 2) % n_vx
            u0 = [section[j][l] - section[i][l] for l in xrange(3)]
            r = [section[k][l] - section[i][l] for l in xrange(3)]
            n = cross(u0, v2)
            nrm = 1. / dot(n, n)**0.5
            if dot(n, r) < 0.: nrm = -nrm
            n = multiply(nrm, n)
            self._faces.append((section[i], n))

        if opts["face_color"] is not None:
            # Build the data vector for the faces.
            format = GeomVertexFormat.getV3c4t2()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(6 * n_vx + 2)
            writer = GeomVertexWriter(data, "vertex")
            writer.addData3f(*bary)
            for x, y, z in section: writer.addData3f(x, y, z)
            writer.addData3f(bary[0] + v2[0], bary[1] + v2[1], bary[2] + v2[2])
            for x, y, z in section: writer.addData3f(
              x + v2[0], y + v2[1], z + v2[2])
            for i in xrange(n_vx):
                j = (i + 1) % n_vx
                writer.addData3f(*section[i])
                writer.addData3f(*section[j])
                writer.addData3f(section[j][0] + v2[0], section[j][1] + v2[1],
                  section[j][2] + v2[2])
                writer.addData3f(section[i][0] + v2[0], section[i][1] + v2[1],
                  section[i][2] + v2[2])

            # Build the data vector for the faces colors.
            writer = GeomVertexWriter(data, "color")
            n = len(opts["face_color"])
            if n == 4:
                for _ in xrange(6 * n_vx + 2):
                    writer.addData4f(opts["face_color"])
            elif n == n_vx + 2:
                for _ in xrange(n_vx + 1):
                    writer.addData4f(opts["face_color"][0])
                for _ in xrange(n_vx + 1):
                    writer.addData4f(opts["face_color"][1])
                for i in xrange(2, n_vx + 2):
                    for _ in xrange(4):
                        writer.addData4f(opts["face_color"][i])
            else:
                raise ValueError("Invalid face color")

            # Build the data vector for the faces textures.
            writer = GeomVertexWriter(data, "texcoord")
            if opts["texture_scale"] is None: scale = 1.
            else: scale = opts["texture_scale"]

            b = [0., 0.]
            for vertex in vertices:
                for i in xrange(2): b[i] += vertex[i]
            nrm = 1. / n_vx
            for i in xrange(2): b[i] *= nrm
            o = vertices[0]
            writer.addData2f((b[0] - o[0]) * scale, (b[1] - o[1]) * scale)
            for vertex in vertices:
                writer.addData2f(
                  (vertex[0] - o[0]) * scale, (vertex[1] - o[1]) * scale)
            writer.addData2f((b[0] - o[0]) * scale, (b[1] - o[1]) * scale)
            for vertex in vertices:
                writer.addData2f(
                  (vertex[0] - o[0]) * scale, (vertex[1] - o[1]) * scale)

            for i in xrange(n_vx):
                j = (i + 1) % n_vx
                x0, y0, z0 = section[i]
                x1, y1, z1 = section[j]
                u0 = (x1 - x0, y1 - y0, z1 - z0)
                L0 = (u0[0]**2 + u0[1]**2 + u0[2]**2)**0.5
                L12 = v2[0]**2 + v2[1]**2 + v2[2]**2
                x1 = (u0[0] * v2[0] + u0[1] * v2[1] + u0[2] * v2[2]) / L0
                y1 = (L12 - x1**2)**0.5
                writer.addData2f(0., 0.)
                writer.addData2f(L0 * scale, 0.)
                writer.addData2f((L0 + x1) * scale, y1 * scale)
                writer.addData2f(x1 * scale, y1 * scale)

            # Build the triangles.
            triangles = GeomTriangles(Geom.UHStatic)
            for i in xrange(n_vx):
                j = (i + 1) % n_vx
                _connect(triangles, (0, i + 1, j + 1))
                _connect(triangles, (0, j + 1, i + 1), n_vx + 1)
            for i in xrange(n_vx):
                offset = 2 * n_vx + 2 + 4 * i
                _connect(triangles, (2, 1, 0), offset)
                _connect(triangles, (3, 2, 0), offset)

            # Build the Geom for the faces and initialise the node.
            faces = Geom(data)
            faces.addPrimitive(triangles)
            if self.node is None: self.node = GeomNode(opts["name"])
            self.node.addGeom(faces)

        if opts["line_color"] is not None:
            # Build the data vector for the border lines.
            format = GeomVertexFormat.getV3c4()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(2 * n_vx)
            writer = GeomVertexWriter(data, "vertex")
            for x, y, z in section: writer.addData3f(x, y, z)
            for x, y, z in section: writer.addData3f(
              x + v2[0], y + v2[1], z + v2[2])
            writer = GeomVertexWriter(data, "color")
            for _ in xrange(2 * n_vx):
                writer.addData4f(opts["line_color"])

            # Build the border lines.
            lines = GeomLines(Geom.UHStatic)
            for i in xrange(n_vx):
                j = (i + 1) % n_vx
                _connect(lines, (i,j))
                _connect(lines, (i,j), n_vx)
                _connect(lines, (i, i + n_vx))
                _connect(lines, (j, j + n_vx))

            # Build the Geom for the borders and add it to the node.
            geom = Geom(data)
            geom.addPrimitive(lines)
            if self.node is None: self.node = GeomNode(opts["name"])
            self.node.addGeom(geom)

    def vertices(self):
        """Return the vertices representation of the rendered object.
        """
        if self.path is not None:
            M = self.path.getMat()
            vertices = [list(M.xformPoint(LVecBase3f(*v)))
                        for v in self._vertices]
        else:
            vertices = self._vertices
        return vertices

    def faces(self):
        """Return the faces representation of the rendered object.
        """
        if self.path is not None:
            M = self.path.getMat()
            faces = [[list(M.xformVec(LVecBase3f(*v[0]))),
                      list(M.xformPoint(LVecBase3f(*v[1])))]
                     for v in self._faces]
        else:
            faces = self._faces
        return faces

    def distance(self, point, direction=None):
        """Compute the signed distance of a point to the closest face.
        """
        pass

class Box(PolyTube):
    """3D box builder from a generic polytube.
    """
    def __init__(self, dx, dy, dz, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "box"
        section = ((-0.5 * dx, -0.5 * dy), (-0.5 * dx, 0.5 * dy),
                   (0.5 * dx, 0.5 * dy), (0.5 * dx, -0.5 * dy))
        PolyTube.__init__(self, section, dz, **kwargs)

class Map(Builder):
    """3D map builder from Panda primitives.
    """
    def __init__(self, x, y, z, face_color=(1,1,1,1), line_color=(0,0,0,1),
      name="map"):
        Builder.__init__(self)
        self.name = name
        nx, ny = len(x), len(y)
        n = nx * ny

        if face_color is not None:
            # Build the data vector for the faces.
            format = GeomVertexFormat.getV3c4t2()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(n)
            writer = GeomVertexWriter(data, "vertex")
            for i, yi in enumerate(y):
                for j, xj in enumerate(x):
                    writer.addData3f(xj, yi, z[i,j])
            writer = GeomVertexWriter(data, "color")
            try:
                if len(face_color[0]) != nx:
                    raise ValueError("Invalid face colors")
            except TypeError:
                for _ in xrange(n): writer.addData4f(face_color)
            else:
                for i in xrange(ny):
                    for j in xrange(nx):
                        writer.addData4f(face_color[i][j])
            writer = GeomVertexWriter(data, "texcoord")
            for i in xrange(ny):
                for j in xrange(nx):
                    writer.addData2f(x[j], y[i])

            # Build the triangles.
            triangles = GeomTriangles(Geom.UHStatic)
            for i in xrange(ny - 1):
                for j in xrange(nx - 1):
                    d1 = abs(z[i][j] - z[i + 1][j + 1])
                    d2 = abs(z[i + 1][j] - z[i][j + 1])
                    if d1 < d2:
                        _connect(triangles,
                          (i * nx + j, i * nx + j + 1, (i + 1) * nx + j + 1))
                        _connect(triangles,
                          ((i + 1) * nx + j, i * nx + j, (i + 1) * nx + j + 1))
                    else:
                        _connect(triangles,
                          (i * nx + j, i * nx + j + 1, (i + 1) * nx + j))
                        _connect(triangles,
                          ((i + 1) * nx + j + 1, (i + 1) * nx + j,
                          i * nx + j + 1))

            # Build the Geom for the faces and initialise the node.
            geom = Geom(data)
            geom.addPrimitive(triangles)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(geom)

        if line_color is not None:
            # Build the data vector for the lines.
            format = GeomVertexFormat.getV3c4()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(n)
            writer = GeomVertexWriter(data, "vertex")
            for i, yi in enumerate(y):
                for j, xj in enumerate(x):
                    writer.addData3f(xj, yi, z[i,j])
            writer = GeomVertexWriter(data, "color")
            for _ in xrange(n): writer.addData4f(line_color)

            # Build the lines.
            lines = GeomLines(Geom.UHStatic)
            for i in xrange(ny):
                for j in xrange(nx - 1):
                    _connect(lines, (j,j + 1), i * nx)
            for j in xrange(nx):
                for i in xrange(ny - 1):
                    _connect(lines, (i * nx,(i + 1) * nx), j)

            # Build the Geom for lines and add it to the node.
            geom = Geom(data)
            geom.addPrimitive(lines)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(geom)

class Terrain(Builder):
    """3D terrain builder from maps, implementing a level of details.
    """
    def __init__(self, x, y, z, face_color=(1,1,1,1), line_color=(0,0,0,1),
      name="terrain", lod=3, dlim=50.):
        Builder.__init__(self)
        self.name = name
        self.node = True
        self.path = NodePath("Terrain")
        self.path.reparentTo(render)

        size = 2**lod - 2**(lod - 1) + 1
        nx, ny = (len(x) - 1) / (size - 1), (len(y) - 1) / (size - 1)
        yoff = 0
        for iy in xrange(ny):
            y2 = y[yoff:(yoff + size)]
            xoff = 0
            for ix in xrange(nx):
                x2 = x[xoff:(xoff + size)]
                z2 = z[yoff:(yoff + size),xoff:(xoff + size)]
                ln = LODNode("root")
                path = NodePath(ln)
                path.reparentTo(self.path)
                d = 0.
                for i in xrange(lod):
                    p = Map(x2[::2**i], y2[::2**i], z2[::2**i,::2**i],
                      face_color, line_color, name).render()
                    if i == 0: di = dlim
                    elif i == lod - 1: di = 1E+12
                    else: di = 2 * d
                    ln.addSwitch(di, d)
                    d = di
                    p.reparentTo(path)
                xoff += size - 1
            yoff += size - 1

class Track(Builder):
    """3D track builder from Panda primitives.
    """
    def __init__(self, vertices, line_color=(0,0,0,1), name="track"):
        Builder.__init__(self)
        self.name = name
        n = len(vertices)

        # Build the data vector for the line segments.
        format = GeomVertexFormat.getV3c4()
        data = GeomVertexData("vertices", format, Geom.UHStatic)
        data.setNumRows(n)
        writer = GeomVertexWriter(data, "vertex")
        for vertex in vertices:
            writer.addData3f(*vertex)
        writer = GeomVertexWriter(data, "color")
        for _ in xrange(n): writer.addData4f(line_color)

        # Connect the segments.
        lines = GeomLines(Geom.UHStatic)
        for i in xrange(n - 1):
            _connect(lines, (i, i + 1))

        # Build the Geom for lines and add it to the node.
        geom = Geom(data)
        geom.addPrimitive(lines)
        if self.node is None: self.node = GeomNode(name)
        self.node.addGeom(geom)
