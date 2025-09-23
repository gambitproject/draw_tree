#!/usr/bin/python
# assumes python 2 but should work with python 3;
# print is used in a single place
# drawing tree as tikz file from .ef file
# version 1.0.5
from __future__ import print_function

import sys
import math 

# constants
DEFAULTFILE = "example.ef"
scale = 1
grid = False

maxplayer = 4
payup = 0.1   # fraction of paydown to shift first payoff up
radius = 0.3   # iset radius
# up to 4 players and chance (in principle more)
# default names
playername = [r"\small chance", "1", "2", "3", "4"]
playertexname = ["playerzero", "playerone", "playertwo", "playerthree", "playerfour"]
# player names that need to be defined in TeX
playerdefined = [False] * (maxplayer+1)

# tikz/TeX constants used, defined in TeX file, not here
paydown = "\\paydown"  # 2.5ex % yshift payoffs down
yup = "\\yup" # 0.5mm % yshift up for moves
yfracup = "\\yfracup" # 0.8mm % yshift up for chance probabilities
spx = "\\spx" # 1mm % single player node xshift
spy = "\\spy" # .5 mm % single player node yshift
ndiam = "\\ndiam" # 1.5mm % node diameter disks
sqwidth = "\\sqwidth" # 1.6 mm % node diameter disks
# thickn = "\\thickn" # {very thick} % line thickness
thickn = "line width=\\treethickn" # {1pt} % line thickness
chancecolor = "\\chancecolor" # gray color of chance node

numepsilon = 1e-9 # checking for almost equality

# isetparams="fill=blue, opacity=0.3"  # parameters for info set drawings
isetparams=""  # draw parameters for info set drawings

# all dimensions in cm
isetradius = 0.3
# elongated single iset in which direction
xsingleiset = 0.4
ysingleiset = 0.0

# how to indent
joinstring = "\n    " 

######### output routines
allowcomments = True

outstream = []
stream0 = []

# output stream to stdout
def outall(stream=outstream):
    for s in stream:
        print (s)
    return

# output single string
def outs(s, stream=outstream):
    stream.append(s)
    return

# output list of strings
def outlist(l):
    global outstream
    outstream += l
    return

# LaTeX command for defining something
def defout(defname, meaning):
    # tikz output (TeX definition, consider changing to
    # LaTeX \newcommand* )
    outs("\\def\\" + defname + "{" + meaning + "}")
    return

# LaTeX command for creating a dimension
# maybe not here
def newdimen(dimname, value):
    # tikz output
    outs("\\newdimen\\" + dimname)
    outs("\\" + dimname + value)
    return

# output comment if not suppressed
def comment(s):
    # tikz code (LaTeX comment)
    if allowcomments:
        outs("%% "+s)
    return

def error(s, stream=outstream): # errors not suppressed
    outs("% ----- Error: "+s, stream)
    return

# read file lines, stripped of blanks at end, if non-empty, into list
# http://stackoverflow.com/questions/12330522/reading-a-file-without-newlines
def readfile(filename):
    temp = open(filename, 'r').read().splitlines()
    out = []
    for line in temp:
        line = line.strip()
        if line:
            out.append(line)
    return out

# float format to [default 3] places, remove trailing ".0"
def fformat(x, places=3):
    fstring = "%." + ("%df" % places)
    s = fstring % x
    if places > 0 :
        s = s.rstrip("0")
        s = s.rstrip(".")
    return s

# coordinates as pair: 3,4 -> "(3,4)"
def coord(x,y):
    return "("+ fformat(x)+","+fformat(y)+")"

# Euclidean length of vector
def twonorm(v):
    l = 0.0
    for x in v:
        l += x**2
    return l**0.5

# stretch to desired length (must be >= 0)
def stretch (v,length=1):
    currl = twonorm (v)
    if currl == 0.0: return v
    out = []
    for x in v:
        out.append(x*length/currl)
    assert aeq(twonorm(out),length) 
    return out 

