#    This file is part of Silk
#    (c) Edward Mills 2023
#    edwardvmills@gmail.com
#    With significant contributions from github member @wandrewkeech, who led this tooltip documentation effort.
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


'''
This file compiles all the tooltips for the respective command files as string variables. By displaying 
the tooltips in command progression order, The goal is to allow building background knowledge, in 
addition to command usage mechanics.

For each command, a 'tooltip' and 'More Info' string variable is prepared.
IF possible, the 'More Info' popup system will be migrated to a resizable and scrollable window type. Ideally reading MarkDown formatted content,
which would then be mirrored in the Silk Wiki.

STRING FORMAT
\n for line returns
" reserved as string delimeter (begin/end each line)
' allowed freely within strings

this line of underscore characters seems to succeed in setting window width, and preventing the popup window from wrapping text unexpectedly.
	"______________________________________________________________________________________________________________________________________ \n"
text cannot reach the end of this line, or it will wrap. see below for reasonable setbacks. Any edit must be tested by opening FreeCAD,
checking the tooltip, and clicking the icon to verify popup formatting, and no unintentional line wraps.

spacing (particularly whitespacing) in your editor may not match spacing in the popup window. all edits must be checked for correct 
line-wrapping.
    
'''

standardTipFooter = (
	"\n     Click this icon with nothing selected to see more information \n"
)

SilkPose_baseTip = (
	"a pose* symbol with a 3D placement calculated from linked references: long line indicates x axis, short line indicates y axis \n"
	"used to attach sketches**, with standard 90 degree rotations as an option: XY (default), YZ, or ZX. \n "
	"* pose means exactly the same thing as FreeCAD Placement. But this is a separate tool, so it gets a separate name. \n"
	"** it can be used to attach anything - Silk uses it for sketches. \n"
	"______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
	"Preselect one of the following: \n"
	" • an object vertex (typically from a sketch) \n"
	" • a vertex AND a separate document object which has placement (typically a second sketch) \n"
	"Apply the function \n"
	"\n"
	"The new Pose object has its origin at the vertex, and follows the orientation of the second object.\n"
	"So the first pick controls the translation, and the second pick controls orientation. \n"
	"\n"
	"If no second selection is made, the first object, from which the vertex was picked, is treated as the orientation reference). \n"
	"\n"
	"Under the data tab for this object, we can change the basic orientation from the default of XY, to ZX, or YZ, of the rotation \n"
	"reference object. The vertex reference object can be changed, as well as the rotation reference.\n"
	"We can now attach Silk sketches to this object, and they allow control not available through MapMode \n"
)

SilkPose_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
	"This is a placement method not available from Attachment MapMode \n"
	"specifically, this tool combines 'translate origin', and Object's XY/XZ/YZ. note that ZX is used instead of XZ (but same idea) \n"
	"now we can copy/paste large structures, and remap the Base sketch. All relative Nodes, 3L sketches, polys, grids, surfaces...\n"
	"everything should translate and rotate correctly! \n"
	"The key is to prepare entire structures with a single, well defined origin object as an orientation reference. When copy pasting, \n"
	"simply reattach this base object to the new desired location and orientation \n"
	"\n"
	"SKETCHING GUIDELINE, NOT PROVEN, BEST GUESS: \n"
	" -use parallel/perpendicular, and (general) distance constraints. \n"
	" -avoid horizontal/vertical, and horizontal/vertical dimension constraints. The goal is to help FreeCAD not mangle our sketches \n"
	" after rotations. Even with completely sepecified axes...i'm not sure FreeCAD won't decide that horizontal is vertical now."
)

ControlPoly4_baseTip = (
	"Creates a ControlPoly4 from a variety of inputs: \n"
	"______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
	"ALL SKETCHES USED MUST BE FROM THE SKETCHER WORKBENCH \n"
	"\n"
	"Preselect one of the following: \n"
	" • One sketch of three lines connected end to end \n"
	" • Two sketches containing a circle and a line each, where one of the line endpoints matches the center of the circle. \n"
	"   These 'Node Sketches' use the circle center to indicate an endpoint, and the line to indicate the desired tangent \n"
	"   direction from that endpoint. \n"
	" • If a single sketch is selected that does not contain three elements, the first element is converted. This works for \n"
	"   line, arc of circle, and arc of ellipse elements. Arcs should be quarter circle or less. \n"
	"Apply the function \n"
	"\n"
	"This control polygon (poly) of 4 points is intended to control a cubic bezier curve, or to control a cubic bezier surface. \n"
	"After creating the poly, you'll probably want to hide the sketches used to create it, so that you can see it. Creating \n"
    "these objects often feels like an 'extra' step, but they need to be fully understood in order to progress in NURBS."
	"\n"
	"Used as input for: \n"
	" • CubicCurve_4 (which is a smooth Bezier curve)\n"
	" • ControlGrid44 (which then produces a smooth Bezier surface)\n"
	" • ControlGrid44_Rotate (which then produces a smooth Bezier surface) \n"
	" • ControlGrid64 (which then produces a less smooth mixed Bezier/NURBS surface)\n"
	)

