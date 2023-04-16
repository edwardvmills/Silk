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


from __future__ import division # allows floating point division from integers
import FreeCAD, Part, math
from FreeCAD import Base
from FreeCAD import Gui
import ArachNURBS as AN

# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')

class Point_onCurve():
	def Activated(self):  
		selx=Gui.Selection.getSelectionEx()[0]
		AN_Curve=selx.Object					# this is a resilient link to the underlying object
		Pick=selx.PickedPoints[0]				# this is the point where the curve was picked		
		u=AN_Curve.Shape.Curve.parameter(Pick)	# picked point is used for an initial value

		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Point_onCurve_000")
		AN.Point_onCurve(a,AN_Curve, u)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.PointSize = 5.00
		a.ViewObject.PointColor = (1.00,0.00,0.00)
		FreeCAD.ActiveDocument.recompute()
			
	def GetResources(self):
		return {'Pixmap' :  path_Silk_icons + '/Point_onCurve.svg',
				'MenuText': 'Point_onCurve',
				'ToolTip': 'Create a point on a Cubic_Curve4 or Cubic_Curve6. \n Select a location on the curve to place the point. \n \n • Input as endpoints of ControlPoly4_Segment'}

Gui.addCommand('Point_onCurve', Point_onCurve())