# angle of vector in degrees in (-180,180]
def degrees (v):
    currl = twonorm (v)
    if aeq(currl): return 0
    onunitcircle = stretch(v)
    x = onunitcircle[0]
    y = onunitcircle[1]
    xd = math.acos(x)*180/math.pi
    if y<0:
        return -xd # in (-180,0)
    return xd # in [0,180]

# almost equal (or equal to zero) numerically
def aeq(x,y=0):
    return abs(x-y) < numepsilon

# determinant
def det(a,b,c,d):
    return a*d - b*c

# is b on the line segment [a,c]?
def isonlineseg(a,b,c):
    bx=b[0]-a[0]
    by=b[1]-a[1]
    cx=c[0]-a[0]
    cy=c[1]-a[1]
    if aeq(bx) and aeq(by) : return True  # a near b
    if aeq( bx*cy - by*cx ): # collinear
        if aeq(cx) and aeq(cy) : # a near c but not near b
            return False
        if aeq(cx): # look at y coordinate
            if aeq(by,cy) : return True  # c near b 
            if cy >= 0: return (by >= 0) and (by <= cy)
            # cy < 0
            return (by <= 0) and (by >= cy)
        # nonzero x coordinate of c, gives info
        if aeq(bx,cx) : return True  # c near b 
        if cx > 0: return (bx >= 0) and (bx <= cx)
        # cx < 0
        return (bx <= 0) and (bx >= cx)
    # not collinear
    return False

# create arc or point around point b in a,b,c
def makearc(a,b,c,radius=isetradius):
    s = stretch([ b[1]-a[1], a[0]-b[0] ], radius)
    t = stretch([ c[1]-b[1], b[0]-c[0] ], radius)
    # print "% s,t    ", s,t
    sangle = degrees(s)
    tangle = degrees(t)
    # make sure to turn anticlockwise
    if tangle < sangle : tangle += 360
    sx = b[0] + s[0]
    sy = b[1] + s[1]
    # tikz code
    out = coord(sx,sy) + " arc("
    out += fformat(sangle,1) + ":"
    out += fformat(tangle,1) + ":"
    out += fformat(radius) + ")"
    # checking if point rather than arc
    # print "%  tangle-sangle ", tangle-sangle 
    if tangle-sangle > 180.01:
        tx = b[0] + t[0]
        ty = b[1] + t[1]
        if tangle-sangle > 359: # very close to straight
            # print "% 359"
            x=(sx+tx)/2
            y=(sy+ty)/2
            out = coord(x,y)
        else:
            ax = a[0] + s[0]
            ay = a[1] + s[1]
            cx = c[0] + t[0]
            cy = c[1] + t[1]
            # print "% sx,sy,tx,ty", sx,sy,tx,ty
            # print "% ax,ay,cx,cy", ax,ay,cx,cy
            D = det (sx-ax,sy-ay,cx-tx,cy-ty)
            if not aeq(D):  # zero determinant - do nothing
                alpha = det(cx-ax,cy-ay,cx-tx,cy-ty) / D
                beta  = det(sx-ax,sy-ay,cx-ax,cy-ay) / D
                # print "% alpha ", alpha
                # print "% beta  ", beta
                assert (alpha<1)
                assert (beta<1)
    ## trying to salvage tight angles, other solution is better
    #           if alpha<0:
    #               x = ax
    #               y = ay
    #           elif beta<0:
    #               x = cx
    #               y = cy
    #           else :
    #               x = ax + (sx-ax)*alpha
    #               y = ay + (sy-ay)*alpha
    #           out = coord(x,y)
                if alpha >= 0 and beta >= 0 :
                    x = ax + (sx-ax)*alpha
                    y = ay + (sy-ay)*alpha
                    out = coord(x,y)
    return out 

