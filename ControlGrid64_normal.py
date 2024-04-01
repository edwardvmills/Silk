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
from ArachNURBS import equalVectors

# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')

class ControlGrid64_normal():
	def Activated(self):
			sel=Gui.Selection.getSelection()
			selx=Gui.Selection.getSelectionEx()[0]
			# this is a resilient link to the underlying object
			Grid64=selx.Object			
			
			# this is the line where the grid was picked. 
			Grid64_pick=selx.SubObjects[0]	
			# the edge this line is a part of is the edge that lies on the intended mirror plane
			# the inner control points of the grid will be modified so all grid legs reaching 
			# this plane are perpendicular to the plane.

			# the 64 surface is assumed to be 6p along u, so the two options are: 
			# mirror along v0
			# mirror along v3
			v0_normalize_2 = 0.0
			v0_normalize_3 = 0.0
			v3_normalize_20 = 0.0
			v3_normalize_21 = 0.0


			# assuming something (line/vertex) was picked along v0 or v3
			p0 = Grid64_pick.Vertexes[0].Point

			if (equalVectors(p0, Grid64.Poles[0], 0.000001) or
			equalVectors(p0, Grid64.Poles[1], 0.000001) or
			equalVectors(p0, Grid64.Poles[2], 0.000001) or
			equalVectors(p0, Grid64.Poles[3], 0.000001) or
			equalVectors(p0, Grid64.Poles[4], 0.000001) or
			equalVectors(p0, Grid64.Poles[5], 0.000001)):
				v0_normalize_2 = 1.0
				v0_normalize_3 = 1.0

			elif (equalVectors(p0, Grid64.Poles[18], 0.000001) or
			equalVectors(p0, Grid64.Poles[19], 0.000001) or
			equalVectors(p0, Grid64.Poles[20], 0.000001) or
			equalVectors(p0, Grid64.Poles[21], 0.000001) or
			equalVectors(p0, Grid64.Poles[22], 0.000001) or
			equalVectors(p0, Grid64.Poles[23], 0.000001)):
				v3_normalize_20 = 1.0
				v3_normalize_21 = 1.0
			# if the selection click wasn't on v0 or v3, do both edges
			else:
				v0_normalize_2 = 1.0
				v0_normalize_3 = 1.0
				v3_normalize_20 = 1.0
				v3_normalize_21 = 1.0
				print ("target edge selection not recognized, normalization applied to both sides")

			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid64_normal_000")
			AN.ControlGrid64_normal(a, Grid64, v0_normalize_2, v0_normalize_3, v3_normalize_20, v3_normalize_21)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.67,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.33,1.00)
			FreeCAD.ActiveDocument.recompute()
			
	def GetResources(self):
		tooltip = (
			"ControlGrid64_normal")

		iconpath = path_Silk_icons + '/WIP.svg'
		return {'Pixmap' :  iconpath, 'MenuText': 'ControlGrid64_normal', 'ToolTip': tooltip}

Gui.addCommand('ControlGrid64_normal', ControlGrid64_normal())
