from __future__ import division # allows floating point division from integers
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
		''' the poles and weights will be defined in specific subclasses where N = 3, 4, 5, 6, and maybe 7.
		the list of poles and weights must be accessible outside the object through the FreeCAD python feature attribute interface:
		the poles and weights must be one of the predefined attribute types. if we choose PropertyVectorList and PropertyFloatList,
		we must then use 'variable' variable names to set N of them. This is not good practice. The other option is using a Matrix. 
		The matrix is probably yhe way to go...later.

		I know how to read and write the entire pole table with 'variable' variable names, but i don't know how to read a single object and then write a single object.

		As of now, there is a functioning N=3 version. The N=3 object passes its attributes and the value N to the functions of the base class. 
		Each function in the base class uses 'variable' variable names to load the entire Poles table of the Subgrids it is working on, 
		do a few simple things, and then overwrite the entire table again for each Subgrid involved! 

		This is pretty horrible way to handle data access across a dataset of unknown size. It is especially gruesome in the last function,
		where i read 1 value from each table, average them all, and assign this value to one address in each table. it takes 4 for loops!

		At least all my functions are defined only once, which is more critical right now for debugging

		loop 1 runs N X 2 pole tables
		loop 2 runs N X 1 pole tables
		loop 3 runs N X 2 pole tables
		loop 4 runs N X 3 pole tables
		loop 5 runs N X 2 pole tables
		Loop 6 runs 1 X N pole tables

		11 X N pole tables are read and written, where in fact the table actually needs to be read about twice, and written LESS than once.
		'''

	def getL1Scale(self, p0, p1, p2):
		L1_scale = (((p1 - p0).normalize()).dot(p2-p1)) / ((p1 - p0).Length)
		return L1_scale

	def StarRow2_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# apply indices and get Poles lists from instance.
		Sub_0 = getattr(fp, 'Poles_%d' % Sub_0_i)
		Sub_1 = getattr(fp, 'Poles_%d' % Sub_1_i)

		#do the thing
		L1Scale_Sub0_v = self.getL1Scale(Sub_0[2], Sub_0[8], Sub_0[14])
		L1Scale_Sub1_u = self.getL1Scale(Sub_1[12], Sub_1[13], Sub_1[14])
		L1Scale_Mid = 0.5 * (L1Scale_Sub0_v + L1Scale_Sub1_u)
		Mid_p2 = Sub_0[17] + L1Scale_Mid * (Sub_0[11]-Sub_0[5])

		Sub_0[17] = Mid_p2
		Sub_1[32] = Mid_p2
		Sub_0[16] = Sub_0[16] + L1Scale_Mid * (Sub_0[10]-Sub_0[4])
		Sub_1[26] = Sub_1[26] + L1Scale_Mid * (Sub_1[25]-Sub_1[24])

		L1Scale_15 = 0.5 * (L1Scale_Sub0_v + L1Scale_Mid)
		L1Scale_20 = 0.5 * (L1Scale_Sub1_u + L1Scale_Mid)
		Sub_0[15] = Sub_0[15] + L1Scale_15 * (Sub_0[9]-Sub_0[3])
		Sub_1[20] = Sub_1[20] + L1Scale_20 * (Sub_1[19]-Sub_1[18])

		# update instance properties using setattr() and string manipulation to set index
		setattr(fp, 'Poles_%d' % Sub_0_i, Sub_0)
		setattr(fp, 'Poles_%d' % Sub_1_i, Sub_1)

		Legs_Row2 = []
		Legs_Row2_i = [[[9,15],[10,16],[11,17],[14,15],[15,16],[16,17]],[[14,20],[19,20],[20,26],[25,26],[26,32]]]
		for i in Legs_Row2_i[0]:
			Legs_Row2.append(Part.LineSegment(Sub_0[i[0]],Sub_0[i[1]]))

		for i in Legs_Row2_i[1]:
			Legs_Row2.append(Part.LineSegment(Sub_1[i[0]],Sub_1[i[1]]))

		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row2 # this explicit assignment works. it modifies the subclass instance property from within the parent class function.
		return 0

	def StarRow2_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow2_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow2_2Sub(fp, N-1, 0)
		return 0

	def StarDiag3_Sub(self, fp, Sub_i):
		# apply index and get Poles list from instance.
		Sub = getattr(fp, 'Poles_%d' % Sub_i)

		#do the thing
		Sub[21] = Sub[20]+Sub[15]-Sub[14]

		# update instance properties using setattr() and string manipulation to set index
		setattr(fp, 'Poles_%d' % Sub_i, Sub)

		# control leg visualization
		Legs_Diag3 = [0,0]
		Legs_Diag3[0] = Part.LineSegment(Sub[15],Sub[21])
		Legs_Diag3[1] = Part.LineSegment(Sub[20],Sub[21])

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Diag3
		return 0

	def StarDiag3_SubLoop(self, fp, N):
		# loop from first element to last. no pairs, no loop back required.
		for i in range(N):
			self.StarDiag3_Sub(fp, i)
		return 0

	def StarRow3_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# apply indices and get Poles lists from instance.
		Sub_0 = getattr(fp, 'Poles_%d' % Sub_0_i)
		Sub_1 = getattr(fp, 'Poles_%d' % Sub_1_i)

		# do the thing
		# prepare seam point
		Mid_p2 = Sub_0[17] + 0.5 * (Sub_0[21]-Sub_0[15]+Sub_1[21]-Sub_1[20])

		# apply seam point locally
		Sub_0[23] = Mid_p2
		Sub_1[33] = Mid_p2

		# average to seam neighbor locally
		Sub_0[22] = Sub_0[16] + 0.5 * (Sub_0[21]-Sub_0[15]+Sub_0[23]-Sub_0[17])
		Sub_1[27] = Sub_1[26] + 0.5 * (Sub_1[21]-Sub_1[20]+Sub_1[33]-Sub_1[32])

		# update instance properties using setattr() and string manipulation to set index
		setattr(fp, 'Poles_%d' % Sub_0_i, Sub_0)
		setattr(fp, 'Poles_%d' % Sub_1_i, Sub_1)

		Legs_Row3 = []
		Legs_Row3_i = [[[16,22],[17,23],[21,22],[22,23]],[[21,27],[26,27],[27,33]]]
		for i in Legs_Row3_i[0]:
			Legs_Row3.append(Part.LineSegment(Sub_0[i[0]],Sub_0[i[1]]))

		for i in Legs_Row3_i[1]:
			Legs_Row3.append(Part.LineSegment(Sub_1[i[0]],Sub_1[i[1]]))

		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row3 # this explicit assignment works. it modifies the subclass instance property from within the parent class function.
		return 0

	def StarRow3_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow3_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow3_2Sub(fp, N-1, 0)
		return 0

	def StarDiag4_3Sub(self, fp, Sub_prev_i, Sub_i, Sub_next_i):
		# apply index and get Poles list from instance.
		Sub_prev = getattr(fp, 'Poles_%d' % Sub_prev_i)
		Sub = getattr(fp, 'Poles_%d' % Sub_i)
		Sub_next = getattr(fp, 'Poles_%d' % Sub_next_i)

		# do the thing
		# parallelogram diagonal 
		Sub_28_raw = Sub[27] + (Sub[22]-Sub[21])
		# scaled down 75% to spread out center
		Sub_28_scaled = Sub[21] + 0.75 * (Sub_28_raw - Sub[21])

		Plane_prev = Part.Plane(Sub[33],Sub[23],Sub_prev[33])
		Plane_next = Part.Plane(Sub[33],Sub[23],Sub_next[23])

		Sub_28_prev_param = Plane_prev.parameter(Sub_28_scaled)
		Sub_28_prev_proj = Plane_prev.value(Sub_28_prev_param[0],Sub_28_prev_param[1])

		Sub_28_next_param = Plane_next.parameter(Sub_28_scaled)
		Sub_28_next_proj = Plane_next.value(Sub_28_next_param[0],Sub_28_next_param[1])

		Sub[28] = 0.5 * Sub_28_scaled + 0.25 * (Sub_28_prev_proj + Sub_28_next_proj)

		# update instance properties using setattr() and string manipulation to set index
		setattr(fp, 'Poles_%d' % Sub_i, Sub)

		# control leg visualization
		Legs_Diag4 = [0,0]
		Legs_Diag4[0] = Part.LineSegment(Sub[22],Sub[28])
		Legs_Diag4[1] = Part.LineSegment(Sub[27],Sub[28])

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Diag4
		return 0

	def StarDiag4_SubLoop(self, fp, N):
		# loop in triples from first element to second to last
		for i in range(N-2):
			self.StarDiag4_3Sub(fp, i, i+1, i+2)
		# close sequence by looping back two triples spanning first and last elements
		self.StarDiag4_3Sub(fp, N-2, N-1, 0)
		self.StarDiag4_3Sub(fp, N-1, 0, 1)
		return 0

	def StarRow4_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# apply indices and get Poles lists from instance.
		Sub_0 = getattr(fp, 'Poles_%d' % Sub_0_i)
		Sub_1 = getattr(fp, 'Poles_%d' % Sub_1_i)

		#do the thing

		# pull up the seam at row 4
		Mid_p4 = 0.5 * (Sub_0[28] + Sub_1[28])
		Sub_0[29] = Mid_p4
		Sub_1[34] = Mid_p4

		# update instance properties using setattr() and string manipulation to set index
		setattr(fp, 'Poles_%d' % Sub_0_i, Sub_0)
		setattr(fp, 'Poles_%d' % Sub_1_i, Sub_1)

		# control leg visualization
		Legs_Row4 = [0,0,0]
		Legs_Row4[0] = Part.LineSegment(Sub_0[23],Sub_0[29])
		Legs_Row4[1] = Part.LineSegment(Sub_0[28],Sub_0[29])
		Legs_Row4[2] = Part.LineSegment(Sub_1[28],Sub_1[34])

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row4
		return 0

	def StarRow4_SubLoop(self, fp, N): # last good test point
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow4_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow4_2Sub(fp, N-1, 0)
		return 0

	def StarCenter(self, fp, N):
		# we are going to average all poles [29] around the loop to define the center
		# collect instance properties using getattr() and string manipulation to set index
		Poles = [0]*N
		for i in range(N):
			Poles[i] = getattr(fp, 'Poles_%d' % i)

		# sum all poles [29]
		Vector_total = Base.Vector(0,0,0)
		for i in range(N):
			Vector_total = Vector_total + Poles[i][29]

		StarCenter = (1.0 / N) * Vector_total 

		# Apply center point to all Poles lists
		for i in range(N):
			Poles[i][35] = StarCenter

		# control leg visualization
		Legs_Row5 = []
		for i in range(N):
			Legs_Row5.append(Part.LineSegment(Poles[i][29],Poles[i][35]))

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row5

		# update instance properties using setattr() and string manipulation to set index
		for i in range(N):
			setattr(fp, 'Poles_%d' % i, Poles[i])

		return 0