# create a list of strings that is the sequence of tikz drawing
# commands around a list of coordinate pairs [x,y]
# not including the "draw" and ";" start and end parts 
def arcseq(nodes,radius=isetradius): 
    nodes = nodes[:] # protect nodes parameter, now a local variable
    if len(nodes) == 0: return [""];
    if len(nodes) == 1: # singleton info set
        x = nodes[0][0]
        y = nodes[0][1]
        # circle only?
        if aeq(xsingleiset) and aeq(ysingleiset): # no offset
            # tikz code 
            s = coord(x,y) + " circle [radius="
            s += fformat(radius) + "cm]"
            return [s]
        # else extend with extra point
        else: 
            nodes.append([x+xsingleiset,y+ysingleiset])
    # now at least length 2
    # successively remove points on same line segment
    a = nodes.pop(0)
    b = nodes.pop(0)
    newnodes = [a]
    while (nodes):
        c = nodes.pop(0)
        if not isonlineseg(a,b,c):
            newnodes.append(b)
            a = b
        b=c
    newnodes.append(b)
    tour = newnodes[1:2]+newnodes[:-1]+newnodes[::-1]
    out = []
    for i in range(1, len(tour)-1):
        out.append(makearc(tour[i-1],tour[i],tour[i+1],radius))
    return out  

# create a list of strings that is the sequence of tikz drawing
# commands around a list of coordinate pairs [x,y]
# including the "draw" and ";" start and end parts 
def iset (nodes,radius=isetradius): 
    arcs = arcseq(nodes,radius)
    # tikz code 
    return "\\draw [" + isetparams + "] " + "\n  -- ".join(arcs) + " -- cycle;"

######################## handling players

# parse "player" command
# writeout player definition if player named or used first time
# returns p,advance (in words list afterwards)
def player(words):
    p = -1  # illegal player
    advance = len(words)
    assert words[0] == "player"
    try:
        x = int(words[1])
    except:
        error("need player number after 'player'")
        return p, advance
    if x < 0 or x > maxplayer:
        error("need player number in 0.."+str(maxplayer)+" after 'player'")
        advance = 2 # allow continued processing
        return p, advance
    p = x
    if len(words) > 2:
        if words[2] == "name":
            if len(words) == 3: # nothing there
                error("player name needed after 'name'")
                return p, advance
            playername[p] = words[3] # got new player name
            playerdefined[p] = False
            advance = 4
        else:
            advance = 2 # only "player p" parsed
    if not playerdefined[p]:
        defout(playertexname[p], playername[p])
        playerdefined[p] = True
    return p, advance

######################## handling nodes

# each node is itself a dict, with the fields
# "x", "y", "player", "from", "move", "xshift"

nodes = {}
xshifts = {}

# finds x,text where x = prefix defining a nonnegative number
# 2a -> 2,"a"  ".3xyz" -> .3,"xyz"
# if no number, return 1: "a" -> 1,"a"
def splitnumtext(s):
    nodotyet = True
    tonum = ""
    remainder = ""
    for i in range(len(s)):
        c = s[i]
        if nodotyet and c == ".":
            nodotyet = False
            tonum += c
        elif c.isdigit():
            tonum += c
        else:
            remainder = s[i:]
            break
    if tonum and tonum != ".":
        return float(tonum), remainder
    return 1, remainder
    ## testing:
    # a = ["2.3abc", ".1b", ".4...f", ".4s1", "22.2xyz)", "a"]
    # for s in a:
    #     print s, splitnumtext(s)
    # quit()

