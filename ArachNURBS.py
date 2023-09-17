#    ArachNURBS
#    (c) Edward Mills 2016-2018
#    edwardvmills@gmail.com
#    
#    ArachNURBS is a library of functions and classes to manipulate NURBS
#    curves, surfaces, and the associated control polygons and grids.
#    ArachNURBS is built on top FreeCAD's standard NURBS functions.
#
#
#    This program is free software: you can redistribute it and/or modify
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
#

from __future__ import division # allows floating point division from integers
import Part
import FreeCAD
from FreeCAD import Base
from FreeCAD import Gui
import math
import numpy as np

# test message to verify load and reloads
print ("importing ArachNURBS")


#
## Basic NURBS rules and terms
## Order >= 2
## Order:  2 = line, 3 = quadratic, 4 = cubic ...
## Degree = Order - 1
## Order = Degree + 1
## nPoles >= Order
## nPoles >= Degree + 1
## nKnots = nPoles + Order
## nKnots = nPoles + degree + 1
## knot vector strictly ascending
## Pinned knot vector: k=Order, first k knots are equal, last k knots are equal

####
#### SECTION 1: DIRECT FUNCTIONS - NO PARAMETRIC LINKING BETWEEN OBJECTS
#### SECTION 2: PYTHON FEATURE CLASSES - PARAMETRIC LINKING BETWEEN OBJECTS (start around line 364)
####

### SECTION 1: DIRECT FUNCTIONS - NO PARAMETRIC LINKING BETWEEN OBJECTS
## Bottom up view:
## poles = 3D points with weights, as [[x,y,z],w], or [x,y,z] (these are leftovers waiting to receive weights).
## These are the basic input data for all that follows.
## They are obtained from the FreeCAD functions .getPoles() and .getWeights()
## NOTE: Poles in FreeCAD, such as returned by .getPoles(), refer only to xyz coordinates of a control point,
## THROUGHOUT the following functions, pole means [[x,y,z],w]
## lists are probably not efficient, but until FreeCAD has fully integrated homogeneous coordinates
## for all NURBS functions, this is easier for me :)
## Right now, the computation of these scripts is ridiculously fast compared
## to the time taken to generate the surfaces using the FreeCAD Part.BSplineSurface() function

## direct functions actually used in the Classes / available through the Silk FreeCAD workbench:

def equalVectors(vector0,vector1,tol):	# 3D point equality test
	if (vector1-vector0).Length <= tol:
		return 1
	elif (vector1-vector0).Length > tol:
		return 0

def int_2l(la,lb):
	pa1=la.StartPoint
	pa2=la.EndPoint
	pb1=lb.StartPoint
	pb2=lb.EndPoint
	va=pa2-pa1
	vb=pb2-pb1
	lab=Part.Line(pa1,pb1)
	ab=lab.length()
	van=va.normalize()
	vbn=vb.normalize()
	pa3=pa1+van.multiply(10*ab)
	pb3=pb1+vbn.multiply(10*ab)
	lax=Part.Line(pa1,pa3)
	lbx=Part.Line(pb1,pb3)
	pln=Part.Plane(pa1,pb1,pa2)
	int_0_1= lax.intersect2d(lbx,pln) # works down to 5.73 degrees between the lines
	if int_0_1==[]:
		return 'intersection failed'
	int_abs_coord=pln.value(int_0_1[0][0],int_0_1[0][1])
	return int_abs_coord

def lineOrPoint(p0,p1):
	if equalVectors(p0, p1, .000001):
		return [0]
	else:
		return [1, Part.LineSegment(p0, p1)]

def drawGrid(poles, columns):
	nbPoles = len(poles)
	# print ('nbPoles = ', nbPoles)
	# print ('columns = ', columns)
	rows = int(len(poles) / columns)
	# print ('rows = ', rows)
	#legs_total = 2 * rows * columns - rows - columns
	#print ('legs_total = ', legs_total)
	#legs = [0] * legs_total
	legs = []

	leg_index = 0
	# loop all rows
	for i in range(0,rows):
		# loop over a row
		for j in range(0, columns-1):
			# print ('in row ', i)
			start = i*columns + j
			# print ('start = ', start)
			end = i*columns + j + 1
			# print ('end = ', end)
			leg = lineOrPoint(poles[start], poles[end])
			if (leg[0] == 1):
				legs.append(leg[1])

	# loop all columns
	for i in range(0,columns):
		# loop over a column
		for j in range(0, rows-1):
			# print ('in column ', i)
			start = j*columns + i
			# print ('start = ', start)
			end = j*columns + columns + i
			# print ('end = ', end)
			leg = lineOrPoint(poles[start], poles[end])
			if (leg[0] == 1):
				legs.append(leg[1])

	return legs

def orient_a_to_b(polesa,polesb):   # polesa and polesb are lists of poles that share one endpoint.
                                    # if needed, this function reorders a so that a.end = b.start or b.end. b is never modified

	if equalVectors(polesa[-1],polesb[0],0.000001):     # last point of first curve is first point of second curve
		# curve 1 is oriented properly
		return polesa
	elif equalVectors(polesa[-1],polesb[-1],0.000001):  # last point of first curve is last point of second curve
		# curve 1 is oriented properly
		return polesa
	elif equalVectors(polesa[0],polesb[0],0.000001):    # first point of first curve is first point of second curve
		# curve 1 is reversed
		return polesa[::-1]
	elif equalVectors(polesa[0],polesb[-1],0.000001):   # first point of first curve is last point of second curve
		# curve 1 is reversed
		return polesa[::-1]
	else:
		print ('curves do not share endpoints')
		return 0

def Cubic_Bezier_ddu(pole0, pole1):          # cubic derivative at curve start (pole1) based on first 
                                             # two poles (no curve required). Weights not included yet
	P0=Base.Vector(pole0)
	P1=Base.Vector(pole1)
	Cubic_Bezier_ddu = (P1 - P0)*3
	return Cubic_Bezier_ddu

def Cubic_6P_ddu(pole0, pole1):              # cubic derivative at curve start (pole1) based on first 
                                             # two poles (no curve required). Weights not included yet.
	P0=Base.Vector(pole0)
	P1=Base.Vector(pole1)
	Cubic_6P_ddu = (P1 - P0)*9
	return Cubic_6P_ddu

def Cubic_Bezier_d2du2(pole0, pole1, pole2): # cubic second derivative at curve start (pole1) based on first 
                                             # three poles (no curve required). Weights not included yet.
	P0=Base.Vector(pole0)
	P1=Base.Vector(pole1)
	P2=Base.Vector(pole2)
	Cubic_Bezier_d2du2 = (P0- P1*2 + P2)*6
	return Cubic_Bezier_d2du2

def Cubic_6P_d2du2(pole0, pole1, pole2):     # cubic second derivative at curve start (pole1) based on first
                                             # three poles (no curve required). Weights not included yet.
	P0=Base.Vector(pole0)
	P1=Base.Vector(pole1)
	P2=Base.Vector(pole2)
	Cubic_6P_d2du2 = (P0*2- P1*3 + P2)*27
	return Cubic_6P_d2du2

def Cubic_Bezier_curvature(pole0, pole1, pole2): # curvature at curve start (pole1) based on the first three 
                                                 # poles (no curve required). Weights not included yet.
	ddu = Cubic_Bezier_ddu(pole0, pole1)
	d2du2 = Cubic_Bezier_d2du2(pole0, pole1, pole2)
	Cubic_Bezier_curvature = ddu.cross(d2du2).Length/ddu.Length.__pow__(3)
	return Cubic_Bezier_curvature

def Cubic_6P_curvature(pole0, pole1, pole2):     # curvature at curve start (pole1) based on the first three
                                                 # poles (no curve required). Weights not included yet
	ddu = Cubic_6P_ddu(pole0, pole1)
	d2du2 = Cubic_6P_d2du2(pole0, pole1, pole2)
	Cubic_6P_curvature = ddu.cross(d2du2).Length/ddu.Length.__pow__(3)
	return Cubic_6P_curvature

def Bezier_Cubic_curve(poles):      # pinned cubic rational B spline, 4 control points
                                    # Part.BSplineCurve(), cubic bezier form
#draws a degree 3 rational bspline from first to last point,
# second and third act as tangents
# poles is a list: [[[x,y,z],w],[[x,y,z],w],[[x,y,z],w],[[x,y,z],w]]
## nKnot = 4 + 3 +1 = 8
## Order = 3 + 1 = 4
	degree=3
	nPoles=4
	knot=[0,0,0,0,1,1,1,1]
	bs=Part.BSplineCurve()
	bs.increaseDegree(degree)
	id=1
	for i in range(0,len(knot)):    #-1):
		bs.insertKnot(knot[i],id,0.0000001)
	i=0
	for ii in range(0,nPoles):
		bs.setPole(ii+1,poles[i][0],poles[i][1])
		i=i+1;
	return bs

def Bezier_Bicubic_surf(grid_44):   # given a 4 x 4 control grid, build the bicubic bezier
                                    # surface from a Part.BSplineSurface() in Bicubic Bezier form
	# len(knot_u) := nNodes_u + degree_u + 1
	# len(knot_v) := nNodes_v + degree_v + 1
	degree_u=3
	degree_v=3
	nNodes_u=4
	nNodes_v=4
	knot_u=[0,0,0,0,1,1,1,1]
	knot_v=[0,0,0,0,1,1,1,1]
	Bezier_Bicubic_surf=Part.BSplineSurface()
	Bezier_Bicubic_surf.increaseDegree(degree_u,degree_v)
	id=1
	for i in range(0,len(knot_u)):    #-1):
		Bezier_Bicubic_surf.insertUKnot(knot_u[i],id,0.0000001)
	id=1
	for i in range(0,len(knot_v)):    #-1):
		Bezier_Bicubic_surf.insertVKnot(knot_v[i],id,0.0000001)
	i=0
	for jj in range(0,nNodes_v):
		for ii in range(0,nNodes_u):
			Bezier_Bicubic_surf.setPole(ii+1,jj+1,grid_44[i][0], grid_44[i][1]);
			i=i+1;
	return Bezier_Bicubic_surf

def NURBS_Cubic_6P_curve(poles):    # pinned cubic rational Bspline, 6 control points
                                    # Part.BSplineCurve(), just enough to have independent endpoint curvature
# draws a degree 3 rational bspline from first to last point,
# second and third act as tangents
# poles is a list: [[[x,y,z],w],[[x,y,z],w],[[x,y,z],w],[[x,y,z],w],[[x,y,z],w],[[x,y,z],w]]
## nKnot = 6 + 3 +1 = 10
## Order = 3 + 1 = 4
	degree=3
	nPoles=6
	knot=[0,0,0,0,1.0/3.0,2.0/3.0,1,1,1,1]
	bs=Part.BSplineCurve()
	bs.increaseDegree(degree)
	id=1
	for i in range(0,len(knot)):    #-1):
		bs.insertKnot(knot[i],id,0.0000001)
	i=0
	for ii in range(0,nPoles):
		bs.setPole(ii+1,poles[i][0],poles[i][1])
		i=i+1;
	return bs

def NURBS_Cubic_66_surf(grid_66):	# given a 6 x 6 control grid, build the cubic
									# NURBS surface from a Part.BSplineSurface().
	# len(knot_u) := nNodes_u + degree_u + 1
	# len(knot_v) := nNodes_v + degree_v + 1
	degree_u=3
	degree_v=3
	nNodes_u=6
	nNodes_v=6
	knot_u=[0,0,0,0,1.0/3.0,2.0/3.0,1,1,1,1]
	knot_v=[0,0,0,0,1.0/3.0,2.0/3.0,1,1,1,1]
	NURBS_Cubic_66_surf=Part.BSplineSurface()
	NURBS_Cubic_66_surf.increaseDegree(degree_u,degree_v)
	id=1
	for i in range(0,len(knot_u)):    #-1):
		NURBS_Cubic_66_surf.insertUKnot(knot_u[i],id,0.0000001)
	id=1
	for i in range(0,len(knot_v)):    #-1):
		NURBS_Cubic_66_surf.insertVKnot(knot_v[i],id,0.0000001)
	i=0
	for jj in range(0,nNodes_v):
		for ii in range(0,nNodes_u):
			NURBS_Cubic_66_surf.setPole(ii+1,jj+1,grid_66[i][0],grid_66[i][1]);
			i=i+1;
	return  NURBS_Cubic_66_surf

def NURBS_Cubic_64_surf(grid_64):	# given a 6 x 4 control grid, build the cubic
									# NURBS surface from a Part.BSplineSurface().
	# len(knot_u) := nNodes_u + degree_u + 1
	# len(knot_v) := nNodes_v + degree_v + 1
	degree_u=3
	degree_v=3
	nNodes_u=6
	nNodes_v=4
	knot_u=[0,0,0,0,1.0/3.0,2.0/3.0,1,1,1,1]
	knot_v=[0,0,0,0,1,1,1,1]
	NURBS_Cubic_64_surf=Part.BSplineSurface()
	NURBS_Cubic_64_surf.increaseDegree(degree_u,degree_v)
	id=1
	for i in range(0,len(knot_u)):    #-1):
		NURBS_Cubic_64_surf.insertUKnot(knot_u[i],id,0.0000001)
	id=1
	for i in range(0,len(knot_v)):    #-1):
		NURBS_Cubic_64_surf.insertVKnot(knot_v[i],id,0.0000001)
	i=0
	for jj in range(0,nNodes_v):
		for ii in range(0,nNodes_u):
			NURBS_Cubic_64_surf.setPole(ii+1,jj+1,grid_64[i][0],grid_64[i][1]);
			i=i+1;
	return  NURBS_Cubic_64_surf

def blend_poly_2x4_1x6(poles_0,weights_0, poles_1, weights_1, scale_0, scale_1, scale_2, scale_3):	
	# blend two cubic bezier into a 6 point cubic NURBS. this function assumes poles_0 flow into poles_1 without checking.
	#print ("weights_0 in blend_poly_2x4_1x6")
	#print (weights_0)
	WeightedPoles_0=[[poles_0[0],weights_0[0]], [poles_0[1],weights_0[1]], [poles_0[2],weights_0[2]], [poles_0[3],weights_0[3]]]
	CubicCurve4_0= Bezier_Cubic_curve(WeightedPoles_0) 
	CubicCurve6_0=CubicCurve4_0
	CubicCurve6_0.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
	CubicCurve6_0.insertKnot(2.0/3.0)

	#print ("weights_1 in blend_poly_2x4_1x6")
	#print (weights_1)
	WeightedPoles_1=[[poles_1[0],weights_1[0]], [poles_1[1],weights_1[1]], [poles_1[2],weights_1[2]], [poles_1[3],weights_1[3]]]
	CubicCurve4_1= Bezier_Cubic_curve(WeightedPoles_1) # checked good BSplineSurface object.
	CubicCurve6_1=CubicCurve4_1
	CubicCurve6_1.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
	CubicCurve6_1.insertKnot(2.0/3.0)

	poles_6_0=CubicCurve6_0.getPoles()
	weights_6_0=CubicCurve6_0.getWeights()

	# if the weights are too similar to each other, the knot insertion can convert them all to 1
	# this is bad for blends with arc, ellipses, etc.
	#print ("weights_6_0 in blend_poly_2x4_1x6")
	#print (weights_6_0)

	poles_6_1=CubicCurve6_1.getPoles()
	weights_6_1=CubicCurve6_1.getWeights()
	# if the weights are too similar to each other, the knot insertion can convert them all to 1
	# this is bad for blends with arcs, ellipses, etc.
	#print ("weights_6_1 in blend_poly_2x4_1x6")
	#print (weights_6_1)

	# check original weights....set == at 1%? 
	# this code is behaving very strangely.
	# it failed to reset on a strict comparison (< .001), but resets correctly on a loose comparison.
	# the numbers under comparison were equal to 8 or more decimals???
	if (((weights_0[0]-weights_0[1] / weights_0[0]).__pow__(2) < .1) and 
     	((weights_0[0]-weights_0[2] / weights_0[0]).__pow__(2) < .1) and 
		((weights_0[0]-weights_0[3] / weights_0[0]).__pow__(2) < .1)):
		a = weights_0[0]
		#print ("a ", a)
		weights_6_0 = [a,a,a,a,a,a]
		print("reseting weights_0")

	if (((weights_1[0]-weights_1[1] / weights_1[0]).__pow__(2) < .1) and 
     	((weights_1[0]-weights_1[2] / weights_1[0]).__pow__(2) < .1) and 
		((weights_1[0]-weights_1[3] / weights_1[0]).__pow__(2) < .1)):
		b = weights_1[0]
		#print ("b ", b)
		weights_6_1 = [b,b,b,b,b,b]
		print("reseting weights_1")
		


	p0=[poles_6_0[0],weights_6_0[0]]
	p1=[poles_6_0[1],weights_6_0[1]]
	p2=[poles_6_0[2],weights_6_0[2]]
	p3=[poles_6_1[3],weights_6_1[3]] ###
	p4=[poles_6_1[4],weights_6_1[4]] ###
	p5=[poles_6_1[5],weights_6_1[5]] ###
	corner='p01p10'
	
	
	### calculate curvature components

	## start point
	if (equalVectors(poles_6_0[0],poles_6_0[3], .000001) == 0):
		# the first curve is non degenerate
		l0 = p1[0]-p0[0]					# first control leg
		tan0=Base.Vector(l0)				# make clean copy
		tan0.normalize()					# unit tangent direction
		l1=Base.Vector(tan0)				# make clean copy
		l1.multiply(tan0.dot(p2[0]-p1[0])) 	# scalar projection of second control leg along unit tangent
		h1=(p2[0]-p1[0])-l1					# height of second control leg orthogonal to tangent
		### scale first control leg
		L0=Base.Vector(l0)					# make clean copy
		L0.multiply(scale_0)				# apply tangent scale
		p1_scl = [p0[0] + L0, p1[1]]		# reposition second control point
		### calc new heights for first inner control leg
		H1 = Base.Vector(h1)				# make clean copy
		H1.multiply(scale_0.__pow__(2))		# apply height scale
		# apply inner scale
		L1 = p1_scl[0] - p0[0]					# rescale to new tangent (scale_0 already applied)	
		L1 = L1.multiply(scale_1)				# apply inner tangent scale
		p2_scl = [p1_scl[0] + H1 + L1, p2[1]]	# reposition third control point
	else:
		# the first curve is degenerate
		# just pass the inputs forward
		p1_scl = [p1[0], p1[1]]
		p2_scl = [p2[0], p2[1]]

	## end point
	if (equalVectors(poles_6_0[0],poles_6_0[3], .000001) == 0):
		# the first curve is non degenerate
		l4 = p4[0]-p5[0]					# last control leg
		tan4=Base.Vector(l4)				# make clean copy
		tan4.normalize()					# unit tangent direction
		l3=Base.Vector(tan4)				# make clean copy
		l3.multiply(tan4.dot(p3[0]-p4[0])) 	# scalar projection of second to last control leg along unit tangent
		h3=(p3[0]-p4[0])-l3					# height of second control leg orthogonal to tangent
		### scale last control leg
		L4=Base.Vector(l4)					# make clean copy
		L4.multiply(scale_3)				# apply tangent scale
		p4_scl = [p5[0] + L4, p4[1]]		# reposition fifth control point
		### calc new heights for last inner control leg
		H3 = Base.Vector(h3)				# make clean copy
		H3.multiply(scale_3.__pow__(2))		# apply height scale
		# apply inner scale
		L3 = p4_scl[0] - p5[0]					# rescale to new tangent (scale_3 already applied)
		L3 = L3.multiply(scale_2)				# apply inner tangent scale
		p3_scl = [p4_scl[0] + H3 + L3, p3[1]]	# reposition third control point
	else:
		# the second curve is degenerate
		# just pass the inputs forward
		p3_scl = [p3[0], p3[1]]
		p4_scl = [p4[0], p4[1]]

	poles=[p0[0], p1_scl[0], p2_scl[0], p3_scl[0], p4_scl[0], p5[0]]
	# set the weights. No scaling at this point. No idea what happens if one of the input curve is an arc.
	# it would probably be a mess, since the curvature formulas above do not incorporate weights yet.
	# actually, it seems to work just fine, with both circle and ellipse arcs? curvature calc unaffected by weights?

	weights = [p0[1], p1[1], p2[1], p3[1], p4[1], p5[1]]

	WeightedPoles= [[poles[0],weights[0]], [poles[1],weights[1]], [poles[2],weights[2]], [poles[3],weights[3]], [poles[4],weights[4]], [poles[5],weights[5]]]

	current_test = NURBS_Cubic_6P_curve(WeightedPoles)
	# we need to return the scales so the function result is compatible with the
	#'Fair' and 'G3' version of the blend function, which modify these values
	# not a strict requirement
	return [poles,weights, scale_1, scale_2]

def Cubic_Bezier_dCds(pole0, pole1, pole2, pole3):  
	# calculate the rate of change of curvature per unit length (chord) 
     # at the beginning of a cubic bezier curve defined by the given poles
	# calculate start point curvature directly from poles
	C0 = Cubic_Bezier_curvature(pole0[0], pole1[0], pole2[0])
	if math.fabs(C0) < 1.0e-6:
		C0= 0.0
	# prepare cubic bezier object to subdivide
	Curve = Bezier_Cubic_curve([pole0, pole1, pole2, pole3])
	# setup refinement loop
	t_seg = 0.05	# initial segmentation value
	segment_degen = 'false'
	tol= 0.01
	error = 1.0
	loop_count = 0
	dCds_last = 'not_ready'
	while (error > tol  and loop_count < 100 and segment_degen != 'true'):
		Curve.segment(0,t_seg)
		Poles = Curve.getPoles()
		# check start curvature after segmentation
		C0_seg = Cubic_Bezier_curvature(Poles[0], Poles[1], Poles[2])
		if math.fabs(C0_seg) < 1.0e-6:
			C0_seg= 0.0 
		# if the start curvature changes dramatically after segmentation,
		# the new values are invalid. not a valid test when C0 = 0.0 to begin with
		if C0 != 0.0:
			if math.fabs((C0_seg - C0)/C0) > 5*tol:
				segment_degen = 'true'
				print ('segmentation has collapsed the curve')
				print ('C0', C0, 'C0_check', C0_seg)
				print ('Cubic_Bezier_dCds step ', loop_count)
		elif C0 == 0.0:
			if math.fabs((C0_seg - C0)) > .00001:
				segment_degen = 'true'
				print ('segmentation has collapsed the curve')
				print ('C0', C0, 'C0_check', C0_seg)
				print ('Cubic_Bezier_dCds step ', loop_count)
		
		# calculate curvature at the end of the current segment
		Cs =  Cubic_Bezier_curvature(Poles[3], Poles[2], Poles[1])
		
		#if the start curvature and first cut curvature are equal, then dCds is 0
		if math.fabs(C0-Cs) <= 1.0e-6 and loop_count == 0:
			return 0.0
				
		# calculate chord length of current segment
		S = Base.Vector(Poles[3])-Base.Vector(Poles[0])
		s = S.Length
		dCds_seg = (Cs-C0)/s
		#print ('step ', loop_count, '  dCds_seg ', dCds_seg)
		if loop_count > 1:
			error = math.fabs((dCds_seg - dCds_last)/dCds_last)
		if segment_degen != 'true':
			dCds_last = dCds_seg
		t_seg = t_seg * 0.9
		loop_count=loop_count + 1
	#print 'step ', loop_count, '  dCds_seg ', dCds_seg, '  error ', error
	if error > tol:
		#print 'no dCds found within ', tol, ' Cubic_Bezier_dCds'
		dCds = dCds_last
		#print 'returning dCds = ', dCds, ' within ', error, ' Cubic_Bezier_dCds'
	else:
		dCds = dCds_seg
	return dCds

def Cubic_6P_dCds(pole0, pole1, pole2, pole3, pole4, pole5):    
	# calculate the rate of change of curvature per unit length (chord)
    # at the beginning of a cubic 6P curve defined by the given poles
	
	# calculate start point curvature directly from poles.
	C0 = Cubic_6P_curvature(pole0[0], pole1[0], pole2[0])
	if math.fabs(C0) < 1.0e-5:
		C0= 0.0		
	# prepare cubic 6P object to segment
	Curve = NURBS_Cubic_6P_curve([pole0, pole1, pole2, pole3, pole4, pole5])
	# cut the 6P below the first internal knot
	Curve.segment(0,.25)
	poles = Curve.getPoles()
	weights = Curve.getWeights()
	# rebuild the weighted poles
	WeightedPoles = [[poles[0],weights[0]], [poles[1],weights[1]], [poles[2],weights[2]], [poles[3],weights[3]]]
	# pass the weighted poles down to the Bezier dCds function
	dCds = Cubic_Bezier_dCds(WeightedPoles[0], WeightedPoles[1], WeightedPoles[2], WeightedPoles[3])

	return dCds