ControlPoly4_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
	"More Info \n"
	"\n"
	"This is THE most important tool, and everything else depends on it. Give it a quick try, use the result as input for the \n"
	"next tool (CubicCurve_4) and then come back to read more about it. \n"
	"Editing the source sketches will automatically update the poly. Curves and surfaces attached to the poly will update as \n"
	"well. In your sketches, make sure to set the view property 'hide dependents' to 'false'. This will give you live updates of \n"
	"polys (and curves, and surfaces) while you edit the sketches. \n"
	"Since polys are used to create surfaces as well as curves, and surfaces are what we are really after, the poly creation is \n"
	"kept as a independent step. It is important to develop a feel for how a poly controls a curve. After you have created a curve/ \n"
	"surface, edit the sketches you used to create the poly and observe how the curve/surface changes. \n"
	"Node sketches are intended to be placed in different planes, so that the resulting resulting polys, curves, and surface \n"
	"edges are fully 3D. they are great to connect to endpoints of 3 line sketches that are on different planes. Node sketches are \n"
	"typically created with the circle at the origin, and the sketch mapped to a new location and orientation using FreeCAD's \n"
	"Mapping tools (found under the data tab of the property view). In this manner, the circle is never edited, and the free \n"
	"endpoint of the line can be freely adjusted. \n"
	"A poly that is used in a grid/surface can be relinked to a different sketch(es), so all the work of making the grid/surface \n"
	"does not need to be redone. Just swap the link to another sketch and recompute (sketch links are also found under the data \n"
	"tab of the property view).\n"
	)

CubicCurve_4_baseTip = (
	"Creates a CubicCurve_4 from a ControlPoly4. \n"
	"______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
    "\n"
	"Preselect one of the following: \n"
    " • one ControlPoly4 \n"
    " • one ControlPoly4_segment. \n"
	"Apply the function \n"
    "\n"
    "This a Bezier cubic curve. All editing is done by editing the ControlPoly4. \n"
	"The main purpose of creating curves is to preview what the edges of our surface will look like if we use the input poly in a \n"
    "control grid (curves themselves are not used directly to make surfaces, but they can share polys with them). Curves are also used\n"
    "by cutting them into segments, which in turn defines how to cut surfaces for blending. \n"
	"\n"
	"Used as input for: \n"
	"• Point_onCurve (which can be a marker to subdivide the curve with ControlPoly4_Segment) \n"
	"• Two CubicCurve_4 that touch at one end can be used to generate a blend poly with the ControlPoly6 tool (not a beginner topic). \n"
)