# parse "xshift" command
def xshift(words):
    assert words[0] == "xshift"
    xs = 0
    advance = len(words)
    if len(words) < 2:
        error("need specification after 'xshift'")
        return xs, 1, advance
    s = words[1]
    # negative slope?
    neg = s[0] == "-"
    if neg:
        s = s[1:]
    # is there an assignment taking place?
    a = s.split("=")
    assignment = len(a) > 1
    if assignment:
        try:
            num = float(a[1])
        except:
            error("assigment '"+ a[1] + "' must be a number")
            return xs, 1, advance
        coeff, xsname = splitnumtext(a[0])
        if xsname in xshifts:
            comment("Warning: xshift '" + xsname + \
                "' re-defined to "+str(num))
        xshifts[xsname] = num
        num *= coeff
    else:
        coeff, xsname = splitnumtext(a[0])
        if xsname: # uses a name
            if not xsname in xshifts:
                error("xshift '" + xsname + "' undefined")
                return xs, 1, advance
            num = coeff * xshifts[xsname]
        else:
            num = coeff
            coeff = 1 # no use of factor without label
    if aeq(num): # nearly zero
        xs = 0
        if aeq(coeff): # coefficient nearly zero
            factor = 1
        else:
            factor = coeff
    else: # num nonzero and therefore coeff nonzero
        factor = coeff
        if neg:
            xs = -num
        else:
            xs = num
    return xs, factor, 2
    ## testing:
    # a = ["xshift", "-2"]
    # b = ["xshift", "-2a=.3"]
    # c = ["xshift", "3a"]
    # l = [a,b,c]
    # for s in l:
    #     print s, xshift(s)
    #     print outstream
    # quit()

# parse "from" command
# return fromn,advance
def fromnode(words):
    assert words[0] == "from"
    advance = len(words)
    fromn = ""
    if len(words) < 2:
        error("need node name after 'from'")
        return fromn, advance
    s = cleannodeid(words[1])
    if not s in nodes:
        error("node "+s+" after 'from' is not defined")
    else:
        fromn = s
        advance = 2
    return fromn, advance

# parse "move" command
# return move, movpos, convex, advance
def move(words):
    assert words[0][:4] == "move"
    advance = len(words)
    mov = ""
    movpos = ""
    convex = -1
    a = words[0].split(":")
    if len(a) > 1:
        movpos = (a[1]+" ")[0].lower() # first character only
    if len(a) > 2:
        try:
            num = float(a[2])
            if num < 0 or num > 1:
                error("Move position in [0,1] required")
            else:
                convex = num
        except:
            error("Move position in [0,1] required")
    if len(words) < 2:
        error("need move name after 'move'")
        return mov, movpos, convex, advance
    mov = words[1]
    advance = 2
    return mov, movpos, convex, advance

    # # testing
    # l = ["move:Right", "T"]
    # print move (l)
    # outall()
    # quit ("done testing.")

# parse "arrow" command
# return arrowpos, arrowcolor, advance
def arrow(words):
    assert words[0][:5] == "arrow"
    a = words[0].split(":")
    if len(a) > 1:
        arrowcolor = a[1]
    else:
        arrowcolor = ""
    arrowpos = 0.5
    try:
        num = float(words[1])
        if num < 0 or num > 1:
            error("Arrow position in [0,1] required, using 0.5")
        else:
            arrowpos = num
    except:
        error("Arrow position in [0,1] required, using 0.5")
    advance = 2
    return arrowpos, arrowcolor, advance

# parse "payoffs" command
# return list of payoff strings for tikz output
def payoffs(words):
    assert words[0] == "payoffs"
    maxp = len(words)
    if len(words) > maxplayer+1:
        error("too many payoffs, discard "+str(words[maxplayer+1:]))
        maxp = maxplayer+1
    paylist = []
    for i in range(1, maxp):
        # tikz code
        t = "   node[below,yshift="
        t += fformat(payup-(i-1)) + paydown
        t += "] {$" + words[i]
        if words[i][0] == "-": # negative payoff
            t += "{\\phantom-}"
        t += "$\\strut}"
        paylist.append(t)
    return paylist
    # # testing
    # s = "payoffs -2 3 4 5"
    # s = "payoffs 0 x 1 3 4 5"
    # a = payoffs(s.split())
    # for s in a:
    #     print s
    # quit()

# draw node, player for square (0) or disk (not 0)
# colors could be added later
def drawnode(v, player=1):
    # tikz code
    out = "\\node[inner sep=0pt,minimum size="
    if player == 0:
        out += sqwidth + ",draw,fill="
        out += chancecolor + ",shape=rectangle] at "
    else:
        out += ndiam + ", draw, fill, shape=circle] at "
    out += coord(v[0], v[1]) + " {};"
    outs(out)
    return out

