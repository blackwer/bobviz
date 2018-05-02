#!/usr/bin/env python

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectSlider import DirectSlider

from panda3d.core import LightNode, TextNode
from panda3d.core import PointLight, AmbientLight
from panda3d.core import Shader
from panda3d.core import Material
from panda3d.core import NodePath
from panda3d.core import Mat4, VBase4
from panda3d.core import AntialiasAttrib

import sys
import socket
import os
import copy
import math
import ast
import time
import struct

import numpy as np

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
        self.cam.node().getLens().setFar(1000.0)
        
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

        self.spheroColor = (0.8,0.0, 0.0, 1.0)

        # Enable anti-aliasing
        render.setAntialias(AntialiasAttrib.MAuto)
        

    def addSphero(self, pos=(0.0, 0.0, 0.0), u=(0.0,0.0,1.0), L=10.0, diameter=1.0, groupid="Spheros"):
        newSphero = render.attachNewNode(groupid)
        self.spheroBase.instanceTo(newSphero)

        self.updateSphero(newSphero, pos, u, L, diameter)

    def updateSphero(self, node, pos, u, L, diameter):
        node.set_shader_input("L", L)
        node.set_shader_input("diameter", diameter)
        node.setPos(pos)

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
        node.setHpr(yaw, 0.0, roll)

        # Make a diffuse material to color our spherocylinder
        myMaterial = Material()
        myMaterial.setAmbient((0.0, 0.0, 0.0, 0.0)) 
        myMaterial.setDiffuse(self.spheroColor)
        node.setMaterial(myMaterial)


print("starting")
t = BobViz()

def changeColor(colorSlot, group):
    color = list(t.spheroColor)
    color[colorSlot] = slider[group][colorSlot]['value']
    t.spheroColor = tuple(color)
    nodes = render.findAllMatches(group)
    for node in nodes:
        node.getMaterial().setDiffuse(t.spheroColor)

slider = dict()
slider["Spheros"] = []
slider["Spheros"].append(DirectSlider(range=(0,1), value=t.spheroColor[0], scale=0.25, pos=(-1.0, 0.0, -0.85),
                         command=changeColor, extraArgs=(0,"Spheros")))
slider["Spheros"].append(DirectSlider(range=(0,1), value=t.spheroColor[1], scale=0.25, pos=(-1.0, 0.0, -0.90),
                         command=changeColor, extraArgs=(1,"Spheros")))
slider["Spheros"].append(DirectSlider(range=(0,1), value=t.spheroColor[2], scale=0.25, pos=(-1.0, 0.0, -0.95),
                         command=changeColor, extraArgs=(2,"Spheros")))



# Create a unix domain socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = './uds_socket'
print('connecting to {}'.format(server_address))
try:
    sock.connect(server_address)
except socket.error as msg:
    print(msg)
    sys.exit(1)

def listener(task):
    try:
        # Send data
        message = b'GETFRAME'
        sock.sendall(message)

        # Read in integer size of frame
        size_in_bytes = int.from_bytes(sock.recv(4), byteorder=sys.byteorder)
        print('Receiving message of length {}'.format(size_in_bytes))

        # Receive frame. Divide into chunks because it struggles with large frames
        received = 0
        recvlist = []
        starttime = time.time()
        
        while received < size_in_bytes:
            data = sock.recv(4096)
            received += len(data)
            recvlist.append(data)

        buf = b''.join(recvlist)
        print('Message transfer took {}'.format(time.time() - starttime))

        nfloats = int(size_in_bytes / 8)
        msgarr = np.array(struct.unpack('{}d'.format(nfloats), buf))
        
        # Replace existing nodes
        starttime = time.time()
        nodes = render.findAllMatches("Spheros")

        oid = 0
        nspheros = int(nfloats / 7)
        for i in range(0, nspheros):
            pos = tuple(msgarr[i*7+0:i*7+3])
            u   = tuple(msgarr[i*7+3:i*7+6])
            L   =       msgarr[i*7+6]
            if oid < nodes.get_num_paths():
                t.updateSphero(node=nodes.getPath(oid),pos=pos,u=u,L=L,diameter=1.0)
                oid += 1
            else:
                t.addSphero(pos=pos,u=u,L=L)

        print('Redraw took {}'.format(time.time() - starttime))

        starttime = time.time()
        for i in range(oid, nodes.get_num_paths()):
            NodePath.remove_node(nodes[oid])

        print('Removal of old objects took {}'.format(time.time() - starttime))
        
    finally:
        return task.again


taskMgr.doMethodLater(2, listener, 'Listener')
t.run()