CubicCurve_4_moreInfo = (
    "______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "This a Bezier cubic curve. A NURBS is Bezier when the number of control points is equal to the degree + 1. So a cubic (degree \n"
    " 3), has 4 control points. Beziers are the smoothest, highest quality NURBS. However, it is very difficult to connect several of \n"
    "them in a satisfying manner. It is relatively easy to obtain tangency (G1) by aligning certain control points, but difficult to \n"
    "obtain curvature matching (G2) as this involves adjusting multiple control points at the same time. G3 is very difficult, but \n"
    "even worse, it is pointless. In the attempt to smooth out the join of two beziers to G3, we have to move the control points \n"
    "around, to the point where one or both of the curves/surfaces become completely unrecognizable. \n"
    "\n"
    "So why use beziers? Well, they are still the best for individual curves/surfaces. Sometimes G1 is fine, so they can be used \n"
    "directly. For higher quality stuff, Silk's design strategy is to use multiple Beziers for the broad strokes of the design, let \n"
    "them meet at sharp angles on a shared edge, and finally trim back and blend. This is not a new crazy idea, the most expensive \n"
    "surfacing software for industrial design uses the same strategy: Bezier as far as they'll take you, and then careful blending\n"
    " of the edges/joints (Silk does not attempt to emulate those programs entirely, this just one common point). \n"
    "\n"
    "Silk currently only works with cubics, but the plan is to move to degree 4 (5 control points), 5 (6 control points), etc in \n"
    "the course of development. Silk still needs a few more functions before we can say 'cubics are done!' and move on the higher \n"
    "degrees. When the higher degrees are introduced, the cubics will still remain the 'bread and potatoes' of design. The higher \n"
    "degrees will only be used when absolutely necessary, as they are harder to use anyways (someone has to define all these extra \n"
    "control points...)"
)

Point_onCurve_baseTip = (
    "Create a point on a Cubic_Curve4 or Cubic_Curve6 (also works on some curves outside of Silk).\n"
    "______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
    "\n"
	"Preselect the following: \n"
	" • Choose a location on the curve in the 3D view by clicking on it. \n"
	"Apply the function \n"
	"\n"
    "A PointOnCurve object is placed on the curve. \n"
    "\n"
	"Used as input for: \n"
	"• Start point and end point of ControlPoly4_Segment (used to cut CubicCurve4s into pieces) \n"
	"• Can be a convenient way to mark a location along a curve, and then place (map) a Node sketch (or whatever you want) at that \n"
	"  location using the Mapping tool under property data tab \n"
	)
            
Point_onCurve_moreInfo = (
    "______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "This works on curves outside of Silk, as long as they are parametrized as '0 to 1'. Allowing any number works in principle, but \n"
    "Silk would then suffer every time a user types in '100' by greatly distorting the model. So Silk is prioritized over other \n"
    "curves.\n"
    "\n"
    "The position of the point can be adjusted along the curve (0.0 to 1.0) by adjusting the 'u'parameter found under the data tab\n"
    " of the property view. This allows precise positioning anywhere along the curve. It is often not obvious which side is 0, and \n"
    "which side is 1. Try to pick clearly towards one end or the other of the curve, it will then be obvious if the point is closer\n"
	" to 0 or 1. To match the endpoints, type in 0 or 1. Try to keep u values generally consistent (.25, .5, .75, etc, or 0.1, 0.2, \n"
    "0.3, 0.4, etc). This is because we will often have to match cut values in different curves/surfaces to line things up. Discipline \n"
    "up front and recognizing your typical values will pay off. \n"
    "Often, two curves we wish to split 'in the same manner' have their orientation reversed to each other. In those cases, set u of \n"
    "the 'next' curve to 1-u (eg. .90 and .10) of the 'previous' curve in order to cut them in the 'same' place.\n"
    "\n"
    "FreeCAD's expression engine allows us to easily connect one cut value to another existing cut value. Then you only need to \n"
    "edit one, and all others follow it automatically.\n"
    "\n"
    "Given curve1, curve2, with point1, point 2 on them, set \n"
    " • u of point2 = point1.u (typing '=' in a data field of the property data view creates an expression)\n"
    "now any changes to point1.u will be automatically propagated to point2.u\n"
    "If the points appear on the wrong side of the curve, set \n"
    " • u of point2 = 1 - point1.u (in the expression) \n"
    "\n"
    "Automatic matching is not really optional on large models, but you don't need to worry about it until you have a large model. \n"
    "You don't have to type much: select the source point in the tree, hit F2 (edit label mode), hit control-C (copy the label), go \n"
    "to the property data view of the point you want to apply the match to, in the 'u' field, hit '=' (expression opens), then \n"
    "control-V (paste), then type '.u', confirm by clicking 'u' in the drop down, hit 'enter'. This works all over FreeCAD. \n"
	)
			
ControlPoly4_segment_baseTip = (
	"Create a ControlPoly4 for a segment of a Cubic_Curve_4, between two points on the curve. \n"
    "______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
    "\n"
    "Preselect the following sequence: \n"
    " • a Cubic_Curve_4 first (Cubic_Curve_6 is unpredictable currently, and the result is not useful yet anyway)\n"
    " • a point on the curve. \n"
    " • another point on the curve \n"
    "(the points must be PointOnCurve objects) \n"
    "(this selection is best done in the model tree, as selecting points in 3D is extremely difficult and unreliable). \n"
	"Apply the function \n"
	"\n"
    "A simple interpretation of the selection is: 'this curve, but only from this point, to this other point'. \n"
    "\n"
	"Used as input for: \n"
	" • CubicCurve_4 (makes a new curve, which is a  segment of the original curve. used to control blending.) \n"
	" • ControlGrid44 (atypical use, but it functions just as any poly 4) \n"
	" • ControlGrid64 (atypical use, but it functions just as any poly 4) \n"
	)
            
ControlPoly4_segment_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "Segmenting/sectioning/cutting is a core Silk modeling technique. It is essential for blending. The current workflow uses curve \n"
    "segments as references to cut surfaces. There are plans to cut surfaces by drawing points directly on them, but since the same \n"
    "result is already possible using curve segments, implementation of this convenience is medium on priority.\n"
    "\n"
	"Why so much segmenting in Silk? segments of curves, then segment of surfaces...so much time segmenting and aligning  \n"
    "segmentation points! So many points. Why? \n"
    "Because if you build off of segments/pieces of a single Bezier curve or surface, the things you build retain \n"
    "'relatedness' to each other. They blend well. Sections separated by gaps nevertheless feel as part of the same surface. \n"
    "This instant feeling of connectedness is almost impossible to achieve by tring to 'harmonize' two curves or surfaces \n"
    "constructed separately and then mushed together. The key to Silk blending is sharing edges between base surfaces (which are \n"
    "not otherwise aligned), and then blending strips of the surfaces near that shared edge. The shared edges and strips make \n"
    "blends that come out decent even before tuning. \n"
	)