# return list of all nodes to be drawn
def drawnodes():
    for n in nodes:
        if nodes[n]["inner"]:
            v = [nodes[n]["x"], nodes[n]["y"]]
            p = nodes[n]["player"] 
            drawnode(v, p)
    return

# create node id from level (a float) and
def setnodeid(lev, s):
    return fformat(lev)+","+s

# standardize node id from "lev,s"
def cleannodeid(ns):
    a = ns.split(",")
    if len(a) < 2:
        error("missing comma in '"+ns+"', using empty node id")
        s = ""
    else:
        s = a[1]
    try:
        lev = float(a[0])
    except:
        error("Unknown level '"+a[0]+"' in '"+ns+"', using 0")
        lev = 0
    return setnodeid(lev, s)
    # # testing
    # s = "1,2 3,4 .0,r x,7 88 ,"
    # a = s.split()
    # a.append("")
    # for s in a:
    #     print s, cleannodeid(s)
    #     print outstream
    # quit()

# handle "level" keyword;
# commands: "node" node , then in any order
# "xshift" [-][2][[a=]1.5|a]  (2= multiple, a= xshift name, 1.5 = dimen)
# "from" nodeid (nodeid = level,node)
# "move" movename
# "payoffs" list of payoffs, comes last
# "inner" boolean: inner node, draw disk/square

def level(words):
    assert words[0] == "level"
    try:
        lev = float(words[1])
    except:
        error("need level number after 'level'")
        return
    try:
        assert words[2] == "node"
    except:
        error("expect keyword 'node' as word 3")
        return
    try:
        s = words[3]
    except:
        error("expect node identifier as word 4")
        return
    nodeid = setnodeid(lev, s)
    count = 4
    p = -1     # no player yet
    xs = 0     # no xshift yet
    factor = 1 # used for positioning move
    fromn = "" # no father yet
    mov = "" # no move yet
    movpos = "" # no move position (l/r) yet
    convex = -1 # no move position along line yet
    pay = []
    arrowposlist = []
    arrowcolorlist = []
    # process remaining words:
    # xshift, from, player, move, payoffs, arrow
    while count < len(words):
        if words[count] == "player": # set player
            p, advance = player(words[count:])
            count += advance
        elif words[count] == "xshift":
            xs, factor, advance = xshift(words[count:])
            count += advance
        elif words[count] == "from":
            fromn, advance = fromnode(words[count:])
            count += advance
        elif words[count][:4] == "move":
            mov, movpos, convex, advance = move(words[count:])
            count += advance
        elif words[count][:5] == "arrow":
            arrowpos, arrowcolor, advance = arrow(words[count:])
            arrowposlist.append(arrowpos)
            arrowcolorlist.append(arrowcolor)
            count += advance
        elif words[count] == "payoffs": # automatically last
            pay = payoffs(words[count:])
            break
        else: # unknown keyword 
            error ("unknown keyword "+words[count])
            count += 1
    # now line has been processed, update data from
    # nodeid, p, xs, fromn, move, lev
    # create x coordinate
    # existsfrom = not (fromn == "") and (fromn in nodes)
    existsfrom = (fromn in nodes)
    if existsfrom: # father exists
        xfrom = nodes[fromn]["x"]
        yfrom = nodes[fromn]["y"]
        xx = xfrom + xs
    else: # no father
        xx = xs
        if fromn:
            error("No 'from' node, move '" + mov +"' ignored")
    # direction down (for later expansion)
    yy = -lev
    nodes[nodeid] = {"x": xx, "y": yy, "player": p}
    nodes[nodeid]["xshift"] = xs
    nodes[nodeid]["move"] = mov
    nodes[nodeid]["from"] = fromn
    # root node always printed
    nodes[nodeid]["inner"] = (pay == []) or (lev == 0)
    # tikz code
    s = "\\draw ["+thickn+"] "+ coord(xx, yy)
    if p >= 0 and playername[p]: # nonempty player name
        # default: player to the right of node. perhaps left?
        if existsfrom and xs < 0:
            s += " node[left,xshift=-"
        else:
            s += " node[right,xshift="
        s += spx + ",yshift=" + spy + "] {\\"
        s += playertexname[p] + "\\strut}"
    outs(s)
    outlist(pay) # possibly empty
    if existsfrom: # draw line to father
        outs("   -- "+coord(xfrom, yfrom) + ";")
        # annotate moves above
        if convex < 0:
            convex = 0.5/factor
        xmove = xx * convex + xfrom * (1-convex)
        ymove = yy * convex + yfrom * (1-convex)
        s = "\\draw "+ coord(xmove, ymove)
        # decide if left or right
        if movpos == "r":
            side = "right,xshift=0.0cm"
        elif movpos == "l":
            side = "left,xshift=0.0cm"
        elif xs > 0: # default
            side = "right"
        else:
            side = "left"
        s += " node["+side+",yshift="
        if "frac" in mov:
            s += yfracup
        else:   
            s += yup
        s += "] {$"+mov+"$\\strut};"
        outs(s)
        # output arrows
        while arrowposlist:
            arrowpos = arrowposlist.pop(0)
            arrowcolor = arrowcolorlist.pop(0)
            xtip  = xfrom * (1 - arrowpos) + xx * arrowpos
            ytip  = yfrom * (1 - arrowpos) + yy * arrowpos
            xback = xfrom * (1.01 - arrowpos) + xx * (arrowpos-0.01)
            yback = yfrom * (1.01 - arrowpos) + yy * (arrowpos-0.01)
            if not arrowcolor == "":
                arrowcolor = "[fill="+arrowcolor+"]"
            s = "\\draw [-{StealthFill" + arrowcolor+"}]"
            s += coord(xback, yback)
            s += " -- " + coord(xtip, ytip) + ";"
            outs(s)
    else:
        outs("   ;")
    return