def blendG3_poly_2x4_1x6(poles_0,weights_0, poles_1, weights_1, scale_0, scale_1, scale_2, scale_3):	# work in progress. complete mess
	# blend two cubic bezier into a 6 point cubic NURBS. 
	# this function assumes poles_0 flow into poles_1 without checking.

	# rebuild both bezier inputs from the poles and weights
	WeightedPoles_0=[[poles_0[0],weights_0[0]], [poles_0[1],weights_0[1]], [poles_0[2],weights_0[2]], [poles_0[3],weights_0[3]]]
	CubicCurve4_0= Bezier_Cubic_curve(WeightedPoles_0) 
	WeightedPoles_1=[[poles_1[0],weights_1[0]], [poles_1[1],weights_1[1]], [poles_1[2],weights_1[2]], [poles_1[3],weights_1[3]]]
	CubicCurve4_1= Bezier_Cubic_curve(WeightedPoles_1) 

	# set end point dC/ds targets
	
	C0 = Cubic_6P_curvature(WeightedPoles_0[0][0], WeightedPoles_0[1][0], WeightedPoles_0[2][0])
	C1 = Cubic_6P_curvature(WeightedPoles_1[3][0], WeightedPoles_1[2][0], WeightedPoles_1[1][0])
	DC = math.fabs(C0-C1)
	
	dCds0 = Cubic_Bezier_dCds(WeightedPoles_0[0], WeightedPoles_0[1], WeightedPoles_0[2], WeightedPoles_0[3])
	dCds1 = Cubic_Bezier_dCds(WeightedPoles_1[3], WeightedPoles_1[2], WeightedPoles_1[1], WeightedPoles_1[0])
	DdCds = math.fabs(dCds0-dCds1)
	
	# quick, cheap, and very incomplete symmetry test.
	if DC < 1.0e-8 and DdCds < 1.0e-8:
		symmetric = 1
	else:
		symmetric = 0
	
	#print "dCds inputs: " "dCds0, ", dCds0, " dCds1, ", dCds1
	
	if math.fabs(dCds0) < 5.0e-6:
		dCds0 = 0.0
	if math.fabs(dCds1) < 5.0e-6:
		dCds1 = 0.0		

	print ("dCds targets: " "dCds0, ", dCds0, " dCds1, ", dCds1," C0, ", C0, " C1, ", C1, "symmetric: ", symmetric)
	
	# convert 4P inputs to 6P
	CubicCurve6_0=CubicCurve4_0
	CubicCurve6_0.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
	CubicCurve6_0.insertKnot(2.0/3.0)
	CubicCurve6_1=CubicCurve4_1
	CubicCurve6_1.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
	CubicCurve6_1.insertKnot(2.0/3.0)

	# extract poles and weights from 6Ps
	poles_6_0=CubicCurve6_0.getPoles()
	weights_6_0=CubicCurve6_0.getWeights()
	poles_6_1=CubicCurve6_1.getPoles()
	weights_6_1=CubicCurve6_1.getWeights()

	# need to come back here and make sure fractional weights were not reset to 1 (in the case where an 
	# entire row is equal). this can screw up rational grids, even though it doesn't matter for curves.

	# check Cubic_6P_dCds
	WeightedPoles_6_0=[[poles_6_0[0],weights_6_0[0]],
						[poles_6_0[1],weights_6_0[1]],
						[poles_6_0[2],weights_6_0[2]],
						[poles_6_0[3],weights_6_0[3]],
						[poles_6_0[4],weights_6_0[4]],
						[poles_6_0[5],weights_6_0[5]]]

	dCds6_0 = Cubic_6P_dCds(WeightedPoles_6_0[0],
							WeightedPoles_6_0[1],
							WeightedPoles_6_0[2],
							WeightedPoles_6_0[3],
							WeightedPoles_6_0[4],
							WeightedPoles_6_0[5])

	WeightedPoles_6_1=[[poles_6_1[0],weights_6_1[0]],
						[poles_6_1[1],weights_6_1[1]],
						[poles_6_1[2],weights_6_1[2]],
						[poles_6_1[3],weights_6_1[3]],
						[poles_6_1[4],weights_6_1[4]],
						[poles_6_1[5],weights_6_1[5]]]

	dCds6_1 = Cubic_6P_dCds(WeightedPoles_6_1[5],
							WeightedPoles_6_1[4],
							WeightedPoles_6_1[3],
							WeightedPoles_6_1[2],
							WeightedPoles_6_1[1],
							WeightedPoles_6_1[0])

	print ("dCds 6P check: " "dCds6_0, ", dCds6_0, " dCds6_1, ", dCds6_1)

	# compile the blend poly. this initial form is G2, but clumped towards the outer points.
	p0=[poles_6_0[0],weights_6_0[0]]
	p1=[poles_6_0[1],weights_6_0[1]]
	p2=[poles_6_0[2],weights_6_0[2]]
	p3=[poles_6_1[3],weights_6_1[3]]
	p4=[poles_6_1[4],weights_6_1[4]]
	p5=[poles_6_1[5],weights_6_1[5]]

	### calculate curvature components
	## start point
	l0 = p1[0]-p0[0]					# first control leg
	tan0=Base.Vector(l0)				# make clean copy
	tan0.normalize()					# unit tangent direction
	l1=Base.Vector(tan0)				# make clean copy
	l1.multiply(tan0.dot(p2[0]-p1[0])) 	# scalar projection of second control leg along unit tangent
	h1=(p2[0]-p1[0])-l1					# height of second control leg orthogonal to tangent
	## end point
	l4 = p4[0]-p5[0]					# last control leg
	tan4=Base.Vector(l4)				# make clean copy
	tan4.normalize()					# unit tangent direction
	l3=Base.Vector(tan4)				# make clean copy
	l3.multiply(tan4.dot(p3[0]-p4[0])) 	# scalar projection of second to last control leg along unit tangent
	h3=(p3[0]-p4[0])-l3					# height of second control leg orthogonal to tangent
	### scale first and last control legs
	L0=Base.Vector(l0)					# make clean copy
	L0.multiply(scale_0)				# apply tangent scale
	p1_scl = [p0[0] + L0, p1[1]]		# reposition second control point
	L4=Base.Vector(l4)					# make clean copy
	L4.multiply(scale_3)				# apply tangent scale
	p4_scl = [p5[0] + L4, p4[1]]		# reposition fifth control point
	### calc new heights for inner control legs
	H1 = Base.Vector(h1)				# make clean copy
	H1.multiply(scale_0.__pow__(2))		# apply height scale
	H3 = Base.Vector(h3)				# make clean copy
	H3.multiply(scale_3.__pow__(2))		# apply height scale

	
	# search loop initial parameters
	scale_1i = 1.0
	scale_2i = 1.0
	error = 1.0
	step_size = 0.1
	dir_0_prev = 0.0
	dir_1_prev = 0.0
	nudge_prev = 'none'
	streak_0_count = 0
	streak_1_count = 0
	#step_stage_complete = 0
	loop_count = 0
	tol= 1.0e-5
	while (error > tol  and loop_count < 200 ):
		# reset for next iteration
		L1 = p1_scl[0] - p0[0]				# rescale to new tangent (scale_0 already applied)
		L3 = p4_scl[0] - p5[0]				# rescale to new tangent (scale_3 already applied)
		# apply scales
		L1 = L1.multiply(scale_1i)			# apply inner tangent scale
		p2_scl = [p1_scl[0] + H1 + L1, p2[1]]	# reposition third control point
		L3 = L3.multiply(scale_2i)			# apply inner tangent scale
		p3_scl = [p4_scl[0] + H3 + L3, p3[1]]	# reposition third control point
		# prepare poles and weights function output
		poles=[p0[0], p1_scl[0], p2_scl[0], p3_scl[0], p4_scl[0], p5[0]]
		weights = [p0[1], p1[1], p2[1], p3[1], p4[1], p5[1]]
		# prepare weighted poles for curvature analysis
		WeightedPoles_6_i = [[poles[0],weights[0]],
							[poles[1],weights[1]],
							[poles[2],weights[2]],
							[poles[3],weights[3]],
							[poles[4],weights[4]],
							[poles[5],weights[5]]]
		# check both end curvatures
		dCds6_0i = Cubic_6P_dCds(WeightedPoles_6_i[0],
								WeightedPoles_6_i[1],
								WeightedPoles_6_i[2],
								WeightedPoles_6_i[3],
								WeightedPoles_6_i[4],
								WeightedPoles_6_i[5])

		dCds6_1i = Cubic_6P_dCds(WeightedPoles_6_i[5],
								WeightedPoles_6_i[4],
								WeightedPoles_6_i[3],
								WeightedPoles_6_i[2],
								WeightedPoles_6_i[1],
								WeightedPoles_6_i[0])

		# define current G3 error
		# proportional in non-zero cases,? absolute if target is 0
		# the proportional error is a problem.
		# it prioritizes smaller errors near zero than large errors proportionally closer to the target.
		# in practice, this causes divergent run away situations
		if dCds0 != 0.0:
			error_0 = (dCds6_0i - dCds6_0) * ( 1 + 1 / math.fabs(dCds0)) / 2
		elif dCds0 == 0.0:
			error_0 = (dCds6_0i - dCds6_0) * ( 1 + 1 / math.fabs(dCds6_0i)) / 2
		else:
			print ("dCds0, ", dCds0, "returned from Cubic_6P_dCds()")
		
		if dCds1 != 0.0:
			error_1 = (dCds6_1i - dCds6_1) * ( 1 + 1 / math.fabs(dCds1)) / 2
		elif dCds1 == 0.0:	
			error_1 = (dCds6_1i - dCds6_1) * ( 1 + 1 / math.fabs(dCds6_1i)) / 2 # < this has caused div by 0 errors
		else:
			print ("dCds1, ", dCds1, "returned from Cubic_6P_dCds()")
		
		# success criteria for normal exit
		if math.fabs(error_0) <= tol and math.fabs(error_1) <= tol:
			print ("final ", loop_count, ": ","scl[", scale_1i, ", ", scale_2i,	"] dCds[", dCds6_0i, ", ", dCds6_1i,"] err[", error_0, ", ", error_1,"]")
			return [poles,weights,scale_1i,scale_2i]
		
		error = math.fabs(error_0) + math.fabs(error_1)
		
		# establish bounds for the errors based on initial guess
		if loop_count == 0:
			error_0_max = error_0
			error_1_max = error_1
		
		# if the loop takes BOTH errors beyond the initial bounds, undo last action, and reduce step size.
		if loop_count != 0 and math.fabs(error_0) > math.fabs(error_0_max) and math.fabs(error_1) > math.fabs(error_1_max):
			#undo last action
			if 	nudge_prev == 0:
				scale_1i = scale_1i - dir_prev * step_size
				
			elif 	nudge_prev == 1:
				scale_2i = scale_2i - dir_prev * step_size
				
			# reduce step size
			step_size = step_size / 2.0
			#print "div - error grew"

		# determine the required adjustment direction for each endpoint.
		if error_0 > tol / 2.0:
			direction_0 = 1
		elif error_0 < -tol / 2.0:
			direction_0 = -1
		else:
			direction_0 = 0
		if error_1 > tol / 2.0:
			direction_1 = 1
		elif error_1 < -tol / 2.0:
			direction_1 = -1
		else:
			direction_1 = 0
			
		# plan the next action
		if 	math.fabs(error_0) >= math.fabs(error_1):
			nudge = 0
			dir = direction_0
			if symmetric != 1:
				streak_0_count = streak_0_count + 1
				streak_1_count = 0
		elif 	math.fabs(error_0) < math.fabs(error_1):
			nudge = 1
			dir = direction_1
			if symmetric != 1:
				streak_1_count = streak_1_count + 1
				streak_0_count = 0
		
		if symmetric == 1 and direction_0 == direction_1:
			nudge = 2
			direction_2 = direction_0
		elif symmetric == 1 and direction_0 != direction_1:
			nudge = 0
			direction = 0
			symmetric = 0
			print ("symmetry assumption has broken down.")
			
		# compare the next planned action to the last executed action
		if nudge == nudge_prev and dir != dir_prev:
			# if we are undoing the previous action, reduce step size
			step_size = step_size / 2.0
			#print "div - direct undo"
			
		# execute planned action, unless it is the same action 5 times in a row.
		if 	(nudge == 0 and streak_0_count <= 5) or streak_1_count > 4:
			scale_1i = scale_1i + direction_0 * step_size
			dir_prev = direction_0
			nudge_prev = 0
			streak_1_count = 0
		
		elif (nudge == 1 and streak_1_count <= 5) or streak_0_count > 4:
			scale_2i = scale_2i + direction_1 * step_size
			dir_prev = direction_1
			nudge_prev = 1
			streak_0_count = 0
		
		elif nudge == 2:
			scale_1i = scale_1i + direction_0 * step_size
			scale_2i = scale_2i + direction_1 * step_size
			dir_prev = direction_2
			nudge_prev = 2
		
		upper_limit = 3.0
		lower_limit = 0.75
		
		if scale_1i > upper_limit:
			scale_1i = upper_limit
		if scale_2i > upper_limit:
			scale_2i = upper_limit
		if scale_1i < lower_limit:
			scale_1i = lower_limit
		if scale_2i < lower_limit:
			scale_2i = lower_limit			
		
		# G3 loop message
		print (loop_count, ": ","scl[", scale_1i, ", ", scale_2i,	"] dCds[", dCds6_0i, ", ", dCds6_1i,"] err[", error_0, ", ", error_1,"] dir[", direction_0, ", ", direction_1,"]act[",nudge_prev, ", ", dir_prev,"] streaks [", streak_0_count, ", ", streak_1_count, "]")
		
		if (scale_1i == upper_limit and scale_2i == upper_limit) or (scale_1i == lower_limit and scale_2i == lower_limit):
			break
		
		if (scale_1i == upper_limit and scale_2i == lower_limit) or (scale_1i == lower_limit and scale_2i == upper_limit):
			break
			
		loop_count=loop_count + 1
	# G3 final message
	print ("final ", loop_count, ": ","scl[", scale_1i, ", ", scale_2i,	"] dCds[", dCds6_0i, ", ", dCds6_1i,"] err[", error_0, ", ", error_1,"]")
	
	# make sure the final values have been applied
	
	L1 = p1_scl[0] - p0[0]				# rescale to new tangent (scale_0 already applied)
	L3 = p4_scl[0] - p5[0]				# rescale to new tangent (scale_3 already applied)
	# apply scales
	L1 = L1.multiply(scale_1i)			# apply inner tangent scale
	p2_scl = [p1_scl[0] + H1 + L1, p2[1]]	# reposition third control point
	L3 = L3.multiply(scale_2i)			# apply inner tangent scale
	p3_scl = [p4_scl[0] + H3 + L3, p3[1]]	# reposition third control point
	# prepare poles and weights function output
	poles=[p0[0], p1_scl[0], p2_scl[0], p3_scl[0], p4_scl[0], p5[0]]
	weights = [p0[1], p1[1], p2[1], p3[1], p4[1], p5[1]]
	
	return [poles,weights,scale_1i,scale_2i]

def blendFair_poly_2x4_1x6(poles_0,weights_0, poles_1, weights_1, scale_0, scale_1, scale_2, scale_3):	# work in progress. complete mess
	# blend two cubic bezier into a 6 point cubic NURBS. 
	# this function assumes poles_0 flow into poles_1 without checking.

	# rebuild both bezier inputs from the poles and weights
	WeightedPoles_0=[[poles_0[0],weights_0[0]], [poles_0[1],weights_0[1]], [poles_0[2],weights_0[2]], [poles_0[3],weights_0[3]]]
	CubicCurve4_0= Bezier_Cubic_curve(WeightedPoles_0) 
	WeightedPoles_1=[[poles_1[0],weights_1[0]], [poles_1[1],weights_1[1]], [poles_1[2],weights_1[2]], [poles_1[3],weights_1[3]]]
	CubicCurve4_1= Bezier_Cubic_curve(WeightedPoles_1) 

	# set end point dC/ds targets
	
	C0 = Cubic_6P_curvature(WeightedPoles_0[0][0], WeightedPoles_0[1][0], WeightedPoles_0[2][0])
	C1 = Cubic_6P_curvature(WeightedPoles_1[3][0], WeightedPoles_1[2][0], WeightedPoles_1[1][0])
	DC = math.fabs(C0-C1)
	
	dCds0 = Cubic_Bezier_dCds(WeightedPoles_0[0], WeightedPoles_0[1], WeightedPoles_0[2], WeightedPoles_0[3])
	dCds1 = Cubic_Bezier_dCds(WeightedPoles_1[3], WeightedPoles_1[2], WeightedPoles_1[1], WeightedPoles_1[0])
	DdCds = math.fabs(dCds0-dCds1)
	
	# quick, cheap, and very incomplete symmetry test.
	if DC < 1.0e-8 and DdCds < 1.0e-8:
		symmetric = 1
	else:
		symmetric = 0
	
	#print "dCds inputs: " "dCds0, ", dCds0, " dCds1, ", dCds1
	
	if math.fabs(dCds0) < 5.0e-6:
		dCds0 = 0.0
	if math.fabs(dCds1) < 5.0e-6:
		dCds1 = 0.0		

	print ("dCds targets: " "dCds0, ", dCds0, " dCds1, ", dCds1," C0, ", C0, " C1, ", C1, "symmetric: ", symmetric)
	
	# convert 4P inputs to 6P
	CubicCurve6_0=CubicCurve4_0
	CubicCurve6_0.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
	CubicCurve6_0.insertKnot(2.0/3.0)
	CubicCurve6_1=CubicCurve4_1
	CubicCurve6_1.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
	CubicCurve6_1.insertKnot(2.0/3.0)

	# extract poles and weights from 6Ps
	poles_6_0=CubicCurve6_0.getPoles()
	weights_6_0=CubicCurve6_0.getWeights()
	poles_6_1=CubicCurve6_1.getPoles()
	weights_6_1=CubicCurve6_1.getWeights()

	# check Cubic_6P_dCds
	WeightedPoles_6_0=[[poles_6_0[0],weights_6_0[0]],
						[poles_6_0[1],weights_6_0[1]],
						[poles_6_0[2],weights_6_0[2]],
						[poles_6_0[3],weights_6_0[3]],
						[poles_6_0[4],weights_6_0[4]],
						[poles_6_0[5],weights_6_0[5]]]

	dCds6_0 = Cubic_6P_dCds(WeightedPoles_6_0[0],
							WeightedPoles_6_0[1],
							WeightedPoles_6_0[2],
							WeightedPoles_6_0[3],
							WeightedPoles_6_0[4],
							WeightedPoles_6_0[5])

	WeightedPoles_6_1=[[poles_6_1[0],weights_6_1[0]],
						[poles_6_1[1],weights_6_1[1]],
						[poles_6_1[2],weights_6_1[2]],
						[poles_6_1[3],weights_6_1[3]],
						[poles_6_1[4],weights_6_1[4]],
						[poles_6_1[5],weights_6_1[5]]]

	dCds6_1 = Cubic_6P_dCds(WeightedPoles_6_1[5],
							WeightedPoles_6_1[4],
							WeightedPoles_6_1[3],
							WeightedPoles_6_1[2],
							WeightedPoles_6_1[1],
							WeightedPoles_6_1[0])

	print ("dCds 6P check: " "dCds6_0, ", dCds6_0, " dCds6_1, ", dCds6_1)

	# compile the blend poly. this initial form is G2, but clumped towards the outer points.
	p0=[poles_6_0[0],weights_6_0[0]]
	p1=[poles_6_0[1],weights_6_0[1]]
	p2=[poles_6_0[2],weights_6_0[2]]
	p3=[poles_6_1[3],weights_6_1[3]]
	p4=[poles_6_1[4],weights_6_1[4]]
	p5=[poles_6_1[5],weights_6_1[5]]

	### calculate curvature components
	## start point
	l0 = p1[0]-p0[0]					# first control leg
	tan0=Base.Vector(l0)				# make clean copy
	tan0.normalize()					# unit tangent direction
	l1=Base.Vector(tan0)				# make clean copy
	l1.multiply(tan0.dot(p2[0]-p1[0])) 	# scalar projection of second control leg along unit tangent
	h1=(p2[0]-p1[0])-l1					# height of second control leg orthogonal to tangent
	## end point
	l4 = p4[0]-p5[0]					# last control leg
	tan4=Base.Vector(l4)				# make clean copy
	tan4.normalize()					# unit tangent direction
	l3=Base.Vector(tan4)				# make clean copy
	l3.multiply(tan4.dot(p3[0]-p4[0])) 	# scalar projection of second to last control leg along unit tangent
	h3=(p3[0]-p4[0])-l3					# height of second control leg orthogonal to tangent
	### scale first and last control legs
	L0=Base.Vector(l0)					# make clean copy
	L0.multiply(scale_0)				# apply tangent scale
	p1_scl = [p0[0] + L0, p1[1]]		# reposition second control point
	L4=Base.Vector(l4)					# make clean copy
	L4.multiply(scale_3)				# apply tangent scale
	p4_scl = [p5[0] + L4, p4[1]]		# reposition fifth control point
	### calc new heights for inner control legs
	H1 = Base.Vector(h1)				# make clean copy
	H1.multiply(scale_0.__pow__(2))		# apply height scale
	H3 = Base.Vector(h3)				# make clean copy
	H3.multiply(scale_3.__pow__(2))		# apply height scale

	# output of the G2 portion
	p0[0]			# start point. unchanged
	p1_scl			# start tangent point. scaled
	H1				# start inner tangent height. scaled
	H3				# end inner tangent height. scaled
	p4_scl[0]		# end  tangent point. scaled
	p5[0]			# end point. unchanged	

	
	
	# stuff involved in making a single fairing attempt and evaluating dCds to establish G3 error.
	p0[0]			# start point. unchanged
	p1_scl[0]		# start tangent point. unchanged
	scale_1i		# start inner tangent scale : independent variable in the attempt
	H1				# start inner tangent height. unchanged
	p2[1]			# start inner tangent weight. unchanged
	p3[1]			# end inner tangent weight. 
	scale_2i		# end inner tangent scale : independent variable in the attempt
	H3				# end inner tangent height. unchanged
	p4_scl[0]		# end  tangent point. unchanged
	p5[0]			# end point. unchanged
	
	dCds0			# input poly start curvature derivative with respect to arclength (along +t). dependent variable in the attempt
	dCds1			# input poly end curvature derivative with respect to arclength (along -t). dependent variable in the attempt
	
	
	
	
	# search loop initial parameters
	scale_1i = 1.0
	scale_2i = 1.0
	error = 1.0
	step_size = 0.1
	dir_0_prev = 0.0
	dir_1_prev = 0.0
	nudge_prev = 'none'
	streak_0_count = 0
	streak_1_count = 0
	#step_stage_complete = 0
	loop_count = 0
	tol= 5.0e-6
	while (error > tol  and loop_count < 200 ):
		# reset for next iteration
		L1 = p1_scl[0] - p0[0]				# rescale to new tangent (scale_0 already applied)
		L3 = p4_scl[0] - p5[0]				# rescale to new tangent (scale_3 already applied)
		# apply scales
		L1 = L1.multiply(scale_1i)			# apply inner tangent scale
		p2_scl = [p1_scl[0] + H1 + L1, p2[1]]	# reposition third control point
		L3 = L3.multiply(scale_2i)			# apply inner tangent scale
		p3_scl = [p4_scl[0] + H3 + L3, p3[1]]	# reposition third control point
		# prepare poles and weights function output
		poles=[p0[0], p1_scl[0], p2_scl[0], p3_scl[0], p4_scl[0], p5[0]]
		weights = [p0[1], p1[1], p2[1], p3[1], p4[1], p5[1]]
		# prepare weighted poles for curvature analysis
		WeightedPoles_6_i = [[poles[0],weights[0]],
							[poles[1],weights[1]],
							[poles[2],weights[2]],
							[poles[3],weights[3]],
							[poles[4],weights[4]],
							[poles[5],weights[5]]]
		# check both end curvatures
		dCds6_0i = Cubic_6P_dCds(WeightedPoles_6_i[0],
								WeightedPoles_6_i[1],
								WeightedPoles_6_i[2],
								WeightedPoles_6_i[3],
								WeightedPoles_6_i[4],
								WeightedPoles_6_i[5])

		dCds6_1i = Cubic_6P_dCds(WeightedPoles_6_i[5],
								WeightedPoles_6_i[4],
								WeightedPoles_6_i[3],
								WeightedPoles_6_i[2],
								WeightedPoles_6_i[1],
								WeightedPoles_6_i[0])

		

		loop_count=loop_count + 1
	# G3 final message
	print ("final ", loop_count, ": ","scl[", scale_1i, ", ", scale_2i,	"] dCds[", dCds6_0i, ", ", dCds6_1i,"] err[", error_0, ", ", error_1,"]")
	return [poles,weights,scale_1i,scale_2i]
	
def match_r_6P_6P_Cubic(p0,p1,p2,tanRatio):
	l1 = p1 - p0
	l2 = p2 - p1

	h4_scalar = (l1.cross(l2)).Length*tanRatio.__pow__(2)/l1.Length

	test0 = ((l1.cross(l2)).cross(l1))
	test1 = equalVectors(test0, Base.Vector(0,0,0), .000001)
	if test1 == 1:
		hn = Base.Vector(0,0,0)
	else:
		hn = ((l1.cross(l2)).cross(l1)).normalize() 
	h4 = hn * h4_scalar

	p3 = p0 - (p1-p0) * tanRatio
	p4 = p3 + h4

	matchSet = [p3, p4]

	return matchSet

## direct functions currently unused in the Classes / unavailable through the Silk FreeCAD workbench 
## (they are kept here because they were successfully used in the pre-parametric version of the tools):

def isect_test(curve, surf, u):		# provides information about a curve point at parameter u as a surface intersection candidate.
	test_point = curve.value(u)											# point on curve
	test_proj_param = surf.parameter(test_point)							# parameter of projection of curve point onto surface
	test_proj = surf.value(test_proj_param[0],test_proj_param[1])			# projection of curve point onto surface
	test_proj_tan = surf.tangent(test_proj_param[0],test_proj_param[1])		# tangents of surface at projection
	test_proj_n = test_proj_tan[0].cross(test_proj_tan[1])					# get surface normal from tangents
	test_error = test_proj - test_point									# error vector
	error = test_error.Length											# distance between curve point and its surface projection
	testdot = test_error.dot(test_proj_n)									# compare orientation of point and surface
	test_center = [test_point, test_error, error, testdot,test_proj_param]					# prepare list of results
	return test_center

def isect_curve_surf(curve, surf):	# curve / surface intersection point
	tol= 0.00000001
	# setup the parameter search span 
	test_span = [curve.FirstParameter, curve.LastParameter]
	# determine whether the curve grows from inside or outside the surface. this will govern how to split the search span
	test_u_direction =  isect_test(curve, surf, curve.FirstParameter) 	# project curve startpoint to determine if it is 'inside' or 'outside' the surface.
	if (test_u_direction[3] < 0):								# compare projection path to surface normal: dot product negative
		direction = 1											# > curve grows 'into' the surface
	elif (test_u_direction[3] > 0):								# compare projection path to surface normal: dot product positive
		direction = -1										# > curve grows 'out of' the surface
	# initialize error
	error = 1.0
	# set up binary search loop
	loop_count = 0
	while (error > tol  and loop_count < 100):
		test_u = (test_span[1] + test_span[0]) / 2	# pick u in the center of the search span
		test =  isect_test(curve, surf, test_u)			# project curve(u) onto surface
		error = test[2]							# set current intersection error
		if ((test[3]*direction) < 0):					# is the projection still coming from outside the surface?
			test_span = [test_u, test_span[1]]		# > use second half of current span for the next search
		if ((test[3]*direction) > 0):					# is the projection coming from inside the surface?
			test_span = [test_span[0], test_u]		# > use first half of current span for the next search
		loop_count=loop_count + 1
	print ('step ', loop_count, '  u ', test_u, '  error ', test[2])
	if error > tol:
		print ('no intersection found within ', tol)
		isect_curve_surf = 'NONE'
	else:
		isect_curve_surf = [test[0], test_u, test[4]]
	return  isect_curve_surf


#### SECTION 2: PYTHON FEATURE CLASSES - PARAMETRIC LINKING BETWEEN OBJECTS

### control polygons (+sketch to input)

class ControlPoly4_3L:	# made from a single sketch containing 3 line objects connected end to end
	def __init__(self, obj , sketch):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly4_3L class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly4_3L","reference Sketch").Sketch = sketch
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_3L","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_3L","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_3L","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get all points on first three lines...error check later
		p00s=fp.Sketch.Geometry[0].StartPoint
		p01s=fp.Sketch.Geometry[0].EndPoint
		p10s=fp.Sketch.Geometry[1].StartPoint
		p11s=fp.Sketch.Geometry[1].EndPoint
		p20s=fp.Sketch.Geometry[2].StartPoint
		p21s=fp.Sketch.Geometry[2].EndPoint
		# to world
		mat=fp.Sketch.Placement.toMatrix()
		p00=mat.multiply(p00s)
		p01=mat.multiply(p01s)
		p20=mat.multiply(p20s)
		p21=mat.multiply(p21s)
		#for now assume
		fp.Poles=[p00,p01,p20,p21]
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p20)
		Leg2=Part.LineSegment(p20,p21)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly4_2N:	# made from 2 node sketches. each node sketch contains one line (tangent), and one circle (endpoint) located at one end of the line.
	def __init__(self, obj , sketch0, sketch1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly4_2N class Init\n")
		obj.addProperty("App::PropertyLink","Sketch0","ControlPoly4_2N","reference Sketch").Sketch0 = sketch0
		obj.addProperty("App::PropertyLink","Sketch1","ControlPoly4_2N","reference Sketch").Sketch1 = sketch1
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_2N","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_2N","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_2N","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process Sketch0
		obj00=fp.Sketch0.Geometry[0]
		obj01=fp.Sketch0.Geometry[1]
		if obj00.__class__==Part.Circle:
			cir0=obj00
		if obj01.__class__==Part.Circle:
			cir0=obj01
		if obj00.__class__==Part.LineSegment:
			lin0=obj00
		if obj01.__class__==Part.LineSegment:
			lin0=obj01
		p00s=cir0.Center
		if lin0.StartPoint==p00s:
			p01s=lin0.EndPoint
		elif lin0.EndPoint==p00s:
			p01s=lin0.StartPoint
		# to world
		mat0=fp.Sketch0.Placement.toMatrix()
		p00=mat0.multiply(p00s)
		p01=mat0.multiply(p01s)
		# process Sketch1
		obj10=fp.Sketch1.Geometry[0]
		obj11=fp.Sketch1.Geometry[1]
		if obj10.__class__==Part.Circle:
			cir1=obj10
		if obj11.__class__==Part.Circle:
			cir1=obj11
		if obj10.__class__==Part.LineSegment:
			lin1=obj10
		if obj11.__class__==Part.LineSegment:
			lin1=obj11
		p11s=cir1.Center
		if lin1.StartPoint==p11s:
			p10s=lin1.EndPoint
		elif lin1.EndPoint==p11s:
			p10s=lin1.StartPoint
		# to world
		mat1=fp.Sketch1.Placement.toMatrix()
		p10=mat1.multiply(p10s)
		p11=mat1.multiply(p11s)
		# set the poles
		fp.Poles=[p00,p01,p10,p11]
		# prepare the polygon
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p10)
		Leg2=Part.LineSegment(p10,p11)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly4_FirstElement:	# made from the first element of a single sketch. tested for straight line, circular arc (less than 90 degrees), and elliptic arc. the number of elements in the sketch should not be 3.
	def __init__(self, obj , sketch):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly4_FirstElement class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly4_FirstElement","reference Sketch").Sketch = sketch
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_FirstElement","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_FirstElement","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_FirstElement","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process the sketch...error check later
		ElemNurbs=fp.Sketch.Shape.Edges[0].toNurbs().Edge1.Curve
		ElemNurbs.increaseDegree(3)
		p0=ElemNurbs.getPole(1)
		p1=ElemNurbs.getPole(2)
		p2=ElemNurbs.getPole(3)
		p3=ElemNurbs.getPole(4)
		# already to world?
		#mat=fp.Sketch.Placement.toMatrix()
		#p0=mat.multiply(p0s)
		#p1=mat.multiply(p1s)
		#p2=mat.multiply(p2s)
		#p3=mat.multiply(p3s)
		fp.Poles=[p0,p1,p2,p3]
		# set the weights
		fp.Weights = ElemNurbs.getWeights()
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p0,p1)
		Leg1=Part.LineSegment(p1,p2)
		Leg2=Part.LineSegment(p2,p3)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly6_5L:	# made from a single sketch containing 5 line objects connected end to end
	def __init__(self, obj , sketch):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_5L class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly4_3L","reference Sketch").Sketch = sketch
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_3L","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_3L","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_3L","Weights").Weights = [1.0,1.0,1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get all points on first three lines...error check later
		p00s=fp.Sketch.Geometry[0].StartPoint
		p01s=fp.Sketch.Geometry[0].EndPoint
		p10s=fp.Sketch.Geometry[1].StartPoint
		p11s=fp.Sketch.Geometry[1].EndPoint
		p20s=fp.Sketch.Geometry[2].StartPoint
		p21s=fp.Sketch.Geometry[2].EndPoint
		p30s=fp.Sketch.Geometry[3].StartPoint
		p31s=fp.Sketch.Geometry[3].EndPoint
		p40s=fp.Sketch.Geometry[4].StartPoint
		p41s=fp.Sketch.Geometry[4].EndPoint
		# to world
		mat=fp.Sketch.Placement.toMatrix()
		p00=mat.multiply(p00s)
		p01=mat.multiply(p01s)
		p20=mat.multiply(p20s)
		p21=mat.multiply(p21s)
		p40=mat.multiply(p40s)
		p41=mat.multiply(p41s)
		#for now assume
		fp.Poles=[p00,p01,p20,p21,p40,p41]
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p20)
		Leg2=Part.LineSegment(p20,p21)
		Leg4=Part.LineSegment(p21,p40)
		Leg5=Part.LineSegment(p40,p41)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg4, Leg5]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly6_2N:	# made from 2 node sketches. each node sketch contain 2 lines, and one circle.
	def __init__(self, obj , sketch0, sketch1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_2N class Init\n")
		obj.addProperty("App::PropertyLink","Sketch0","ControlPoly6_2N","reference Sketch").Sketch0 = sketch0
		obj.addProperty("App::PropertyLink","Sketch1","ControlPoly6_2N","reference Sketch").Sketch1 = sketch1
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly6_2N","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly6_2N","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly6_2N","Weights").Weights = [1.0,1.0,1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process Sketch0
		obj00=fp.Sketch0.Geometry[0]
		obj01=fp.Sketch0.Geometry[1]
		obj02=fp.Sketch0.Geometry[2]
		# must draw the pieces in the correct order! improve later
		p00s=obj00.Center
		p01s=obj01.EndPoint
		p02s=obj02.EndPoint
		# to world
		mat0=fp.Sketch0.Placement.toMatrix()
		p00=mat0.multiply(p00s)
		p01=mat0.multiply(p01s)
		p02=mat0.multiply(p02s)
		# process Sketch1
		obj10=fp.Sketch1.Geometry[0]
		obj11=fp.Sketch1.Geometry[1]
		obj12=fp.Sketch1.Geometry[2]
		# must draw the pieces in the correct order! improve later
		p12s=obj10.Center
		p11s=obj11.EndPoint
		p10s=obj12.EndPoint
		# to world
		mat1=fp.Sketch1.Placement.toMatrix()
		p10=mat1.multiply(p10s)
		p11=mat1.multiply(p11s)
		p12=mat1.multiply(p12s)
		# set the poles
		fp.Poles=[p00,p01,p02,p10,p11, p12]
		# prepare the polygon
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p02)
		Leg2=Part.LineSegment(p02,p10)
		Leg3=Part.LineSegment(p10,p11)
		Leg4=Part.LineSegment(p11,p12)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg3, Leg4]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly6_FirstElement:	# made from the first element of a single sketch
	def __init__(self, obj , sketch):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_FirstElement class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly6_FirstElement","reference Sketch").Sketch = sketch
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly6_FirstElement","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly6_FirstElement","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly6_FirstElement","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process the sketch element...error check later
		ElemNurbs=fp.Sketch.Shape.Edges[0].toNurbs().Edge1.Curve
		ElemNurbs.increaseDegree(3)
		start=ElemNurbs.FirstParameter
		end=ElemNurbs.LastParameter
		knot1=start+(end-start)/3.0
		knot2=end-(end-start)/3.0
		ElemNurbs.insertKnot(knot1)
		ElemNurbs.insertKnot(knot2)
		p0=ElemNurbs.getPole(1)
		p1=ElemNurbs.getPole(2)
		p2=ElemNurbs.getPole(3)
		p3=ElemNurbs.getPole(4)
		p4=ElemNurbs.getPole(5)
		p5=ElemNurbs.getPole(6)
		# already to world?
		#mat=fp.Sketch.Placement.toMatrix()
		#p0=mat.multiply(p0s)
		#p1=mat.multiply(p1s)
		#p2=mat.multiply(p2s)
		#p3=mat.multiply(p3s)
		fp.Poles=[p0,p1,p2,p3,p4,p5]
		# set the weights
		fp.Weights = ElemNurbs.getWeights()
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p0,p1)
		Leg1=Part.LineSegment(p1,p2)
		Leg2=Part.LineSegment(p2,p3)
		Leg3=Part.LineSegment(p3,p4)
		Leg4=Part.LineSegment(p4,p5)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg3, Leg4]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