ControlGrid44_baseTip = (
	"Create a ControlGrid44 from four connected ControlPoly4 edges. \n"
    "______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
    "\n"	
    "Prepare the following selection: \n"
    " • four ControlPoly4 objects that form a loop \n"
    " • the ControlPoly4s should only touch at their endpoints, and form a distinct angle where they meet \n"
	" • Select each edge in the loop sequentially, counter clock-wise looking from the 'outer side' of the surface we want to create. \n"
	"Apply the function \n"
    "\n"
	"Used as input for: \n"
	"• CubicSurface_44 (makes a smooth cubic Bezier surface)\n"
	"• ControlGrid64_2Grid44 (makes a blend grid to join surfaces)\n"
    )
    
ControlGrid44_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "Silk does it's first useful task beyond using existing FreeCAD functions and forcing us to use a strange format: it generates \n"
    "inner control points of the grid based on the polys. This is not the only way to generate the inner control points, but it is \n"
    "a great default starting point. The user provides 12 points through the polys, and Silk provides 4 more. 4/12 doesn't seem \n"
    "much, but it snowballs from here, and the rest of the tools will generate 10s and 100s of useful control points with less and \n"
    "less input from the user at each step. \n"
	"\n"
    "TANGENCY RULES \n"
	"If you don't intend to segment and blend adjacent CubicSurface_4s, then their ControlGrid44s must follow strict \n"
	"rules to get tangency (G1) across the shared edge (imagine two grids/surfaces side by side, left and right): \n"
	" • There must be a shared edge (G0) in the middle. The entire edge. This is done by selecting the same poly for that edge \n"
	"   in both grids. Do not trace the poly. Do not approximate it, do not copy, do not link. Use the same object during both \n"
	"   grid creations. \n"
	" • The legs of the polys that meet on the shared edge must be COLINEAR (/aligned/parallel). \n"
	" • The RATIO of the length of the poly legs that meet on the shared edge must be EQUAL. So if the top poly on the left \n"
	"   has a last leg of length 3, and meets a leg of length 1 of top of the right grid, the tangency ratio is 3:1 from left \n"
    "   grid to right grid. Now if the bottom poly on the left grid has a last leg of length 6, the connecting poly on the right \n"
    "   grid must have a first leg of length 2 (keeping it 3:1). This ratio rule goes away if all poly legs are parallel across the \n"
    "   shared edge.\n"
	" • Users do not need to do anything except prepare the polys. if the polys follow these rules, the generated adjacent \n"
	"   grids will always be G1, as Silk calculates all the internal control points of the surface (the ones not on edges). \n"
	"\n"
    "Following tangency rules (G1) forces us to modify our polys, which changes our entire surfaces. when we don't want to modify \n"
    "a surface, we blend it instead of aligning it. G1 aligning is useful to patch small holes, or to connect to planes, cylinders \n"
    "and spheres \n"
    "\n"
	"OPTIONAL - FLAWED -  use with caution \n"
	"select 3 connected ControlPoly4 edges to produce a 'triangle' grid, which will yield a surface of low quality. \n"
	"\n"
	"The 'triangle' will have a degenerate (collapsed) edge between the first and third selected polys, because internally this grid \n"
    "has just as many points and lines as a four sided grid. The lines and points which are collapsed cause visible defects in the \n"
    "surface. This also makes further operations with this grid, or surfaces that use this grid, difficult or even impossible. This \n"
    "'triangle' does respect tangency rules, and will connect cleanly to other grids, despite its inner flaw point. In fact, the \n"
    "feature that it conforms to G1 on the edges makes it particularly flawed and ugly on the inside. Removing it is being \n"
    "considered, but some users seem to want it despite the warnings, so it remains.\n"
	)

ControlGrid44_Rotate_baseTip = (
	"Creates a ControlGrid44 from three ControlPoly4 edges. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"	
    "Prepare the following selection: \n"
    " • three ControlPoly4 objects that form a loop \n"
    " • the ControlPoly4s should only touch at their endpoints, and form a distinct angle where they meet \n"
	" • Select each edge in the loop sequentially, counter clock-wise looking from the 'outer side' of the surface we want to create. \n"
	"Apply the function \n"
    "\n"
	"Used to produce a 'triangle' surface which 'rotates' from the first edge selected to the third edge following along the second \n"
    "edge. Order is 'left, bottom, right' with the rotational pivot at the 'top' corner.\n"
	"\n"
	"Typical use is to merge a set of surfaces to a point (like closing a tube). Also used to interface with spheres and ellipsoids. \n"
	"\n"
	"Used as input for: \n"
	" • CubicSurface_44 \n"
	" • ControlGrid64_2Grid44 \n"
	"\n"
    )