######################## isets

def isetgen(words):
    assert words[0] == "iset"
    nodelist = []
    p = -1
    count = 1
    where = 0 # where "player" was found
    while count < len(words):
        if words[count] == "player":
            p, advance = player(words[count:])
            where = count
            count += advance
        else:
            nodeid = cleannodeid(words[count])
            if not nodeid in nodes:
                error(" ".join(words)+" :", stream0)
                error("Node '"+nodeid+"' in iset not defined", stream0)
            else:
                v = [nodes[nodeid]["x"], nodes[nodeid]["y"]]
                nodelist.append(v)
            count += 1
    # generate and ship iset
    if len(nodelist) == 0:
        error(" ".join(words)+" :", stream0)
        error("No valid nodes in iset", stream0)
        return
    outs( iset(nodelist, radius/scale), stream0)
    # locate and print player
    if p >= 0 and playername[p]:
        if len(nodelist) == 1:
            n = nodelist[0]
            # tikz code
            s = "\\draw "+ coord(n[0], n[1])
            # player to the right of node (for later expansion)
            s += " node[right,xshift="
            s += spx + ",yshift=" + spy + "] {\\"
            # s += playertexname[p] + "\strut} ;"
            s += playertexname[p] + "} ;"
            outs(s)
        else: # at least two nodes
            if where > len(nodelist): # "player" at end
                where = int(len(nodelist)/2) + 1
            if where < 2:
                where = 2
            n1 = nodelist[where-2]
            n2 = nodelist[where-1]
            # tikz code
            s = "\\draw "
            s += coord((n1[0]+n2[0])/2, (n1[1]+n2[1])/2)
            # s += " node[xshift=0.0cm] {\\" + playertexname[p] + "\strut} ;"
            s += " node[xshift=0.0cm] {\\" + playertexname[p] + "} ;"
            outs(s)
    return

########### command-line arguments

