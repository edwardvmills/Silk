#    This file is part of Silk
#    (c) Edward Mills 2016-2017
#    edwardvmills@gmail.com
#	
#    NURBS Surface modeling tools focused on low degree and seam continuity (FreeCAD Workbench) 
#
#    Silk is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import FreeCAD, Part, math
from FreeCAD import Base
from FreeCAD import Gui
import ArachNURBS as AN

# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')


class ControlGrid44_Rotate():
	def Activated(self):
		sel=Gui.Selection.getSelection()
		if len(sel)==4:
			mode='4sided'
		elif len(sel)==3:
			mode='3sided'

		if mode=='4sided':
			print ('4 sided mode not implemented for rotating edge grid')
			'''
			poly0=Gui.Selection.getSelection()[0]
			poly1=Gui.Selection.getSelection()[1]
			poly2=Gui.Selection.getSelection()[2]
			poly3=Gui.Selection.getSelection()[3]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid44_4")
			AN.ControlGrid44_4(a,poly0, poly1, poly2, poly3)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.67,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.33,1.00)
			FreeCAD.ActiveDocument.recompute()
			'''

		if mode=='3sided':
			poly0=Gui.Selection.getSelection()[0]
			poly1=Gui.Selection.getSelection()[1]
			poly2=Gui.Selection.getSelection()[2]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid44_3_Rotate_000")
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			AN.ControlGrid44_3_Rotate(a,poly0, poly1, poly2)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.67,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.33,1.00)
			FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		tooltip = (
			"Creates a ControlGrid44 from three ControlPoly4 edges. \n"
			"\n"
			"Select three ControlPoly4 edges, the selection order determines orientation. \n"
			'Used to produce a surface which "rotates" from the first edge selected to the \n'
			"third edge following along the second edge. \n"
			'Order is "left, bottom, right" with the rotational pivot at the "top" corner.\n'
			"\n"
			"Typical use is to merge a set of surfaces to a point (like closing a tube) \n"
			"\n"
			"Input for: \n"
			"-CubicSurface_44 \n"
			"-ControlGrid64_2Grid44 \n"
			"\n"
			"MORE INFO \n"
			"This is a degenerate grid (one edge collapsed to a point) that results in\n"
			'a "revolve" like surface. Will produce true spheres from arc polys, true\n'
			"ellipsoids from ellipse arc polys, but also accepts non-arc polys. \n"
			"\n"
			"Surface tangency from multiple grids can be produced automatically from well \n"
			"prepared arcs of circles and ellipses, but using general curves as input does\n"
			"not have an easily predictable outcome. Additional blending may be required.\n"
			"\n"
			"Although degenerate, this grid is the correct way to interface with spheres, \n"
			"where it does not introduce additional collapsed edges.\n")

		iconPath = path_Silk_icons + '/ControlGrid44_Rotate.svg'

		return {'Pixmap' : iconPath,
				'MenuText': 'ControlGrid44_Rotate', 
				'ToolTip': tooltip}

Gui.addCommand('ControlGrid44_Rotate', ControlGrid44_Rotate())