ControlGrid44_Rotate_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
	"This is a degenerate grid (one edge collapsed to a point) that results in a 'revolve' like surface. Will produce true spheres \n"
    "from arc polys, true ellipsoids from ellipse arc polys, but also accepts non-arc polys. \n"
	"\n"
	"Surface tangency from multiple grids can be produced automatically from well prepared arcs of circles and ellipses, but using \n"
    "general curves as input does not have an easily predictable outcome. Additional blending may be required.\n"
	"\n"
	"Although degenerate, this grid is the correct way to interface with spheres, where it does not introduce additional collapsed \n"
    "edges. In this particular case, the NURBS degeneracy is not considered a flaw at all, but a standard CAD construct.\n"
    "\n"
    "A four sided version which would be able to create true tori (and sphere strips) is planned, but not ready \n"
    )

ControlGrid44_flow_baseTip = (
	"IN DEVELOPMENT - PARTIAL USEFUL RESULT\n"
	"Create a ControlGrid44_flow from a ControlGrid44. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
    "Prepare the following selection: \n"
    " • one ControlGrid44 \n"
	"Apply the function \n"
	"\n"
	"The output grid will have more gradual internal changes, at the cost of less predictable tangency across edges. This can help \n"
    "untangle and puff up basic grids. Various parameters allow scaling of the effect, restoring specific tangencies, and maintaining \n"
    "G1 'mirrorability' in the plane of each edge (if the edge was planar, and G1 mirrorable in the original grid). \n"
	"\n"
	"Used as input for: \n"
	" • CubicSurface_44 \n"
	" • ControlGrid64_2Grid44 \n"
    " • literally anywhere you would use a ControlGrid44 as an input...\n"
    " • ...even as input into another ControlGrid44_flow object (no clear reason to do this, but you can) \n"
    )

ControlGrid44_flow_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "The standard ControlGrid44_4 object follows strict rules so that tangency is obtained by following 'simple' rules when creating \n"
    "polys. The goal is that the simplest Silk job, patching a 4 sided hole in a model while maintaining tangency (G1), should be the \n"
    "default result of the simplest operation. This can often make ugly/distorted grids (even though they are correct and must be \n"
    "kept so for tangency). flattish, squarish and rectangularish grids are typically just fine at default G1. \n"
    "\n"
    "As you progress to making independent Silk models, you will want to blend your bezier surfaces (grid44/surface_44). Doing \n"
    "G1 alignment on an edge that will be blended is a waste of time. Even worse, two surfaces that are G1 are actually awkward \n"
    "to blend G2. Blending is recommend on a sharp edge between two surfaces (G0). This gives design freedom, and skips all the \n"
    "tangency rules. \n"
    "\n"
    "The default grid for G1 is fairly distorted (all corners are strict parallelograms), and can easily result in criss-crossing \n"
    "grids. ControlGrid44_flow recalcultaes the inner control points so that grid lines 'flow' progressively from one edge to the \n"
    "other. the inner control points are no longer confined to the plane defined by the edge polys' corners. They are free to rotate \n"
    "and lengthen for better 'flow'. This greatly reduces pinching. ControlGrid44_Rotate is also an example of this principle of \n"
    "breaking G1 on purpose, except it is fully automatic and only does ONE job, and ONLY for triangles\n"
    "\n"
    "Additional parameters in the Property-Data tab: \n"
    " • flow_11, flow_12, flow_21, flow_22. Scale the flow effect for each of the 4 inner control points. When the value is 1, you get \n"
    "   the fully reflowed inner control point position. when the value is 0, the inner control point reverts to it's G1 compliant \n"
    "   automatic position. Anywhere in between is an artistic choice. To make an edge G1 compliant, set both inner control points \n"
    "   closest to the edge to flow = 0. How do you know which point is which? currently you just type in 0 or 1 in the Property \n"
    "   Data parameter field...and see which control point moved in the 3D view. Sorry this is awkward, but this is alpha software. \n"
    "   Setting all 4 values to 0 means you just get the input grid back (not particularly useful, except as a temporary reset).  \n"
    "BELOW NOT IMPLEMENTED. STRICTER EFFECT ALREADY OBTAINED WITH PARAMETER DESCRIBED ABOVE \n"
    " • mirror_u0, mirror_u1, mirror_u0, mirror_u1. maintain the angles of the grid 'legs' that touch one of the 4 edges of the grid. \n"
    "   this still allows the length of these legs to vary and hopefully flow better. Less strict than setting flow = 0 for the inner \n"
    "   control points that touch this edge, but still preserves G1 if you mirror the surface along the plane containing this edge. \n"
    "   mirror  = 0  is full flow, mirror = 1 is exact angle match to original grid. Anywhere in between is an artistic choice. \n"
    "   Expected use is to apply to 1 edge of a grid, perhaps 2 opposite edges. Setting 3 or all 4 edges to mirror = 1 is not \n"
    "   expected to have a very meaningful result. Available for artistic purposes, no specific behavior guaranteed."
    )

