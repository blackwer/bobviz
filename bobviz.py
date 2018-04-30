#!/usr/bin/env python

from direct.showbase.ShowBase import ShowBase
from panda3d.core import LightNode, TextNode
from panda3d.core import PointLight, AmbientLight
from panda3d.core import Shader
from panda3d.core import Material
from panda3d.core import NodePath
from panda3d.core import Mat4, VBase4
from panda3d.core import AntialiasAttrib
from direct.gui.OnscreenText import OnscreenText
import sys
import os
import copy
import math

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, pos=(-0.1, 0.09), scale=.08,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))


class BobViz(ShowBase):
    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        # Set clipping planes on lens. 
        self.cam.node().getLens().setNear(10.0)
        self.cam.node().getLens().setFar(200.0)
        
        # Show instructions in the corner of the window.
        self.title = addTitle("BobViz Demo")

        # Spherocylinder is a special sphere where there are two hemispheres,
        # one just barely below z, and one just barely above z
        self.spheroBase = loader.loadModel("models/sphere.egg")

        # The default shader for the spherocylinder should just be a simple one
        # This could be changed for other objects, but the vertex shader scales a
        # a sphere to a spherocylinder.
        spheroShader = Shader.load(Shader.SL_GLSL,
                               vertex  ="shaders/spherocylinder.vert",
                               fragment="shaders/spherocylinder.frag")
        self.spheroBase.set_shader(spheroShader)

        # Just some test objects for now. 
        self.addSphero(pos=(0.0,0.0,0.0), u=(-0.0001, 0.0, 1.0), L=0.0, diameter = 1.2)
        self.addSphero(pos=(-0.5 * 5 / math.sqrt(3), 0.5 * 5 / math.sqrt(3), 0.5 * 5 / math.sqrt(3)),
                       u=(-1/math.sqrt(3), 1/math.sqrt(3), 1/math.sqrt(3)))

        
        # Create an ambient light. We could use other light sources to make sexier graphics,
        # but this is good enough for gov't work. 
        alightnode = AmbientLight("ambient light")
        alightnode.setColor((1.0, 1.0, 1.0, 1))
        alight = render.attachNewNode(alightnode)
        render.setLight(alight)

        # Set the default camera position.
        # Mouse control resets it to zero, so we need to calculate the
        # appropriate transform to put the camera back into place.
        # I put the camera along -y, pointing at the origin.
        # Default view is +x -> right, +y -> into screen, +z -> up
        self.disableMouse()
        self.camera.setPos(0, -50, 0)
        mat=Mat4(camera.getMat())
        mat.invertInPlace()
        self.mouseInterfaceNode.setMat(mat)
        self.enableMouse()

        # Make the background default to white
        self.win.setClearColorActive(True)
        self.win.setClearColor(VBase4(1, 1, 1, 1))

        # Enable anti-aliasing
        render.setAntialias(AntialiasAttrib.MAuto)
        

    def addSphero(self, pos=(0.0, 0.0, 0.0), u=(0.0,0.0,1.0), L=10.0, diameter=1.0):
        newSphero = copy.copy(self.spheroBase)
        newSphero.set_shader_input("L", L)
        newSphero.set_shader_input("diameter", diameter)
        newSphero.setPos(pos)

        # Theta is the amount to rotate about x, the 'roll'
        roll = math.acos(u[2]) * 180 / math.pi
        
        # Determine amount to rotate about z ('yaw' or 'heading')
        length_xy = math.sqrt(u[0]*u[0] + u[1]*u[1])
        if length_xy > 0.0:
            yaw = math.acos(u[0] / length_xy) * 180 / math.pi
            if u[1] < 0.0:
                yaw = 360 - yaw
        else:
            yaw = 0.0

        # Apply transforms (heading/yaw, pitch, roll)
        newSphero.setHpr(yaw, 0.0, roll)

        # Make a diffuse material to color our spherocylinder
        myMaterial = Material()
        myMaterial.setAmbient((0.0, 0.0, 0.0, 0.0)) 
        if u[0] < 0:
            myMaterial.setDiffuse((0.8,0,0.0,1.0))
        else:
            myMaterial.setDiffuse((0.0,0,0.8,1.0))
        newSphero.setMaterial(myMaterial)
        
        # Add it to the scene
        newSphero.reparentTo(render)



t = BobViz()
t.run()
