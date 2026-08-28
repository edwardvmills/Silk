# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileNotice: Part of the Silk addon.

################################################################################
#                                                                              #
#   (c) 2016 Edward Mills <edwardvmills@gmail.com>                             #
#                                                                              #
#   Silk is free software: you can redistribute it and/or modify it            #
#   under the terms of the GNU General Public License as published by          #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       #
#                                                                              #
#   See the GNU General Public License for more details.                       #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with this program. If not, see <http://www.gnu.org/licenses/>.       #
#                                                                              #
################################################################################


from __future__ import division # allows floating point division from integers
import FreeCAD, Part, math
from FreeCAD import Base
from FreeCAD import Gui
import ArachNURBS as AN
from popup import tipsDialog
import Silk_tooltips

# get strings
tooltip = (Silk_tooltips.ControlGrid44_2EdgeSegments_baseTip + Silk_tooltips.standardTipFooter)
moreInfo = (Silk_tooltips.ControlGrid44_2EdgeSegments_baseTip + Silk_tooltips.ControlGrid44_2EdgeSegments_moreInfo)


# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')
iconPath = path_Silk_icons + '/ControlGrid44_2EdgeSegments.svg'

def makeSingle(surface,curve_a,curve_b):
	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid44_2EdgeSegments_000")
	AN.ControlGrid44_2EdgeSegments(a,surface,curve_a,curve_b)
	a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
	a.ViewObject.LineWidth = 1.00
	a.ViewObject.LineColor = (0.0,170/255,255/255)
	a.ViewObject.PointSize = 2.00
	a.ViewObject.PointColor = (0.0,85/255,255/255)
	return

class ControlGrid44_2EdgeSegments():
	def Activated(self):
		sel=Gui.Selection.getSelection()
		if len(sel)==0:
			tipsDialog("Silk: ControlGrid44_2EdgeSegments", moreInfo)
			return
		if len(sel)!=3 and len(sel)!=7:
			tipsDialog("Silk: ControlGrid44_2EdgeSegments", 
			  "invalid input, click the icon with nothing selected for a tooltip. \n\n"
			  "select: one surface and two curve segments on adjacent sides, \n"
			  "or: one surface and 3 curve segments on two adjacent sides \n"
			  "(3 consecutive segments for each side)")
			return
		
		if len(sel)==3:
			print("in single")
			surface=Gui.Selection.getSelection()[0]
			curve_a=Gui.Selection.getSelection()[1]
			curve_b=Gui.Selection.getSelection()[2]
			makeSingle(surface,curve_a,curve_b)

		if len(sel)==7:
			# check types later?
			surface=Gui.Selection.getSelection()[0]
			# side 1
			curve_a0=Gui.Selection.getSelection()[1]
			curve_a1=Gui.Selection.getSelection()[2]
			curve_a2=Gui.Selection.getSelection()[3]
			# side 2
			curve_b0=Gui.Selection.getSelection()[4]
			curve_b1=Gui.Selection.getSelection()[5]
			curve_b2=Gui.Selection.getSelection()[6]
			# middle piece
			makeSingle(surface,curve_a1,curve_b1)
			# bottom
			makeSingle(surface,curve_a1,curve_b0)
			# right
			makeSingle(surface,curve_a2,curve_b1)
			# top
			makeSingle(surface,curve_a1,curve_b2)
			# left
			makeSingle(surface,curve_a0,curve_b1)

		'''
		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid44_2EdgeSegments_000")
		AN.ControlGrid44_2EdgeSegments(a,surface,curve_a,curve_b)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (0.0,170/255,255/255)
		a.ViewObject.PointSize = 2.00
		a.ViewObject.PointColor = (0.0,85/255,255/255)
		'''

		FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
				return {'Pixmap' :  iconPath,
	  					'MenuText': 'ControlGrid44_2EdgeSegments',
						'ToolTip': tooltip}

Gui.addCommand('ControlGrid44_2EdgeSegments', ControlGrid44_2EdgeSegments())
