#    This file is part of Silk
#    (c) Edward Mills 2016-2017
#    edwardvmills@gmail.com
#	
#    Silk is the user interface of ArachNURBS. This implementation is a FreeCAD workbench.
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

class CubicCurve_4():
	def Activated(self):
		poly=Gui.Selection.getSelection()[0]
		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","CubicCurve_4")
		AN.CubicCurve_4(a,poly)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		return {'Pixmap' :  FreeCAD.__path__[3] + '\Silk\Resources\Icons\CubicCurve_4.svg', 'MenuText': 'CubicCurve_4', 'ToolTip': 'CubicCurve_4: \n creates a NURBS from a ControlPoly4 object (Cubic Bezier Curve)'}

Gui.addCommand('CubicCurve_4', CubicCurve_4())
