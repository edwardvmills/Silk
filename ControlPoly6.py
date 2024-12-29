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
from popup import tipsDialog
import tooltips

# get strings
tooltip = (tooltips.ControlPoly6_baseTip + tooltips.standardTipFooter)
moreInfo = (tooltips.ControlPoly6_baseTip + tooltips.ControlPoly6_moreInfo)

# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')
iconPath = path_Silk_icons + '/ControlPoly6.svg'

class ControlPoly6():
	def Activated(self):
		mode = None
		sel=Gui.Selection.getSelection()
		if len(sel)==0:
			tipsDialog("Silk: ControlPoly6", moreInfo)
			return
		elif len(sel)==1:
			try:
				if sel[0].Shape.Edges[0].Curve.NbPoles==4:
					mode='Bezier'
			except Exception: 
				pass
			try:
				if sel[0].GeometryCount==5:
					mode='5L'
			except Exception: 
				pass
			try:
				if mode != 'Bezier' and mode != '5L':
					#if isinstance(sel[0].Geometry[0], Part.ArcOfCircle):
					mode='FirstElement'
			except Exception: 
				pass
		elif len(sel)==2:
			if  sel[0].TypeId=='Sketcher::SketchObject' and sel[1].TypeId=='Sketcher::SketchObject':
				mode='2N'
			try:	
				if sel[0].Shape.Curve.NbPoles==4 and sel[1].Shape.Curve.NbPoles==4:
					mode='FilletBezier'
			except Exception: 
				pass
		else:
			print ("no valid mode found for ControlPoly6 based on the current selection")
			print ("mode,", mode)
			return		

		print ('selection processed as ', mode, ' operation')

		if mode == '5L':
			sketch=Gui.Selection.getSelection()[0]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_5L_000")
			AN.ControlPoly6_5L(a,sketch)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode == 'FirstElement' or mode == 'Bezier':
			sketch=Gui.Selection.getSelection()[0]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_FirstElement_000")
			AN.ControlPoly6_FirstElement(a,sketch)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode =='2N':
			sketch0=Gui.Selection.getSelection()[0]
			sketch1=Gui.Selection.getSelection()[1]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_2N_000")
			AN.ControlPoly6_2N(a,sketch0,sketch1)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode == 'FilletBezier':
			CubicCurve4_0=Gui.Selection.getSelection()[0]
			CubicCurve4_1=Gui.Selection.getSelection()[1]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly6_FilletBezier_000")
			AN.ControlPoly6_FilletBezier(a,CubicCurve4_0,CubicCurve4_1)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		return {'Pixmap' :  iconPath,
	  			'MenuText': 'ControlPoly6',
				'ToolTip': tooltip}

Gui.addCommand('ControlPoly6', ControlPoly6())