CubicSurface_44_baseTip = (
	"Create a CubicSurface from a ControlGrid44. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
        "\n"	
    "Prepare the following selection: \n"
    " • one ControlGrid44 of any type (made from polys, or made by segmenting, etc)\n"
	"Apply the function \n"
    "\n"
    "This a Bezier cubic surface, and is intended to be the basic 'building block' surface that complex models are based on. All \n"
    "editing is done by editing the ControlGrid44. Refer to ControlGrid44 tooltip and 'More Info' section for design rules \n"
    "\n"
	"Can be used for hard edge surfacing, or manually aligned for tangency (G1). Can also be blended along hard edges with \n"
    "other CubicSurface_44 objects (by way of CubicSurface64 objects), for high continuity (G2). \n"
    "\n"
    "Used as input for: \n"
	"-ControlGrid44_EdgeSegment (a 44 grid which corresponds to a 'full strip' segment of the surface)\n" 
	"-ControlGrid44_2EdgeSegments (a 44 grid which corresponds to a 'rectangular' segment of the surface) \n"
    )
    
CubicSurface_44_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "This does for the ControlGrid44 object what the CubicCurve_4 does for the ControlPoly4. Refer to the extensive description \n"
    "given for CubicCurve_4. Those comments apply here to the surface, instead of just a curve. \n"
    "\n"
    "ControlGrid44s that are manually built from poly4s are almost exclusively intended to be used by surfaces, but many \n"
    "automatically created ControlGrid44s are intended to be consumed by blend grids. Because of these different possible paths, \n"
    "the creation of grids is kept separate from the creation of surfaces. That way, a useful grid is not locked inside a surface, \n"
    "and harder to access by other operations. At some point in the future, it is planned to allow clicking a surface where a grid is \n"
    "expected, automatically finding the grid inside the surface, allowing tools to use either the grid or surface as needed. This is \n"
    "straightforward, but a lot of programming work. For the time being, the exact object type needed is expected to be directly \n"
    "'fed in' to functions.\n"
    )

ControlGrid44_EdgeSegment_baseTip = (
    "Create a ControlGrid44 from a CubicSurface44 and one CubicCurve4 segment. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"  
    "Prepare the following selection: \n"
    " • first a CubicSurface_4 \n"
    " • then a CubicCurve_4 that matches part of an edge of that surface (see More Info section) \n"
    "Apply the function \n"
    "\n"
    "The resulting grid represents a strip of the input surface cut in either u or v to match the CubicCurve segment along the \n"
    "surface edge. \n"
    "\n"
    "Used in pairs to create ControlGrid64_2Grid44 to blend edges of CubicSurface_44 to blend surfaces and create a continuous \n"
    "(G2) contour. Also used to re-create the portions of the original surface that are to be preserved and not blended \n"
    "\n"
    "Used as input for: \n"
    " • CubicSurface_44 \n"
    " • ControlGrid64_2Grid44 \n"
    )

ControlGrid44_EdgeSegment_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "How to prepare selection item number 2, the 'CubicCurve_4 that matches part of an edge of that surface'? If you have \n"
    "followed all the tips so far and created the previous objects, you already have almost everything you need. If you are \n"
    "just reading before trying, it is to be expected that the explanation below will seem convoluted and onerous. \n"
    "\n"
    "You cannot directly 'cut'/segment the edge of a surface with points (yet*). What you cut is a CubicCurve_4 that matches the \n"
    "entire edge of the surface. How do you get this separate CubicCurve_4 that matches the entire edge of the surface? You make \n"
    "it by using the same poly that went into the grid of the surface. So if you checked your polys along the way by applying \n"
    "curves to them, which is recommended, then you already have this entire edge curve in your model. Segment this curve by \n"
    "creating 2 PointOnCurves, a ControlPoly4_segment, and applying a CubciCurve_4 to the ControlPoly4_segment. \n"
    "\n"
    "*This is a planned feature, but since a practical solution already exists, as shown above, it is low priority. \n"
    )

