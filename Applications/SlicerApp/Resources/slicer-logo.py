#!/bin/python

import math

from OpenGL import GL

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

_sx = -1.0
_sy = -1.0
_sz = 4.0
_oradius = math.sqrt((_sz * _sz) + (6.0 * 6.0))
_iradius = math.sqrt((_sz * _sz) + ((3.0 * 3.0) + (3.0 * 3.0)))
_sw = 9.0
_sd = 10.0
_view = 14.0
_skew = 0.3

#------------------------------------------------------------------------------
def drange(start, end, step=1.0):
  value = start
  if step > 0:
    while value < end:
      yield value
      value += step

  else:
    while value > end:
      yield value
      value += step

#==============================================================================
class logoWidget(QGLWidget):
  #----------------------------------------------------------------------------
  def initializeGL(self):
    self.qglClearColor(Qt.white)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_CULL_FACE)
    GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
    GL.glPolygonOffset(1.0, 1.0)

    vertexShaderSource = """
      varying vec4 position;

      void main()
      {
        position = gl_ModelViewMatrix * gl_Vertex;
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
      }
      """

    fragmentShaderSource = """
      varying vec4 position;

      void main()
      {
        float x = position[0] / position[3];
        float y = position[1] / position[3];
        float z = position[2] / position[3];

        if (x > %(sx)f && y > %(sy)f && z < %(sz)f)
          discard;

        gl_FragColor = vec4(0.5, 0.5, 0.8, 1.0); // FIXME
      }
      """ % { 'sx': _sx, 'sy': _sy, 'sz': _sz }

    shader = QGLShaderProgram(self.context())
    shader.addShaderFromSourceCode(QGLShader.Vertex, vertexShaderSource)
    shader.addShaderFromSourceCode(QGLShader.Fragment, fragmentShaderSource)
    shader.link()

    self._shader = shader

  #----------------------------------------------------------------------------
  def _drawSphereFace(self, qx, qy, qz, r):
    if (qx * qy * qz) > 0:
      GL.glFrontFace(GL.GL_CCW)
    else:
      GL.glFrontFace(GL.GL_CW)

    rs = r * r

    for j in xrange(0, 9):
      n = 9 - j
      y0 = r * qy * math.sin((j + 0) * math.pi / 18.0)
      y1 = r * qy * math.sin((j + 1) * math.pi / 18.0)
      p0 = math.sqrt(rs - (y0 * y0))
      p1 = math.sqrt(rs - (y1 * y1))

      GL.glBegin(GL.GL_TRIANGLE_STRIP)

      for i in xrange(0, n):
        t0 = 0.5 * (i + 0) * math.pi / n
        t2 = 0.5 * (i + 0) * math.pi / (n - 1) if n > 1 else 0
        GL.glVertex3d(p0 * qx * math.sin(t0), y0, p0 * qz * math.cos(t0))
        GL.glVertex3d(p1 * qx * math.sin(t2), y1, p1 * qz * math.cos(t2))

      GL.glVertex3d(p0 * qx, y0, 0.0)

      GL.glEnd()

  #----------------------------------------------------------------------------
  def paintGL(self):
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    # X slice
    self.qglColor(Qt.black)
    orx = math.sqrt((_oradius * _oradius) - (_sx * _sx))
    GL.glBegin(GL.GL_LINE_LOOP)
    for i in xrange(0, 36):
      t = math.pi * i / 18.0
      GL.glVertex3d(_sx, orx * math.sin(t), orx * math.cos(t))
    GL.glEnd()

    self.qglColor(Qt.gray)
    GL.glBegin(GL.GL_LINES)
    for i in drange(_sy, orx):
      GL.glVertex3d(_sx, i, _sz)
      GL.glVertex3d(_sx, i, -math.sqrt((orx * orx) - (i * i)))
    for i in drange(_sz, -orx, -1.0):
      GL.glVertex3d(_sx, _sy, i)
      GL.glVertex3d(_sx, math.sqrt((orx * orx) - (i * i)), i)
    GL.glEnd()

    GL.glColor3d(0.3, 0.3, 0.6)
    irx = math.sqrt((_iradius * _iradius) - (_sx * _sx))
    GL.glBegin(GL.GL_QUAD_STRIP)
    for i in xrange(0, 36 + 1):
      t = math.pi * i / 18.0
      GL.glVertex3d(_sx, irx * math.sin(t), irx * math.cos(t))
      GL.glVertex3d(_sx, orx * math.sin(t), orx * math.cos(t))
    GL.glEnd()

    # Y slice
    self.qglColor(Qt.black)
    ory = math.sqrt((_oradius * _oradius) - (_sy * _sy))
    GL.glBegin(GL.GL_LINE_LOOP)
    for i in xrange(0, 36):
      t = math.pi * i / 18.0
      GL.glVertex3d(ory * math.sin(t), _sy, ory * math.cos(t))
    GL.glEnd()

    self.qglColor(Qt.gray)
    GL.glBegin(GL.GL_LINES)
    for i in drange(_sx, ory):
      GL.glVertex3d(i, _sy, _sz)
      GL.glVertex3d(i, _sy, -math.sqrt((ory * ory) - (i * i)))
    for i in drange(_sz, -ory, -1.0):
      GL.glVertex3d(_sx, _sy, i)
      GL.glVertex3d(math.sqrt((ory * ory) - (i * i)), _sy, i)
    GL.glEnd()

    GL.glColor3d(0.8, 0.8, 1.0)
    iry = math.sqrt((_iradius * _iradius) - (_sy * _sy))
    GL.glBegin(GL.GL_QUAD_STRIP)
    for i in xrange(0, 36 + 1):
      t = math.pi * i / 18.0
      GL.glVertex3d(ory * math.sin(t), _sy, ory * math.cos(t))
      GL.glVertex3d(iry * math.sin(t), _sy, iry * math.cos(t))
    GL.glEnd()

    # Z slice
    self.qglColor(Qt.black)
    orz = math.sqrt((_oradius * _oradius) - (_sz * _sz))
    GL.glBegin(GL.GL_LINE_LOOP)
    for i in xrange(0, 36):
      t = math.pi * i / 18.0
      GL.glVertex3d(orz * math.sin(t), orz * math.cos(t), _sz)
    GL.glEnd()

    self.qglColor(Qt.gray)
    GL.glBegin(GL.GL_LINES)
    for i in drange(_sx, orz + 0.5):
      GL.glVertex3d(i, _sy, _sz)
      GL.glVertex3d(i, orz, _sz)
    for i in drange(_sy, orz + 0.5):
      GL.glVertex3d(_sx, i, _sz)
      GL.glVertex3d(orz, i, _sz)
    GL.glEnd()

    GL.glColor3d(0.4, 0.4, 0.8)
    irz = math.sqrt((_iradius * _iradius) - (_sz * _sz))
    GL.glBegin(GL.GL_QUAD_STRIP)
    for i in xrange(0, 36 + 1):
      t = math.pi * i / 18.0
      GL.glVertex3d(orz * math.sin(t), orz * math.cos(t), _sz)
      GL.glVertex3d(irz * math.sin(t), irz * math.cos(t), _sz)
    GL.glEnd()

    # X cutting plane
    self.qglColor(Qt.black)
    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex3d(_sx, _sy + _sw, +_sd)
    GL.glVertex3d(_sx, _sy + _sw, -_sd)
    GL.glVertex3d(_sx, _sy - _sw, -_sd)
    GL.glVertex3d(_sx, _sy - _sw, +_sd)
    GL.glEnd()

    # Y cutting plane
    self.qglColor(Qt.black)
    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex3d(_sx + _sw, _sy, +_sd)
    GL.glVertex3d(_sx + _sw, _sy, -_sd)
    GL.glVertex3d(_sx - _sw, _sy, -_sd)
    GL.glVertex3d(_sx - _sw, _sy, +_sd)
    GL.glEnd()

    # Sphere surface
    self._shader.bind()
    self._drawSphereFace(-1.0, -1.0, -1.0, _oradius)
    self._drawSphereFace(-1.0, -1.0, +1.0, _oradius)
    self._drawSphereFace(-1.0, +1.0, -1.0, _oradius)
    self._drawSphereFace(-1.0, +1.0, +1.0, _oradius)
    self._drawSphereFace(+1.0, -1.0, -1.0, _oradius)
    self._drawSphereFace(+1.0, -1.0, +1.0, _oradius)
    self._drawSphereFace(+1.0, +1.0, -1.0, _oradius)
    self._drawSphereFace(+1.0, +1.0, +1.0, _oradius)
    self._shader.release()

  #----------------------------------------------------------------------------
  def resizeGL(self, width, height):
    side = min(width, height)
    GL.glViewport(0, 0, width, height)

    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()

    if width > height:
      w = _view * width / height
      h = _view

    else:
      w = _view
      h = _view * height / width

    GL.glOrtho(-w, w, -h, h, -_view, _view)
    GL.glMultMatrixd([[1.0, 0.0, 0.0, 0.0],
                      [0.0, 1.0, 0.0, 0.0],
                      [_skew, _skew, -1.0, 0.0],
                      [0.0, 0.0, 0.0, 1.0]])

    GL.glMatrixMode(GL.GL_MODELVIEW)

#------------------------------------------------------------------------------
def main():
  app = QApplication([])
  w = logoWidget()
  w.show()
  app.exec_()

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if __name__ == '__main__':
  main()