### control grids (+poly to input)

class ControlGrid44_4:	# made from 4 CubicControlPoly4.
	def __init__(self, obj , poly0, poly1, poly2, poly3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly0","ControlGrid44_4","control polygon").Poly0 = poly0
		obj.addProperty("App::PropertyLink","Poly1","ControlGrid44_4","control polygon").Poly1 = poly1
		obj.addProperty("App::PropertyLink","Poly2","ControlGrid44_4","control polygon").Poly2 = poly2
		obj.addProperty("App::PropertyLink","Poly3","ControlGrid44_4","control polygon").Poly3 = poly3
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_4","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_4","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_4","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles1=fp.Poly0.Poles
		poles2=fp.Poly1.Poles
		poles3=fp.Poly2.Poles
		poles4=fp.Poly3.Poles
		weights1=fp.Poly0.Weights
		weights2=fp.Poly1.Weights
		weights3=fp.Poly2.Weights
		weights4=fp.Poly3.Weights
		quad12 = orient_a_to_b(poles1,poles2)
		quad23 = orient_a_to_b(poles2,poles3)
		quad34 = orient_a_to_b(poles3,poles4)
		quad41 = orient_a_to_b(poles4,poles1)
		escape_malformed_loop = 0
		if (quad12 == 0):
			print ("first and second selected polys do not share endpoints")
			escape_malformed_loop = 1
		if (quad23 == 0):
			print ("second and third selected polys do not share endpoints")
			escape_malformed_loop = 1
		if (quad34 == 0):
			print ("third and fourth selected polys do not share endpoints")
			escape_malformed_loop = 1
		if (quad41 == 0):
			print ("first and fourth selected polys do not share endpoints")
			escape_malformed_loop = 1
		if (escape_malformed_loop == 1):
			print ("the object is created in the document, but awaits resolution of endpoint matching.",
	  				" inspect the sketches that define the Controloly4 objects.",
	  				" prioritize coincident constraints for the endpoints.",
					" do not trust a point on object constraint to result in theoratical point matching")
			return
		if quad12[0]!=poles1[0] and quad12[0]==poles1[-1]:
			weights1=weights1[::-1]
		if quad23[0]!=poles2[0] and quad23[0]==poles2[-1]:
			weights2=weights2[::-1]
		if quad34[0]!=poles3[0] and quad34[0]==poles3[-1]:
			weights3=weights3[::-1]
		if quad41[0]!=poles4[0] and quad41[0]==poles4[-1]:
			weights4=weights4[::-1]
		p00 = quad12[0]
		p01 = quad12[1]
		p02 = quad12[2]
		p03 = quad12[3]
		p13 = quad23[1]
		p23 = quad23[2]
		p33 = quad23[3]
		p32 = quad34[1]
		p31 = quad34[2]
		p30 = quad34[3]
		p20 = quad41[1]
		p10 = quad41[2]
		p11 = p00 + (p01 - p00) +  (p10 - p00)
		p12 = p03 + (p02 - p03) +  (p13 - p03)
		p21 = p30 + (p31 - p30) +  (p20 - p30)
		p22 = p33 + (p23 - p33) +  (p32 - p33)
		fp.Poles = [p00 ,p01, p02, p03,
					p10, p11, p12, p13,
					p20, p21, p22, p23,
					p30, p31, p32, p33]
		w00 = weights1[0]
		w01 = weights1[1]
		w02 = weights1[2]
		w03 = weights1[3]
		w13 = weights2[1]
		w23 = weights2[2]
		w33 = weights2[3]
		w32 = weights3[1]
		w31 = weights3[2]
		w30 = weights3[3]
		w20 = weights4[1]
		w10 = weights4[2]
		w11 = w01*w20
		w12 = w02*w13
		w21 = w32*w10
		w22 = w23*w31
		fp.Weights = [w00 ,w01, w02, w03,
					w10, w11, w12, w13,
					w20, w21, w22, w23,
					w30, w31, w32, w33]
		
		fp.Legs = drawGrid(fp.Poles, 4)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid44_3:	# made from 3 CubicControlPoly4. 
						#degenerate grid along one edge (4 points), and two inner points neighboring this edge.
	def __init__(self, obj , poly0, poly1, poly2):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_3 class Init\n")
		obj.addProperty("App::PropertyLink","Poly0","ControlGrid44_3","control polygon").Poly0 = poly0
		obj.addProperty("App::PropertyLink","Poly1","ControlGrid44_3","control polygon").Poly1 = poly1
		obj.addProperty("App::PropertyLink","Poly2","ControlGrid44_3","control polygon").Poly2 = poly2
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_3","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_3","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_3","Weights").Weights
		obj.addProperty("App::PropertyFloat","TweakWeight11","ControlGrid44_3","Weights").TweakWeight11 = 1.0
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles1=fp.Poly0.Poles
		poles2=fp.Poly1.Poles
		poles3=fp.Poly2.Poles
		weights1=fp.Poly0.Weights
		weights2=fp.Poly1.Weights
		weights3=fp.Poly2.Weights
		quad12 = orient_a_to_b(poles1,poles2)
		quad23 = orient_a_to_b(poles2,poles3)
		quad31 = orient_a_to_b(poles3,poles1)

		if quad12[0]!=poles1[0] and quad12[0]==poles1[-1]:
			weights1=weights1[::-1]
		if quad23[0]!=poles2[0] and quad23[0]==poles2[-1]:
			weights2=weights2[::-1]
		if quad31[0]!=poles3[0] and quad31[0]==poles3[-1]:
			weights3=weights3[::-1]
		# make sure this is a degenerate quadrangle, i.e. a triangle
		if (quad31[3] != quad12[0]):
			print ('edge loop does not form a triangle')
		#no further error handling is implemented

		p00 = quad12[0]
		p01 = quad12[1]
		p02 = quad12[2]
		p03 = quad12[3]

		p13 = quad23[1]
		p23 = quad23[2]
		p33 = quad23[3]

		p32 = quad31[1]
		p31 = quad31[2]
		p30 = p00

		p20 = p00
		p10 = p00

		p11 = p01+p31-p30
		p12 = p02+p13-p03
		p21 = p11
		p22 = p23+p32-p33

		fp.Poles = [p00 ,p01, p02, p03,
					p10, p11, p12, p13,
					p20, p21, p22, p23,
					p30, p31, p32, p33]

		# weights below are meh. surface edges follow curves, but internal degenerate point has too much draw.
		w00 = weights1[0]
		w01 = weights1[1]
		w02 = weights1[2]
		w03 = weights1[3]

		w13 = weights2[1]
		w23 = weights2[2]
		w33 = weights2[3]

		w32 = weights3[1]
		w31 = weights3[2]
		w30 = weights3[3]

		w10 = fp.TweakWeight11
		w20 = fp.TweakWeight11

		w11 = w01*w10
		w12 = w02*w13
		w21 = w31*w20
		w22 = w23*w31


		fp.Weights = [w00 ,w01, w02, w03,
					w10, w11, w12, w13,
					w20, w21, w22, w23,
					w30, w31, w32, w33]
		
		fp.Legs = drawGrid(fp.Poles, 4)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid44_3_Rotate_OLD:	# made from 3 CubicControlPoly4. 
								# degenerate grid along one edge (4 points). two inner points are rotated
								# to align towards the degenerate corner.
	def __init__(self, obj , poly0, poly1, poly2):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_3_Rotate class Init\n")
		obj.addProperty("App::PropertyLink","Poly0","ControlGrid44_3_Rotate","control polygon").Poly0 = poly0
		obj.addProperty("App::PropertyLink","Poly1","ControlGrid44_3_Rotate","control polygon").Poly1 = poly1
		obj.addProperty("App::PropertyLink","Poly2","ControlGrid44_3_Rotate","control polygon").Poly2 = poly2
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_3_Rotate","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_3_Rotate","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_3_Rotate","Weights").Weights
		obj.addProperty("App::PropertyFloat","TweakWeight11","ControlGrid44_3_Rotate","Weights").TweakWeight11 = 1.0
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles1=fp.Poly0.Poles
		poles2=fp.Poly1.Poles
		poles3=fp.Poly2.Poles
		weights1=fp.Poly0.Weights
		weights2=fp.Poly1.Weights
		weights3=fp.Poly2.Weights
		quad12 = orient_a_to_b(poles1,poles2)
		quad23 = orient_a_to_b(poles2,poles3)
		quad31 = orient_a_to_b(poles3,poles1)

		if quad12[0]!=poles1[0] and quad12[0]==poles1[-1]:
			weights1=weights1[::-1]
		if quad23[0]!=poles2[0] and quad23[0]==poles2[-1]:
			weights2=weights2[::-1]
		if quad31[0]!=poles3[0] and quad31[0]==poles3[-1]:
			weights3=weights3[::-1]
		# make sure this is a degenerate quadrangle, i.e. a triangle
		if (not equalVectors(quad31[3],quad12[0],.00001)):
			print ('edge loop does not form a triangle')
		#no further error handling is implemented

		p00 = quad12[0]
		p01 = quad12[1]
		p02 = quad12[2]
		p03 = quad12[3]

		p13 = quad23[1]
		p23 = quad23[2]
		p33 = quad23[3]

		p32 = quad31[1]
		p31 = quad31[2]
		p30 = p00

		p20 = p00
		p10 = p00

		p11_Temp = p01+p31-p30
		p12 = p02+p13-p03
		p21_Temp = p11_Temp
		p22 = p23+p32-p33

		# define a plane going through the degenerate corner, p00, and the last two opposite points of poly0
		Plane0_pt = p00
		Plane0_N = (p12-p13).cross(p00-p13)
		
		# define a line going through p01 and p11_Temp. we will want p11 (final) to be somewhere along his line.
		Line0_pt = p01
		Line0_N = p11_Temp-p01
		
		# define a plane going through the degenerate corner, p00, and the last two opposite points of poly3
		Plane1_pt = p00
		Plane1_N = (p22-p23).cross(p30-p23)
		
		# define a line going through p31 and p21_Temp. we will want p21 (final) to be somewhere along his line.
		Line1_pt = p31
		Line1_N = p21_Temp-p31
		
		# if the plane0 and Line0 are not parallel or coincident, set p11 at the intersection.
		# if they are, [TBD]
		test0 = math.fabs(Plane0_N.dot(Line0_N))
		print('test0: ',test0)
		if test0 >= .00001 :
			print('test0: ',test0)
			factor0 = (Plane0_pt-Line0_pt).dot(Plane0_N) / Line0_N.dot(Plane0_N)
			p11 = Line0_N.multiply(factor0)+Line0_pt
		else:
			print ('poly0 / poly2 combination: edge/plane parallel, cannot intersect for inner control point p11')
		 
		# if the plane1 and Line1 are not parallel or coincident, set p21 at the intersection.
		# if they are, [TBD]
		test1 = math.fabs(Plane1_N.dot(Line1_N))
		print('test1: ',test1)
		if test1 >= .00001 :
			factor1 = (Plane1_pt-Line1_pt).dot(Plane1_N) / Line1_N.dot(Plane1_N)
			p21 = Line1_N.multiply(factor1)+Line1_pt
		else:
			print ('poly2 / poly3 combination: edge/plane parallel, cannot intersect for inner control point p21')
		 

		fp.Poles = [p00 ,p01, p02, p03,
					p10, p11, p12, p13,
					p20, p21, p22, p23,
					p30, p31, p32, p33]

		# weights below are in progress
		w00 = weights1[0]
		w01 = weights1[1]
		w02 = weights1[2]
		w03 = weights1[3]

		w13 = weights2[1]
		w23 = weights2[2]
		w33 = weights2[3]

		w32 = weights3[1]
		w31 = weights3[2]
		w30 = weights3[3]

		w10 = w13 #fp.TweakWeight11 # or maybe try = p13?
		w20 = w23 #fp.TweakWeight11 # or maybe try = p23?

		w11 = w01*w10
		w12 = w02*w13
		w21 = w31*w20
		w22 = w23*w31


		fp.Weights = [w00 ,w01, w02, w03,
					w10, w11, w12, w13,
					w20, w21, w22, w23,
					w30, w31, w32, w33]
		Legs=[0]*20
		for i in range(0,3):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(3,6):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(6,9):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(9,12):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(12,15): #skip 0-4
			Legs[i]=Part.LineSegment(fp.Poles[i-11],fp.Poles[i-7])
		for i in range(15,17): #skip 4-8 and 5-9
			Legs[i]=Part.LineSegment(fp.Poles[i-9],fp.Poles[i-5])
		for i in range(17,20): #skip 8-12
			Legs[i]=Part.LineSegment(fp.Poles[i-8],fp.Poles[i-4])
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid44_3_Rotate:	# made from 3 CubicControlPoly4. 
								# degenerate grid along one edge (4 points). Four inner points are rotated
								# to align towards the degenerate corner.
	def __init__(self, obj , poly0, poly1, poly2):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_3_Rotate class Init\n")
		obj.addProperty("App::PropertyLink","Poly0","ControlGrid44_3_Rotate","control polygon").Poly0 = poly0
		obj.addProperty("App::PropertyLink","Poly1","ControlGrid44_3_Rotate","control polygon").Poly1 = poly1
		obj.addProperty("App::PropertyLink","Poly2","ControlGrid44_3_Rotate","control polygon").Poly2 = poly2
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_3_Rotate","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_3_Rotate","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_3_Rotate","Weights").Weights
		obj.addProperty("App::PropertyFloat","TweakWeight11","ControlGrid44_3_Rotate","Weights").TweakWeight11 = 1.0
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles1=fp.Poly0.Poles
		poles2=fp.Poly1.Poles
		poles3=fp.Poly2.Poles
		weights1=fp.Poly0.Weights
		weights2=fp.Poly1.Weights
		weights3=fp.Poly2.Weights
		quad12 = orient_a_to_b(poles1,poles2)
		quad23 = orient_a_to_b(poles2,poles3)
		quad31 = orient_a_to_b(poles3,poles1)

		if quad12[0]!=poles1[0] and quad12[0]==poles1[-1]:
			weights1=weights1[::-1]
		if quad23[0]!=poles2[0] and quad23[0]==poles2[-1]:
			weights2=weights2[::-1]
		if quad31[0]!=poles3[0] and quad31[0]==poles3[-1]:
			weights3=weights3[::-1]
		# make sure this is a degenerate quadrangle, i.e. a triangle
		if (not equalVectors(quad31[3],quad12[0],.00001)):
			print ('edge loop does not form a triangle')
		#no further error handling is implemented

		p00 = quad12[0]
		p01 = quad12[1]
		p02 = quad12[2]
		p03 = quad12[3]

		p13 = quad23[1]
		p23 = quad23[2]
		p33 = quad23[3]

		p32 = quad31[1]
		p31 = quad31[2]
		p30 = p00

		p20 = p00
		p10 = p00

		p11_Temp = p01+p31-p30
		p12_Temp = p02+p13-p03
		p21_Temp = p11_Temp
		p22_Temp = p23+p32-p33

		# check that poly0 and poly2 aren't parallel
		# define the rotation center and axis
		test_Rot_N = ((p01-p00).cross(p10-p00)).Length
		print('test_Rot_N: ',test_Rot_N)
		if test_Rot_N <= .00001 :
			Rot_pt = p00
			Rot_N = (p01-p00).cross(p31-p00)
		else:
			print('poly0 / poly2 combination: selected polys do not define a normal at the degenerate point')
			
		### define a target 'meridian' plane for p11 and p12
		# contains p00, p13, and Rot_N
		Plane1_pt = Rot_pt
		Plane1_N = Rot_N.cross(p13-p00)
		
		## define a line going through p01 and p11_Temp. we will want p11 (final) to be somewhere along his line.
		Line11_pt = p01
		Line11_N = p11_Temp-p01
	
		# if plane1 and Line11 are not parallel or coincident, set p11 at the intersection.
		# if they are, [TBD]
		test11 = math.fabs(Plane1_N.dot(Line11_N))
		print('test11: ',test11)
		if test11 >= .00001 :
			factor11 = (Plane1_pt-Line11_pt).dot(Plane1_N) / Line11_N.dot(Plane1_N)
			p11 = Line11_N.multiply(factor11)+Line11_pt
		else:
			print('cannot intersect standard p11 with meridian plane 1 to produce rotated inner control point p11')
		
		## define a line going through p02 and p12_Temp. we will want p12 (final) to be somewhere along his line.
		Line12_pt = p02
		Line12_N = p12_Temp-p02
		
		# if plane1 and Line12 are not parallel or coincident, set p12 at the intersection.
		# if they are, [TBD]
		test12 = math.fabs(Plane1_N.dot(Line12_N))
		print('test12: ',test12)
		if test12 >= .00001 :
			factor12 = (Plane1_pt-Line12_pt).dot(Plane1_N) / Line12_N.dot(Plane1_N)
			p12 = Line12_N.multiply(factor12)+Line12_pt
		else:
			print('cannot intersect standard p12 with meridian plane 1 to produce rotated inner control point p12')
		
		### define a target 'meridian' plane for p21 and p22
		# contains p00, p23, and Rot_N
		Plane2_pt = Rot_pt
		Plane2_N = Rot_N.cross(p23-p00)
		
		## define a line going through p31 and p21_Temp. we will want p21 (final) to be somewhere along his line.
		Line21_pt = p31
		Line21_N = p21_Temp-p31			
		
		# if plane2 and Line21 are not parallel or coincident, set p21 at the intersection.
		# if they are, [TBD]
		test21 = math.fabs(Plane2_N.dot(Line21_N))
		print('test21: ',test21)
		if test21 >= .00001 :
			factor21 = (Plane2_pt-Line21_pt).dot(Plane2_N) / Line21_N.dot(Plane2_N)
			p21 = Line21_N.multiply(factor21)+Line21_pt
		else:
			print('cannot intersect standard p21 with meridian plane 2 to produce rotated inner control point p21')		
		
		## define a line going through p32 and p22_Temp. we will want p22 (final) to be somewhere along his line.
		Line22_pt = p32
		Line22_N = p22_Temp-p32
		
		# if plane2 and Line22 are not parallel or coincident, set p22 at the intersection.
		# if they are, [TBD]
		test22 = math.fabs(Plane2_N.dot(Line22_N))
		print('test22: ',test22)
		if test22 >= .00001 :
			factor22 = (Plane2_pt-Line22_pt).dot(Plane2_N) / Line22_N.dot(Plane2_N)
			p22 = Line22_N.multiply(factor22)+Line22_pt
		else:
			print('cannot intersect standard p22 with meridian plane 2 to produce rotated inner control point p22')		
					
		fp.Poles = [p00 ,p01, p02, p03,
					p10, p11, p12, p13,
					p20, p21, p22, p23,
					p30, p31, p32, p33]

		# weights below are in progress
		w00 = weights1[0]
		w01 = weights1[1]
		w02 = weights1[2]
		w03 = weights1[3]

		w13 = weights2[1]
		w23 = weights2[2]
		w33 = weights2[3]

		w32 = weights3[1]
		w31 = weights3[2]
		w30 = weights3[3]

		w10 = w13 #fp.TweakWeight11 # or maybe try = p13?
		w20 = w23 #fp.TweakWeight11 # or maybe try = p23?

		w11 = w01*w10
		w12 = w02*w13
		w21 = w31*w20
		w22 = w23*w31


		fp.Weights = [w00 ,w01, w02, w03,
					w10, w11, w12, w13,
					w20, w21, w22, w23,
					w30, w31, w32, w33]
		
		fp.Legs = drawGrid(fp.Poles, 4)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid44_flow: # create a copy of a ControlGrid44 grid whose internal points will 'flow' instead of providing predictable tangency
	def __init__(self, obj , input_grid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_flow class Init\n")
		obj.addProperty("App::PropertyLink","InputGrid","ControlGrid44_flow","input control grid").InputGrid = input_grid
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_flow","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_flow","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_flow","Weights").Weights
		flow_lower = 0.0
		flow_upper = 1.0
		flow_step = 0.01
		flow_11 = 1.0
		flow_12 = 1.0
		flow_21 = 1.0
		flow_22 = 1.0
		obj.addProperty("App::PropertyFloatConstraint",
		  				"flow_11","ControlGrid44_flow",
						" impact on inner control point 11 \n set 0.0 to 1.0, where 0.0 will match the input grid").flow_11 = (flow_11, flow_lower, flow_upper, flow_step)
		obj.addProperty("App::PropertyFloatConstraint",
		  				"flow_12","ControlGrid44_flow",
						" impact on inner control point 12 \n set 0.0 to 1.0, where 0.0 will match the input grid").flow_12 = (flow_12, flow_lower, flow_upper, flow_step)
		obj.addProperty("App::PropertyFloatConstraint",
		  				"flow_21","ControlGrid44_flow",
						" impact on inner control point 21 \n set 0.0 to 1.0, where 0.0 will match the input grid").flow_21 = (flow_21, flow_lower, flow_upper, flow_step)
		obj.addProperty("App::PropertyFloatConstraint",
		  				"flow_22","ControlGrid44_flow",
						" impact on inner control point 22 \n set 0.0 to 1.0, where 0.0 will match the input grid").flow_22 = (flow_22, flow_lower, flow_upper, flow_step)
		obj.addProperty("App::PropertyBool",
						"mirror_u0", "ControlGrid44_flow",
						" maintain the direction of the original grid line that touch this edge \n inner control points will slide along these lines \n maintains mirrorability if it was present in the original grid").mirror_u0 = False
		obj.addProperty("App::PropertyBool",
						"mirror_u1", "ControlGrid44_flow",
						" maintain the direction of the original grid line that touch this edge \n inner control points will slide along these lines \n maintains mirrorability if it was present in the original grid").mirror_u1 = False
		obj.addProperty("App::PropertyBool",
						"mirror_v0", "ControlGrid44_flow",
						" maintain the direction of the original grid line that touch this edge \n inner control points will slide along these lines \n maintains mirrorability if it was present in the original grid").mirror_v0 = False
		obj.addProperty("App::PropertyBool",
						"mirror_v1", "ControlGrid44_flow",
						" maintain the direction of the original grid line that touch this edge \n inner control points will slide along these lines \n maintains mirrorability if it was present in the original grid").mirror_v1 = False
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		Poles = fp.InputGrid.Poles
		p00 = Poles[0]
		p01 = Poles[1]
		p02 = Poles[2]
		p03 = Poles[3]
		p10 = Poles[4]
		p11 = Poles[5]
		p12 = Poles[6]
		p13 = Poles[7]
		p20 = Poles[8]
		p21 = Poles[9]
		p22 = Poles[10]
		p23 = Poles[11]
		p30 = Poles[12]
		p31 = Poles[13]
		p32 = Poles[14]
		p33 = Poles[15]

		# first attempt to rotate the first inner legs towards each other	
		'''
		def pdir_test_01(p10, p11, p12):
			# edge to inner point
			L10_11_dir_u = (p11-p10).Length
			# inner point to next inner point
			L11_12_dir_u = (p12-p11).Length
			# determine scale of first inner leg to second inner leg
			Lscale_p11_dir_u = L10_11_dir_u / (L10_11_dir_u + L11_12_dir_u)
			# find the point from edge to second inner point that matches the scale
			p11_dir_u = p10 + Lscale_p11_dir_u * (p12-p10)
			return p11_dir_u
		def run_pdir_test_01(): # pass and handle a grid if you want to use this standalone
			p11_dir_u = pdir_test_01(p10, p11, p12)
			p21_dir_u = pdir_test_01(p20, p21, p22)
			p12_dir_u = pdir_test_01(p13, p12, p11)
			p22_dir_u = pdir_test_01(p23, p22, p21)
			p11_dir_v = pdir_test_01(p01, p11, p21)
			p21_dir_v = pdir_test_01(p31, p21, p11)
			p12_dir_v = pdir_test_01(p02, p12, p22)
			p22_dir_v = pdir_test_01(p32, p22, p12)
			p11a = (p11_dir_u + p11_dir_v) / 2.0
			p12a = (p12_dir_u + p12_dir_v) / 2.0
			p21a = (p21_dir_u + p21_dir_v) / 2.0
			p22a= (p22_dir_u + p22_dir_v) / 2.0
			Legs=[0]*8
			Legs[0]=Part.LineSegment(p10,p11a)
			Legs[1]=Part.LineSegment(p20,p21a)
			Legs[2]=Part.LineSegment(p13,p12a)
			Legs[3]=Part.LineSegment(p23,p22a)
			Legs[4]=Part.LineSegment(p01,p11a)
			Legs[5]=Part.LineSegment(p31,p21a)
			Legs[6]=Part.LineSegment(p02,p12a)
			Legs[7]=Part.LineSegment(p32,p22a)
			return Legs
		Legs = run_pdir_test_01()
		'''
		# not great. does what it was told to do, but not very interesting.
		# dramatically 'deflates' the grid. like overstretched plastic pulled over hard edges.
		# not sure if it is recursevely stable or not.
		# not 'flowy', i.e. u=1 row does not look like u=0 morphing into u=3
		# keeps the new inner points relatively close to old ones (leg angles differ greatly)
		# keep it around, maybe move it to raw functions as Tighten_Grid(grid44) or something

		# next try. let's interpolate first across-edge legs from two opposite corners to set leg orientation
		# then scale along the resulting direction.
		# if the two legs are colinear and dot is positive, great. new orientation equal to either, then scale.
		# if two legs are colinear and dot is negative, new direction should be perpendicular. 
		### check next edge segment to perpendicular up or down. this could be different for each inner point?
		# ok to reject insane folded grids.
		# if the legs are colinear, opposite, and of equal length, same as above, but also watch out for zeros along the way.

		# if the legs are in plane and dot is positive, simple interp.
		# if the legs are in plane and dot is negative...figure it out when you get to it. maybe do another perpendicular dealio?
		# maybe test for in plane before testing colinear? could cover both cases. colinear is super cheap tho.

		# write it for one edge first, then make it a function of a grid. 
		# then we'll need to rotate the grid to apply it 4 times.../shudder.

		# assume we're adjusting only p11 and p12 (along v=1). we'll also refer to p00, p01, p02, p03, p10, p13, p21, and p22.
		# lets call this "flowing along v=0, or flow_v0"? this identifies the edge we're flowing along...not the cps we're adjusting tho...
		L0 = p10 - p00
		L3 = p13 - p03

		# check if both legs are coplanar
		# use p00 as origin, p10 as x, p03 as yish, project p13 to plane?

		PlaneNormal = ((p10-p00).cross(p03-p00)).normalize()
		PointToPlane = (p13-p00).dot(PlaneNormal)
		print("PointToPlane, ", PointToPlane)
		testCoplanar = (PointToPlane < .000001 and PointToPlane > -.000001)
		print("testCoplanar, ", testCoplanar)
		# check cross-product for colinear legs
		testColinearCross = (p10 - p00).cross(p13 - p03)
		testColinear = (testColinearCross.Length <= .000001)
		print("testColinear, ", testColinear)
		# these test work, but won't be used yet.

		# Simple case for now, wrap in(/within?) exceptions after
		# find average leg direction across edge
		def flowEdge(p00, p01, p02, p03, p10, p13):
			L0 = p10 - p00
			L3 = p13 - p03
			legAvg = ((L0 + L3 ).normalize() * (L0.Length + L3.Length) * .5 )
			L1 = (1/3)*L0 + (2/3)*legAvg
			L2 = (1/3)*L3 + (2/3)*legAvg
			p11_by_v0 = p01 + L1
			p12_by_v0 = p02 + L2
			return [p11_by_v0, p12_by_v0]

		flow_v0 = flowEdge(p00, p01, p02, p03, p10, p13)
		flow_u0 = flowEdge(p00, p10, p20, p30, p01, p31)
		flow_v1 = flowEdge(p30, p31, p32, p33, p20, p23)
		flow_u1 = flowEdge(p03, p13, p23, p33, p02, p32)
		# above tests out ok
		'''
		Legs=[0]*8
		Legs[0]=Part.LineSegment(p01, flow_v0[0])
		Legs[1]=Part.LineSegment(p02, flow_v0[1])
		Legs[2]=Part.LineSegment(p10, flow_u0[0])
		Legs[3]=Part.LineSegment(p20, flow_u0[1])
		Legs[4]=Part.LineSegment(p31, flow_v1[0])
		Legs[5]=Part.LineSegment(p32, flow_v1[1])
		Legs[6]=Part.LineSegment(p13, flow_u1[0])
		Legs[7]=Part.LineSegment(p23, flow_u1[1])
		'''
		# p11, connects to p01 and p10
		p11_flow = 0.5 * (flow_v0[0] + flow_u0[0])
		# p12, connects to p02 and p13
		p12_flow = 0.5 * (flow_v0[1] + flow_u1[0])
		# p21, connects to p20 and p31
		p21_flow = 0.5 * (flow_u0[1] + flow_v1[0])		
		# p22, connects to p32 and p23
		p22_flow = 0.5 * (flow_v1[1] + flow_u1[1])


		p11_final = p11_flow * fp.flow_11 + p11 * (1-fp.flow_11)
		p12_final = p12_flow * fp.flow_12 + p12 * (1-fp.flow_12)
		p21_final = p21_flow * fp.flow_21 + p21 * (1-fp.flow_21)
		p22_final = p22_flow * fp.flow_22 + p22 * (1-fp.flow_22)

		fp.Poles = [p00 ,p01, p02, p03,
			p10, p11_final, p12_final, p13,
			p20, p21_final, p22_final, p23,
			p30, p31, p32, p33]
		
		fp.Weights = fp.InputGrid.Weights

		fp.Legs = drawGrid(fp.Poles, 4)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid66_4:	# made from 4 CubicControlPoly6.
	# ControlGrid66_4(poly0, poly1, poly2, poly3)
	def __init__(self, obj , poly0, poly1, poly2, poly3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid66_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly0","ControlGrid66_4","control polygon").Poly0 = poly0
		obj.addProperty("App::PropertyLink","Poly1","ControlGrid66_4","control polygon").Poly1 = poly1
		obj.addProperty("App::PropertyLink","Poly2","ControlGrid66_4","control polygon").Poly2 = poly2
		obj.addProperty("App::PropertyLink","Poly3","ControlGrid66_4","control polygon").Poly3 = poly3
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid66_4","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid66_4","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid66_4","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles1=fp.Poly0.Poles
		poles2=fp.Poly1.Poles
		poles3=fp.Poly2.Poles
		poles4=fp.Poly3.Poles
		weights1=fp.Poly0.Weights
		weights2=fp.Poly1.Weights
		weights3=fp.Poly2.Weights
		weights4=fp.Poly3.Weights
		sext12 = orient_a_to_b(poles1,poles2)
		sext23 = orient_a_to_b(poles2,poles3)
		sext34 = orient_a_to_b(poles3,poles4)
		sext41 = orient_a_to_b(poles4,poles1)
		# the weight orientation check below doesn't look complete.
		# checking first and last isn't enough. need to fix.
		if sext12[0]!=poles1[0] and sext12[0]==poles1[-1]:
			weights1=weights1[::-1]
		if sext23[0]!=poles2[0] and sext23[0]==poles2[-1]:
			weights2=weights2[::-1]
		if sext34[0]!=poles3[0] and sext34[0]==poles3[-1]:
			weights3=weights3[::-1]
		if sext41[0]!=poles4[0] and sext41[0]==poles4[-1]:
			weights4=weights4[::-1]
		p00 = sext12[0]
		p01 = sext12[1]
		p02 = sext12[2]
		p03 = sext12[3]
		p04 = sext12[4]
		p05 = sext12[5]
		p15 = sext23[1]
		p25 = sext23[2]
		p35 = sext23[3]
		p45 = sext23[4]
		p55 = sext23[5]
		p54 = sext34[1]
		p53 = sext34[2]
		p52 = sext34[3]
		p51 = sext34[4]
		p50 = sext34[5]
		p40 = sext41[1]
		p30 = sext41[2]
		p20 = sext41[3]
		p10 = sext41[4]
		p11 = p01 + (p10 - p00)
		p14 = p04 + (p15 - p05)
		p41 = p51 + (p40 - p50)
		p44 = p45 + (p54 - p55)
		p12 = p02 + (p10 - p00)
		p13 = p03 + (p15 - p05)
		p24 = p25 + (p04 - p05)
		p34 = p35 + (p54 - p55)
		p42 = p52 + (p40 - p50)
		p43 = p53 + (p45 - p55)
		p21 = p20 + (p01 - p00)
		p31 = p30 + (p51 - p50)
		p22 = p12 + (p20 - p10)
		p23 = p13 + (p25 - p15)
		p32 = p42 + (p30 - p40)
		p33 = p43 + (p35 - p45)
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35,
					p40, p41, p42, p43, p44, p45,
					p50, p51, p52, p53, p54, p55]
		w00 = weights1[0]
		w01 = weights1[1]
		w02 = weights1[2]
		w03 = weights1[3]
		w04 = weights1[4]
		w05 = weights1[5]
		w15 = weights2[1]
		w25 = weights2[2]
		w35 = weights2[3]
		w45 = weights2[4]
		w55 = weights2[5]
		w54 = weights3[1]
		w53 = weights3[2]
		w52 = weights3[3]
		w51 = weights3[4]
		w50 = weights3[5]
		w40 = weights4[1]
		w30 = weights4[2]
		w20 = weights4[3]
		w10 = weights4[4]
		# maybe i should average instead of multiply? needs testing.
		# currently based on the idea all weights are between 0 and 1.
		# previous used cumulative neighbor multiplication. this drives weights too low.
		# current method multiplies the two weights along isos to the closest edge
		w11 = w01*w10
		w12 = w02*w10 
		w21 = w01*w20
		w22 = w02*w20
		w14 = w04*w15
		w13 = w03*w15
		w24 = w04*w25
		w23 = w03*w25
		w44 = w45*w54
		w34 = w35*w54
		w43 = w54*w45
		w33 = w35*w53
		w41 = w40*w51
		w31 = w30*w51
		w42 = w52*w40
		w32 = w30*w52

		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35,
					w40, w41, w42, w43, w44, w45,
					w50, w51, w52, w53, w54, w55]

		fp.Legs = drawGrid(fp.Poles, 6)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid64_4:	# made from 2 CubicControlPoly6 and 2 CubicControlPoly4.
	def __init__(self, obj , poly6_0, poly4_1, poly6_2, poly4_3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly6_0","ControlGrid64_4","control polygon").Poly6_0 = poly6_0
		obj.addProperty("App::PropertyLink","Poly4_1","ControlGrid64_4","control polygon").Poly4_1 = poly4_1
		obj.addProperty("App::PropertyLink","Poly6_2","ControlGrid64_4","control polygon").Poly6_2 = poly6_2
		obj.addProperty("App::PropertyLink","Poly4_3","ControlGrid64_4","control polygon").Poly4_3 = poly4_3
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_4","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_4","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_4","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles6_0=fp.Poly6_0.Poles
		poles4_1=fp.Poly4_1.Poles
		poles6_2=fp.Poly6_2.Poles
		poles4_3=fp.Poly4_3.Poles
		weights6_0=fp.Poly6_0.Weights
		weights4_1=fp.Poly4_1.Weights
		weights6_2=fp.Poly6_2.Weights
		weights4_3=fp.Poly4_3.Weights
		sext12 = orient_a_to_b(poles6_0,poles4_1)
		quad23 = orient_a_to_b(poles4_1,poles6_2)
		sext34 = orient_a_to_b(poles6_2,poles4_3)
		quad41 = orient_a_to_b(poles4_3,poles6_0)
		if sext12[0]!=poles6_0[0] and sext12[0]==poles6_0[-1]:
			weights6_0=weights6_0[::-1]
		if quad23[0]!=poles4_1[0] and quad23[0]==poles4_1[-1]:
			weights4_1=weights4_1[::-1]
		if sext34[0]!=poles6_2[0] and sext34[0]==poles6_2[-1]:
			weights6_2=weights6_2[::-1]
		if quad41[0]!=poles4_3[0] and quad41[0]==poles4_3[-1]:
			weights4_3=weights4_3[::-1]
		p00 = sext12[0]
		p01 = sext12[1]
		p02 = sext12[2]
		p03 = sext12[3]
		p04 = sext12[4]
		p05 = sext12[5]
		p15 = quad23[1]
		p25 = quad23[2]
		p35 = quad23[3]
		p34 = sext34[1]
		p33 = sext34[2]
		p32 = sext34[3]
		p31 = sext34[4]
		p30 = sext34[5]
		p20 = quad41[1]
		p10 = quad41[2]
		p11 = p01 + (p10 - p00)
		p14 = p04 + (p15 - p05)
		p21 = p31 + (p20 - p30)
		p24 = p25 + (p34 - p35)
		p12 = p02 + (p10 - p00)
		p13 = p03 + (p15 - p05)
		p22 = p32 + (p20 - p30)
		p23 = p33 + (p25 - p35)
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35]
		w00 = weights6_0[0]
		w01 = weights6_0[1]
		w02 = weights6_0[2]
		w03 = weights6_0[3]
		w04 = weights6_0[4]
		w05 = weights6_0[5]
		w15 = weights4_1[1]
		w25 = weights4_1[2]
		w35 = weights4_1[3]
		w34 = weights6_2[1]
		w33 = weights6_2[2]
		w32 = weights6_2[3]
		w31 = weights6_2[4]
		w30 = weights6_2[5]
		w20 = weights4_3[1]
		w10 = weights4_3[2]
		# maybe i should average instead of multiply? needs testing.
		# currently based on the idea all weights are between 0 and 1.
		# previous used cumulative neighbor multiplication. this drives weights too low.
		# current method multiplies the two weights along isos to the closest edge
		w11 = w01*w10
		w12 = w02*w10
		w13 = w03*w15
		w14 = w04*w15
		w21 = w31*w20
		w22 = w32*w20
		w23 = w33*w25
		w24 = w34*w25
		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35]

		fp.Legs = drawGrid(fp.Poles, 6)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid64_3:	# made from 2 CubicControlPoly4 and 1 CubicControlPoly6. degenerate grid.
	def __init__(self, obj , poly4_0, poly6_1, poly4_2):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly4_0","ControlGrid64_3","control polygon").Poly4_0 = poly4_0
		obj.addProperty("App::PropertyLink","Poly6_1","ControlGrid64_3","control polygon").Poly6_1 = poly6_1
		obj.addProperty("App::PropertyLink","Poly4_2","ControlGrid64_3","control polygon").Poly4_2 = poly4_2
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_3","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_3","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_3","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		print ('first one')
		poles4_0=fp.Poly4_0.Poles
		poles6_1=fp.Poly6_1.Poles
		poles4_2=fp.Poly4_2.Poles

		weights4_0=fp.Poly4_0.Weights
		weights6_1=fp.Poly6_1.Weights
		weights4_2=fp.Poly4_2.Weights

		sext12 = orient_a_to_b(poles6_1,poles4_2)
		quad23 = orient_a_to_b(poles4_2,poles4_0)
		quad31 = orient_a_to_b(poles4_0,poles6_1)

		if sext12[0]!=poles6_1[0] and sext12[0]==poles6_1[-1]:
			weights6_1=weights6_1[::-1]
		if quad23[0]!=poles4_2[0] and quad23[0]==poles4_2[-1]:
			weights4_2=weights4_2[::-1]
		if quad31[0]!=poles4_0[0] and quad31[0]==poles4_0[-1]:
			weights4_0=weights4_0[::-1]

		p00 = sext12[0]
		p01 = sext12[1]
		p02 = sext12[2]
		p03 = sext12[3]
		p04 = sext12[4]
		p05 = sext12[5]

		p15 = quad23[1]
		p25 = quad23[2]
		p35 = quad23[3]

		p34 = p35
		p33 = p35
		p32 = p35
		p31 = p35
		p30 = p35

		p20 = quad31[1]
		p10 = quad31[2]

		p11 = p01 + (p10 - p00)
		p14 = p04 + (p15 - p05)
		p12 = p11
		p13 = p14
		p21 = p20 + (p25 - p35)
		p22 = p21
		p23 = p21
		p24 = p21
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35]

		w00 = weights6_1[0]
		w01 = weights6_1[1]
		w02 = weights6_1[2]
		w03 = weights6_1[3]
		w04 = weights6_1[4]
		w05 = weights6_1[5]
		w15 = weights4_2[1]
		w25 = weights4_2[2]
		w35 = weights4_2[3]
		w34 = 1
		w33 = 1
		w32 = 1
		w31 = 1
		w30 = weights4_0[0]
		w20 = weights4_0[1]
		w10 = weights4_0[2]

		# maybe i should average instead of multiply? needs testing.
		# currently based on the idea all weights are between 0 and 1.
		# previous used cumulative neighbor multiplication. this drives weights too low.
		# current method multiplies the two weights along isos to the closest edge
		w11 = w01*w10*0.5
		w12 = w02*w10*0.5
		w13 = w03*w15*0.5
		w14 = w04*w15*0.5
		w21 = w31*w20*0.25
		w22 = w32*w20*0.25
		w23 = w33*w25*0.25
		w24 = w34*w25*0.25
		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35]
		Legs=[0]*22
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		Legs[5]=Part.LineSegment(p10,p11)
		Legs[6]=Part.LineSegment(p12,p13)
		Legs[7]=Part.LineSegment(p14,p15)
		Legs[8]=Part.LineSegment(p20,p21)
		Legs[9]=Part.LineSegment(p24,p25)

		for i in range(10,16):
			Legs[i]=Part.LineSegment(fp.Poles[i-10],fp.Poles[i-4])

		Legs[16]=Part.LineSegment(p10,p20)
		Legs[17]=Part.LineSegment(p11,p21)
		Legs[18]=Part.LineSegment(p14,p24)
		Legs[19]=Part.LineSegment(p15,p25)
		Legs[20]=Part.LineSegment(p20,p30)
		Legs[21]=Part.LineSegment(p25,p35)

		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

