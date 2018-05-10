# bobviz
Socket based molecular dynamics visualization

This project aims to be a simple graphics tool for visualizing custom molecular dynamics/Monte Carlo simulations of 
non-spherical objects. The idea is to have something with no additional dependencies to avoid complicated compilation
issues when compiling on headless machines such as supercomputers, but still allow real-time display of computer
simulations for debugging or visualization purposes.

# Installation
Currently bobviz is implemented in python using the Panda3D library.
```
pip install Panda3D
pip install numpy
```
should suffice if python3 is your default python environment. If you are using conda, you might elect to 
install numpy via conda instead, though you've probably already done that.

# Getting started
Bobviz is a simple client software. It relies on unix domain sockets to communicate via a simple protocol.
A simple test server `test_server.py` is included to demonstrate how drawing commands are submitted to the client.
To try bobviz, in the same directory, call `test_server.py` and then background or open a new terminal, and run `bobviz.py` 
in the same directory.

Eventually, it would be nice to be able to use bobviz.py directly without sockets, as a proper library, *and* with sockets
as a real-time extension to some other software. A simple C-library that manages the socket will be included to 
simplify the drawing process when using low level codes.