ControlGrid44_2EdgeSegments_baseTip = (
    "Create a ControlGrid44 from a CubicSurface44 and two CubicCurve4 segments. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"  
    "Prepare the following selection: \n"
    " • first a CubicSurface_4 \n"
    " • then a CubicCurve_4 that matches part of an edge of that surface (see More Info section) \n"
    " • then another CubicCurve_4 that matches part of an adjacent edge of that surface (the two partial curves cannot be on \n"
    "   opposite edges of the surface) \n"
    "Apply the function \n"
    "\n"
    "The resulting grid represents a 'rectangular' cut of the input surface, cut in both u or v to match the CubicCurve segments \n"
    "along the surface edges. \n"
    "\n"
    "Used in pairs to create ControlGrid64_2Grid44 to blend edges of CubicSurface_44 to blend surfaces and create a continuous \n"
    "(G2) contour. Also used to re-create the portion of the original surface that are to be preserved and not blended. \n"
    "\n"

    "Used as input for: \n"
    " • CubicSurface_44 (remake a surface that is a portion of the orignal surface)\n"
    " • ControlGrid64_2Grid44 (prepare a blend grid that will align well with the original surface)\n"
    " • ControlGrid64_3_1Grid44 (rounds off one corner of the grid, see tip for this function further on) \n"

    )

ControlGrid44_2EdgeSegments_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "How to prepare selection items number 2 and 3, the 'CubicCurve_4 that matches part of an edge of that surface'? If you have \n"
    "followed all the tips so far and created the previous objects, you already have almost everything you need. If you are \n"
    "just reading before trying, it is to be expected that the explanation below will seem convoluted and onerous. \n"
    "\n"
    "You cannot directly 'cut'/segment the edge of a surface with points (yet*). What you cut is a CubicCurve_4 that matches the \n"
    "entire edge of the surface. How do you get this separate CubicCurve_4 that matches the entire edge of the surface? You make \n"
    "it by using the same poly that went into the grid of the surface. So if you checked your polys along the way by applying \n"
    "curves to them, which is recommended, then you already have this entire edge curve in your model. Segment this curve by \n"
    "creating 2 PointOnCurves, a ControlPoly4_segment, and applying a CubciCurve_4 to the ControlPoly4_segment. \n"
    "\n"
    "*This is a planned feature, but since a practical solution already exists, as shown above, it is low priority. \n"
    )

ControlPoly6_baseTip = (
    "Create a ControlPoly6 from various inputs \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
    "Prepare ONE of the following selections: \n"
    " • One sketch of five lines connected end to end \n"
    " • Two 'extended Node' sketches (circle + 1st line from center + 2nd line from endpoint of 1st) \n"
    " • Two CubicCurve_4 objects connected at one end. This will produce a G2 blend (* see More Info) \n"
    " • One CubicCurve_4 object. This produces an exact match in the poly6 format (** see More Info)\n"
    "Apply the function \n"
    "\n"
    "Mostly intended for blending existing Bezier curves/curve-segments. It can be used directly from sketches, but this approach \n"
    "has limits (*** see More Info). \n"
    "\n"
    "Examples of direct use: \n"
    " • Use the 6 control points to directly model a curve more complex than through ControlPoly4, without a blending step (***). \n"
    " • 3D (non-planar) ControlPoly6 can be generated out of two planar 'extended Node' sketches, each in different planes. \n"
    " • 3D (non-planar) ControlPoly6 can be generated out of CubicCurve_4 segments that connect at one endpoint, each from \n"
    "   'Node' sketches in different planes. \n"
    "\n"
    "Used as input for: \n"
    " • CubicCurve_6 \n"
    " • ControlGrid64 \n"
    " • ControlGrid66 \n"
    )
    
ControlPoly6_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "There are a lot of of warnings following, but they boil down to this: if you like it, use it. If you want to play it safe, \n"
    "use it as little as possible \n"
    "\n"
    "This control polygon is used to produce non-Bezier cubic curves and/or surfaces (number of control points > degree+1). It \n"
    "only guarantees G2 internally. It's benefit is that it allows controlling curvature at connection points/edges to cubic \n"
    "Bezier curves/surfaces. Mostly intended for blending existing Bezier curves/curve-segments. \n"
    "\n"
    "* This is Bezier curve blending, which is the main use case, and it provides a good preview of how blending grids/surfaces \n"
    "works as well. The hard corner between the two bezier curves will disappear, and the start and end of the poly matches the \n"
    "original curves up to G2. \n"
    "\n"
    "** If you choose to go ahead and manually build ControlPoly6s, ControlGrid64s, and ControlGrid66s, you will likely find \n"
    "yourself at times with a ControlPoly4 or a CubicCurve_4 in a location where you wish there was a ControlPoly6. Silk can always\n"
    "convert a CubicCurve_4 to a ControlPoly6 exactly. The reverse is not true. All Beziers have an exact match ControlPoly6, but \n"
    "a random ControlPoly6 does not generally have a matching Bezier. \n"
    "\n"
    "*** 6 point cubic curves/surfaces are intended to be generated automatically by other tools because of their G2 connection \n"
    "properties. Even when generated automatically, the poly is not recommended to use directly in building grids/surfaces (but \n"
    "it is allowed). The single truly valuable use case (in the context of the official workflow) is if you want to study a set of \n"
    "beziers and their blends in 2D before building the surfaces in 3D. This is very useful on the mirror plane of a design for \n"
    "example, when we may not be certain how many Beziers and blends the design requires. \n"
    "\n"
    
    )

