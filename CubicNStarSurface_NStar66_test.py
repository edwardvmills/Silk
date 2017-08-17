from __future__ import division # allows floating point division from integers
import Part
import FreeCAD
from FreeCAD import Base
from FreeCAD import Gui
import ArachNURBS as AN
				
class CubicNStarSurface_NStar66:
	def __init__(self, obj , NStarGrid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicNStarSurface_NStar66 Init\n")
		obj.addProperty("App::PropertyLink","NStarGrid","CubicNStarSurface_NStar66","control grid star").NStarGrid = NStarGrid
		obj.addProperty("Part::PropertyGeometryList","NSurf","CubicNStarSurface_NStar66","N Cubic Surfaces").NSurf
		obj.Proxy = self
		
	def HomogeneousGrids(self, fp, N):
		
		HGrids = [0] * N
		for i in range(N):
			FreeCAD.Console.PrintMessage("\nsetting homogeneous grid\n")
			FreeCAD.Console.PrintMessage(i)
			# this linked grid attribute cycling seems to work
			Poles_i = getattr(fp.NStarGrid, 'Poles_%d' % i)
			Weights_i = getattr(fp.NStarGrid, 'Weights_%d' % i)
			FreeCAD.Console.PrintMessage("\np00\n")
			FreeCAD.Console.PrintMessage(Poles_i[0])
			HGrid_i = [0] *36
			for j in range(36):
				HGrid_i[j] = [Poles_i[j], Weights_i[j]]
			HGrids[i] = HGrid_i	
		return HGrids	
		
	def makeNSurf(self, fp, HomogeneousGrids, N):
		NSurf = [0] * N
		for i in range(N):
			NSurf[i] = AN.NURBS_Cubic_66_surf(HomogeneousGrids[i])
		return NSurf

	def execute(self,fp):
		
		HGrids = self.HomogeneousGrids(fp, fp.NStarGrid.N)
		FreeCAD.Console.PrintMessage("\nHGrids[0][0]\n")
		FreeCAD.Console.PrintMessage(HGrids[0][0])
		FreeCAD.Console.PrintMessage("\nHGrids[1][0]\n")
		FreeCAD.Console.PrintMessage(HGrids[1][0])
		FreeCAD.Console.PrintMessage("\nHGrids[2][0]\n")
		FreeCAD.Console.PrintMessage(HGrids[2][0])
		
		fp.NSurf = self.makeNSurf(fp, HGrids, fp.NStarGrid.N)

		fp.Shape = Part.Shape(fp.NSurf)
		

sel=Gui.Selection.getSelection()
Sub_0=Gui.Selection.getSelection()[0] 
#Sub_1=Gui.Selection.getSelection()[1]
#Sub_2=Gui.Selection.getSelection()[2]

NStarGrid = Sub_0


a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","CubicNStarSurface_NStar66")
CubicNStarSurface_NStar66(a,NStarGrid)
a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
a.ViewObject.LineWidth = 1.00
a.ViewObject.LineColor = (1.00,0.67,0.00)
a.ViewObject.PointSize = 2.00
a.ViewObject.PointColor = (1.00,1.00,0.00)		
FreeCAD.ActiveDocument.recompute()


	