# sets ef_file, scale, grid
def commandline(argv): # process command-line args
    global grid
    global scale 
    global ef_file
    for arg in argv[1:]:
        if arg[:5] == "scale":
            a = arg.split("=")
            try:    
                num = float(a[1])
                if num >= 0.01 and num <= 100:
                    scale = num
                else: 
                    outs("% Command-line argument 'scale=x' needs x in 0.01 .. 100", stream0)
            except:
                outs("% Command-line argument 'scale=x' needs x in 0.01 .. 100", stream0)
        elif arg == "grid":
            grid = True
        else:
            ef_file = arg
    return

def create_tikz_from_file(tex_file_path, macros_file_path="macros-drawtree.tex"):
    """
    Create TikZ code by combining macros and game tree content from separate files.

    Args:
        tex_file_path (str): Path to the .tex file containing the tikzpicture content
        macros_file_path (str): Path to the macros file (default: "macros-drawtree.tex")

    Returns:
        str: Complete TikZ code ready for %%tikz magic command
    """

    # Read the macros file
    try:
        with open(macros_file_path, "r") as f:
            macros_content = f.read()
    except FileNotFoundError:
        print(f"Warning: Could not find macros file {macros_file_path}")
        macros_content = ""

    # Read the tikzpicture content
    try:
        with open(tex_file_path, "r") as f:
            tikz_content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file {tex_file_path}")
        return ""
    
    # Create wrapper document with tex_file_path substituted for o.tex
    tikz_content = f"""% wrapper file for game tree drawing 
                        \\documentclass[a4paper,12pt]{{article}}
                        % \\usepackage{{mathptmx}}
                        \\usepackage{{newpxtext,newpxmath}}
                        \\linespread{{1.10}}        % Palatino needs more leading (space between lines) 
                        \\usepackage{{graphicx}}
                        \\usepackage{{tikz}}
                        % \\usepackage{{bimatrixgame}}
                        \\usetikzlibrary{{shapes}}
                        \\usetikzlibrary{{arrows.meta}}
                        \\oddsidemargin=.46cm 
                        \\textwidth=15cm
                        \\textheight=24cm
                        \\topmargin=-1.3cm
                        \\parindent 0pt
                        \\parskip1ex
                        \\pagestyle{{empty}}

                        \\input macros-drawtree

                        \\begin{{document}}

                        \\hrule

                        % Game tree content from {tex_file_path}
                        {tikz_content}

                        \\hrule

                        \\end{{document}}
                    """
    
    # Extract macro definitions from the macros file
    macro_lines = []
    for line in macros_content.split("\n"):
        line = line.strip()
        if line and not line.startswith("%"):
            macro_lines.append(line)

    # Create the complete TikZ code
    tikz_code = """% Load required TikZ libraries
                \\usetikzlibrary{shapes}
                \\usetikzlibrary{arrows.meta}

                % Macro definitions from macros-drawtree.tex
                """

    # Add macro definitions
    for macro in macro_lines:
        tikz_code += macro + "\n"

    tikz_code += "\n% Game tree content from " + tex_file_path + "\n"
    tikz_code += tikz_content

    return tikz_code

######################## main

if __name__ == "__main__":
    ef_file = DEFAULTFILE
    commandline(sys.argv)
    outs("% using file: "+ef_file, stream0)
    lines = readfile(ef_file)

    isets = {}

    # begin tikz picture
    outs("\\begin{tikzpicture}[scale="+str(scale), stream0)
    ss = "  , StealthFill/.tip={Stealth[line width=.7pt"
    outs(ss+",inset=0pt,length=13pt,angle'=30]}]", stream0)
    ss = ""
    if not grid:
        ss = "% "
    outs(ss+"\\draw [help lines, color=green] (-5,0) grid (5,-6);", stream0)

    # main loop
    for line in lines:
        comment(line)
        words = line.split()
        if words[0] == "player":
            player(words)
        elif words[0] == "level":
            level(words)
        elif words[0] == "iset":
            isetgen(words)

    # print "---------------"
    # for x in nodes:
        # print x, nodes[x]

    outall(stream0)
    drawnodes()
    # end tikz picture
    outs("\\end{tikzpicture}")
    outall()

    quit("done.")
