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
import Silk_tooltips

# get strings
tooltip = (Silk_tooltips.ControlPoly4_segment_baseTip + Silk_tooltips.standardTipFooter)
moreInfo = (Silk_tooltips.ControlPoly4_segment_baseTip + Silk_tooltips.ControlPoly4_segment_moreInfo)

# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')
iconPath = path_Silk_icons + '/ControlPoly4_segment.svg'

class ControlPoly4_segment():
	def Activated(self):
		selx=Gui.Selection.getSelectionEx()
		try:
			Pick=selx[0].PickedPoints[0]
		except:
			pass
		if len(selx)==0:
			tipsDialog("Silk: ControlPoly4_segment", moreInfo)
			return

		elif len(selx)==1:
			# auto point selection mode
			# print("selx =", selx[0].Object)
			try:
				selType = selx[0].Object.object_type
				# print(selType)
			except:
				print("single object in selection does not have the 'object_type' property")
				return
			if selType != 'CubicCurve_4':
				print("for single input, the selection must be a CubicCurve_4 object")
				return
			AN_Curve=selx[0].Object 	# this is a resilient link to the underlying object
			u=AN_Curve.Shape.Curve.parameter(Pick)
			# print("picked point = ", Pick, " param = ", u)
			below = None
			above = None
			uBelow = 0.0
			uAbove = 1.0
			if AN_Curve.Poly.object_type == 'ControlPoly4_segment':
				below = AN_Curve.Poly.Point_onCurve_0
				above = AN_Curve.Poly.Point_onCurve_1
			CurveInList  = AN_Curve.InList
			if len(CurveInList) == 0:
				print("there is no cutting point defined on this curve")
				return
			for i in CurveInList:
				try:
					InType = i.object_type
					if InType == 'Point_onCurve':
						if i.u < u and i.u >= uBelow:
							below = i
							uBelow = i.u
						if i.u > u and i.u <= uAbove:
							above = i
							uAbove = i.u
				except:
					pass
			if below == None:
				below = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Point_onCurve_000")
				AN.Point_onCurve(below,AN_Curve, 0)
				below.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
				below.ViewObject.PointSize = 8.00
				below.ViewObject.PointColor = (0.00,0.00,0.00)
			if above == None:
				above =FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Point_onCurve_000")
				AN.Point_onCurve(above,AN_Curve, 1)
				above.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
				above.ViewObject.PointSize = 8.00
				above.ViewObject.PointColor = (0.00,0.00,0.00)
			# print("below :", below, ", ", uBelow)
			# print("above :", above, ", ", uAbove)
			Point_onCurve_0 = below	# this is a resilient link to the underlying object
			Point_onCurve_1 = above	# this is a resilient link to the underlying object			
		
		elif len(selx)==3:
			#selx=Gui.Selection.getSelectionEx()
			AN_Curve=selx[0].Object			# this is a resilient link to the underlying object
			Point_onCurve_0=selx[1].Object	# this is a resilient link to the underlying object
			Point_onCurve_1=selx[2].Object	# this is a resilient link to the underlying object

		else:
			print("ControlPoly4_segment: selection input not recognized")
			return

		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly4_segment_000")
		AN.ControlPoly4_segment(a,AN_Curve, Point_onCurve_0, Point_onCurve_1)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (0.00,1.00,1.00)
		a.ViewObject.PointSize = 4.00
		a.ViewObject.PointColor = (0.00,0.00,1.00)
		FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		return {'Pixmap' :  iconPath,
	  			'MenuText': 'ControlPoly4_segment',
				'ToolTip': tooltip}

Gui.addCommand('ControlPoly4_segment', ControlPoly4_segment())
