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

class ControlGrid44_2EdgeSegments():
	def Activated(self):
		surface=Gui.Selection.getSelection()[0]
		curve_a=Gui.Selection.getSelection()[1]
		curve_b=Gui.Selection.getSelection()[2]
		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid44_2EdgeSegments")
		AN.ControlGrid44_2EdgeSegments(a,surface,curve_a,curve_b)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (0.67,1.00,1.00)
		a.ViewObject.PointSize = 4.00
		a.ViewObject.PointColor = (0.00,0.33,1.00)
		FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		return {'Pixmap' :  path_Silk_icons + '/ControlGrid44_2EdgeSegments.svg', 'MenuText': 'ControlGrid44_2EdgeSegments', 'ToolTip': 'Create a ControlGrid44 from CubicSurface and two CubicCurve segments. \n Make the CubicCurve segments from ControlPoly4_Segments, select the \n CubicSurface, then CubicCurve segments on orthogonal sides. \n \n • Use to create ControlGrid64_2Grid44 to blend edges of CubicSurface_44 \n   where blending three or more orthogonal surfaces to a corner \n • Input for ControlGrid64_2Grid44 and CubicSurface_44'}

Gui.addCommand('ControlGrid44_2EdgeSegments', ControlGrid44_2EdgeSegments())
