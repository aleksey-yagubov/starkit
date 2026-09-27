===========================
Welcome to starkit module
===========================

Installation
============
Install latest version from `PyPI`_:

type following text in cms window

$ pip install -i https://test.pypi.org/simple/ starkit

Basic usage
===========

 Import the module
 import starkit

Methods
===========
alpha_calculation(xt, yt, zt, x, y, z, w, sizes, limAlpha)

where:

sizes = [ a5, b5, c5, a6, a7, a8, a9, a10, b10, c10 ]

a5 - distance between axis of symmetry and axis of servo drive number 5 (mm)
b5 - distance between axis of servo drives №5 and #6 in horizontal plane (mm)
c5 - distance between axis of servo drive №6 and origin point of Z axis (mm)
a6 - distance between axis of servo drives №6 and №7 (mm)
a7 - distance between axis of servo drives №7 and №8 (mm)
a8 - distance between axis of servo drives №8 and №9 (mm)
a9 - distance between axis of servo drives №9 and №10 (mm)
a10 - distance between axis of servo drive №10 and foot in horizontall plane (mm)
b10 - distance between axis of servo drive №10 and foot (mm)
c10 - distance between axis of servo drives №6 and №10 in horizontal plane (mm)

xt, yt, zt, x, y, z, w may be double or long types
sizes - list of sizes in robot's body
limAlpha

usage 

starkit.alpha_calculation(xt, yt, zt, x, y, z, w, sizes, limAlpha)