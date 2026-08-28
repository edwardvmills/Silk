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
tooltip = (Silk_tooltips.ControlPoly4_baseTip + Silk_tooltips.standardTipFooter)
moreInfo = (Silk_tooltips.ControlPoly4_baseTip + Silk_tooltips.ControlPoly4_moreInfo)

# Locate Workbench Directory & icon
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')
iconPath = path_Silk_icons + '/ControlPoly4.svg'

def is3L(sketch):
	geom = sketch.Geometry
	geom_count = geom.__len__()
	# does the sketch contain three visible objects, which are line segments?
	visible_count = 0
	visible_line_count = 0
	for i in range(0, geom_count):
		if sketch.getConstruction(i) == False:
			visible_count = visible_count + 1
			if geom[i].TypeId =='Part::GeomLineSegment':
				visible_line_count = visible_line_count + 1
	if visible_line_count==3 and visible_count==visible_line_count:
		return True
	else:
		return False
	
def isGrid44(obj):
	ControlGrid44_types = ['ControlGrid44_2EdgeSegments',
							'ControlGrid44_EdgeSegment',
							'ControlGrid44_flow',
							'ControlGrid44_Rotate',
							'ControlGrid44_4']
	try:
		if obj.object_type in ControlGrid44_types:
			return True
	except:
		return False

def isControlPoly4(obj):
	ControlPoly4_types = ['ControlPoly4_3L',
							'ControlPoly4_2N',
							'ControlPoly4_2P',
							'ControlPoly4_FirstElement',
							'ControlPoly4_GridEdge']
	try:
		if obj.object_type in ControlPoly4_types:
			return True
	except:
		return False

class ControlPoly4():
	def Activated(self):
		sel=Gui.Selection.getSelectionEx()
		if len(sel)==0:
			# empty selection - show tool information window
			tipsDialog("Silk: ControlPoly4", moreInfo)
			return		
		if len(sel)==1:
			# one object selected for input
			if sel[0].Object.TypeId == 'Sketcher::SketchObject':
				# which is a sketch
				sketch = sel[0].Object
				if is3L(sketch):
					mode='3L'				
				else: 
					# anything except 3 visible lines will only consider the first 
					# 'priority' element in the geometry listing
					# the downstream function will prioritize sketch geometry by type
					mode='FirstElement'
			else:
				obj=sel[0].Object
				if isGrid44(obj):
					mode = 'GridEdge'				
					poles = sel[0].Object.Poles
					edge0p = [1,2]
					edge1p = [7,11]
					edge2p = [13,14]
					edge3p = [4,8]

					if sel[0].SubObjects[0].ShapeType == 'Vertex':
						v0 = sel[0].SubObjects[0].Point
						# p0 = poles.index(v0) - worked in console, but not here. decimal places are mismatched?
						p0 = AN.VectorIndex(poles, v0)
						if p0 in edge0p:
							SelectedEdge = 0
						elif p0 in edge1p:
							SelectedEdge = 1
						elif p0 in edge2p:
							SelectedEdge = 2
						elif p0 in edge3p:
							SelectedEdge = 3
						else:
							print("ControlPoly4: 'GridEdge' mode. The selected grid vertex is not on an edge, the input cannot be interpreted")
							return

					elif sel[0].SubObjects[0].ShapeType == 'Edge':
						v0 = sel[0].SubObjects[0].firstVertex().Point
						v1 = sel[0].SubObjects[0].lastVertex().Point
						# p0 = poles.index(v0) - worked in console, but not here. decimal places are mismatched?
						# p1 = poles.index(v1) - worked in console, but not here. decimal places are mismatched?
						p0 = AN.VectorIndex(poles, v0)
						p1 = AN.VectorIndex(poles, v1)
						if p0 in edge0p:
							SelectedEdge = 0
						elif p0 in edge1p:
							SelectedEdge = 1
						elif p0 in edge2p:
							SelectedEdge = 2
						elif p0 in edge3p:
							SelectedEdge = 3
						if p1 in edge0p:
							SelectedEdge = 0
						elif p1 in edge1p:
							SelectedEdge = 1
						elif p1 in edge2p:
							SelectedEdge = 2
						elif p1 in edge3p:
							SelectedEdge = 3
						else:
							print("ControlPoly4: 'GridEdge' mode. The selected grid line is not along an edge, the input cannot be interpreted")
							return

					else:
						print('GridEdge mode failed to identify either a vertex or an edge in the selection')
						return
					# print("SelectedEdge index = ", SelectedEdge)
		elif len(sel)==2:
			# two sketches
			if sel[0].Object.TypeId == 'Sketcher::SketchObject' and sel[1].Object.TypeId == 'Sketcher::SketchObject':
				mode='2N'
			# two ControlPoly4s
			elif isControlPoly4(sel[0].Object) ==  True and isControlPoly4(sel[1].Object) ==  True:
				mode='2X4P'
			# last chance, two PointonCurves
			else:
				try:
					if sel[0].Object.object_type == 'Point_onCurve' and sel[1].Object.object_type == 'Point_onCurve':
						mode = '2P'
				except:
					pass
		else:
			print ('Selection not recognized, check tooltip')
			return
		
		print ('ControlPoly4 input selection interpreted as ', mode)
		if mode=='3L':
			sketch=Gui.Selection.getSelection()[0]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly4_3L_000")
			AN.ControlPoly4_3L(a,sketch)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode=='FirstElement':
			sketch=Gui.Selection.getSelection()[0]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly4_FirstElement_000")
			AN.ControlPoly4_FirstElement(a,sketch)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode=='GridEdge':
			grid = Gui.Selection.getSelection()[0]
			edge = SelectedEdge
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly4_GridEdge_000")
			AN.ControlPoly4_GridEdge(a,grid, edge)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()
			
		if mode=='2N':
			sketch0=Gui.Selection.getSelection()[0]
			sketch1=Gui.Selection.getSelection()[1]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly4_2N_000")
			AN.ControlPoly4_2N(a,sketch0,sketch1)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode=='2X4P':
			poly4_0=Gui.Selection.getSelection()[0]
			poly4_1=Gui.Selection.getSelection()[1]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly4_2X4P_000")
			AN.ControlPoly4_2X4P(a,poly4_0,poly4_1)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()

		if mode=='2P':
			Point0=Gui.Selection.getSelection()[0]
			Point1=Gui.Selection.getSelection()[1]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlPoly4_2P_000")
			AN.ControlPoly4_2P(a,Point0,Point1)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.00,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.00,1.00)
			FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		return {'Pixmap':  iconPath,
	  			'MenuText': 'ControlPoly4',
				'ToolTip': tooltip}

Gui.addCommand('ControlPoly4', ControlPoly4())