# ***********************************************

class ControlGrid3Star66_3Sub(ControlGridNStar66_NSub):
	def __init__(self, fp , SubList):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid3Star66_3Sub class Init\n")
		ControlGridNStar66_NSub.__init__(self, fp, SubList)
		# create the additional properties for N =3
		fp.addProperty("App::PropertyInteger","N","ControlGrid3Star66_3Sub","N").N=3
		fp.setEditorMode("N", 2) 
		fp.addProperty("App::PropertyVectorList","Poles_0","ControlGrid3Star66_3Sub","Poles_0").Poles_0
		fp.addProperty("App::PropertyVectorList","Poles_1","ControlGrid3Star66_3Sub","Poles_1").Poles_1
		fp.addProperty("App::PropertyVectorList","Poles_2","ControlGrid3Star66_3Sub","Poles_2").Poles_2
		fp.addProperty("App::PropertyFloatList","Weights_0","ControlGrid3Star66_3Sub","Weights_0").Weights_0
		fp.addProperty("App::PropertyFloatList","Weights_1","ControlGrid3Star66_3Sub","Weights_0").Weights_1
		fp.addProperty("App::PropertyFloatList","Weights_2","ControlGrid3Star66_3Sub","Weights_2").Weights_2


	def execute(self, fp):
		N=3
		# refresh properties back to linked SubGrids every time the Star gets recomputed
		fp.Poles_0 = SubList[0].Poles
		fp.Weights_0 = SubList[0].Weights
		fp.Poles_1 = SubList[1].Poles
		fp.Weights_1 = SubList[1].Weights
		fp.Poles_2 = SubList[2].Poles
		fp.Weights_2 = SubList[2].Weights
		fp.Legs = []
		self.StarRow2_SubLoop(fp, fp.N)
		self.StarDiag3_SubLoop(fp, fp.N)
		self.StarRow3_SubLoop(fp, fp.N)
		self.StarDiag4_SubLoop(fp, fp.N)
		self.StarRow4_SubLoop(fp, fp.N)
		self.StarCenter(fp, fp.N)

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



