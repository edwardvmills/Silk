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

class ControlPoly6():
	def Activated(self):
		sel=Gui.Selection.getSelection()
		if len(sel)==1:
			try:
				if sel[0].Shape.Curve.NbPoles==4:
					mode='Bezier'
			except Exception: 
				pass
			try:
				if sel[0].GeometryCount==5L:
					mode='5L'
			except Exception: 
				pass
			try:
				if sel[0].GeometryCount!=5L:
					#if isinstance(sel[0].Geometry[0], Part.ArcOfCircle):
					mode='FirstElement'
			except Exception: 
				pass
		if len(sel)==2:
			if  sel[0].TypeId=='Sketcher::SketchObject' and sel[1].TypeId=='Sketcher::SketchObject':
				mode='2N'
			try:	
				if sel[0].Shape.Curve.NbPoles==4 and sel[1].Shape.Curve.NbPoles==4:
					mode='FilletBezier'
			except Exception: 
				pass		

		print 'selection processed as ', mode, ' operation'

		if mode=='5L':
			sketch=Gui.Selection.getSelection()[0]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_5L")
			AN.ControlPoly6_5L(a,sketch)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode=='FirstElement':
			sketch=Gui.Selection.getSelection()[0]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_FirstElement")
			AN.ControlPoly6_FirstElement(a,sketch)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode=='Bezier':
			bezier=Gui.Selection.getSelection()[0]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_Bezier")
			AN.ControlPoly6_FirstElement(a,bezier)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode=='2N':
			sketch0=Gui.Selection.getSelection()[0]
			sketch1=Gui.Selection.getSelection()[1]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_2N")
			AN.ControlPoly6_2N(a,sketch0,sketch1)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode=='FilletBezier':
			CubicCurve4_0=Gui.Selection.getSelection()[0]
			CubicCurve4_1=Gui.Selection.getSelection()[1]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_FilletBezier")
			AN.ControlPoly6_FilletBezier(a,CubicCurve4_0,CubicCurve4_1)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		return {'Pixmap' :  FreeCAD.__path__[3] + '\Silk\Resources\Icons\ControlPoly6.svg', 'MenuText': 'ControlPoly6', 'ToolTip': 'ControlPoly6'}

Gui.addCommand('ControlPoly6', ControlPoly6())
