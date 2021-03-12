## Silk Workbench

![example of current capability](https://github.com/edwardvmills/Silk/blob/master/Resources/Demo_files/Silk_Demo_02.png?raw=true)

## Description
NURBS Surface modeling tools focused on low degree and seam continuity ([FreeCAD](https://www.freecadweb.org/) Workbench). Silk is the new name of the [NURBSlib_EVM](http://edwardvmills.github.io/NURBSlib_EVM/) project.

NURBS: smooth curves and surfaces whose form is controlled by a relatively small number of "control points", which sort of float close to the curves and surfaces. As their name indicates, the "control points" are what the user modifies in order to control the curves or surfaces. The "refinement" of a NURBS is controlled by its degree, and the "distance of effect" of a control point is controlled by the knot vector of the NURBS.

![example of current capability](https://github.com/edwardvmills/Silk/blob/master/Resources/Demo_files/Silk_Demo_03_01.png?raw=true)

Low Degree: Silk NURBS curves and surfaces are of the minimum degree suitable for the intended goal. The knot vectors are kept to a small consistent set. Often with NURBS modeling problems, the apparent solution is to increase the degree and number of knots. While this is perfectly valid, it raises the computational difficulty and organizational challenges of the control points. Silk aims to provide tools of the absolute minimum mathematical complexity for each problem solved.

Seam Continuity: Silk's goal is to allow complex models to be built from individual NURBS sections, alternatively creating new surfaces to be continuous to existing surfaces, or providing tools to to create smooth transitions where surfaces are initially created with discontinuities.

FreeCAD does the heavy lifting:

-providing a planar sketch interface that we can locate anywhere in 3D to manipulate simply groups of control points. Silk can use multiple sketches in different planes to construct truly 3D curves and surface edges.

-drawing the beautiful and smooth surfaces once appropriate control grids have been prepared using Silk tools.

The animation below demonstrates fine surface tuning through sketches with full engineering control of curve and surface continuity. Notice the low number of control points used on the profile control sketch. Up to a certain complexity, Silk updates virtually in real time with sketch editing.

![example of current capability](https://github.com/edwardvmills/Silk/blob/master/Resources/Demo_files/Steering_Wheel_01_01.gif?raw=true)


## Limitations
Although Silk is intended to provide efficient and user friendly tools in the long term, at this time, it behaves more like a low level library with GUI access to its functions. The individual functions create individual document objects, and in the future, relevant functions might be chained together automatically to create complex nested objects. The current objects are very likely to persist, both as individual document objects, and as sub-objects in the future.

Modeling can be done in the current state, and the resulting data structures are efficient, but the process can be laborious. The best path forward for user friendliness will depend heavily upon the outcome of several debates within the FreeCAD community on how parts, solid bodies, assemblies, and object linking are organized.

In the meantime Silk does offer a few tools not otherwise available in FreeCAD (eg. 3D splines), and can in general be seen as a sandbox for surface design, control strategies, data strucutres, and algorithms.

![example of current capability](https://github.com/edwardvmills/Silk/blob/master/Resources/Demo_files/Steering_Wheel_03_05.png?raw=true)

## Installation
Recommended installation is through the FreeCAD [Addon Manager](https://wiki.freecadweb.org/AddonManager) via `Tools -> Addon Manager`

## Documentation
Until documentation and tutorials are rewritten for Silk, [NURBSlib_EVM](http://edwardvmills.github.io/NURBSlib_EVM/) is the best source of information regarding the project. 
The tutorials can still be followed, simply skip setup, color, and display mode instructions. All setup is handled by installing the workbench, and the object display properties have been set to reasonable defaults. ([Silk Wiki in progress](https://github.com/edwardvmills/Silk/wiki))



## Licence
All program files (.py, .pyc, .FCMacro) are offered under the terms of the [Gnu gpl-v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)

![gplv3](https://www.gnu.org/graphics/gplv3-127x51.png)

Icon .svg files, icon .png files, demo models .FCStd files, and tutorial model .FCStd files are offered under the terms of CC-BY 4.0

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
