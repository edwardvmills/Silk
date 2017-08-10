import Part
import FreeCAD
from FreeCAD import Base
from FreeCAD import Gui

class ControlGridNStar66_NSub:		
	def __init__(self, fp , SubList):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGridNStar66_NSub class Init\n")
		fp.addProperty("App::PropertyLinkList","SubList","ControlGridNStar66_NSub","Reference Sub Grids").SubList = SubList
		fp.addProperty("Part::PropertyGeometryList","Legs","ControlGridNStar66_NSub","control segments").Legs
		fp.Proxy = self

	# lay out the individual functions common to all stars here

	def starfunctiontest(self,Sub_0, Sub_1):
		line=Part.LineSegment(Sub_0.Poles[0], Sub_1.Poles[0])
		return line
		
	
		
	''''
	def execute(self, fp):
		# this function CAN be omitted entirely
		# should i write the sequence of function loops common to all stars here?
		# or do nothing here, and run the main loop in the specific subclass?
		
	'''

class ControlGrid3Star66_3Sub(ControlGridNStar66_NSub):		
	def __init__(self, fp , SubList):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid3Star66_3Sub class Init\n")
		ControlGridNStar66_NSub.__init__(self, fp, SubList)
		# create the additional properties for N =3
		fp.addProperty("App::PropertyVectorList","Poles_0","ControlGrid3Star66_3Sub","Poles_0").Poles_0
		fp.addProperty("App::PropertyVectorList","Poles_1","ControlGrid3Star66_3Sub","Poles_1").Poles_1
		fp.addProperty("App::PropertyVectorList","Poles_2","ControlGrid3Star66_3Sub","Poles_2").Poles_2
		fp.addProperty("App::PropertyFloatList","Weights_0","ControlGrid3Star66_3Sub","Weights_0").Weights_0
		fp.addProperty("App::PropertyFloatList","Weights_1","ControlGrid3Star66_3Sub","Weights_0").Weights_1
		fp.addProperty("App::PropertyFloatList","Weights_2","ControlGrid3Star66_3Sub","Weights_2").Weights_2

	def execute(self, fp):
		
		FreeCAD.Console.PrintMessage("\n now in the body of ControlGrid3Star66_3Sub.execute()\n")
		
		#write a loop to test the function from the base class
			
		N=3
		
		Legs = [0] * N
		
		# loop from first element to last
		for i in range(N-1):
			Legs[i] = self.starfunctiontest(fp.SubList[i],fp.SubList[i+1])
		
		# close sequence by looping back from last to first element
		Legs[N-1] = self.starfunctiontest(fp.SubList[N-1],fp.SubList[0])	
			
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)	
		

sel=Gui.Selection.getSelection()
Sub_0=Gui.Selection.getSelection()[0] 
Sub_1=Gui.Selection.getSelection()[1]
Sub_2=Gui.Selection.getSelection()[2]

SubList = [Sub_0, Sub_1, Sub_2]


a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid3Star66_3Sub")
ControlGrid3Star66_3Sub(a,SubList)
a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
a.ViewObject.LineWidth = 1.00
a.ViewObject.LineColor = (1.00,0.67,0.00)
a.ViewObject.PointSize = 2.00
a.ViewObject.PointColor = (1.00,1.00,0.00)		
FreeCAD.ActiveDocument.recompute()


	