### NURBS curves (+poly to input)

class CubicCurve_4:
	def __init__(self, obj , poly):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicCurve_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly","CubicCurve_4","control polygon").Poly = poly
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[[fp.Poly.Poles[0],fp.Poly.Weights[0]],
				[fp.Poly.Poles[1],fp.Poly.Weights[1]],
				[fp.Poly.Poles[2],fp.Poly.Weights[2]],
				[fp.Poly.Poles[3],fp.Poly.Weights[3]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = Bezier_Cubic_curve(WeightedPoles).toShape()

class CubicCurve_6:
	def __init__(self, obj , poly):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicCurve_6 class Init\n")
		obj.addProperty("App::PropertyLink","Poly","CubicCurve_6","control polygon").Poly = poly
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[[fp.Poly.Poles[0],fp.Poly.Weights[0]],
				[fp.Poly.Poles[1],fp.Poly.Weights[1]],
				[fp.Poly.Poles[2],fp.Poly.Weights[2]],
				[fp.Poly.Poles[3],fp.Poly.Weights[3]],
				[fp.Poly.Poles[4],fp.Poly.Weights[4]],
				[fp.Poly.Poles[5],fp.Poly.Weights[5]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = NURBS_Cubic_6P_curve(WeightedPoles).toShape()

class ControlPoly6_Bezier:
	def __init__(self, obj , cubiccurve4_0):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_Bezier class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly6_Bezier","reference Bezier Curve").CubicCurve4_0 = cubiccurve4_0
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly6_Bezier","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly6_Bezier","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly6_Bezier","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process the sketch arc...error check later
		curve=fp.fp.CubicCurve4_0.Shape
		curve.increaseDegree(3)
		start=curve.FirstParameter
		end=curve.LastParameter
		knot1=start+(end-start)/3.0
		knot2=end-(end-start)/3.0
		curve.insertKnot(knot1)
		curve.insertKnot(knot2)
		p0=curve.getPole(1)
		p1=curve.getPole(2)
		p2=curve.getPole(3)
		p3=curve.getPole(4)
		p4=curve.getPole(5)
		p5=curve.getPole(6)
		fp.Poles=[p0,p1,p2,p3,p4,p5]
		# set the weights
		fp.Weights = curve.getWeights()
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p0,p1)
		Leg1=Part.LineSegment(p1,p2)
		Leg2=Part.LineSegment(p2,p3)
		Leg3=Part.LineSegment(p3,p4)
		Leg4=Part.LineSegment(p4,p5)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg3, Leg4]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

### curve derived objects (+curve to input)
class ControlPoly6_FilletBezier:
	def __init__(self, obj , cubiccurve4_0, cubiccurve4_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_FilletBezier class Init\n")
		obj.addProperty("App::PropertyLink","CubicCurve4_0","ControlPoly6_FilletBezier","First reference Bezier Curve").CubicCurve4_0 = cubiccurve4_0
		obj.addProperty("App::PropertyLink","CubicCurve4_1","ControlPoly6_FilletBezier","Second reference Bezier Curve").CubicCurve4_1 = cubiccurve4_1
		obj.addProperty("App::PropertyFloat","Scale_0","ControlPoly6_FilletBezier","First curve tangent scaling").Scale_0 = 2.0
		obj.addProperty("App::PropertyFloat","Scale_3","ControlPoly6_FilletBezier","Second curve tangent scaling READ ONLY").Scale_3 = 2.0
		obj.addProperty("App::PropertyFloat","Scale_1","ControlPoly6_FilletBezier","First curve inner scaling READ ONLY").Scale_1 = 2.0
		obj.setEditorMode("Scale_1", 0)
		obj.addProperty("App::PropertyFloat","Scale_2","ControlPoly6_FilletBezier","Second curve inner scaling").Scale_2 = 2.0
		obj.setEditorMode("Scale_2", 0)
		obj.addProperty("App::PropertyInteger", "autoG3", "ControlPoly6_FilletBezier", "Try to set G3 to the input polys").autoG3 = 0
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly6_FilletBezier","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly6_FilletBezier","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly6_FilletBezier","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles_0 = fp.CubicCurve4_0.Poly.Poles
		poles_1 = fp.CubicCurve4_1.Poly.Poles

		weights_0 = fp.CubicCurve4_0.Poly.Weights
		weights_1 = fp.CubicCurve4_1.Poly.Weights

		blend_0 = orient_a_to_b(poles_0,poles_1)

		blend_1_flip = orient_a_to_b(poles_1,poles_0)
		blend_1 = blend_1_flip[::-1]

		if blend_0[0] != poles_0[0] and blend_0[0] == poles_0[-1]:
			weights_0=weights_0[::-1]
		if blend_1[0] != poles_1[0] and blend_1[0] == poles_1[-1]:
			weights_1=weights_1[::-1]

		scale_0 = fp.Scale_0
		scale_1 = fp.Scale_1
		scale_2 = fp.Scale_2
		scale_3 = fp.Scale_3

		if fp.autoG3 == 0:
			blend = blend_poly_2x4_1x6(blend_0, weights_0, blend_1, weights_1, scale_0, scale_1, scale_2, scale_3)		
		
		if fp.autoG3 == 1:
			blend = blendG3_poly_2x4_1x6(blend_0, weights_0, blend_1, weights_1, scale_0, scale_1, scale_2, scale_3)

		
		fp.Poles = blend[0]
		fp.Weights = blend[1]
		fp.Scale_1 = blend[2]
		fp.Scale_2 = blend[3]
		
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(fp.Poles[0],fp.Poles[1])
		Leg1=Part.LineSegment(fp.Poles[1],fp.Poles[2])
		Leg2=Part.LineSegment(fp.Poles[2],fp.Poles[3])
		Leg3=Part.LineSegment(fp.Poles[3],fp.Poles[4])
		Leg4=Part.LineSegment(fp.Poles[4],fp.Poles[5])
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg3, Leg4]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class Point_onCurve:
	def __init__(self, obj ,NL_Curve,u):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nPoint_onCurve class Init\n")
		obj.addProperty("App::PropertyLink","NL_Curve","Point_onCurve","reference curve").NL_Curve = NL_Curve
		lower = 0.0
		upper = 1.0
		step = 0.01
		obj.addProperty("App::PropertyFloatConstraint","u","Point_onCurve","parameter along curve").u = (u, lower, upper, step)
		obj.addProperty("App::PropertyVector","Position","Point_onCurve","position vector").Position
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		fp.Position=fp.NL_Curve.Shape.Curve.value(fp.u)
		fp.Shape = Part.Point(fp.Position).toShape()

### point derived objects (+point to input)
class ControlPoly4_segment:
	def __init__(self, obj , NL_Curve, Point_onCurve_0, Point_onCurve_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly4_segment class Init\n")
		obj.addProperty("App::PropertyLink","NL_Curve","ControlPoly4_segment","reference Curve").NL_Curve = NL_Curve
		obj.addProperty("App::PropertyLink","Point_onCurve_0","ControlPoly4_segment","first reference point").Point_onCurve_0 = Point_onCurve_0
		obj.addProperty("App::PropertyLink","Point_onCurve_1","ControlPoly4_segment","second reference point").Point_onCurve_1 = Point_onCurve_1
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_3L","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_3L","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_3L","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the curve
		curve=fp.NL_Curve.Shape.Curve
		# get the u span
		u0=curve.parameter(fp.Point_onCurve_0.Position)
		print(u0)
		u1=curve.parameter(fp.Point_onCurve_1.Position)
		print(u1)
		if u0<u1:
			a=u0
			b=u1
		elif u1<u0:
			a=u1
			b=u0
		# cut the curve...need to copy first to keep original?
		curve.segment(a,b)
		fp.Poles=curve.getPoles()
		fp.Weights=curve.getWeights()

		# prepare visualization elements
		p00=fp.Poles[0]
		p01=fp.Poles[1]
		p20=fp.Poles[2]
		p21=fp.Poles[3]

		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p20)
		Leg2=Part.LineSegment(p20,p21)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

### NURBS surfaces (+grid to input)

class CubicSurface_44:
	def __init__(self, obj , grid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicSurface_44 class Init\n")
		obj.addProperty("App::PropertyLink","Grid","CubicSurface_44","control grid").Grid = grid
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[
			[fp.Grid.Poles[0],fp.Grid.Weights[0]],
			[fp.Grid.Poles[1],fp.Grid.Weights[1]],
			[fp.Grid.Poles[2],fp.Grid.Weights[2]],
			[fp.Grid.Poles[3],fp.Grid.Weights[3]],
			[fp.Grid.Poles[4],fp.Grid.Weights[4]],
			[fp.Grid.Poles[5],fp.Grid.Weights[5]],
			[fp.Grid.Poles[6],fp.Grid.Weights[6]],
			[fp.Grid.Poles[7],fp.Grid.Weights[7]],
			[fp.Grid.Poles[8],fp.Grid.Weights[8]],
			[fp.Grid.Poles[9],fp.Grid.Weights[9]],
			[fp.Grid.Poles[10],fp.Grid.Weights[10]],
			[fp.Grid.Poles[11],fp.Grid.Weights[11]],
			[fp.Grid.Poles[12],fp.Grid.Weights[12]],
			[fp.Grid.Poles[13],fp.Grid.Weights[13]],
			[fp.Grid.Poles[14],fp.Grid.Weights[14]],
			[fp.Grid.Poles[15],fp.Grid.Weights[15]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = Bezier_Bicubic_surf(WeightedPoles).toShape()

class CubicSurface_66:
	def __init__(self, obj , grid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicSurface_66 class Init\n")
		obj.addProperty("App::PropertyLink","Grid","CubicSurface_66","control grid").Grid = grid
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[
			[fp.Grid.Poles[0],fp.Grid.Weights[0]],
			[fp.Grid.Poles[1],fp.Grid.Weights[1]],
			[fp.Grid.Poles[2],fp.Grid.Weights[2]],
			[fp.Grid.Poles[3],fp.Grid.Weights[3]],
			[fp.Grid.Poles[4],fp.Grid.Weights[4]],
			[fp.Grid.Poles[5],fp.Grid.Weights[5]],
			[fp.Grid.Poles[6],fp.Grid.Weights[6]],
			[fp.Grid.Poles[7],fp.Grid.Weights[7]],
			[fp.Grid.Poles[8],fp.Grid.Weights[8]],
			[fp.Grid.Poles[9],fp.Grid.Weights[9]],
			[fp.Grid.Poles[10],fp.Grid.Weights[10]],
			[fp.Grid.Poles[11],fp.Grid.Weights[11]],
			[fp.Grid.Poles[12],fp.Grid.Weights[12]],
			[fp.Grid.Poles[13],fp.Grid.Weights[13]],
			[fp.Grid.Poles[14],fp.Grid.Weights[14]],
			[fp.Grid.Poles[15],fp.Grid.Weights[15]],
			[fp.Grid.Poles[16],fp.Grid.Weights[16]],
			[fp.Grid.Poles[17],fp.Grid.Weights[17]],
			[fp.Grid.Poles[18],fp.Grid.Weights[18]],
			[fp.Grid.Poles[19],fp.Grid.Weights[19]],
			[fp.Grid.Poles[20],fp.Grid.Weights[20]],
			[fp.Grid.Poles[21],fp.Grid.Weights[21]],
			[fp.Grid.Poles[22],fp.Grid.Weights[22]],
			[fp.Grid.Poles[23],fp.Grid.Weights[23]],
			[fp.Grid.Poles[24],fp.Grid.Weights[24]],
			[fp.Grid.Poles[25],fp.Grid.Weights[25]],
			[fp.Grid.Poles[26],fp.Grid.Weights[26]],
			[fp.Grid.Poles[27],fp.Grid.Weights[27]],
			[fp.Grid.Poles[28],fp.Grid.Weights[28]],
			[fp.Grid.Poles[29],fp.Grid.Weights[29]],
			[fp.Grid.Poles[30],fp.Grid.Weights[30]],
			[fp.Grid.Poles[31],fp.Grid.Weights[31]],
			[fp.Grid.Poles[32],fp.Grid.Weights[32]],
			[fp.Grid.Poles[33],fp.Grid.Weights[33]],
			[fp.Grid.Poles[34],fp.Grid.Weights[34]],
			[fp.Grid.Poles[35],fp.Grid.Weights[35]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = NURBS_Cubic_66_surf(WeightedPoles).toShape()

class CubicSurface_64:
	def __init__(self, obj , grid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicSurface_64 class Init\n")
		obj.addProperty("App::PropertyLink","Grid","CubicSurface_64","control grid").Grid = grid
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[
			[fp.Grid.Poles[0],fp.Grid.Weights[0]],
			[fp.Grid.Poles[1],fp.Grid.Weights[1]],
			[fp.Grid.Poles[2],fp.Grid.Weights[2]],
			[fp.Grid.Poles[3],fp.Grid.Weights[3]],
			[fp.Grid.Poles[4],fp.Grid.Weights[4]],
			[fp.Grid.Poles[5],fp.Grid.Weights[5]],
			[fp.Grid.Poles[6],fp.Grid.Weights[6]],
			[fp.Grid.Poles[7],fp.Grid.Weights[7]],
			[fp.Grid.Poles[8],fp.Grid.Weights[8]],
			[fp.Grid.Poles[9],fp.Grid.Weights[9]],
			[fp.Grid.Poles[10],fp.Grid.Weights[10]],
			[fp.Grid.Poles[11],fp.Grid.Weights[11]],
			[fp.Grid.Poles[12],fp.Grid.Weights[12]],
			[fp.Grid.Poles[13],fp.Grid.Weights[13]],
			[fp.Grid.Poles[14],fp.Grid.Weights[14]],
			[fp.Grid.Poles[15],fp.Grid.Weights[15]],
			[fp.Grid.Poles[16],fp.Grid.Weights[16]],
			[fp.Grid.Poles[17],fp.Grid.Weights[17]],
			[fp.Grid.Poles[18],fp.Grid.Weights[18]],
			[fp.Grid.Poles[19],fp.Grid.Weights[19]],
			[fp.Grid.Poles[20],fp.Grid.Weights[20]],
			[fp.Grid.Poles[21],fp.Grid.Weights[21]],
			[fp.Grid.Poles[22],fp.Grid.Weights[22]],
			[fp.Grid.Poles[23],fp.Grid.Weights[23]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = NURBS_Cubic_64_surf(WeightedPoles).toShape()

# 11/25/2016. update 12/09/2016.
# There a mess to clean up in re. passing the pole/weight list to FreeCAD. 
# The 3 legacy _surf functions used above want a list of 16 X [[x,y,z],w] as input,
# but internally, they run two loops to break it back into 2D array form to feed into the actual BSplineSurface(). 
# This is only because this was the first working example i found for BSplineSurface. This was fine for a long time. Not anymore.
# To rotate grids easily, i need to rewrite all the code to stay in 2D array form at all times. 'all the code' means anything related to 
# grid generators and nurbs surfaces.
#
# a BSplineSurface with u along x, v along y, looked at from the top returns the following poles list
#
# [[00,01,02,03],[10,11,12,13],[20,21,22,23],[30,31,32,33]]
#
# with the following topology (rows of the list read UP in xyz topo)
#	v=1			1,1
#	03 13 23 33
#	02 12 22 32
#	01 11 21 31
#	00 10 20 30 
#u,v=0,0		u=1
#
# So the pole list is  list of pole columns
# But the list reads as follows in the interpreter (rows DOWN)
#	00 10 20 30
#	01 11 21 31
#	02 12 22 23
#	03 13 23 33
#
# numpy.Rot90(array,n) operates ccw on the DOWN version, which is cw in xyz topo.
#
# Unfortunately, all my grid numbering schemes so far were row>column, as in
#
#	30 31 32 33 
#	20 21 22 23
#	10 11 12 13
#	00 01 02 03
#
# this will be annoying to rewrite.
#

#### surface derived objects (+surf to input)

# need to separate a function out that determines the surface paramters corresponding to endpoints of a curve
# along a border of the surface
# develop here until ready, then move up to stand alone functions
# will be used by ControlGrid44_EdgeSegment and ControlGrid44_2EdgeSegments

def paramsSurface44BorderSegmentCurve(AN_Surface, AN_Curve, tol, degenTol):
	# from a surface and a curve that matches a segment of a border edge of the sruface,
	# return the cut direction (u or v), and the cut parameters
	# only written for a 16 control point surface (4X4)

	surface=AN_Surface.Shape.Surface
	curve=AN_Curve.Shape.Curve
	p0 = curve.StartPoint
	# print ('p0 = ', p0)
	p1 = curve.EndPoint
	# print ('p1 = ', p1)
	# get parameter span from cutting points
	param0=surface.parameter(p0) # returns (u,v) on surface of curve start point
	# print ('param0: ', param0)
	param1=surface.parameter(p1) # returns (u,v) on surface of curve end point
	# print ('param1: ', param1)
	# CAUTION
	# the values returned by .parameter() are random if the curve point is on a degenerate (collapsed) edge

	# look for an identify degenerate edges
	if (AN_Surface.Grid.Poles[0] == AN_Surface.Grid.Poles[3]):
		degen_grid = 1
		degen_point = AN_Surface.Grid.Poles[0]
		degen_t = 0
	elif (AN_Surface.Grid.Poles[3] == AN_Surface.Grid.Poles[15]):
		degen_grid = 1
		degen_point = AN_Surface.Grid.Poles[3]
		degen_t = 1
	elif (AN_Surface.Grid.Poles[15] == AN_Surface.Grid.Poles[12]):
		degen_grid = 1
		degen_point = AN_Surface.Grid.Poles[12]
		degen_t = 1
	elif (AN_Surface.Grid.Poles[12] == AN_Surface.Grid.Poles[0]):
		degen_grid = 1
		degen_point = AN_Surface.Grid.Poles[0]
		degen_t = 0
	else:
		degen_grid = 0
		degen_point = 0

	# even if the grid is degenerate, the degnerate point may not be at the cutting curve endpoints
	# and therefore may not interfere with paramter determination.
	degen_cut = 0
	if (degen_grid == 1):
		# compare to curve start point
		if (equalVectors(p0, degen_point, .001)):
			# print ('degenerate point matches curve start')
			# desired segment include degenerate point
			degen_cut = 1
			# the parameters of interest come from the end point
			param_cut = param1
		# compare to curve end point
		if (equalVectors(p1, degen_point, .001)):
			# print ('degenerate point matches curve end')
			# desired segment include degenerate point
			degen_cut = 1
			# the parameters of interest come from the start point
			param_cut = param0

	# for degenerate cuts
	if (degen_cut == 1):
		if (param_cut[0]<0.001 or param_cut[0]>.999):
			segdir = 'v'
			# print ("segmentation along", segdir)
			if (degen_t == 0):
				t0 = 0.0
				t1=param_cut[1]
			if (degen_t == 1):
				t0 = param_cut[1]
				t1= 1.0

		if (param_cut[1]<0.001 or param_cut[1]>.999):
			segdir = 'u'
			# print ("segmentation along", segdir)
			if (degen_t == 0):
				t0 = 0.0
				t1=param_cut[0]
			if (degen_t == 1):
				t0 = param_cut[0]
				t1= 1.0
			

	# for non degenerate cuts
	if (degen_cut == 0):
		if ((param0[0]<0.001 and param1[0]<0.001) or (param0[0]>0.999 and param1[0]>0.999)): # if u is constant 0 or constant 1 along curve
			segdir = 'v'
			# print ("segmentation along", segdir)
			if param0[1] < param1[1]:
				t0=param0[1]
				t1=param1[1]
			if param0[1] > param1[1]:
				t0=param1[1]
				t1=param0[1]
		if ((param0[1]<0.001 and param1[1]<0.001) or (param0[1]>0.999 and param1[1]>0.999)): # if v is constant 0 or constant 1 along curve
			segdir = 'u'
			# print ("segmentation along", segdir)
			if param0[0] < param1[0]:
				t0=param0[0]
				t1=param1[0]
			if param0[0] > param1[0]:
				t0=param1[0]
				t1=param0[0]
		
	# filter out t0<0 and t1>1 that may occur when the xyz position is projected to uv
	if t0<0:
		t0=0
	if t1>1:
		t1=1

	print ('paramsSurfaceBorderSegmentCurve')
	print ('segdir = ', segdir)
	print ('t0 = ', t0)
	print ('t1 = ', t1)
	print ('')

	return [segdir, t0, t1]

class ControlGrid44_EdgeSegment:
	def __init__(self, obj , NL_Surface, NL_Curve):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_EdgeSegment class Init\n")
		obj.addProperty("App::PropertyLink","NL_Surface","ControlGrid44_EdgeSegment","Base Surface").NL_Surface = NL_Surface
		obj.addProperty("App::PropertyLink","NL_Curve","ControlGrid44_EdgeSegment","reference Curve").NL_Curve = NL_Curve
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_EdgeSegment","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_EdgeSegment","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_EdgeSegment","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''

		# get segmentation parameters
		cutParams = paramsSurface44BorderSegmentCurve(fp.NL_Surface, fp.NL_Curve, .001, .001)
		segdir = cutParams[0]
		t0 = cutParams[1]
		t1 = cutParams[2]
		print ('segdir: ', segdir)
		print ('t0 ', t0)
		print ('t1 ', t1)

		# create surface segment. this works very nicely most of the time, but! 
		#sometimes .segment returns [[vector],[vector],[vector],[vector]] instead of a whole grid.
		surface = fp.NL_Surface.Shape.Surface

		if segdir=='u':
			surface.segment(t0,t1,0,1)
		if segdir=='v':
			surface.segment(0,1,t0,t1) # 
		# extract the control grid information from the surface segment
		poles_2dArray = surface.getPoles()
		# extract the control grid information from the surface segment
		# first version flips the grid along v???? need to run down 3 to 0 on v while looping 0 to 3 on u ?????
		# this is internal to ArachNURBS. segmenting directly in FreeCAD python console does not flip sontrol points.
		# one day i need to revisit my control point ordering scheme to avoid this flip
		# print(poles_2dArray)
		if len(poles_2dArray[0]) == 1:
			print ('collapsed surface segment')
			#print ('segdira: ', segdira) # segdira undefined?? not sure what the intention was here
			#print ('segdirb: ', segdirb) # segdirb undefined?? not sure what the intention was here
			#print ('s0 ', s0) # s0 undefined?? not sure what the intention was here
			#print ('s1 ', s1) # s1 undefined?? not sure what the intention was here
			print ('t0 ', t0)
			print ('t1 ', t1)
			print ('poles_2dArray', poles_2dArray)
		
		fp.Poles = [poles_2dArray[3][0],
					poles_2dArray[3][1],
					poles_2dArray[3][2],
					poles_2dArray[3][3],
					poles_2dArray[2][0],
					poles_2dArray[2][1],
					poles_2dArray[2][2],
					poles_2dArray[2][3],
					poles_2dArray[1][0],
					poles_2dArray[1][1],
					poles_2dArray[1][2],
					poles_2dArray[1][3],
					poles_2dArray[0][0],
					poles_2dArray[0][1],
					poles_2dArray[0][2],
					poles_2dArray[0][3]]

		weights_2dArray = surface.getWeights()
		fp.Weights = [weights_2dArray[3][0],
					weights_2dArray[3][1],
					weights_2dArray[3][2],
					weights_2dArray[3][3],
					weights_2dArray[2][0],
					weights_2dArray[2][1],
					weights_2dArray[2][2],
					weights_2dArray[2][3],
					weights_2dArray[1][0],
					weights_2dArray[1][1],
					weights_2dArray[1][2],
					weights_2dArray[1][3],
					weights_2dArray[0][0],
					weights_2dArray[0][1],
					weights_2dArray[0][2],
					weights_2dArray[0][3]]
		
		fp.Legs = drawGrid(fp.Poles, 4)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid44_2EdgeSegments:
	def __init__(self, obj , NL_Surface, NL_Curve_a,NL_Curve_b):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_2EdgeSegments class Init\n")
		obj.addProperty("App::PropertyLink","NL_Surface","ControlGrid44_2EdgeSegments","Base Surface").NL_Surface = NL_Surface
		obj.addProperty("App::PropertyLink","NL_Curve_a","ControlGrid44_2EdgeSegments","reference Curve a").NL_Curve_a = NL_Curve_a
		obj.addProperty("App::PropertyLink","NL_Curve_b","ControlGrid44_2EdgeSegments","reference Curve b").NL_Curve_b = NL_Curve_b
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_2EdgeSegments","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_2EdgeSegments","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_2EdgeSegments","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		
		# get segmentation parameters
		cutParamsa = paramsSurface44BorderSegmentCurve(fp.NL_Surface, fp.NL_Curve_a, .001, .001)
		segdira = cutParamsa[0]
		s0 = cutParamsa[1]
		s1 = cutParamsa[2]
		print ('segdira: ', segdira)
		print ('s0 ', s0)
		print ('s1 ', s1)
		# get segmentation parameters
		cutParamsb = paramsSurface44BorderSegmentCurve(fp.NL_Surface, fp.NL_Curve_b, .001, .001)
		segdirb = cutParamsb[0]
		t0 = cutParamsb[1]
		t1 = cutParamsb[2]
		print ('segdirb: ', segdirb)
		print ('t0 ', t0)
		print ('t1 ', t1)
		
		
		'''
		# get surface
		surface=fp.NL_Surface.Shape.Surface
		# get cutting points from curves
		curve_a=fp.NL_Curve_a.Shape.Curve
		a0 = curve_a.StartPoint
		a1 = curve_a.EndPoint

		curve_b=fp.NL_Curve_b.Shape.Curve
		b0 = curve_b.StartPoint
		b1 = curve_b.EndPoint


		# determine u or v segmentation and get parameter span from cutting points for curve a
		param_a0=surface.parameter(a0)
		#print 'param_a0: ', param_a0
		param_a1=surface.parameter(a1)
		#print 'param_a1: ', param_a1
		if ((param_a0[0]<0.001 and param_a1[0]<0.001) or (param_a0[0]>0.999 and param_a1[0]>0.999)): # if u is constant 0 or constant 1 along curve
			segdira = 'v'
			if param_a0[1] < param_a1[1]:
				s0=param_a0[1]
				s1=param_a1[1]
			if param_a0[1] > param_a1[1]:
				s0=param_a1[1]
				s1=param_a0[1]
		if ((param_a0[1]<0.001 and param_a1[1]<0.001) or (param_a0[1]>0.999 and param_a1[1]>0.999)): # if v is constant 0 or constant 1 along curve
			segdira = 'u'
			if param_a0[0] < param_a1[0]:
				s0=param_a0[0]
				s1=param_a1[0]
			if param_a0[0] > param_a1[0]:
				s0=param_a1[0]
				s1=param_a0[0]
		# filter out s0<0 and s1>1 that may occur when the xyz position is projected to uv
		if s0<0:
			s0=0
		if s1>1:
			s1=1

		# determine u or v segmentation and get parameter span from cutting points for curve b
		param_b0=surface.parameter(b0)
		#print 'param_b0: ', param_b0
		param_b1=surface.parameter(b1)
		#print 'param_b1: ', param_b1
		if ((param_b0[0]<0.001 and param_b1[0]<0.001) or (param_b0[0]>0.999 and param_b1[0]>0.999)): # if u is constant 0 or constant 1 along curve
			segdirb = 'v'
			if param_b0[1] < param_b1[1]:
				t0=param_b0[1]
				t1=param_b1[1]
			if param_b0[1] > param_b1[1]:
				t0=param_b1[1]
				t1=param_b0[1]
		if ((param_b0[1]<0.001 and param_b1[1]<0.001) or (param_b0[1]>0.999 and param_b1[1]>0.999)): # if v is constant 0 or constant 1 along curve
			segdirb = 'u'
			if param_b0[0] < param_b1[0]:
				t0=param_b0[0]
				t1=param_b1[0]
			if param_b0[0] > param_b1[0]:
				t0=param_b1[0]
				t1=param_b0[0]
		# filter out t0<0 and t1>1 that may occur when the xyz position is projected to uv
		if t0<0:
			t0=0
		if t1>1:
			t1=1
		'''

		# create surface segment. this works very nicely most of the time, but! 
		#sometimes .segment returns [[vector],[vector],[vector],[vector]] instead of a whole grid.
		surface = fp.NL_Surface.Shape.Surface

		if segdira=='u' and segdirb=='v':
			surface.segment(s0,s1,t0,t1)
		if segdira=='v' and segdirb=='u':
			surface.segment(t0,t1,s0,s1) # 
		# extract the control grid information from the surface segment
		# first version flips the grid along v???? need to run down 3 to 0 on v while looping 0 to 3 on u ?????
		# this is internal to ArachNURBS. segmenting directly in FreeCAD python console does not flip sontrol points.
		# one day i need to revisit my control point ordering scheme to avoid this flip
		poles_2dArray = surface.getPoles()
		if len(poles_2dArray[0]) == 1:
			print ('collapsed surface segment')
			print ('segdira: ', segdira)
			print ('segdirb: ', segdirb)
			print ('s0 ', s0)
			print ('s1 ', s1)
			print ('t0 ', t0)
			print ('t1 ', t1)
			print ('poles_2dArray', poles_2dArray)


		fp.Poles = [poles_2dArray[3][0],
					poles_2dArray[3][1],
					poles_2dArray[3][2],
					poles_2dArray[3][3],
					poles_2dArray[2][0],
					poles_2dArray[2][1],
					poles_2dArray[2][2],
					poles_2dArray[2][3],
					poles_2dArray[1][0],
					poles_2dArray[1][1],
					poles_2dArray[1][2],
					poles_2dArray[1][3],
					poles_2dArray[0][0],
					poles_2dArray[0][1],
					poles_2dArray[0][2],
					poles_2dArray[0][3]]

		weights_2dArray = surface.getWeights()
		fp.Weights = [weights_2dArray[3][0],
					weights_2dArray[3][1],
					weights_2dArray[3][2],
					weights_2dArray[3][3],
					weights_2dArray[2][0],
					weights_2dArray[2][1],
					weights_2dArray[2][2],
					weights_2dArray[2][3],
					weights_2dArray[1][0],
					weights_2dArray[1][1],
					weights_2dArray[1][2],
					weights_2dArray[1][3],
					weights_2dArray[0][0],
					weights_2dArray[0][1],
					weights_2dArray[0][2],
					weights_2dArray[0][3]]

		fp.Legs = drawGrid(fp.Poles, 4)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid64_2Grid44:  # surfaces not strictly used as input, but this is the logical position
	def __init__(self, obj , Grid_0, Grid_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_2Grid44 class Init\n")
		obj.addProperty("App::PropertyLink","Grid_0","ControlGrid64_2Grid44","first reference 4X4 grid").Grid_0 = Grid_0
		obj.addProperty("App::PropertyLink","Grid_1","ControlGrid64_2Grid44","second reference 4X4 grid").Grid_1 = Grid_1
		obj.addProperty("App::PropertyFloat","scale_tangent_0","ControlGrid64_2Grid44","first grid tangent scale").scale_tangent_0 = 2.0
		obj.addProperty("App::PropertyFloat","scale_tangent_1","ControlGrid64_2Grid44","second grid tangent scale").scale_tangent_1 = 2.0
		obj.addProperty("App::PropertyFloatList","scale_inner_0","ControlGrid64_2Grid44","first side inner scale").scale_inner_0 = [2.0, 2.0, 2.0, 2.0]
		#obj.setEditorMode("scale_inner_0", 0)
		obj.addProperty("App::PropertyFloatList","scale_inner_1","ControlGrid64_2Grid44","second side inner scale").scale_inner_1 = [2.0, 2.0, 2.0, 2.0]
		#obj.setEditorMode("scale_inner_1", 0)
		obj.addProperty("App::PropertyInteger", "autoG3", "ControlGrid64_2Grid44", "Try to set G3 along the external seams").autoG3 = 0
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_2Grid44","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_2Grid44","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_2Grid44","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# this is the monolithic version. This deserves a future breakdown:
		# -find seam points
		# -rotate grids to match uv flow
		# -extract and line up grid rows in pairs
		# -blend: upgrade, stitch, scale
		# -stack each blend poly back into a grid

		# extract corner points
		corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[3],fp.Grid_0.Poles[15],fp.Grid_0.Poles[12]]
		corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[3],fp.Grid_1.Poles[15],fp.Grid_1.Poles[12]]

		# additional processing for degenerate grids
		# do not assume which edge is collapsed. it is predictable for ControlGrid44_3_Rotate and its segmentation,
		# but future segments may not be. for example when we eventually segment 64s and 66s, which may also include
		# degenerate grids

		# grid 0

		if (equalVectors(corners_0[0], corners_0[1], .000001)):
			degen_0 = 1
			degen_0_index = [0, 1]
		elif (equalVectors(corners_0[1], corners_0[2], .000001)):
			degen_0 = 1
			degen_0_index = [1, 2]
		elif (equalVectors(corners_0[2], corners_0[3], .000001)):
			degen_0 = 1
			degen_0_index = [2, 3]
		elif (equalVectors(corners_0[3], corners_0[0], .000001)):
			degen_0 = 1
			degen_0_index = [0,3]
		else:
			degen_0 = 0
			degen_0_index = []
		
		print ("degen_0: ", degen_0)
		print ("degen_0_index: ", degen_0_index)

		# grid 1
		if (equalVectors(corners_1[0], corners_1[1], .000001)):
			degen_1 = 1
			degen_1_index = [0, 1]
		elif (equalVectors(corners_1[1], corners_1[2], .000001)):
			degen_1 = 1
			degen_1_index = [1, 2]
		elif (equalVectors(corners_1[2], corners_1[3], .000001)):
			degen_1 = 1
			degen_1_index = [2, 3]
		elif (equalVectors(corners_1[3], corners_1[0], .000001)):
			degen_1 = 1
			degen_1_index = [0,3]
		else:
			degen_1 = 0
			degen_1_index = []

		print ("degen_1: ", degen_1)
		print ("degen_1_index: ", degen_1_index)
		
		degen = degen_0 + degen_1

		# find all matching corner points across the two grids
		# degenerate edges will cause repeat values
		seam_index_raw_0 = []
		seam_index_raw_1 = []
		for i in range(0,4):
			for j in range(0,4):
				if equalVectors(corners_0[i],corners_1[j],0.000001):
					seam_index_raw_0.append(i)
					seam_index_raw_1.append(j)
		seam_index_dedupe_0 = [*set(seam_index_raw_0)] # the * unpacks the set into the list
		seam_index_dedupe_0.sort()
		print("seam_index_dedupe_0: ",seam_index_dedupe_0)
		seam_index_dedupe_1 = [*set(seam_index_raw_1)]
		seam_index_dedupe_1.sort()
		print("seam_index_dedupe_1: ",seam_index_dedupe_1)

		if (len(seam_index_dedupe_0) == 3):
			# the true seam is the non-degenrate point, and the degenerate point closest to it
			for i in range(0,3):
				if (seam_index_dedupe_0[i] not in degen_0_index):
					non_degen_index_0 = i
					non_degen_corner_0 = seam_index_dedupe_0[i]
			print ("non_degen_index_0: ", non_degen_index_0)
			print ("non_degen_corner_0: ", non_degen_corner_0)
			if (non_degen_index_0 == 0 ):
				if ((seam_index_dedupe_0[1]-seam_index_dedupe_0[0]) == 1 ):
					seam_0 = [seam_index_dedupe_0[0], seam_index_dedupe_0[1]]
				else:
					seam_0 = [seam_index_dedupe_0[0], seam_index_dedupe_0[2]]
			if (non_degen_index_0 == 1 ):
				if ((seam_index_dedupe_0[1]-seam_index_dedupe_0[0]) == 1 ):
					seam_0 = [seam_index_dedupe_0[0], seam_index_dedupe_0[1]]
				else:
					seam_0 = [seam_index_dedupe_0[1], seam_index_dedupe_0[2]]
			if (non_degen_index_0 == 2 ):
				if ((seam_index_dedupe_0[2]-seam_index_dedupe_0[1]) == 1 ):
					seam_0 = [seam_index_dedupe_0[1], seam_index_dedupe_0[2]]
				else:
					seam_0 = [seam_index_dedupe_0[0], seam_index_dedupe_0[2]]
		elif (len(seam_index_dedupe_0) == 2):
			seam_0 = seam_index_dedupe_0
		print ('seam_0 ', seam_0)


		if (len(seam_index_dedupe_1) == 3):
			# the true seam is the non-degenrate point, and the degenerate point closest to it
			for i in range(0,3):
				if (seam_index_dedupe_1[i] not in degen_1_index):
					non_degen_index_1 = i
					non_degen_corner_1 = seam_index_dedupe_1[i]
			print ("non_degen_index_1: ", non_degen_index_1)
			print ("non_degen_corner_1: ", non_degen_corner_1)
			if (non_degen_index_1 == 0 ):
				if ((seam_index_dedupe_1[1]-seam_index_dedupe_1[0]) == 1 ):
					seam_1 = [seam_index_dedupe_1[0], seam_index_dedupe_1[1]]
				else:
					seam_1 = [seam_index_dedupe_1[0], seam_index_dedupe_1[2]]
			if (non_degen_index_1 == 1 ):
				if ((seam_index_dedupe_1[1]-seam_index_dedupe_1[0]) == 1 ):
					seam_1 = [seam_index_dedupe_1[0], seam_index_dedupe_1[1]]
				else:
					seam_1 = [seam_index_dedupe_1[1], seam_index_dedupe_1[2]]
			if (non_degen_index_1 == 2 ):
				if ((seam_index_dedupe_1[2]-seam_index_dedupe_1[1]) == 1 ):
					seam_1 = [seam_index_dedupe_1[1], seam_index_dedupe_1[2]]
				else:
					seam_1 = [seam_index_dedupe_1[0], seam_index_dedupe_1[2]]
		elif (len(seam_index_dedupe_1) == 2):
			seam_1 = seam_index_dedupe_1
		print ('seam_1 ', seam_1)

		# rotate the grids so that the seam is on the right side for Grid_0 and the left side for Grid_1
		# in the ideal case, no rotation is required:
		# seam_index[0]=[1,0], and
		# seam_index[1]=[2,3]

		# left grid correction rotation
		if seam_0 == [1,2]:
			rotate_0 = 0 # times 90 degrees clockwise
		if seam_0 == [2,3]:
			rotate_0 = 1
		if seam_0 == [0,3]:
			rotate_0 = 2 
		if seam_0 == [0,1]:
			rotate_0 = 3 

		# right grid correction rotation
		if seam_1 == [0,3] or seam_1 == [3,0]:
			rotate_1 = 0 # times 90 degrees clockwise
		if seam_1 == [0,1] or seam_1 == [1,0]:
			rotate_1 = 1 
		if seam_1 == [1,2] or seam_1 == [2,1]:
			rotate_1 = 2 
		if seam_1 == [3,2] or seam_1 == [2,3]:
			rotate_1 = 3

		print ('rotate left: ', rotate_0)
		print ('rotate right: ', rotate_1)

		# get grid data back into array
		lin_poles_0 = fp.Grid_0.Poles
		lin_weights_0 = fp.Grid_0.Weights

		lin_poles_1 = fp.Grid_1.Poles
		lin_weights_1 = fp.Grid_1.Weights

		# first shot: simple partition.this is an array of rows
		poles_0 = [[lin_poles_0[0], lin_poles_0[1], lin_poles_0[2], lin_poles_0[3]],
					[lin_poles_0[4], lin_poles_0[5], lin_poles_0[6], lin_poles_0[7]],
					[lin_poles_0[8], lin_poles_0[9], lin_poles_0[10], lin_poles_0[11]],
					[lin_poles_0[12], lin_poles_0[13], lin_poles_0[14], lin_poles_0[15]]]

		weights_0 = [[lin_weights_0[0], lin_weights_0[1], lin_weights_0[2], lin_weights_0[3]],
					[lin_weights_0[4], lin_weights_0[5], lin_weights_0[6], lin_weights_0[7]],
					[lin_weights_0[8], lin_weights_0[9], lin_weights_0[10], lin_weights_0[11]],
					[lin_weights_0[12], lin_weights_0[13], lin_weights_0[14], lin_weights_0[15]]]

		poles_1 = [[lin_poles_1[0], lin_poles_1[1], lin_poles_1[2], lin_poles_1[3]],
					[lin_poles_1[4], lin_poles_1[5], lin_poles_1[6], lin_poles_1[7]],
					[lin_poles_1[8], lin_poles_1[9], lin_poles_1[10], lin_poles_1[11]],
					[lin_poles_1[12], lin_poles_1[13], lin_poles_1[14], lin_poles_1[15]]]

		weights_1 = [[lin_weights_1[0], lin_weights_1[1], lin_weights_1[2], lin_weights_1[3]],
					[lin_weights_1[4], lin_weights_1[5], lin_weights_1[6], lin_weights_1[7]],
					[lin_weights_1[8], lin_weights_1[9], lin_weights_1[10], lin_weights_1[11]],
					[lin_weights_1[12], lin_weights_1[13], lin_weights_1[14], lin_weights_1[15]]]

		#print 'poles_0', poles_0
		#print 'poles_1', poles_1

		# apply rotation correction. vector type gets stripped in numpy
		uv_poles_0_temp = np.rot90(poles_0,rotate_0).tolist()
		uv_weights_0 = np.rot90(weights_0,rotate_0).tolist()
		#print ("uv_weights_0 ")
		#print (uv_weights_0)

		uv_poles_1_temp = np.rot90(poles_1,rotate_1).tolist()
		uv_weights_1 = np.rot90(weights_1,rotate_1).tolist()
		#print ("uv_weights_1 ")
		#print (uv_weights_1)

		#print 'uv_poles_0_temp', uv_poles_0_temp
		#print 'uv_poles_1_temp', uv_poles_1_temp
		#print 'uv_poles_0_temp[0][0] ', uv_poles_0_temp[0][0]
		#print 'uv_poles_0_temp[3][3] ', uv_poles_0_temp[3][3]

		# get ready to recast to vector
		uv_poles_0 = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
		uv_poles_1 = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

		for i in range(0,4):
			for j in range(0,4):
				uv_poles_0[i][j]= Base.Vector(uv_poles_0_temp[i][j][0],uv_poles_0_temp[i][j][1],uv_poles_0_temp[i][j][2])
			#print uv_poles_0

		for i in range(0,4):
			for j in range(0,4):
				uv_poles_1[i][j]= Base.Vector(uv_poles_1_temp[i][j][0],uv_poles_1_temp[i][j][1],uv_poles_1_temp[i][j][2])
			#print uv_poles_1


		#print 'uv_poles_0', uv_poles_0
		#print 'uv_poles_1', uv_poles_1

		#b=Base.Vector(a[0],a[1],a[2])

		# run ControlPoly6_FilletBezier or equivalent internal function on each pair running across the seam
		if fp.autoG3 == 1:
			print ("G3 on row_0")
			row_0 = blendG3_poly_2x4_1x6(uv_poles_0[0],
										uv_weights_0[0],
										uv_poles_1[0],
										uv_weights_1[0],
										fp.scale_tangent_0,
										fp.scale_inner_0[0],
										fp.scale_inner_1[0],
										fp.scale_tangent_1)
			blend_poles_0 = row_0[0]
			blend_weights_0 = row_0[1]
			
			print ("G3 on row_1")
			row_1 = blendG3_poly_2x4_1x6(uv_poles_0[1], uv_weights_0[1], uv_poles_1[1], uv_weights_1[1], fp.scale_tangent_0, fp.scale_inner_0[1], fp.scale_inner_1[1], fp.scale_tangent_1)
			blend_poles_1 = row_1[0]
			blend_weights_1 = row_1[1]

			print ("G3 on row_2")
			row_2 = blendG3_poly_2x4_1x6(uv_poles_0[2], uv_weights_0[2], uv_poles_1[2], uv_weights_1[2], fp.scale_tangent_0, fp.scale_inner_0[2], fp.scale_inner_1[2], fp.scale_tangent_1)
			blend_poles_2 = row_2[0]
			blend_weights_2 = row_2[1]

			print ("G3 on row_3")
			row_3 = blendG3_poly_2x4_1x6(uv_poles_0[3], uv_weights_0[3], uv_poles_1[3], uv_weights_1[3], fp.scale_tangent_0, fp.scale_inner_0[3], fp.scale_inner_1[3], fp.scale_tangent_1)
			blend_poles_3 = row_3[0]
			blend_weights_3 = row_3[1]
			
			fp.scale_inner_0 = [row_0[2], row_1[2], row_2[2], row_3[2]]
			fp.scale_inner_1 = [row_0[3], row_1[3], row_2[3], row_3[3]]			
		
		if fp.autoG3 == 0:
			row_0 = blend_poly_2x4_1x6(uv_poles_0[0], uv_weights_0[0], uv_poles_1[0], uv_weights_1[0], fp.scale_tangent_0, fp.scale_inner_0[0], fp.scale_inner_1[0], fp.scale_tangent_1)
			blend_poles_0 = row_0[0]
			blend_weights_0 = row_0[1]
			#print (blend_weights_0)
			
			#print ("uv_weights_0[1]")
			#print (uv_weights_0[1])
			row_1 = blend_poly_2x4_1x6(uv_poles_0[1], uv_weights_0[1], uv_poles_1[1], uv_weights_1[1], fp.scale_tangent_0, fp.scale_inner_0[1], fp.scale_inner_1[1], fp.scale_tangent_1)
			blend_poles_1 = row_1[0]
			blend_weights_1 = row_1[1]
			#print (blend_weights_1)
			
			#print ("uv_weights_0[2]")
			#print (uv_weights_0[2])
			row_2 = blend_poly_2x4_1x6(uv_poles_0[2], uv_weights_0[2], uv_poles_1[2], uv_weights_1[2], fp.scale_tangent_0, fp.scale_inner_0[2], fp.scale_inner_1[2], fp.scale_tangent_1)
			blend_poles_2 = row_2[0]
			blend_weights_2 = row_2[1]
			#print (blend_weights_2)

			row_3 = blend_poly_2x4_1x6(uv_poles_0[3], uv_weights_0[3], uv_poles_1[3], uv_weights_1[3], fp.scale_tangent_0, fp.scale_inner_0[3], fp.scale_inner_1[3], fp.scale_tangent_1)
			blend_poles_3 = row_3[0]
			blend_weights_3 = row_3[1]
			#print (blend_weights_3)
		
		
		
		# stack the ControlPoly6s into a 64 grid - poles and weights
		fp.Poles=[blend_poles_0[0],
				blend_poles_0[1],
				blend_poles_0[2],
				blend_poles_0[3],
				blend_poles_0[4],
				blend_poles_0[5],
				blend_poles_1[0],
				blend_poles_1[1],
				blend_poles_1[2],
				blend_poles_1[3],
				blend_poles_1[4],
				blend_poles_1[5],
				blend_poles_2[0],
				blend_poles_2[1],
				blend_poles_2[2],
				blend_poles_2[3],
				blend_poles_2[4],
				blend_poles_2[5],
				blend_poles_3[0],
				blend_poles_3[1],
				blend_poles_3[2],
				blend_poles_3[3],
				blend_poles_3[4],
				blend_poles_3[5]]

		fp.Weights=[blend_weights_0[0],
				blend_weights_0[1],
				blend_weights_0[2],
				blend_weights_0[3],
				blend_weights_0[4],
				blend_weights_0[5],
				blend_weights_1[0],
				blend_weights_1[1],
				blend_weights_1[2],
				blend_weights_1[3],
				blend_weights_1[4],
				blend_weights_1[5],
				blend_weights_2[0],
				blend_weights_2[1],
				blend_weights_2[2],
				blend_weights_2[3],
				blend_weights_2[4],
				blend_weights_2[5],
				blend_weights_3[0],
				blend_weights_3[1],
				blend_weights_3[2],
				blend_weights_3[3],
				blend_weights_3[4],
				blend_weights_3[5]]

		# build the leg list for viz
		fp.Legs = drawGrid(fp.Poles, 6)
		fp.Shape = Part.Shape(fp.Legs)

class SubGrid33_2Grid64s_old:
	def __init__(self, obj , Grid_0, Grid_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nSubGrid33_2Grid64s class Init\n")
		obj.addProperty("App::PropertyLink","Grid_0","SubGrid33_2Grid64s","first reference 6X4 grid").Grid_0 = Grid_0
		obj.addProperty("App::PropertyLink","Grid_1","SubGrid33_2Grid64s","second reference 6X4 grid").Grid_1 = Grid_1
		obj.addProperty("Part::PropertyGeometryList","Legs","SubGrid33_2Grid64s","control segments").Legs
		obj.addProperty("App::PropertyVectorList","u_row0_poles","SubGrid33_2Grid64s","u_row0_poles").u_row0_poles
		obj.addProperty("App::PropertyVectorList","u_row1_poles","SubGrid33_2Grid64s","u_row1_poles").u_row1_poles
		obj.addProperty("App::PropertyVectorList","v_col0_poles","SubGrid33_2Grid64s","v_col0_poles").v_col0_poles
		obj.addProperty("App::PropertyVectorList","v_col1_poles","SubGrid33_2Grid64s","v_col1_poles").v_col1_poles
		obj.addProperty("App::PropertyFloatList","u_row0_weights","SubGrid33_2Grid64s","u_row0_weights").u_row0_weights
		obj.addProperty("App::PropertyFloatList","u_row1_weights","SubGrid33_2Grid64s","u_row1_weights").u_row1_weights
		obj.addProperty("App::PropertyFloatList","v_col0_weights","SubGrid33_2Grid64s","v_col0_weights").v_col0_weights
		obj.addProperty("App::PropertyFloatList","v_col1_weights","SubGrid33_2Grid64s","v_col1_weights").v_col1_weights
		obj.Proxy = self


	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# outline:
		# -find shared corner
		# -set 'u' row - imagine the future surface as uvn (n is normal). 
		# -set 'v' row - imagine the future surface as uvn (n is normal).
		# -build a corner focused 33 grid using the same logic as the corner focused 66 grid. 
		# the $10 question here is whether this even maintains G1? maybe...it has been many steps since the bezier surface was segmented.

		# extract corner points
		corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
		corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
		# find the common point
		common = 'not_found_yet'
		for i in range(0,4):
			for j in range(0,4):
				if corners_0[i] == corners_1[j]:
					common=[i,j]

		if common == 'not_found_yet':
			print ('common point of grids not found. If this object was working, this is an evaluation error')
		#print 'common ', common
		# tested-runs-

		# the two '6s' of each grid should form a V when looking at the future grid
		# a is the left leg of the V, i.e. common[0] = 0 or 3
		# b is the right leg of the V i.e. common[1] = 2 or 1

		# check input grid order, swap grids if necessary
		if (common[0] == 1 or common[0] == 2) and (common[1] == 0 or common[1] == 3):
			print ('swapping grid order')
			temp=fp.Grid_0
			fp.Grid_0=fp.Grid_1
			fp.Grid_1=temp
			# get the corners again
			corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
			corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
			# find common again
			for i in range(0,4):
				for j in range(0,4):
					if corners_0[i] == corners_1[j]:
						common=[i,j]
			print ('common ', common)

		if common[0] == 0:
			fp.u_row0_poles = [fp.Grid_0.Poles[0],fp.Grid_0.Poles[1],fp.Grid_0.Poles[2]]
			fp.u_row0_weights = [fp.Grid_0.Weights[0],fp.Grid_0.Weights[1],fp.Grid_0.Weights[2]]
			fp.u_row1_poles = [fp.Grid_0.Poles[6],fp.Grid_0.Poles[7],fp.Grid_0.Poles[8]]
			fp.u_row1_weights = [fp.Grid_0.Weights[6],fp.Grid_0.Weights[7],fp.Grid_0.Weights[8]]

		if common[0] == 3:
			fp.u_row0_poles = [fp.Grid_0.Poles[23],fp.Grid_0.Poles[22],fp.Grid_0.Poles[21]]
			fp.u_row0_weights = [fp.Grid_0.Weights[23],fp.Grid_0.Weights[22],fp.Grid_0.Weights[21]]
			fp.u_row1_poles = [fp.Grid_0.Poles[17],fp.Grid_0.Poles[16],fp.Grid_0.Poles[15]]
			fp.u_row1_weights = [fp.Grid_0.Weights[17],fp.Grid_0.Weights[16],fp.Grid_0.Weights[15]]

		if common[1] == 1:
			fp.v_col0_poles = [fp.Grid_1.Poles[5],fp.Grid_1.Poles[4],fp.Grid_1.Poles[3]]
			fp.v_col0_weights = [fp.Grid_1.Weights[5],fp.Grid_1.Weights[4],fp.Grid_1.Weights[3]]
			fp.v_col1_poles = [fp.Grid_1.Poles[11],fp.Grid_1.Poles[10],fp.Grid_1.Poles[9]]
			fp.v_col1_weights = [fp.Grid_1.Weights[11],fp.Grid_1.Weights[10],fp.Grid_1.Weights[9]]

		if common[1] == 2:
			fp.v_col0_poles = [fp.Grid_1.Poles[18],fp.Grid_1.Poles[19],fp.Grid_1.Poles[20]]
			fp.v_col0_weights = [fp.Grid_1.Weights[18],fp.Grid_1.Weights[19],fp.Grid_1.Weights[20]]
			fp.v_col1_poles = [fp.Grid_1.Poles[12],fp.Grid_1.Poles[13],fp.Grid_1.Poles[14]]
			fp.v_col1_weights = [fp.Grid_1.Weights[12],fp.Grid_1.Weights[13],fp.Grid_1.Weights[14]]


		Legs=[0]*10

		Legs[0]=Part.LineSegment(fp.u_row0_poles[0], fp.u_row0_poles[1])
		Legs[1]=Part.LineSegment(fp.u_row0_poles[1], fp.u_row0_poles[2])

		Legs[2]=Part.LineSegment(fp.u_row0_poles[0], fp.u_row1_poles[0])
		Legs[3]=Part.LineSegment(fp.u_row0_poles[1], fp.u_row1_poles[1])
		Legs[4]=Part.LineSegment(fp.u_row0_poles[2], fp.u_row1_poles[2])

		Legs[5]=Part.LineSegment(fp.v_col0_poles[0], fp.v_col0_poles[1])
		Legs[6]=Part.LineSegment(fp.v_col0_poles[1], fp.v_col0_poles[2])

		Legs[7]=Part.LineSegment(fp.v_col0_poles[0], fp.v_col1_poles[0])
		Legs[8]=Part.LineSegment(fp.v_col0_poles[1], fp.v_col1_poles[1])
		Legs[9]=Part.LineSegment(fp.v_col0_poles[2], fp.v_col1_poles[2])

		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class SubGrid33_2Grid64:
	def __init__(self, obj , Grid_0, Grid_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nSubGrid33_2Grid64 class Init\n")
		obj.addProperty("App::PropertyLink","Grid_0","SubGrid33_2Grid64","first reference 6X4 grid").Grid_0 = Grid_0
		obj.addProperty("App::PropertyLink","Grid_1","SubGrid33_2Grid64","second reference 6X4 grid").Grid_1 = Grid_1
		obj.addProperty("App::PropertyFloat","adjust_0","SubGrid33_2Grid64","adjust along Grid_0").adjust_0 = 0
		obj.addProperty("App::PropertyFloat","adjust_1","SubGrid33_2Grid64","adjust along Grid_1").adjust_1 = 0
		obj.addProperty("Part::PropertyGeometryList","Legs","SubGrid33_2Grid64","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","SubGrid33_2Grid64","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","SubGrid33_2Grid64","Weights").Weights

		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# outline:
		# -find shared corner
		# -set 'u' row - imagine the future surface as uvn (n is normal). 
		# -set 'v' row - imagine the future surface as uvn (n is normal).
		# -build a corner focused 33 grid using similar logic as the corner focused 66 grid. 
		#the $10 question here is whether this even maintains G1? maybe...it has been many steps since the bezier surface was segmented.

		# extract corner points
		corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
		corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
		# find the common point
		common = 'not_found_yet'
		for i in range(0,4):
			for j in range(0,4):
				if equalVectors(corners_0[i],corners_1[j],0.000001):
					common=[i,j]
		if common == 'not_found_yet':
			print ('common point of grids not found. If this object was working previously, this is an evaluation error')
		print ('common ', common)
		# tested-runs-

		# the two 6 point sides of each grid should form a V when looking at the future grid
		# a is the left leg of the V, i.e. common[0] = 0 or 3
		# b is the right leg of the V i.e. common[1] = 2 or 1

		# check input grid order, swap grids if necessary
		if (common[0] == 1 or common[0] == 2) and (common[1] == 0 or common[1] == 3):
			print ('swapping grid order')
			temp=fp.Grid_0
			fp.Grid_0=fp.Grid_1
			fp.Grid_1=temp
			# get the corners again
			corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
			corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
			# find common again
			for i in range(0,4):
				for j in range(0,4):
					if equalVectors(corners_0[i],corners_1[j],0.000001):
						common=[i,j]
			print ('common ', common)

		if common[0] == 0:
			v_col0_poles = [fp.Grid_0.Poles[0],fp.Grid_0.Poles[1],fp.Grid_0.Poles[2]]
			v_col0_weights = [fp.Grid_0.Weights[0],fp.Grid_0.Weights[1],fp.Grid_0.Weights[2]]
			v_col1_poles = [fp.Grid_0.Poles[6],fp.Grid_0.Poles[7],fp.Grid_0.Poles[8]]
			v_col1_weights = [fp.Grid_0.Weights[6],fp.Grid_0.Weights[7],fp.Grid_0.Weights[8]]

		if common[0] == 3:
			v_col0_poles = [fp.Grid_0.Poles[23],fp.Grid_0.Poles[22],fp.Grid_0.Poles[21]]
			v_col0_weights = [fp.Grid_0.Weights[23],fp.Grid_0.Weights[22],fp.Grid_0.Weights[21]]
			v_col1_poles = [fp.Grid_0.Poles[17],fp.Grid_0.Poles[16],fp.Grid_0.Poles[15]]
			v_col1_weights = [fp.Grid_0.Weights[17],fp.Grid_0.Weights[16],fp.Grid_0.Weights[15]]

		if common[1] == 1:
			u_row0_poles = [fp.Grid_1.Poles[5],fp.Grid_1.Poles[4],fp.Grid_1.Poles[3]]
			u_row0_weights = [fp.Grid_1.Weights[5],fp.Grid_1.Weights[4],fp.Grid_1.Weights[3]]
			u_row1_poles = [fp.Grid_1.Poles[11],fp.Grid_1.Poles[10],fp.Grid_1.Poles[9]]
			u_row1_weights = [fp.Grid_1.Weights[11],fp.Grid_1.Weights[10],fp.Grid_1.Weights[9]]

		if common[1] == 2:
			u_row0_poles = [fp.Grid_1.Poles[18],fp.Grid_1.Poles[19],fp.Grid_1.Poles[20]]
			u_row0_weights = [fp.Grid_1.Weights[18],fp.Grid_1.Weights[19],fp.Grid_1.Weights[20]]
			u_row1_poles = [fp.Grid_1.Poles[12],fp.Grid_1.Poles[13],fp.Grid_1.Poles[14]]
			u_row1_weights = [fp.Grid_1.Weights[12],fp.Grid_1.Weights[13],fp.Grid_1.Weights[14]]

		u_tan_ratio = (u_row0_poles[1]-u_row0_poles[0]).Length / (v_col1_poles[0]-v_col0_poles[0]).Length
		v_tan_ratio = (v_col0_poles[1]-v_col0_poles[0]).Length / (u_row1_poles[0]-u_row0_poles[0]).Length

		p00 = u_row0_poles[0]
		p01 = u_row0_poles[1]
		p02 = u_row0_poles[2]
		p10 = v_col0_poles[1]
		p20 = v_col0_poles[2]
		p11_u = p01 + (u_row0_poles[1]-u_row1_poles[1])*v_tan_ratio
		p12 = p02 + (u_row0_poles[2]-u_row1_poles[2])*v_tan_ratio
		p11_v = p10 + (v_col0_poles[1]-v_col1_poles[1])*u_tan_ratio
		p21 = p20 + (v_col0_poles[2]-v_col1_poles[2])*u_tan_ratio
		p11 = (p11_u + p11_v) * 0.5
		p22_u = p12 + (p21-p11)
		p22_v = p21 + (p12-p11)
		p22_temp = (p22_u + p22_v) * 0.5

		p22 = p22_temp + fp.adjust_0 * (p01-p00) + fp.adjust_1 * (p10-p00)

		fp.Poles = [p00, p01, p02, p10, p11, p12, p20, p21, p22]

		w00 = u_row0_weights[0]
		w01 = u_row0_weights[1]
		w02 = u_row0_weights[2]
		w10 = v_col0_weights[1]
		w20 = v_col0_weights[2]

		w11 = w01 * w10
		w12 = w02 * w10
		w21 = w01 * w20
		w22 = w02 * w20

		fp.Weights = [w00, w01, w02, w10, w11, w12, w20, w21, w22]

		Legs=[0]*12

		Legs[0]=Part.LineSegment(p00,p01)
		Legs[1]=Part.LineSegment(p01,p02)

		Legs[2]=Part.LineSegment(p00,p10)
		Legs[3]=Part.LineSegment(p10,p20)

		Legs[4]=Part.LineSegment(p01,p11)
		Legs[5]=Part.LineSegment(p02,p12)

		Legs[6]=Part.LineSegment(p10,p11)
		Legs[7]=Part.LineSegment(p20,p21)

		Legs[8]=Part.LineSegment(p11,p12)
		Legs[9]=Part.LineSegment(p11,p21)

		Legs[10]=Part.LineSegment(p12,p22)
		Legs[11]=Part.LineSegment(p21,p22)

		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid66_4Sub_old:
	def __init__(self, obj , SubGrid_0, SubGrid_1, SubGrid_2, SubGrid_3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid66_4Sub class Init\n")
		obj.addProperty("App::PropertyLink","SubGrid_0","ControlGrid66_4Sub","first reference 3X3 sub grid").SubGrid_0 = SubGrid_0
		obj.addProperty("App::PropertyLink","SubGrid_1","ControlGrid66_4Sub","second reference 3X3 sub grid").SubGrid_1 = SubGrid_1
		obj.addProperty("App::PropertyLink","SubGrid_2","ControlGrid66_4Sub","third reference 3X3 sub grid").SubGrid_2 = SubGrid_2
		obj.addProperty("App::PropertyLink","SubGrid_3","ControlGrid66_4Sub","fourth reference 3X3 sub grid").SubGrid_3 = SubGrid_3
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid66_4Sub","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid66_4Sub","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid66_4Sub","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		p00 = fp.SubGrid_0.u_row_poles[0]
		p01 = fp.SubGrid_0.u_row_poles[1]
		p02 = fp.SubGrid_0.u_row_poles[2]
		p03 = fp.SubGrid_1.v_col_poles[2]
		p04 = fp.SubGrid_1.v_col_poles[1]
		p05 = fp.SubGrid_1.v_col_poles[0]

		p15 = fp.SubGrid_1.u_row_poles[1]
		p25 = fp.SubGrid_1.u_row_poles[2]
		p35 = fp.SubGrid_2.v_col_poles[2]
		p45 = fp.SubGrid_2.v_col_poles[1]
		p55 = fp.SubGrid_2.v_col_poles[0]

		p54 = fp.SubGrid_2.u_row_poles[1]
		p53 = fp.SubGrid_2.u_row_poles[2]
		p52 = fp.SubGrid_3.v_col_poles[2]
		p51 = fp.SubGrid_3.v_col_poles[1]
		p50 = fp.SubGrid_3.v_col_poles[0]

		p40 = fp.SubGrid_3.u_row_poles[1]
		p30 = fp.SubGrid_3.u_row_poles[2]
		p20 = fp.SubGrid_0.v_col_poles[2]
		p10 = fp.SubGrid_0.v_col_poles[1]

		p11 = p01 + (p10 - p00)
		p14 = p04 + (p15 - p05)
		p41 = p51 + (p40 - p50)
		p44 = p45 + (p54 - p55)
		p12 = p02 + (p10 - p00)
		p13 = p03 + (p15 - p05)
		p24 = p25 + (p04 - p05)
		p34 = p35 + (p54 - p55)
		p42 = p52 + (p40 - p50)
		p43 = p53 + (p45 - p55)
		p21 = p20 + (p01 - p00)
		p31 = p30 + (p51 - p50)
		p22 = p12 + (p20 - p10)
		p23 = p13 + (p25 - p15)
		p32 = p42 + (p30 - p40)
		p33 = p43 + (p35 - p45)
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35,
					p40, p41, p42, p43, p44, p45,
					p50, p51, p52, p53, p54, p55]
		w00 = fp.SubGrid_0.u_row_weights[0]
		w01 = fp.SubGrid_0.u_row_weights[1]
		w02 = fp.SubGrid_0.u_row_weights[2]
		w03 = fp.SubGrid_1.v_col_weights[2]
		w04 = fp.SubGrid_1.v_col_weights[1]
		w05 = fp.SubGrid_1.v_col_weights[0]
		w15 = fp.SubGrid_1.u_row_weights[1]
		w25 = fp.SubGrid_1.u_row_weights[2]
		w35 = fp.SubGrid_2.v_col_weights[2]
		w45 = fp.SubGrid_2.v_col_weights[1]
		w55 = fp.SubGrid_2.v_col_weights[0]
		w54 = fp.SubGrid_2.u_row_weights[1]
		w53 = fp.SubGrid_2.u_row_weights[2]
		w52 = fp.SubGrid_3.v_col_weights[2]
		w51 = fp.SubGrid_3.v_col_weights[1]
		w50 = fp.SubGrid_3.v_col_weights[0]
		w40 = fp.SubGrid_3.u_row_weights[1]
		w30 = fp.SubGrid_3.u_row_weights[2]
		w20 = fp.SubGrid_0.v_col_weights[2]
		w10 = fp.SubGrid_0.v_col_weights[1]
		# maybe i should average instead of multiply? needs testing.
		# currently based on the idea all weights are between 0 and 1.
		# previous used cumulative neighbor multiplication. this drives weights too low.
		# current method multiplies the two weights along isos to the closest edge
		w11 = w01*w10
		w12 = w02*w10 
		w21 = w01*w20
		w22 = w02*w20
		w14 = w04*w15
		w13 = w03*w15
		w24 = w04*w25
		w23 = w03*w25
		w44 = w45*w54
		w34 = w35*w54
		w43 = w54*w45
		w33 = w35*w53
		w41 = w40*w51
		w31 = w30*w51
		w42 = w52*w40
		w32 = w30*w52

		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35,
					w40, w41, w42, w43, w44, w45,
					w50, w51, w52, w53, w54, w55]
		Legs=[0]*60
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(5,10):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(10,15):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(15,20):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(20,25):
			Legs[i]=Part.LineSegment(fp.Poles[i+4],fp.Poles[i+5])
		for i in range(25,30):
			Legs[i]=Part.LineSegment(fp.Poles[i+5],fp.Poles[i+6])
		for i in range(30,36):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(36,42):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(42,48):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(48,54):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(54,60):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])

		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid66_4Sub:
	def __init__(self, obj , SubGrid_0, SubGrid_1, SubGrid_2, SubGrid_3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid66_4Sub class Init\n")
		obj.addProperty("App::PropertyLink","SubGrid_0","ControlGrid66_4Sub","first reference 3X3 sub grid").SubGrid_0 = SubGrid_0
		obj.addProperty("App::PropertyLink","SubGrid_1","ControlGrid66_4Sub","second reference 3X3 sub grid").SubGrid_1 = SubGrid_1
		obj.addProperty("App::PropertyLink","SubGrid_2","ControlGrid66_4Sub","third reference 3X3 sub grid").SubGrid_2 = SubGrid_2
		obj.addProperty("App::PropertyLink","SubGrid_3","ControlGrid66_4Sub","fourth reference 3X3 sub grid").SubGrid_3 = SubGrid_3
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid66_4Sub","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid66_4Sub","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid66_4Sub","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		p00 = fp.SubGrid_0.Poles[0]
		p01 = fp.SubGrid_0.Poles[1]
		p02 = fp.SubGrid_0.Poles[2]
		p03 = fp.SubGrid_1.Poles[6]
		p04 = fp.SubGrid_1.Poles[3]
		p05 = fp.SubGrid_1.Poles[0]

		p15 = fp.SubGrid_1.Poles[1]
		p25 = fp.SubGrid_1.Poles[2]
		p35 = fp.SubGrid_2.Poles[6]
		p45 = fp.SubGrid_2.Poles[3]
		p55 = fp.SubGrid_2.Poles[0]

		p54 = fp.SubGrid_2.Poles[1]
		p53 = fp.SubGrid_2.Poles[2]
		p52 = fp.SubGrid_3.Poles[6]
		p51 = fp.SubGrid_3.Poles[3]
		p50 = fp.SubGrid_3.Poles[0]

		p40 = fp.SubGrid_3.Poles[1]
		p30 = fp.SubGrid_3.Poles[2]
		p20 = fp.SubGrid_0.Poles[6]
		p10 = fp.SubGrid_0.Poles[3]

		p11 = fp.SubGrid_0.Poles[4]
		p12 = fp.SubGrid_0.Poles[5]
		p13 = fp.SubGrid_1.Poles[7]
		p14 = fp.SubGrid_1.Poles[4]

		p24 = fp.SubGrid_1.Poles[5]
		p34 = fp.SubGrid_2.Poles[7]
		p44 = fp.SubGrid_2.Poles[4]

		p43 = fp.SubGrid_2.Poles[5]
		p42 = fp.SubGrid_3.Poles[7]
		p41 = fp.SubGrid_3.Poles[4]

		p31 = fp.SubGrid_3.Poles[5]
		p21 = fp.SubGrid_0.Poles[7]

		p22 = fp.SubGrid_0.Poles[8]
		p23 = fp.SubGrid_1.Poles[8]
		p33 = fp.SubGrid_2.Poles[8]
		p32 = fp.SubGrid_3.Poles[8]

		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35,
					p40, p41, p42, p43, p44, p45,
					p50, p51, p52, p53, p54, p55]

		w00 = fp.SubGrid_0.Weights[0]
		w01 = fp.SubGrid_0.Weights[1]
		w02 = fp.SubGrid_0.Weights[2]
		w03 = fp.SubGrid_1.Weights[6]
		w04 = fp.SubGrid_1.Weights[3]
		w05 = fp.SubGrid_1.Weights[0]

		w15 = fp.SubGrid_1.Weights[1]
		w25 = fp.SubGrid_1.Weights[2]
		w35 = fp.SubGrid_2.Weights[6]
		w45 = fp.SubGrid_2.Weights[3]
		w55 = fp.SubGrid_2.Weights[0]

		w54 = fp.SubGrid_2.Weights[1]
		w53 = fp.SubGrid_2.Weights[2]
		w52 = fp.SubGrid_3.Weights[6]
		w51 = fp.SubGrid_3.Weights[3]
		w50 = fp.SubGrid_3.Weights[0]

		w40 = fp.SubGrid_3.Weights[1]
		w30 = fp.SubGrid_3.Weights[2]
		w20 = fp.SubGrid_0.Weights[6]
		w10 = fp.SubGrid_0.Weights[3]

		w11 = fp.SubGrid_0.Weights[4]
		w12 = fp.SubGrid_0.Weights[5]
		w13 = fp.SubGrid_1.Weights[7]
		w14 = fp.SubGrid_1.Weights[4]

		w24 = fp.SubGrid_1.Weights[5]
		w34 = fp.SubGrid_2.Weights[7]
		w44 = fp.SubGrid_2.Weights[4]

		w43 = fp.SubGrid_2.Weights[5]
		w42 = fp.SubGrid_3.Weights[7]
		w41 = fp.SubGrid_3.Weights[4]

		w31 = fp.SubGrid_3.Weights[5]
		w21 = fp.SubGrid_0.Weights[7]

		w22 = fp.SubGrid_0.Weights[8]
		w23 = fp.SubGrid_1.Weights[8]
		w33 = fp.SubGrid_2.Weights[8]
		w32 = fp.SubGrid_3.Weights[8]

		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35,
					w40, w41, w42, w43, w44, w45,
					w50, w51, w52, w53, w54, w55]
		
		fp.Legs = drawGrid(fp.Poles, 6)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid64_3_1Grid44:
	def __init__(self, obj , ControlGrid44, Corner):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_3_1Grid44 class Init\n")
		obj.addProperty("App::PropertyLink","ControlGrid44","ControlGrid64_3_1Grid44","Reference Bezier Surface").ControlGrid44 = ControlGrid44
		obj.addProperty("App::PropertyFloat","Corner","ControlGrid64_3_1Grid44","Corner blending curve").Corner = Corner
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_3_1Grid44","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_3_1Grid44","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_3_1Grid44","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the control poly of the bezier
		grid_44 = fp.ControlGrid44
		# get the target corner
		corner = fp.Corner

		if corner == 0:
			rotate = 0
		elif corner == 1:
			rotate = 1
		elif corner == 2:
			rotate = 2
		elif corner == 3:
			rotate = 3

		# rotate the grid so that the corner is in the 00 position
				# get grid data back into array
		lin_poles = grid_44.Poles
		lin_weights = grid_44.Weights

		# first shot: simple partition.this is an array of rows
		Apoles = [[lin_poles[0], lin_poles[1], lin_poles[2], lin_poles[3]],
					[lin_poles[4], lin_poles[5], lin_poles[6], lin_poles[7]],
					[lin_poles[8], lin_poles[9], lin_poles[10], lin_poles[11]],
					[lin_poles[12], lin_poles[13], lin_poles[14], lin_poles[15]]]

		Aweights = [[lin_weights[0], lin_weights[1], lin_weights[2], lin_weights[3]],
					[lin_weights[4], lin_weights[5], lin_weights[6], lin_weights[7]],
					[lin_weights[8], lin_weights[9], lin_weights[10], lin_weights[11]],
					[lin_weights[12], lin_weights[13], lin_weights[14], lin_weights[15]]]

		#print 'Apoles', Apoles

		# apply rotation correction. vector type gets stripped in numpy
		uv_poles_temp = np.rot90(Apoles,rotate).tolist()
		uv_weights = np.rot90(Aweights,rotate).tolist()

		#print 'uv_poles_temp', uv_poles_temp
		#print 'uv_poles_temp[0][0] ', uv_poles_temp[0][0]
		#print 'uv_poles_temp[3][3] ', uv_poles_temp[3][3]

		# get ready to recast to vector
		uv_poles = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

		for i in range(0,4):
			for j in range(0,4):
				uv_poles[i][j]= Base.Vector(uv_poles_temp[i][j][0],uv_poles_temp[i][j][1],uv_poles_temp[i][j][2])
			#print uv_poles

		#print 'uv_poles', uv_poles

		set_poles = [ uv_poles[0][0],
		uv_poles[0][1],
		uv_poles[0][2],
		uv_poles[0][3],
		uv_poles[1][0],
		uv_poles[1][1],
		uv_poles[1][2],
		uv_poles[1][3],
		uv_poles[2][0],
		uv_poles[2][1],
		uv_poles[2][2],
		uv_poles[2][3],
		uv_poles[3][0],
		uv_poles[3][1],
		uv_poles[3][2],
		uv_poles[3][3]]

		set_weights = [ uv_weights[0][0],
		uv_weights[0][1],
		uv_weights[0][2],
		uv_weights[0][3],
		uv_weights[1][0],
		uv_weights[1][1],
		uv_weights[1][2],
		uv_weights[1][3],
		uv_weights[2][0],
		uv_weights[2][1],
		uv_weights[2][2],
		uv_weights[2][3],
		uv_weights[3][0],
		uv_weights[3][1],
		uv_weights[3][2],
		uv_weights[3][3]]


		#first degenerate topology try. naive Grid44 to Grid64 triangle mapping with some midpoints. p22=p23=p24=p25=set_poles[10]. this causes folding.
		#second iteration: add tiny spacing around p22, p23, p24, p25. this will break G1 slightly. The goal is to balance G1 loss versus folding over.
		#as these point 'un-degenerate' it is tempting to reintroduce curvature matching. On the other hand, aligning them for 0 curvature may help get G1 back.
		#maybe some weighted average of these various avenues will be best.
		p00=set_poles[12]
		p01=set_poles[8]
		p02=set_poles[4]
		p03=set_poles[1]
		p04=set_poles[2]
		p05=set_poles[3]

		p10=set_poles[13]
		p11=set_poles[9]

		p14=set_poles[6]
		p15=set_poles[7]


		p20=set_poles[14]
		''' # 1st strategy
		p21=set_poles[10]
		p22=set_poles[10]
		p23=set_poles[10]
		p24=set_poles[10]
		'''
		p25=set_poles[11]


		# 2nd strategy
		''' this was better, sure, but it stills folds. going to set the whole corner planar, but non collapsed for third try.
		degen_tan_factor=0.5 #initial was 0.75
		degen_curv_factor=1.0/6.0 #initial was 0.1
		#trim tangent
		p21=p20+(set_poles[10]-p20)*degen_tan_factor
		# add a segment control line snippet towards the third control point of the underlying 44 grid
		p22=p21+(p14-p21)*degen_curv_factor
		#trim tangent
		p24=p25+(set_poles[10]-p25)*degen_tan_factor
		# add a segment control line snippet towards the third control point of the underlying 44 grid
		p23=p24+(p11-p24)*degen_curv_factor
		'''

		#third strategy
		p21=p20+(set_poles[10]-p20)*.5 # trim tangent
		p22=p21+(set_poles[10]-p21)*.5 # 0 curvature along tangent trim

		p24=p25+(set_poles[10]-p25)*.5 # trim tangent
		p23=p24+(set_poles[10]-p24)*.5 # 0 curvature along tangent trim


		p30=set_poles[15]
		p31=set_poles[15]
		p32=set_poles[15]
		p33=set_poles[15]
		p34=set_poles[15]
		p35=set_poles[15]

		p12=(set_poles[5]+p11).multiply(0.5)
		p13=(set_poles[5]+p14).multiply(0.5)


		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35]

		w00=set_weights[12]
		w01=set_weights[8]
		w02=set_weights[4]
		w03=set_weights[1]
		w04=set_weights[2]
		w05=set_weights[3]

		w10=set_weights[13]
		w11=set_weights[9]

		w14=set_weights[6]
		w15=set_weights[7]

		w20=set_weights[14]
		w21=set_weights[10]
		w22=set_weights[10]
		w23=set_weights[10]
		w24=set_weights[10]
		w25=set_weights[11]

		w30=set_weights[15]
		w31=set_weights[15]
		w32=set_weights[15]
		w33=set_weights[15]
		w34=set_weights[15]
		w35=set_weights[15]

		w12=(w02+w21)/2
		w13=(w03+w24)/2

		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35]
		
		fp.Legs = drawGrid(fp.Poles, 6)
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid64_normal:
	def __init__(self, obj , Grid64, v0_normalize, v3_normalize):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_normal class Init\n")
		obj.addProperty("App::PropertyLink","Input_Grid","ControlGrid64_normal","Reference 6X4 Grid").Input_Grid = Grid64
		obj.addProperty("App::PropertyFloat","v0_normalize","ControlGrid64_normal","Normalization factor along v0 edge").v0_normalize = v0_normalize
		obj.addProperty("App::PropertyFloat","v3_normalize","ControlGrid64_normal","Normalization factor along v3 edge").v3_normalize = v3_normalize
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_normal","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_normal","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_normal","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		print ("ControlGrid64_normal doesn't do anything yet")
		Poles = fp.Input_Grid.Poles
		Weights = fp.Input_Grid.Weights

		# do stuff here

		# basic use case: 2 grid44s are mirrorable G1 across a plane, but the grid64 blend that results is not 
		# necessarily mirrorable g1 across the original plane (existing models show this to be the case). 
		# we want to modify the control points of this grid64 so that it becomes mirrorable G1 across the plane

		# in practice, this simply means that all grid legs reaching the mirror plane must be perpendicaulr to this plane*.
		# the naming comes from this 'perpendicularity/normal' aspect of the method: the tool returns a 'normalized' 
		# version of the grid64. 
		# *use of weights complicates this, and weight matching is required in addition to alignment of grid legs.

		# there may be cases where we can extend from 'mirroring' to G1 continuation, allowing us to have 2 grid64s 
		# side by side with good G1, even though the edge is not planar (exsiting models appears to indicate this is possible)
		# in light of this goal, the 'normal' name seems more appropriate long term than 'mirrorable' or some such.

		# in the simple mirroring case, the mirrorability of the base grid44s plays an important role in limiting the problem.
		# since all tangents in the grid44s are normal, the ControlGrid64_2Gridd44 blend grid will have the first 2 and
		# last 2 u rows perpendicular to the mirror plane
		# it is only the 3rd and 4th inner leges reaching the edge that can have the issue.

		# v0 runs on poles 0->5, v3 runs on poles 18->23
		
		v0_tan_0 = Poles[6]- Poles[0]
		v0_tan_1 = Poles[7]- Poles[1]

		v0_tan_4 = Poles[10]- Poles[4]
		v0_tan_5 = Poles[11]- Poles[5]

		v3_tan_0 = Poles[12]- Poles[18]
		v3_tan_1 = Poles[13]- Poles[19]

		v3_tan_4 = Poles[16]- Poles[22]
		v3_tan_5 = Poles[17]- Poles[23]


		# in the simplest case, which is the intended case,
		# all poles on target edge (v0, v3, or both) are in a plane (the mirror plane we are setting the surface edge 'normal' to)
		# the tangents reaching the corners are normal to the mirror plane.
		# the first inner u legs reaching the v edge should also be normal to the mirror plane as well, if the grid44s being blended were
		# mirrorable

		



		fp.Poles = Poles
		fp.Weights = Weights

		fp.Legs = drawGrid(fp.Poles, 6)
		fp.Shape = Part.Shape(fp.Legs)

class SubGrid63_2Surf64:
	def __init__(self, obj , Surf_0, Surf_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nSubGrid62Tri_2Surf64 class Init\n")
		obj.addProperty("App::PropertyLink","Surf_0","SubGrid63_2Surf64","first reference 6X4 surface").Surf_0 = Surf_0
		obj.addProperty("App::PropertyLink","Surf_1","SubGrid63_2Surf64","second reference 6X4 surface").Surf_1 = Surf_1
		obj.addProperty("Part::PropertyGeometryList","Legs","SubGrid63_2Surf64","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","SubGrid63_2Surf64","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","SubGrid63_2Surf64","Weights").Weights

		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''

		# get grids form the surfaces
		Grid_0=fp.Surf_0.Grid
		Grid_1=fp.Surf_1.Grid

		#get the FreeCAD surface form the NL surface object
		Surf_0 = fp.Surf_0.Shape.Surface
		Surf_1 = fp.Surf_1.Shape.Surface

		# extract corner points
		corners_0=[Grid_0.Poles[0],Grid_0.Poles[5],Grid_0.Poles[18],Grid_0.Poles[23]]
		corners_1=[Grid_1.Poles[0],Grid_1.Poles[5],Grid_1.Poles[18],Grid_1.Poles[23]]

		# find the common point that defines the corner
		common = 'not_found_yet'
		for i in range(0,4):
			for j in range(0,4):
				if equalVectors(corners_0[i], corners_1[j], 0.000001):
					common=[i,j]
		if common == 'not_found_yet':
			print ('common point of grids not found. If this object was working previously, this is an evaluation error')
		print ('common ', common)

		# the two 6 point sides of each grid should form a V when looking at the future grid
		# a is the left leg of the V, i.e. common[0] = 0 or 3
		# b is the right leg of the V i.e. common[1] = 2 or 1

		# check input grid order, swap grids if necessary
		if (common[0] == 1 or common[0] == 2) and (common[1] == 0 or common[1] == 3):
			print ('swap surfaces - internal only?')
			temp_grid=Grid_0
			Grid_0=Grid_1
			Grid_1=temp_grid

			temp_surf=Surf_0
			Surf_0=Surf_1
			Surf_1=temp_surf

			# get the corners again, based on swapped grids
			corners_0=[Grid_0.Poles[0],Grid_0.Poles[5],Grid_0.Poles[18],Grid_0.Poles[23]]
			corners_1=[Grid_1.Poles[0],Grid_1.Poles[5],Grid_1.Poles[18],Grid_1.Poles[23]]
			# find common again
			for i in range(0,4):
				for j in range(0,4):
					if equalVectors(corners_0[i], corners_1[j], 0.000001):
						common=[i,j]
			print ('common ', common)


		# cut surfaces in half, insert knots to re-establish Poly6 along u
		if common[0]==0:
			Surf_0.segment(0,0.5,0,1)
			#print 'Surf_0 UKnotSequence after cut = ', Surf_0.UKnotSequence
			#print 'pole count surf_0 = ', Surf_0.getPoles().__len__()
			Surf_0.insertUKnots([1.0/6.0],[1],0.000001)
			#print 'Surf_0 UKnotSequence after bump = ', Surf_0.UKnotSequence

		if common[0]==3:
			Surf_0.segment(0.5,1,0,1)
			#print 'Surf_0 UKnotSequence after cut = ', Surf_0.UKnotSequence
			#print 'pole count surf_0 = ', Surf_0.getPoles().__len__()
			Surf_0.insertUKnots([5.0/6.0],[1],0.000001)
			#print 'Surf_0 UKnotSequence after bump = ', Surf_0.UKnotSequence

		if common[1]==2:
			Surf_1.segment(0,0.5,0,1)
			#print 'Surf_1 UKnotSequence after cut = ', Surf_0.UKnotSequence
			#print 'pole count surf_1 = ', Surf_1.getPoles().__len__()
			Surf_1.insertUKnots([1.0/6.0],[1],0.000001)
			#print 'Surf_1 UKnotSequence after bump = ', Surf_0.UKnotSequence

		if common[1]==1:
			Surf_1.segment(0.5,1,0,1)
			#print 'Surf_1 UKnotSequence after cut = ', Surf_0.UKnotSequence
			#print 'pole count surf_1 = ', Surf_1.getPoles().__len__()
			Surf_1.insertUKnots([5.0/6.0],[1],0.000001)
			#print 'Surf_1 UKnotSequence after bump = ', Surf_0.UKnotSequence

		# insert knots along v to establish Poly6 along v
		Surf_0.insertVKnots([1.0/3.0,2.0/3.0],[1,1],0.000001)
		Surf_1.insertVKnots([1.0/3.0,2.0/3.0],[1,1],0.000001)

		Poles66_0=Surf_0.getPoles()
		#print 'len Poles66_0 = ', Poles66_0.__len__()
		Weights66_0=Surf_0.getWeights()

		Poles66_1=Surf_1.getPoles()
		#print 'len Poles66_1 = ', Poles66_1.__len__()
		Weights66_1=Surf_1.getWeights()

		if common[0] == 0:
			v_col0_poles = [Poles66_0[0][0],Poles66_0[1][0],Poles66_0[2][0],Poles66_0[3][0],Poles66_0[4][0],Poles66_0[5][0]]
			v_col0_weights = [Weights66_0[0][0],Weights66_0[1][0],Weights66_0[2][0],Weights66_0[3][0],Weights66_0[4][0],Weights66_0[5][0]]
			v_col1_poles = [Poles66_0[0][1],Poles66_0[1][1],Poles66_0[2][1],Poles66_0[3][1],Poles66_0[4][1],Poles66_0[5][1]]
			v_col1_weights = [Weights66_0[0][1],Weights66_0[1][1],Weights66_0[2][1],Weights66_0[3][1],Weights66_0[4][1],Weights66_0[5][1]]
			v_col2_poles = [Poles66_0[0][2],Poles66_0[1][2],Poles66_0[2][2],Poles66_0[3][2],Poles66_0[4][2],Poles66_0[5][2]]
			v_col2_weights = [Weights66_0[0][2],Weights66_0[1][2],Weights66_0[2][2],Weights66_0[3][2],Weights66_0[4][2],Weights66_0[5][2]]

		if common[0] == 3:
			v_col0_poles = [Poles66_0[5][5],Poles66_0[4][5],Poles66_0[3][5],Poles66_0[2][5],Poles66_0[1][5],Poles66_0[0][5]]
			v_col0_weights = [Weights66_0[5][5],Weights66_0[4][5],Weights66_0[3][5],Weights66_0[2][5],Weights66_0[1][5],Weights66_0[0][5]]
			v_col1_poles = [Poles66_0[5][4],Poles66_0[4][4],Poles66_0[3][4],Poles66_0[2][4],Poles66_0[1][4],Poles66_0[0][4]]
			v_col1_weights = [Weights66_0[5][4],Weights66_0[4][4],Weights66_0[3][4],Weights66_0[2][4],Weights66_0[1][4],Weights66_0[0][4]]
			v_col2_poles = [Poles66_0[5][3],Poles66_0[4][3],Poles66_0[3][3],Poles66_0[2][3],Poles66_0[1][3],Poles66_0[0][3]]
			v_col2_weights = [Weights66_0[5][3],Weights66_0[4][3],Weights66_0[3][3],Weights66_0[2][3],Weights66_0[1][3],Weights66_0[0][3]]

		if common[1] == 1:
			u_row0_poles = [Poles66_1[5][0],Poles66_1[4][0],Poles66_1[3][0],Poles66_1[2][0],Poles66_1[1][0],Poles66_1[0][0]]
			u_row0_weights = [Weights66_1[5][0],Weights66_1[4][0],Weights66_1[3][0],Weights66_1[2][0],Weights66_1[1][0],Weights66_1[0][0]]
			u_row1_poles = [Poles66_1[5][1],Poles66_1[4][1],Poles66_1[3][1],Poles66_1[2][1],Poles66_1[1][1],Poles66_1[0][1]]
			u_row1_weights = [Weights66_1[5][1],Weights66_1[4][1],Weights66_1[3][1],Weights66_1[2][1],Weights66_1[1][1],Weights66_1[0][1]]
			u_row2_poles = [Poles66_1[5][2],Poles66_1[4][2],Poles66_1[3][2],Poles66_1[2][2],Poles66_1[1][2],Poles66_1[0][2]]
			u_row2_weights = [Weights66_1[5][2],Weights66_1[4][2],Weights66_1[3][2],Weights66_1[2][2],Weights66_1[1][2],Weights66_1[0][2]]

		if common[1] == 2:
			u_row0_poles = [Poles66_1[0][5],Poles66_1[1][5],Poles66_1[2][5],Poles66_1[3][5],Poles66_1[4][5],Poles66_1[5][5]]
			u_row0_weights = [Weights66_1[0][5],Weights66_1[1][5],Weights66_1[2][5],Weights66_1[3][5],Weights66_1[4][5],Weights66_1[5][5]]
			u_row1_poles = [Poles66_1[0][4],Poles66_1[1][4],Poles66_1[2][4],Poles66_1[3][4],Poles66_1[4][4],Poles66_1[5][4]]
			u_row1_weights = [Weights66_1[0][4],Weights66_1[1][4],Weights66_1[2][4],Weights66_1[3][4],Weights66_1[4][4],Weights66_1[5][4]]
			u_row2_poles = [Poles66_1[0][3],Poles66_1[1][3],Poles66_1[2][3],Poles66_1[3][3],Poles66_1[4][3],Poles66_1[5][3]]
			u_row2_weights = [Weights66_1[0][3],Weights66_1[1][3],Weights66_1[2][3],Weights66_1[3][3],Weights66_1[4][3],Weights66_1[5][3]]

		# sorta checked 07/08/2017? rows and cols still dubious

		# set known edges
		p00 = u_row0_poles[0]
		p01 = u_row0_poles[1]
		p02 = u_row0_poles[2]
		p03 = u_row0_poles[3]
		p04 = u_row0_poles[4]
		p05 = u_row0_poles[5]

		w00 = u_row0_weights[0]
		w01 = u_row0_weights[1]
		w02 = u_row0_weights[2]
		w03 = u_row0_weights[3]
		w04 = u_row0_weights[4]
		w05 = u_row0_weights[5]

		p10 = v_col0_poles[1]
		p20 = v_col0_poles[2]
		p30 = v_col0_poles[3]
		p40 = v_col0_poles[4]
		p50 = v_col0_poles[5]

		w10 = v_col0_weights[1]
		w20 = v_col0_weights[2]
		w30 = v_col0_weights[3]
		w40 = v_col0_weights[4]
		w50 = v_col0_weights[5]

		# set weights
		w11 = w01 * w10
		w12 = w02 * w10
		w13 = w03 * w10
		w14 = w04 * w10
		w15 = w05 * w10

		w21 = w01 * w20
		w22 = w02 * w20
		w23 = w03 * w20
		w24 = w04 * w20
		w25 = w05 * w20

		w31 = w01 * w30
		w32 = w02 * w30
		w33 = w03 * w30
		w34 = w04 * w30
		w35 = w05 * w30

		w41 = w01 * w40
		w42 = w02 * w40
		w43 = w03 * w40
		w44 = w04 * w40
		w45 = w05 * w40

		w51 = w01 * w50
		w52 = w02 * w50
		w53 = w03 * w50
		w54 = w04 * w50
		w55 = w05 * w50

		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35,
					w40, w41, w42, w43, w44, w45,
					w50, w51, w52, w53, w54, w55,]


		# establish tangent ratios for G1

		u_tan_ratio = (p01-p00).Length / (v_col1_poles[0]-p00).Length
		v_tan_ratio = (p10-p00).Length / (u_row1_poles[0]-p00).Length


		# build first row and column of inner control points.

		p11_u = p01 + (p01-u_row1_poles[1])*v_tan_ratio
		p11_v = p10 + (p10-v_col1_poles[1])*u_tan_ratio
		p11 = (p11_u + p11_v) * 0.5

		p12 = p02 + (p02-u_row1_poles[2])*v_tan_ratio
		p13 = p03 + (p03-u_row1_poles[3])*v_tan_ratio
		p14 = p04 + (p04-u_row1_poles[4])*v_tan_ratio
		p15 = p05 + (p05-u_row1_poles[5])*v_tan_ratio

		p21 = p20 + (p20-v_col1_poles[2])*u_tan_ratio
		p31 = p30 + (p30-v_col1_poles[3])*u_tan_ratio
		p41 = p40 + (p40-v_col1_poles[4])*u_tan_ratio
		p51 = p50 + (p50-v_col1_poles[5])*u_tan_ratio


		# build the second row and column as projections of the input grids
		# there is some redundancy here, as first inner row/column points are recalculated in the curvature matching function

		# p22 using u_rows : surf_1 points with surf_0 tangent ratio
		proj_u_rows_u2 = match_r_6P_6P_Cubic(u_row0_poles[2], u_row1_poles[2], u_row2_poles[2], v_tan_ratio)
		if equalVectors(proj_u_rows_u2[0], p12, 0.0000001):
			p22_u = proj_u_rows_u2[1]
		else:
			print ('failed to match tangent segment on p22_u calculation')
		p22_u_ext = p22_u + (p12 - p02) * 5.0
		p22_u_ext_L = Part.LineSegment(p22_u,p22_u_ext)
		# p22 using v_cols : surf_0 points with surf_1 tangent ratio
		proj_v_cols_v2 = match_r_6P_6P_Cubic(v_col0_poles[2], v_col1_poles[2], v_col2_poles[2], u_tan_ratio)
		if equalVectors(proj_v_cols_v2[0], p21, 0.0000001):
			p22_v = proj_v_cols_v2[1]
		else:
			print ('failed to match tangent segment on p22_v calculation')
		p22_v_ext = p22_v + (p21 - p20) * 5.0
		p22_v_ext_L = Part.LineSegment(p22_v,p22_v_ext)
		# combine both p22 versions
		p22_u_isect = int_2l(p22_u_ext_L,p22_v_ext_L)
		p22_v_isect = int_2l(p22_v_ext_L,p22_u_ext_L)
		p22 = (p22_u_isect +p22_v_isect)*.5 

		# p23 using u_rows: surf_1 points with surf_0 tangent ratio
		proj_u_rows_u3 = match_r_6P_6P_Cubic(u_row0_poles[3], u_row1_poles[3], u_row2_poles[3], v_tan_ratio)
		if equalVectors(proj_u_rows_u3[0], p13, 0.0000001):
			p23_h = proj_u_rows_u3[1]
		else:
			print ('failed to match tangent segment on p23_h calculation')

		# p24 using u_rows: surf_1 points with surf_0 tangent ratio
		proj_u_rows_u4 = match_r_6P_6P_Cubic(u_row0_poles[4], u_row1_poles[4], u_row2_poles[4], v_tan_ratio)
		if equalVectors(proj_u_rows_u4[0], p14, 0.0000001):
			p24_h = proj_u_rows_u4[1]
		else:
			print ('failed to match tangent segment on p24_h calculation')

		# p25 using u_rows: surf_1 points with surf_0 tangent ratio
		proj_u_rows_u5 = match_r_6P_6P_Cubic(u_row0_poles[5], u_row1_poles[5], u_row2_poles[5], v_tan_ratio)
		if equalVectors(proj_u_rows_u5[0], p15, 0.0000001):
			p25_h = proj_u_rows_u5[1]
		else:
			print ('failed to match tangent segment on p25_h calculation')

		# p32 using v_cols : surf_0 points with surf_1 tangent ratio
		proj_v_cols_v3 = match_r_6P_6P_Cubic(v_col0_poles[3], v_col1_poles[3], v_col2_poles[3], u_tan_ratio)
		if equalVectors(proj_v_cols_v3[0], p31, 0.0000001):
			p32_h = proj_v_cols_v3[1]
		else:
			print ('failed to match tangent segment on p32_h calculation')
		# p42 using v_cols : surf_0 points with surf_1 tangent ratio
		proj_v_cols_v4 = match_r_6P_6P_Cubic(v_col0_poles[4], v_col1_poles[4], v_col2_poles[4], u_tan_ratio)
		if equalVectors(proj_v_cols_v4[0], p41, 0.0000001):
			p42_h = proj_v_cols_v4[1]
		else:
			print ('failed to match tangent segment on p42_h calculation')
		# p52 using v_cols : surf_0 points with surf_1 tangent ratio
		proj_v_cols_v5 = match_r_6P_6P_Cubic(v_col0_poles[5], v_col1_poles[5], v_col2_poles[5], u_tan_ratio)
		if equalVectors(proj_v_cols_v5[0], p51, 0.0000001):
			p52_h = proj_v_cols_v5[1]
		else:
			print ('failed to match tangent segment on p52_h calculation')

		v00 = Base.Vector(0,0,0)

		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23_h, p24_h, p25_h,
					p30, p31, p32_h, v00, v00, v00,
					p40, p41, p42_h, v00, v00, v00,
					p50, p51, p52_h, v00, v00, v00]





		Legs=[0]*30

		Legs[0]=Part.LineSegment(p00,p01)
		Legs[1]=Part.LineSegment(p01,p02)
		Legs[2]=Part.LineSegment(p02,p03)
		Legs[3]=Part.LineSegment(p03,p04)
		Legs[4]=Part.LineSegment(p04,p05)

		Legs[5]=Part.LineSegment(p00,p10)
		Legs[6]=Part.LineSegment(p10,p20)
		Legs[7]=Part.LineSegment(p20,p30)
		Legs[8]=Part.LineSegment(p30,p40)
		Legs[9]=Part.LineSegment(p40,p50)

		Legs[10]=Part.LineSegment(p01,p11_u)
		Legs[11]=Part.LineSegment(p02,p12)
		Legs[12]=Part.LineSegment(p03,p13)
		Legs[13]=Part.LineSegment(p04,p14)
		Legs[14]=Part.LineSegment(p05,p15)

		Legs[15]=Part.LineSegment(p10,p11_v)
		Legs[16]=Part.LineSegment(p20,p21)
		Legs[17]=Part.LineSegment(p30,p31)
		Legs[18]=Part.LineSegment(p40,p41)
		Legs[19]=Part.LineSegment(p50,p51)

		Legs[20]=Part.LineSegment(p11,p12)
		Legs[21]=Part.LineSegment(p12,p13)
		Legs[22]=Part.LineSegment(p13,p14)
		Legs[23]=Part.LineSegment(p14,p15)

		Legs[24]=Part.LineSegment(p11,p21)
		Legs[25]=Part.LineSegment(p21,p31)
		Legs[26]=Part.LineSegment(p31,p41)
		Legs[27]=Part.LineSegment(p41,p51)

		Legs[28]=Part.LineSegment(p12,p22_u_isect)

		#Legs[29]=Part.LineSegment(p13,p23_h)  # these points can collapse. need to test before making lines.
		#Legs[30]=Part.LineSegment(p14,p24_h) 
		#Legs[31]=Part.LineSegment(p15, p25_h)

		Legs[29]=Part.LineSegment(p21,p22_v_isect)

		#Legs[33]=Part.LineSegment(p31, p32_h)
		#Legs[34]=Part.LineSegment(p41, p42_h)
		#Legs[35]=Part.LineSegment(p51, p52_h)

		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGridNStar66_NSub:
	def __init__(self, fp , SubList):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGridNStar66_NSub class Init\n")
		fp.addProperty("App::PropertyLinkList","SubList","ControlGridNStar66_NSub","Reference Sub Grids").SubList = SubList
		fp.addProperty("App::PropertyInteger","N","ControlGridNStar66_NSub","N").N
		fp.setEditorMode("N", 2)
		fp.addProperty("Part::PropertyGeometryList","Legs","ControlGridNStar66_NSub","control segments").Legs
		fp.addProperty("App::PropertyPythonObject","StarGrid","ControlGridNStar66_NSub","Poles").StarGrid
		fp.addProperty("App::PropertyInteger","SquishDiag4","ControlGridNStar66_NSub","SquishDiag4").SquishDiag4 = 0
		fp.Proxy = self

	def getL1Scale(self, p0, p1, p2):
		L1_scale = (((p1 - p0).normalize()).dot(p2-p1)) / ((p1 - p0).Length)
		return L1_scale

	def StarRow2_2Sub(self, fp, Sub_0_i, Sub_1_i):
		L1Scale_Sub0_v = self.getL1Scale(fp.StarGrid[Sub_0_i][2][0], fp.StarGrid[Sub_0_i][8][0], fp.StarGrid[Sub_0_i][14][0])
		L1Scale_Sub1_u = self.getL1Scale(fp.StarGrid[Sub_1_i][12][0], fp.StarGrid[Sub_1_i][13][0], fp.StarGrid[Sub_1_i][14][0])
		L1Scale_Mid = 0.5 * (L1Scale_Sub0_v + L1Scale_Sub1_u)
		Mid_p2 = fp.StarGrid[Sub_0_i][17][0] + L1Scale_Mid * (fp.StarGrid[Sub_0_i][11][0]-fp.StarGrid[Sub_0_i][5][0])

		fp.StarGrid[Sub_0_i][17][0] = Mid_p2
		fp.StarGrid[Sub_1_i][32][0] = Mid_p2
		fp.StarGrid[Sub_0_i][16][0] = fp.StarGrid[Sub_0_i][16][0] + L1Scale_Mid * (fp.StarGrid[Sub_0_i][10][0]-fp.StarGrid[Sub_0_i][4][0])
		fp.StarGrid[Sub_1_i][26][0] = fp.StarGrid[Sub_1_i][26][0] + L1Scale_Mid * (fp.StarGrid[Sub_1_i][25][0]-fp.StarGrid[Sub_1_i][24][0])

		L1Scale_15 = 0.5 * (L1Scale_Sub0_v + L1Scale_Mid)
		L1Scale_20 = 0.5 * (L1Scale_Sub1_u + L1Scale_Mid)
		fp.StarGrid[Sub_0_i][15][0] = fp.StarGrid[Sub_0_i][15][0] + L1Scale_15 * (fp.StarGrid[Sub_0_i][9][0]-fp.StarGrid[Sub_0_i][3][0])
		fp.StarGrid[Sub_1_i][20][0] = fp.StarGrid[Sub_1_i][20][0] + L1Scale_20 * (fp.StarGrid[Sub_1_i][19][0]-fp.StarGrid[Sub_1_i][18][0])

		# control leg visualization
		Legs_Row2 = []
		Legs_Row2_i = [[[9,15],[10,16],[11,17],[14,15],[15,16],[16,17]],[[14,20],[19,20],[20,26],[25,26],[26,32]]]
		for i in Legs_Row2_i[0]:
			Legs_Row2.append(Part.LineSegment(fp.StarGrid[Sub_0_i][i[0]][0],fp.StarGrid[Sub_0_i][i[1]][0]))

		for i in Legs_Row2_i[1]:
			Legs_Row2.append(Part.LineSegment(fp.StarGrid[Sub_1_i][i[0]][0],fp.StarGrid[Sub_1_i][i[1]][0]))

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
		fp.StarGrid[Sub_i][21][0] = fp.StarGrid[Sub_i][20][0] + fp.StarGrid[Sub_i][15][0] - fp.StarGrid[Sub_i][14][0]

		# control leg visualization
		Legs_Diag3 = [0,0]
		Legs_Diag3[0] = Part.LineSegment(fp.StarGrid[Sub_i][15][0], fp.StarGrid[Sub_i][21][0])
		Legs_Diag3[1] = Part.LineSegment(fp.StarGrid[Sub_i][20][0], fp.StarGrid[Sub_i][21][0])

		Legs = fp.Legs
		fp.Legs = Legs + Legs_Diag3
		return 0

	def StarDiag3_SubLoop(self, fp, N):
		# loop from first element to last. no pairs, no loop back required.
		for i in range(N):
			self.StarDiag3_Sub(fp, i)
		return 0

	def StarRow3_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# prepare seam point
		Mid_p2 = fp.StarGrid[Sub_0_i][17][0] + 0.5 * (fp.StarGrid[Sub_0_i][21][0]-fp.StarGrid[Sub_0_i][15][0]+fp.StarGrid[Sub_1_i][21][0]-fp.StarGrid[Sub_1_i][20][0])

		# apply seam point locally
		fp.StarGrid[Sub_0_i][23][0] = Mid_p2
		fp.StarGrid[Sub_1_i][33][0] = Mid_p2

		# average to seam neighbor locally
		fp.StarGrid[Sub_0_i][22][0] = fp.StarGrid[Sub_0_i][16][0] + 0.5 * (fp.StarGrid[Sub_0_i][21][0]-fp.StarGrid[Sub_0_i][15][0]+fp.StarGrid[Sub_0_i][23][0]-fp.StarGrid[Sub_0_i][17][0])
		fp.StarGrid[Sub_1_i][27][0] = fp.StarGrid[Sub_1_i][26][0] + 0.5 * (fp.StarGrid[Sub_1_i][21][0]-fp.StarGrid[Sub_1_i][20][0]+fp.StarGrid[Sub_1_i][33][0]-fp.StarGrid[Sub_1_i][32][0])

		Legs_Row3 = []
		Legs_Row3_i = [[[16,22],[17,23],[21,22],[22,23]],[[21,27],[26,27],[27,33]]]
		for i in Legs_Row3_i[0]:
			Legs_Row3.append(Part.LineSegment(fp.StarGrid[Sub_0_i][i[0]][0],fp.StarGrid[Sub_0_i][i[1]][0]))

		for i in Legs_Row3_i[1]:
			Legs_Row3.append(Part.LineSegment(fp.StarGrid[Sub_1_i][i[0]][0],fp.StarGrid[Sub_1_i][i[1]][0]))

		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row3 
		return 0

	def StarRow3_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow3_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow3_2Sub(fp, N-1, 0)
		return 0

	def StarDiag4_3Sub(self, fp, Sub_prev_i, Sub_i, Sub_next_i):
		# parallelogram diagonal
		#Sub_28_raw = fp.StarGrid[Sub_i][27][0] + (fp.StarGrid[Sub_i][22][0]-fp.StarGrid[Sub_i][21][0])

		# components of the parallelogram diagonals, scaled by opposite edge on adjacent grid
		u_28_i = fp.StarGrid[Sub_i][22][0] - fp.StarGrid[Sub_i][21][0]
		v_28_i = fp.StarGrid[Sub_i][27][0] - fp.StarGrid[Sub_i][21][0]

		u_28_prev_i = fp.StarGrid[Sub_prev_i][27][0] - fp.StarGrid[Sub_prev_i][21][0]
		v_28_next_i = fp.StarGrid[Sub_next_i][22][0] - fp.StarGrid[Sub_next_i][21][0]

		scaled_u_28_i = u_28_i * ( 1 +  ( u_28_prev_i.Length - u_28_i.Length ) / ( 3.0 * u_28_i.Length ) )
		scaled_v_28_i = v_28_i * ( 1 +  ( v_28_next_i.Length - v_28_i.Length ) / ( 3.0 * v_28_i.Length ) )

		Sub_28_raw = fp.StarGrid[Sub_i][21][0] + scaled_u_28_i +scaled_v_28_i

		# scaling factor. based on N? 
		# no. need to fix this. the scaling factor needs to achieve alignment between neighboring subgrids if they align,
		# and a smooth rotation if they do not align.
		# something...something...angle in the normal or maybe tangent plane. something...(1-cos()) factor.

		if fp.N == 3:
			scale = 0.75 # scaled down 75% to spread out center this works quite well for triangles actually
		if fp.N == 5:
			scale = 1.25 # this is a mess. a single factor doesn't do it. oh well, moving on.
		if fp.N == 6:
			scale = 1.5

		Sub_28_scaled = fp.StarGrid[Sub_i][21][0] + scale * (Sub_28_raw - fp.StarGrid[Sub_i][21][0])

		Plane_prev = Part.Plane(fp.StarGrid[Sub_i][33][0],fp.StarGrid[Sub_i][23][0],fp.StarGrid[Sub_prev_i][33][0])
		Plane_next = Part.Plane(fp.StarGrid[Sub_i][33][0],fp.StarGrid[Sub_i][23][0],fp.StarGrid[Sub_next_i][23][0])

		Sub_28_prev_param = Plane_prev.parameter(Sub_28_scaled)
		Sub_28_prev_proj = Plane_prev.value(Sub_28_prev_param[0],Sub_28_prev_param[1])

		Sub_28_next_param = Plane_next.parameter(Sub_28_scaled)
		Sub_28_next_proj = Plane_next.value(Sub_28_next_param[0],Sub_28_next_param[1])

		fp.StarGrid[Sub_i][28][0] = 0.5 * Sub_28_scaled + 0.25 * (Sub_28_prev_proj + Sub_28_next_proj) 
		# best first round result for N=3, bad for recursion. N=5 is distorted in the center
		
		# fp.StarGrid[Sub_i][28][0] = 0.0 * Sub_28_scaled + 0.5 * (Sub_28_prev_proj + Sub_28_next_proj) 
		# N=3 round 1 shmushed, but good result on round 2. round 3 too pointy. unclear for N=5

		# control leg visualization
		Legs_Diag4 = [0,0]
		Legs_Diag4[0] = Part.LineSegment(fp.StarGrid[Sub_i][22][0],fp.StarGrid[Sub_i][28][0])
		Legs_Diag4[1] = Part.LineSegment(fp.StarGrid[Sub_i][27][0],fp.StarGrid[Sub_i][28][0])

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

	def StarDiag4_squish(self, fp, N):
		# we are going to average all poles [28] around the loop to define the squish center

		# sum all poles [28]
		Poles_28_total = Base.Vector(0,0,0)
		for i in range(N):
			Poles_28_total = Poles_28_total + fp.StarGrid[i][28][0]

		SquishCenter = (1.0 / N) * Poles_28_total

		# do cross products in pairs around the loops to get a list of normal direction approximations
		cross_total = Base.Vector(0,0,0)
		for i in range(N-1):
			cross_total = cross_total + (fp.StarGrid[i][28][0]-SquishCenter).cross(fp.StarGrid[i+1][28][0]-SquishCenter)
		# close sequence by looping back
		cross_total = cross_total + (fp.StarGrid[N-1][28][0]-SquishCenter).cross(fp.StarGrid[0][28][0]-SquishCenter)

		# define squish plane from squish center and squish normal
		Squish_Plane = Part.Plane(SquishCenter, cross_total)

		# project all diag4 points to this plane.
		projections = [0] * N
		for i in range(N):
			param = Squish_Plane.parameter(fp.StarGrid[i][28][0])
			fp.StarGrid[i][28][0] = Squish_Plane.value(param[0],param[1])

	def StarRow4_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# pull up the seam at row 4
		Mid_p4 = 0.5 * (fp.StarGrid[Sub_0_i][28][0] + fp.StarGrid[Sub_1_i][28][0])
		fp.StarGrid[Sub_0_i][29][0] = Mid_p4
		fp.StarGrid[Sub_1_i][34][0] = Mid_p4

		# control leg visualization
		Legs_Row4 = [0,0,0]
		Legs_Row4[0] = Part.LineSegment(fp.StarGrid[Sub_0_i][23][0],fp.StarGrid[Sub_0_i][29][0])
		Legs_Row4[1] = Part.LineSegment(fp.StarGrid[Sub_0_i][28][0],fp.StarGrid[Sub_0_i][29][0])
		Legs_Row4[2] = Part.LineSegment(fp.StarGrid[Sub_1_i][28][0],fp.StarGrid[Sub_1_i][34][0])

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row4
		return 0

	def StarRow4_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow4_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow4_2Sub(fp, N-1, 0)
		return 0

	def StarCenter(self, fp, N):
		# we are going to average all poles [29] around the loop to define the center
		# sum all poles [29]
		Vector_total = Base.Vector(0,0,0)
		for i in range(N):
			Vector_total = Vector_total + fp.StarGrid[i][29][0]

		StarCenter = (1.0 / N) * Vector_total 

		# Apply center point to all Poles lists
		for i in range(N):
			fp.StarGrid[i][35][0] = StarCenter

		# control leg visualization
		Legs_Row5 = []
		for i in range(N):
			Legs_Row5.append(Part.LineSegment(fp.StarGrid[i][29][0],fp.StarGrid[i][35][0]))

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row5

		return 0

	def execute(self, fp):
		# refresh properties back to linked SubGrids every time the Star gets recomputed
		# determine number of SubGrids
		fp.N=len(fp.SubList)
		# set size of Stargrid attribute
		fp.StarGrid = [0] * fp.N
		# compile all SubGrid Poles and Weights into StarGrid attribute
		for n in range(fp.N):
			#set size of single SubGrid
			StarGrid_n = [0] * 36
			for i in range(36):
				# set Pole/Weight format [Base.Vector(), Float]
				StarGrid_n_i = [0,0]
				StarGrid_n_i[0] = fp.SubList[n].Poles[i]
				StarGrid_n_i[1] = fp.SubList[n].Weights[i]
				StarGrid_n[i] = StarGrid_n_i
			fp.StarGrid[n] = StarGrid_n
		# a specific Pole is now addressed as StarGrid[n][i][0]
		# a specific Weight is now addresses as StarGrid[n][i][1]


		fp.Legs = []
		self.StarRow2_SubLoop(fp, fp.N)
		self.StarDiag3_SubLoop(fp, fp.N)
		self.StarRow3_SubLoop(fp, fp.N)
		self.StarDiag4_SubLoop(fp, fp.N)
		if fp.SquishDiag4 == 1:
			self.StarDiag4_squish(fp, fp.N)
			print ("Squish Diagonal 4")
		else:
			print ("no Squish Diagonal 4!")

		self.StarRow4_SubLoop(fp, fp.N)
		self.StarCenter(fp, fp.N)

		fp.Shape = Part.Shape(fp.Legs)

		# convert all vectors in StarGrid to lists. this allows saving the PythonObject attribute. The data needs to be fed back to Base.Vector() downstream.
		for n in range(fp.N):
			#set size of single SubGrid
			StarGrid_n = [0] * 36
			for i in range(36):
				# set Pole/Weight format [Base.Vector(), Float]
				StarGrid_n_i = [0,0]
				StarGrid_n_i[0] = [fp.StarGrid[n][i][0].x, fp.StarGrid[n][i][0].y, fp.StarGrid[n][i][0].z]
				StarGrid_n_i[1] = fp.SubList[n].Weights[i]
				StarGrid_n[i] = StarGrid_n_i
			fp.StarGrid[n] = StarGrid_n

class CubicNStarSurface_NStar66: 
	def __init__(self, obj , NStarGrid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicNStarSurface_NStar66 Init\n")
		obj.addProperty("App::PropertyLink","NStarGrid","CubicNStarSurface_NStar66","control grid star").NStarGrid = NStarGrid
		obj.addProperty("Part::PropertyGeometryList","NSurf","CubicNStarSurface_NStar66","N Cubic Surfaces").NSurf
		obj.Proxy = self

	def HomogeneousGrids(self, fp, N):
		HomogeneousGrids = [0] * N
		for i in range(N):
			HGrid_i = [0] *36
			for j in range(36):
				# convert the float list from NStarGrid back to Base.Vector.
				HGrid_i[j] = [Base.Vector(fp.NStarGrid.StarGrid[i][j][0][0],fp.NStarGrid.StarGrid[i][j][0][1],fp.NStarGrid.StarGrid[i][j][0][2]), fp.NStarGrid.StarGrid[i][j][1]] 
			HomogeneousGrids[i] = HGrid_i
		return HomogeneousGrids

	def makeNSurf(self, fp, HomogeneousGrids, N):
		NSurf = [0] * N
		for i in range(N):
			NSurf[i] = NURBS_Cubic_66_surf(HomogeneousGrids[i])
		return NSurf

	def execute(self,fp):
		# cast [x ,y, z] in linked NstarGrid back to Base.Vector
		HomogeneousGrids = self.HomogeneousGrids(fp, fp.NStarGrid.N)

		#loop over the homogeneous grids to make the surfaces
		NSurf = self.makeNSurf(fp, HomogeneousGrids, fp.NStarGrid.N)
		fp.NSurf = NSurf

		fp.Shape = Part.Shape(fp.NSurf)

class StarTrim_CubicNStar:
	def __init__(self, obj , CubicNStar):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nStarTrim_CubicNStar Init\n")
		obj.addProperty("App::PropertyLink","CubicNStar","StarTrim_CubicNStar","base Surface star").CubicNStar = CubicNStar
		obj.addProperty("Part::PropertyGeometryList","NSurf_main","StarTrim_CubicNStar","N Cubic Surfaces, main corner section").NSurf_main
		obj.addProperty("Part::PropertyGeometryList","NSurf_lead","StarTrim_CubicNStar","N Cubic Surfaces, leading edge section").NSurf_lead
		obj.addProperty("Part::PropertyGeometryList","NSurf_lag","StarTrim_CubicNStar","N Cubic Surfaces, lagging edge section").NSurf_lag
		obj.addProperty("Part::PropertyGeometryList","NSurf_center","StarTrim_CubicNStar","N Cubic Surfaces, center section").NSurf_center
		obj.Proxy = self

	def execute(self, fp):

		N = fp.CubicNStar.NStarGrid.N

		NSurf_main = [0] * N
		for i in range(N):
			surf_main = fp.CubicNStar.NSurf[i]
			surf_main.segment(0.0, 0.5, 0.0, 0.5)
			NSurf_main[i] = surf_main
		fp.NSurf_main = NSurf_main

		NSurf_lead = [0] * N
		for i in range(N):
			surf_lead = fp.CubicNStar.NSurf[i]
			surf_lead.segment(0.5, 1.0, 0.0, 0.5)
			NSurf_lead[i] = surf_lead
		fp.NSurf_lead = NSurf_lead

		NSurf_lag = [0] * N
		for i in range(N):
			surf_lag = 	fp.CubicNStar.NSurf[i]
			surf_lag.segment(0.0, 0.5, 0.5, 1.0)
			NSurf_lag[i] = surf_lag
		fp.NSurf_lag = NSurf_lag

		NSurf_center = [0] * N
		for i in range(N):
			surf_center = 	fp.CubicNStar.NSurf[i]
			surf_center.segment(0.5, 1.0, 0.5, 1.0)
			surf_center.insertUKnots([5.0/6.0],[1],0.000001)
			surf_center.insertVKnots([5.0/6.0],[1],0.000001)
			NSurf_center[i] = surf_center
		fp.NSurf_center = NSurf_center

		trim = fp.NSurf_main + fp.NSurf_lead + fp.NSurf_lag

		fp.Shape = Part.Shape(trim)

class ControlGridNStar66_StarTrim: # quick and dirty test for star center refinement. uses a list of subgrids within the single linked StarTrim, instead of a linklist. 
	def __init__(self, fp , StarTrim):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGridNStar66_StarTrim class Init\n")
		fp.addProperty("App::PropertyLink","StarTrim","ControlGridNStar66_StarTrim","Reference StarTrim").StarTrim = StarTrim
		fp.addProperty("App::PropertyInteger","N","ControlGridNStar66_StarTrim","N").N
		fp.setEditorMode("N", 2)
		fp.addProperty("Part::PropertyGeometryList","Legs","ControlGridNStar66_StarTrim","control segments").Legs
		fp.addProperty("App::PropertyPythonObject","StarGrid","ControlGridNStar66_StarTrim","Poles").StarGrid
		fp.addProperty("App::PropertyInteger","SquishDiag4","ControlGridNStar66_NSub","SquishDiag4").SquishDiag4 = 0
		fp.Proxy = self


	def getL1Scale(self, p0, p1, p2):
		L1_scale = (((p1 - p0).normalize()).dot(p2-p1)) / ((p1 - p0).Length)
		return L1_scale

	def StarRow2_2Sub(self, fp, Sub_0_i, Sub_1_i):
		L1Scale_Sub0_v = self.getL1Scale(fp.StarGrid[Sub_0_i][2][0], fp.StarGrid[Sub_0_i][8][0], fp.StarGrid[Sub_0_i][14][0])
		L1Scale_Sub1_u = self.getL1Scale(fp.StarGrid[Sub_1_i][12][0], fp.StarGrid[Sub_1_i][13][0], fp.StarGrid[Sub_1_i][14][0])
		L1Scale_Mid = 0.5 * (L1Scale_Sub0_v + L1Scale_Sub1_u)
		Mid_p2 = fp.StarGrid[Sub_0_i][17][0] + L1Scale_Mid * (fp.StarGrid[Sub_0_i][11][0]-fp.StarGrid[Sub_0_i][5][0])

		fp.StarGrid[Sub_0_i][17][0] = Mid_p2
		fp.StarGrid[Sub_1_i][32][0] = Mid_p2
		fp.StarGrid[Sub_0_i][16][0] = fp.StarGrid[Sub_0_i][16][0] + L1Scale_Mid * (fp.StarGrid[Sub_0_i][10][0]-fp.StarGrid[Sub_0_i][4][0])
		fp.StarGrid[Sub_1_i][26][0] = fp.StarGrid[Sub_1_i][26][0] + L1Scale_Mid * (fp.StarGrid[Sub_1_i][25][0]-fp.StarGrid[Sub_1_i][24][0])

		L1Scale_15 = 0.5 * (L1Scale_Sub0_v + L1Scale_Mid)
		L1Scale_20 = 0.5 * (L1Scale_Sub1_u + L1Scale_Mid)
		fp.StarGrid[Sub_0_i][15][0] = fp.StarGrid[Sub_0_i][15][0] + L1Scale_15 * (fp.StarGrid[Sub_0_i][9][0]-fp.StarGrid[Sub_0_i][3][0])
		fp.StarGrid[Sub_1_i][20][0] = fp.StarGrid[Sub_1_i][20][0] + L1Scale_20 * (fp.StarGrid[Sub_1_i][19][0]-fp.StarGrid[Sub_1_i][18][0])

		# control leg visualization
		Legs_Row2 = []
		Legs_Row2_i = [[[9,15],[10,16],[11,17],[14,15],[15,16],[16,17]],[[14,20],[19,20],[20,26],[25,26],[26,32]]]
		for i in Legs_Row2_i[0]:
			Legs_Row2.append(Part.LineSegment(fp.StarGrid[Sub_0_i][i[0]][0],fp.StarGrid[Sub_0_i][i[1]][0]))

		for i in Legs_Row2_i[1]:
			Legs_Row2.append(Part.LineSegment(fp.StarGrid[Sub_1_i][i[0]][0],fp.StarGrid[Sub_1_i][i[1]][0]))

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
		fp.StarGrid[Sub_i][21][0] = fp.StarGrid[Sub_i][20][0] + fp.StarGrid[Sub_i][15][0] - fp.StarGrid[Sub_i][14][0]

		# control leg visualization
		Legs_Diag3 = [0,0]
		Legs_Diag3[0] = Part.LineSegment(fp.StarGrid[Sub_i][15][0], fp.StarGrid[Sub_i][21][0])
		Legs_Diag3[1] = Part.LineSegment(fp.StarGrid[Sub_i][20][0], fp.StarGrid[Sub_i][21][0])

		Legs = fp.Legs
		fp.Legs = Legs + Legs_Diag3
		return 0

	def StarDiag3_SubLoop(self, fp, N):
		# loop from first element to last. no pairs, no loop back required.
		for i in range(N):
			self.StarDiag3_Sub(fp, i)
		return 0

	def StarRow3_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# prepare seam point
		Mid_p2 = fp.StarGrid[Sub_0_i][17][0] + 0.5 * (fp.StarGrid[Sub_0_i][21][0]-fp.StarGrid[Sub_0_i][15][0]+fp.StarGrid[Sub_1_i][21][0]-fp.StarGrid[Sub_1_i][20][0])

		# apply seam point locally
		fp.StarGrid[Sub_0_i][23][0] = Mid_p2
		fp.StarGrid[Sub_1_i][33][0] = Mid_p2

		# average to seam neighbor locally
		fp.StarGrid[Sub_0_i][22][0] = fp.StarGrid[Sub_0_i][16][0] + 0.5 * (fp.StarGrid[Sub_0_i][21][0]-fp.StarGrid[Sub_0_i][15][0]+fp.StarGrid[Sub_0_i][23][0]-fp.StarGrid[Sub_0_i][17][0])
		fp.StarGrid[Sub_1_i][27][0] = fp.StarGrid[Sub_1_i][26][0] + 0.5 * (fp.StarGrid[Sub_1_i][21][0]-fp.StarGrid[Sub_1_i][20][0]+fp.StarGrid[Sub_1_i][33][0]-fp.StarGrid[Sub_1_i][32][0])

		Legs_Row3 = []
		Legs_Row3_i = [[[16,22],[17,23],[21,22],[22,23]],[[21,27],[26,27],[27,33]]]
		for i in Legs_Row3_i[0]:
			Legs_Row3.append(Part.LineSegment(fp.StarGrid[Sub_0_i][i[0]][0],fp.StarGrid[Sub_0_i][i[1]][0]))

		for i in Legs_Row3_i[1]:
			Legs_Row3.append(Part.LineSegment(fp.StarGrid[Sub_1_i][i[0]][0],fp.StarGrid[Sub_1_i][i[1]][0]))

		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row3 
		return 0

	def StarRow3_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow3_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow3_2Sub(fp, N-1, 0)
		return 0

	def StarDiag4_3Sub(self, fp, Sub_prev_i, Sub_i, Sub_next_i):
		# parallelogram diagonal
		#Sub_28_raw = fp.StarGrid[Sub_i][27][0] + (fp.StarGrid[Sub_i][22][0]-fp.StarGrid[Sub_i][21][0])

		# components of the parallelogram diagonals, scaled by opposite edge on adjacent grid
		u_28_i = fp.StarGrid[Sub_i][22][0] - fp.StarGrid[Sub_i][21][0]
		v_28_i = fp.StarGrid[Sub_i][27][0] - fp.StarGrid[Sub_i][21][0]

		u_28_prev_i = fp.StarGrid[Sub_prev_i][27][0] - fp.StarGrid[Sub_prev_i][21][0]
		v_28_next_i = fp.StarGrid[Sub_next_i][22][0] - fp.StarGrid[Sub_next_i][21][0]

		scaled_u_28_i = u_28_i * ( 1 +  ( u_28_prev_i.Length - u_28_i.Length ) / ( 3.0 * u_28_i.Length ) )
		scaled_v_28_i = v_28_i * ( 1 +  ( v_28_next_i.Length - v_28_i.Length ) / ( 3.0 * v_28_i.Length ) )

		Sub_28_raw = fp.StarGrid[Sub_i][21][0] + scaled_u_28_i +scaled_v_28_i

		# scaling factor. based on N? 
		# no. need to fix this. the scaling factor needs to achieve alignment between neighboring subgrids if they align,
		# and a smooth rotation if they do not align.
		# something...something...angle in the normal or maybe tangent plane. something...(1-cos()) factor.

		if fp.N == 3:
			scale = 0.75 # scaled down 75% to spread out center this works quite well for triangles actually
		if fp.N == 5:
			scale = 1.00 # this is a mess. a single factor doesn't do it. oh well, moving on.




		Sub_28_scaled = fp.StarGrid[Sub_i][21][0] + scale * (Sub_28_raw - fp.StarGrid[Sub_i][21][0])

		Plane_prev = Part.Plane(fp.StarGrid[Sub_i][33][0],fp.StarGrid[Sub_i][23][0],fp.StarGrid[Sub_prev_i][33][0])
		Plane_next = Part.Plane(fp.StarGrid[Sub_i][33][0],fp.StarGrid[Sub_i][23][0],fp.StarGrid[Sub_next_i][23][0])

		Sub_28_prev_param = Plane_prev.parameter(Sub_28_scaled)
		Sub_28_prev_proj = Plane_prev.value(Sub_28_prev_param[0],Sub_28_prev_param[1])

		Sub_28_next_param = Plane_next.parameter(Sub_28_scaled)
		Sub_28_next_proj = Plane_next.value(Sub_28_next_param[0],Sub_28_next_param[1])

		fp.StarGrid[Sub_i][28][0] = 0.5 * Sub_28_scaled + 0.25 * (Sub_28_prev_proj + Sub_28_next_proj)

		# control leg visualization
		Legs_Diag4 = [0,0]
		Legs_Diag4[0] = Part.LineSegment(fp.StarGrid[Sub_i][22][0],fp.StarGrid[Sub_i][28][0])
		Legs_Diag4[1] = Part.LineSegment(fp.StarGrid[Sub_i][27][0],fp.StarGrid[Sub_i][28][0])

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

	def StarDiag4_squish(self, fp, N):
		# we are going to average all poles [28] around the loop to define the squish center

		# sum all poles [28]
		Poles_28_total = Base.Vector(0,0,0)
		for i in range(N):
			Poles_28_total = Poles_28_total + fp.StarGrid[i][28][0]

		SquishCenter = (1.0 / N) * Poles_28_total

		# do cross products in pairs around the loops to get a list of normal direction approximations
		cross_total = Base.Vector(0,0,0)
		for i in range(N-1):
			cross_total = cross_total + (fp.StarGrid[i][28][0]-SquishCenter).cross(fp.StarGrid[i+1][28][0]-SquishCenter)
		# close sequence by looping back
		cross_total = cross_total + (fp.StarGrid[N-1][28][0]-SquishCenter).cross(fp.StarGrid[0][28][0]-SquishCenter)

		# define squish plane from squish center and squish normal
		Squish_Plane = Part.Plane(SquishCenter, cross_total)

		# project all diag4 points to this plane.
		projections = [0] * N
		for i in range(N):
			param = Squish_Plane.parameter(fp.StarGrid[i][28][0])
			fp.StarGrid[i][28][0] = Squish_Plane.value(param[0],param[1])

	def StarRow4_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# pull up the seam at row 4
		Mid_p4 = 0.5 * (fp.StarGrid[Sub_0_i][28][0] + fp.StarGrid[Sub_1_i][28][0])
		fp.StarGrid[Sub_0_i][29][0] = Mid_p4
		fp.StarGrid[Sub_1_i][34][0] = Mid_p4

		# control leg visualization
		Legs_Row4 = [0,0,0]
		Legs_Row4[0] = Part.LineSegment(fp.StarGrid[Sub_0_i][23][0],fp.StarGrid[Sub_0_i][29][0])
		Legs_Row4[1] = Part.LineSegment(fp.StarGrid[Sub_0_i][28][0],fp.StarGrid[Sub_0_i][29][0])
		Legs_Row4[2] = Part.LineSegment(fp.StarGrid[Sub_1_i][28][0],fp.StarGrid[Sub_1_i][34][0])

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row4
		return 0

	def StarRow4_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow4_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow4_2Sub(fp, N-1, 0)
		return 0

	def StarCenter(self, fp, N):
		# we are going to average all poles [29] around the loop to define the center
		# sum all poles [29]
		Vector_total = Base.Vector(0,0,0)
		for i in range(N):
			Vector_total = Vector_total + fp.StarGrid[i][29][0]

		StarCenter = (1.0 / N) * Vector_total 

		# Apply center point to all Poles lists
		for i in range(N):
			fp.StarGrid[i][35][0] = StarCenter

		# control leg visualization
		Legs_Row5 = []
		for i in range(N):
			Legs_Row5.append(Part.LineSegment(fp.StarGrid[i][29][0],fp.StarGrid[i][35][0]))

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row5

		return 0

	def execute(self, fp):
		# instead of a list of Subgrid Links, we have a single link to a list of surface segments. we have to make our own SubGrids


		# this version works directly from NSurf_Center. this isn't directly equivalent, because the curvature row/col is not 'collapsed' to the tangent row/col, as it would be in a fresh SubGrid63
		# refresh properties back to linked Startrim every time the Star gets recomputed
		# determine number of SubGrids in the StarTrim
		fp.N= fp.StarTrim.CubicNStar.NStarGrid.N
		# set size of Stargrid attribute
		fp.StarGrid = [0] * fp.N
		# compile all SubGrid Poles and Weights into StarGrid attribute
		for n in range(fp.N):
			print ('n = ', n)
			# extract subgrid info from each StarTrim center section
			PoleArray = fp.StarTrim.NSurf_center[n].getPoles()
			Poles = [0] *36
			for v in range(6):
				for u in range(6):
					Poles[v*6+u] = PoleArray[u][v]

			WeightArray = fp.StarTrim.NSurf_center[n].getWeights()
			Weights = [0] *36
			for v in range(6):
				for u in range(6):
					Weights[v*6+u] = WeightArray[u][v]

			StarGrid_n = [0] * 36
			for i in range(36):
				# set Pole/Weight format [Base.Vector(), Float]
				print ('i = ', i)
				StarGrid_n_i = [0,0]
				StarGrid_n_i[0] = Poles[i]
				StarGrid_n_i[1] = Weights[i]
				StarGrid_n[i] = StarGrid_n_i
			fp.StarGrid[n] = StarGrid_n
		# a specific Pole is now addressed as StarGrid[n][i][0]
		# a specific Weight is now addresses as StarGrid[n][i][1]


		# now that we effectilvely have a list of N Subgrids, make an NStar control grid
		fp.Legs = []
		# self.StarRow2_SubLoop(fp, fp.N) # skip row 2 since we carry in the curvature rows? just go right to row 3?
		self.StarDiag3_SubLoop(fp, fp.N)
		self.StarRow3_SubLoop(fp, fp.N)
		self.StarDiag4_SubLoop(fp, fp.N)
		self.StarDiag4_squish(fp, fp.N)
		self.StarRow4_SubLoop(fp, fp.N)
		self.StarCenter(fp, fp.N)

		fp.Shape = Part.Shape(fp.Legs)

		# convert all vectors in StarGrid to lists. this allows saving the PythonObject attribute. The data needs to be fed back to Base.Vector() downstream.
		for n in range(fp.N):
			#set size of single SubGrid
			StarGrid_n = [0] * 36
			for i in range(36):
				# set Pole/Weight format [Base.Vector(), Float]
				StarGrid_n_i = [0,0]
				StarGrid_n_i[0] = [fp.StarGrid[n][i][0].x, fp.StarGrid[n][i][0].y, fp.StarGrid[n][i][0].z]
				StarGrid_n_i[1] = fp.StarGrid[n][i][1]
				StarGrid_n[i] = StarGrid_n_i
			fp.StarGrid[n] = StarGrid_n