CubicCurve_6_baseTip = (
    "Creates a CubicCurve_6 from a ControlPoly6\n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
    "Prepare the following selection: \n"
    " • one ControlPoly6  \n"
    "Apply the function \n"
    "\n"
    "A 6 control point cubic NURBS. G2 continuous throughout. G3 continuous throughout EXCEPT at two points along the curve, \n"
    "where it is G2 only. The practical use of this curve is to preview blends on curves before doing all the work of blending \n"
    "surfaces. \n"
    "\n"
    "Used as input for: \n" 
    " • this is currently an endpoint in the Silk design workflow \n"
    " • you can use the input ControlPoly6 to build grids and surfaces however \n"
    " • you can use it with the rest of FreeCAD, extrude it, revolve it, etc, if all you want to do in Silk is design curves. \n"
    )
    
CubicCurve_6_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "The curve segmentation tools actually work on these curves, meaning an object is produced, but if the segment crosses one \n"
    "of the 'G2 only' points, the result will not match expectations. \n"
    "\n"
    "In the future, a tool will be added to split these curves into 3 pieces, right on the predefined 'G2 only' points (and nowhere \n"
    "else). The three pieces actually end up being exact cubic Bezier poly4s, and the workflow can start all over again with all the \n"
    "poly4 and gridd44 tools, instead of being a deadend.\n"
    )



ControlGrid66_baseTip = (
    "Create a ControlGrid66 from four connected ControlPoly6 edges. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
    "\n"
    "Prepare the following selection: \n"
    " • 4 ControlPoly6  objects\n"
    " • 4 Select each ControlPoly6 sequentially, counter clock-wise looking from the outer side. \n"
    "Apply the function \n"
    "\n"
    "All comments for ControlPoly6 and CubicCurve_6 apply here as well. 6 point edges and 6x6 surfaces cannot be blended with Silk \n"
    "tools (yet), so this grid and associated surface are a final product at this stage. \n"
    "\n"
    "Input for: \n"
    "-CubicSurface_66 \n"
    )
    
ControlGrid66_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "This is not a recommended method to create main surfaces, but it is available. This type of grid is best when generated \n"
    "automatically by other tools. Manually creating this type of grid (and associated surface) directly from polys has \n"
    "limitations, because they cannot be segmented (yet). They cannot be blended either (yet). They are still compatible \n"
    "with all tools which take a ControlGrid64 as input, even though those tools assume that the grids were generated \n"
    "automatically.\n"
    "\n"
    "When segmentation does become available, it will be like so: the grid/surface will be cut into nine(9) ControlGrid44s \n"
    "at preset locations (in a 3 by 3 pattern like tic-tac-toe). This is an exact conversion with no loss of\n precision. These \n"
    "nine Bezier 44 pieces will then be workable through all the tools available for ControlGrid44s and CubicSurface_44s. \n"
    )


CubicSurface_66_baseTip = (
    "Create a CubicSurface_66 from a ControlGrid66. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
    "Prepare the following selection: \n"
    " • one ControlGrid66  \n"
    "Apply the function \n"
    "\n"
    "A reasonably high quality cubic surface (G2 throughout), allows two blends to run through each other. \n"
    "All comments for ControlPoly6, CubicCurve_6, and ControlGrid66 apply here as well. Main purpose is to to be applied to \n"
    "automatically generated grids. Can also be used manually for hard edge surfacing, manually aligned for tangency, or even \n"
    "manually aligned for G2 (very difficult and limited). \n"
    "\n"
    "6 point edges/surfaces cannot be blended with Silk tools (yet). \n"            
    )
    
CubicSurface_66_moreInfo = (
 	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"   
	"This is still a cubic surface (degree 3). But it is no longer Bezier, so additional control points are \n"
    "allowed. The price paid for these extra control points is that this surface is only garanteed G2 \n"
    " internally (may be G3 under the right setup) \n"
    "\n"
    "When segmentation does become available, it will be like so: the grid/surface will be cut into nine(9) \n"
    "ControlGrid44s at preset locations. This is an exact conversion with no loss of precision. These nine \n"
    "pieces will then be workable through all the tools available for ControlGrid44s and CubicSurface_44 \n"
    )

'''
ControlGrid64_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
CubicSurface_64_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid64_2Grid44_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid64_3_1Grid44_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
SubGrid33_2Grid64_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid66_4Sub_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
SubGrid63_2Surf64_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGridNStar66_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
CubicNStarSurface_NStar66_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
StarTrim_CubicNStar_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
Reload_Silk_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
'''