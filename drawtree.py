#!/usr/bin/python
"""
Game tree drawing as TikZ file from .ef file
Version 1.0.5

This module provides functionality to generate TikZ code for game trees
from extensive form (.ef) files, with support for Jupyter notebooks.
"""
from __future__ import annotations

import sys
import math
from typing import List, Optional 

# Constants
DEFAULTFILE: str = "example.ef"
scale: float = 1
grid: bool = False

maxplayer: int = 4
payup: float = 0.1   # fraction of paydown to shift first payoff up
radius: float = 0.3   # iset radius

# Up to 4 players and chance (in principle more)
# Default names
playername: List[str] = [r"\small chance", "1", "2", "3", "4"]
playertexname: List[str] = ["playerzero", "playerone", "playertwo", "playerthree", "playerfour"]
# Player names that need to be defined in TeX
playerdefined: List[bool] = [False] * (maxplayer + 1)

# TikZ/TeX constants used, defined in TeX file, not here
paydown: str = "\\paydown"  # 2.5ex % yshift payoffs down
yup: str = "\\yup"  # 0.5mm % yshift up for moves
yfracup: str = "\\yfracup"  # 0.8mm % yshift up for chance probabilities
spx: str = "\\spx"  # 1mm % single player node xshift
spy: str = "\\spy"  # .5 mm % single player node yshift
ndiam: str = "\\ndiam"  # 1.5mm % node diameter disks
sqwidth: str = "\\sqwidth"  # 1.6 mm % node diameter disks
thickn: str = "line width=\\treethickn"  # {1pt} % line thickness
chancecolor: str = "\\chancecolor"  # gray color of chance node

numepsilon: float = 1e-9  # checking for almost equality

# Parameters for info set drawings
isetparams: str = ""  # draw parameters for info set drawings

# All dimensions in cm
isetradius: float = 0.3
# Elongated single iset in which direction
xsingleiset: float = 0.4
ysingleiset: float = 0.0

# How to indent
joinstring: str = "\n    "

# Output routines
allowcomments: bool = True

outstream: List[str] = []
stream0: List[str] = []


def outall(stream: Optional[List[str]] = None) -> None:
    """
    Output stream to stdout.
    
    Args:
        stream: List of strings to output. Defaults to global outstream.
    """
    if stream is None:
        stream = outstream
    for s in stream:
        print(s)


def outs(s: str, stream: Optional[List[str]] = None) -> None:
    """
    Output single string to stream.
    
    Args:
        s: String to append to stream.
        stream: Target stream list. Defaults to global outstream.
    """
    if stream is None:
        stream = outstream
    stream.append(s)


def outlist(string_list: List[str]) -> None:
    """
    Output list of strings to global outstream.
    
    Args:
        string_list: List of strings to append to global outstream.
    """
    global outstream
    outstream += string_list


def defout(defname: str, meaning: str) -> None:
    """
    LaTeX command for defining something.
    
    Args:
        defname: Name of the definition.
        meaning: Value/meaning of the definition.
        
    Note:
        Outputs TeX definition. Consider changing to LaTeX \\newcommand*.
    """
    outs("\\def\\" + defname + "{" + meaning + "}")


def newdimen(dimname: str, value: str) -> None:
    """
    LaTeX command for creating a dimension.
    
    Args:
        dimname: Name of the dimension.
        value: Value of the dimension.
    """
    outs("\\newdimen\\" + dimname)
    outs("\\" + dimname + value)


def comment(s: str) -> None:
    """
    Output comment if not suppressed.
    
    Args:
        s: Comment text to output.
    """
    if allowcomments:
        outs("%% " + s)


def error(s: str, stream: Optional[List[str]] = None) -> None:
    """
    Output error message (errors not suppressed).
    
    Args:
        s: Error message text.
        stream: Target stream. Defaults to global outstream.
    """
    if stream is None:
        stream = outstream
    outs("% ----- Error: " + s, stream)

def readfile(filename: str) -> List[str]:
    """
    Read file lines, stripped of blanks at end, if non-empty, into list.
    
    Args:
        filename: Path to file to read.
        
    Returns:
        List of non-empty, stripped lines from the file.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        
    Reference:
        http://stackoverflow.com/questions/12330522/reading-a-file-without-newlines
    """
    with open(filename, 'r') as file:
        temp = file.read().splitlines()
    out = []
    for line in temp:
        line = line.strip()
        if line:
            out.append(line)
    return out


def fformat(x: float, places: int = 3) -> str:
    """
    Format float to specified places, remove trailing ".0".
    
    Args:
        x: Number to format.
        places: Number of decimal places (default: 3).
        
    Returns:
        Formatted string representation of the number.
        
    Examples:
        >>> fformat(3.14159)
        '3.142'
        >>> fformat(3.0)
        '3'
        >>> fformat(3.100, 2)
        '3.1'
    """
    fstring = "%." + ("%df" % places)
    s = fstring % x
    if places > 0:
        s = s.rstrip("0")
        s = s.rstrip(".")
    return s


def coord(x: float, y: float) -> str:
    """
    Format coordinates as pair: 3,4 -> "(3,4)".
    
    Args:
        x: X coordinate.
        y: Y coordinate.
        
    Returns:
        Formatted coordinate string.
        
    Examples:
        >>> coord(1.0, 2.0)
        '(1,2)'
    """
    return "(" + fformat(x) + "," + fformat(y) + ")"


def twonorm(v: List[float]) -> float:
    """
    Calculate Euclidean length of vector.
    
    Args:
        v: Vector as list of coordinates.
        
    Returns:
        Euclidean length of the vector.
        
    Examples:
        >>> twonorm([3, 4])
        5.0
    """
    length = 0.0
    for x in v:
        length += x**2
    return length**0.5


def stretch(v: List[float], length: float = 1) -> List[float]:
    """
    Stretch vector to desired length (must be >= 0).
    
    Args:
        v: Input vector.
        length: Desired length (default: 1).
        
    Returns:
        Stretched vector with specified length.
        
    Raises:
        AssertionError: If the result doesn't have the expected length.
    """
    currl = twonorm(v)
    if currl == 0.0:
        return v
    out = []
    for x in v:
        out.append(x * length / currl)
    assert aeq(twonorm(out), length)
    return out


def degrees(v: List[float]) -> float:
    """
    Calculate angle of vector in degrees in (-180,180].
    
    Args:
        v: Vector as list of coordinates.
        
    Returns:
        Angle in degrees.
    """
    currl = twonorm(v)
    if aeq(currl):
        return 0
    onunitcircle = stretch(v)
    x = onunitcircle[0]
    y = onunitcircle[1]
    xd = math.acos(x) * 180 / math.pi
    if y < 0:
        return -xd  # in (-180,0)
    return xd  # in [0,180]


def aeq(x: float, y: float = 0) -> bool:
    """
    Test if numbers are almost equal (or equal to zero) numerically.
    
    Args:
        x: First number.
        y: Second number (default: 0).
        
    Returns:
        True if numbers are approximately equal.
    """
    return abs(x - y) < numepsilon


def det(a: float, b: float, c: float, d: float) -> float:
    """
    Calculate determinant of 2x2 matrix.
    
    Args:
        a, b, c, d: Matrix elements [[a, b], [c, d]].
        
    Returns:
        Determinant value (ad - bc).
    """
    return a * d - b * c

def isonlineseg(a: List[float], b: List[float], c: List[float]) -> bool:
    """
    Check if point b lies on the line segment [a,c].
    
    Args:
        a: Starting point as [x, y] coordinates.
        b: Point to test as [x, y] coordinates.
        c: Ending point as [x, y] coordinates.
        
    Returns:
        True if point b is on the line segment from a to c, False otherwise.
    """
    bx=b[0]-a[0]
    by=b[1]-a[1]
    cx=c[0]-a[0]
    cy=c[1]-a[1]
    if aeq(bx) and aeq(by):
        return True  # a near b
    if aeq( bx*cy - by*cx ): # collinear
        if aeq(cx) and aeq(cy) : # a near c but not near b
            return False
        if aeq(cx): # look at y coordinate
            if aeq(by,cy):
                return True  # c near b 
            if cy >= 0:
                return (by >= 0) and (by <= cy)
            # cy < 0
            return (by <= 0) and (by >= cy)
        # nonzero x coordinate of c, gives info
        if aeq(bx,cx):
            return True  # c near b 
        if cx > 0:
            return (bx >= 0) and (bx <= cx)
        # cx < 0
        return (bx <= 0) and (bx >= cx)
    # not collinear
    return False

def makearc(a: List[float], b: List[float], c: List[float], radius: float = isetradius) -> str:
    """
    Create arc or point around point b in triangle a,b,c.
    
    Args:
        a: First point as [x, y] coordinates.
        b: Center point as [x, y] coordinates.
        c: Third point as [x, y] coordinates.
        radius: Radius for the arc. Defaults to isetradius.
        
    Returns:
        TikZ coordinate string for the arc or point.
    """
    s = stretch([ b[1]-a[1], a[0]-b[0] ], radius)
    t = stretch([ c[1]-b[1], b[0]-c[0] ], radius)
    # print "% s,t    ", s,t
    sangle = degrees(s)
    tangle = degrees(t)
    # make sure to turn anticlockwise
    if tangle < sangle:
        tangle += 360
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

def arcseq(nodes: List[List[float]], radius: float = isetradius) -> List[str]:
    """
    Create a list of TikZ drawing commands around a list of coordinate pairs.
    
    Creates a sequence of arcs around the given nodes, removing collinear points
    and handling singleton information sets appropriately.
    
    Args:
        nodes: List of coordinate pairs [x,y].
        radius: Radius for the arcs. Defaults to isetradius.
        
    Returns:
        List of TikZ command strings (without "draw" and ";" wrapper).
    """ 
    nodes = nodes[:] # protect nodes parameter, now a local variable
    if len(nodes) == 0:
        return [""]
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

def iset(nodes: List[List[float]], radius: float = isetradius) -> str:
    """
    Create complete TikZ drawing commands for an information set.
    
    Args:
        nodes: List of coordinate pairs [x,y].
        radius: Radius for the arcs. Defaults to isetradius.
        
    Returns:
        Complete TikZ draw command string with semicolon.
    """ 
    arcs = arcseq(nodes,radius)
    # tikz code 
    return "\\draw [" + isetparams + "] " + "\n  -- ".join(arcs) + " -- cycle;"

######################## handling players

def player(words: List[str]) -> tuple[int, int]:
    """
    Parse 'player' command and handle player definitions.
    
    Processes player number and optional name, writing out player definition
    if the player is named or used for the first time.
    
    Args:
        words: List of command words starting with 'player'.
        
    Returns:
        Tuple of (player_number, advance_count) where advance_count is 
        the number of words consumed from the input.
    """
    p = -1  # illegal player
    advance = len(words)
    assert words[0] == "player"
    try:
        x = int(words[1])
    except ValueError:
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

def splitnumtext(s: str) -> tuple[float, str]:
    """
    Split a string into numeric prefix and text remainder.
    
    Extracts a leading number (including decimal) from a string and returns
    both the number and the remaining text.
    
    Args:
        s: Input string to parse.
        
    Returns:
        Tuple of (number, remainder_text). If no number is found, 
        returns (1, original_string).
        
    Examples:
        "2.3abc" -> (2.3, "abc")
        ".1b" -> (0.1, "b") 
        "a" -> (1, "a")
    """
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

def xshift(words: List[str]) -> tuple[float, float, int]:
    """
    Parse 'xshift' command to determine horizontal positioning.
    
    Handles xshift assignments and lookups, including named xshift variables
    and coefficient multipliers.
    
    Args:
        words: List of command words starting with 'xshift'.
        
    Returns:
        Tuple of (x_shift, factor, advance_count) where:
        - x_shift: The calculated horizontal shift value
        - factor: The coefficient factor for scaling
        - advance_count: Number of words consumed (always 2)
    """
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
        except ValueError:
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
            if xsname not in xshifts:
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

def fromnode(words: List[str]) -> tuple[str, int]:
    """
    Parse 'from' command to identify parent node.
    
    Args:
        words: List of command words starting with 'from'.
        
    Returns:
        Tuple of (parent_node_id, advance_count) where parent_node_id
        is the cleaned node identifier and advance_count is words consumed.
    """
    assert words[0] == "from"
    advance = len(words)
    fromn = ""
    if len(words) < 2:
        error("need node name after 'from'")
        return fromn, advance
    s = cleannodeid(words[1])
    if s not in nodes:
        error("node "+s+" after 'from' is not defined")
    else:
        fromn = s
        advance = 2
    return fromn, advance

def move(words: List[str]) -> tuple[str, str, float, int]:
    """
    Parse 'move' command to extract move name and positioning.
    
    Handles move syntax like "move:Left:0.3" where the colon-separated parts
    specify positioning and convexity parameters.
    
    Args:
        words: List of command words starting with 'move'.
        
    Returns:
        Tuple of (move_name, move_position, convex_value, advance_count).
    """
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
        except ValueError:
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

def arrow(words: List[str]) -> tuple[float, str, int]:
    """
    Parse 'arrow' command to extract arrow positioning and color.
    
    Args:
        words: List of command words starting with 'arrow'.
        
    Returns:
        Tuple of (arrow_position, arrow_color, advance_count).
    """
    assert words[0][:5] == "arrow"
    a = words[0].split(":")
    if len(a) > 1:
        arrowcolor = a[1]
    else:
        arrowcolor = ""
    arrowpos = 0.5
    advance = 2  # Default advance value
    try:
        num = float(words[1])
        if num < 0 or num > 1:
            error("Arrow position in [0,1] required, using 0.5")
        else:
            arrowpos = num
    except Exception:
        error("Arrow position in [0,1] required, using 0.5")
    return arrowpos, arrowcolor, advance

def payoffs(words: List[str]) -> List[str]:
    """
    Parse 'payoffs' command to generate TikZ payoff display code.
    
    Args:
        words: List of command words starting with 'payoffs'.
        
    Returns:
        List of TikZ node commands for displaying payoffs.
    """
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

def drawnode(v: List[float], player: int = 1) -> str:
    """
    Generate TikZ code to draw a game tree node.
    
    Creates either a square (for chance/player 0) or circle (for other players).
    
    Args:
        v: Node position as [x, y] coordinates.
        player: Player number (0 for chance node, >0 for player node).
        
    Returns:
        TikZ node command string.
    """
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

def drawnodes() -> None:
    """
    Draw all inner (non-leaf) nodes in the game tree.
    
    Iterates through all nodes and draws those marked as 'inner' nodes
    using appropriate shapes based on player type.
    """
    for n in nodes:
        if nodes[n]["inner"]:
            v = [nodes[n]["x"], nodes[n]["y"]]
            p = nodes[n]["player"] 
            drawnode(v, p)
    return

def setnodeid(lev: float, s: str) -> str:
    """
    Create node identifier from level and name.
    
    Args:
        lev: Level number (typically a float).
        s: Name string for the node.
        
    Returns:
        Formatted node identifier string "level,name".
    """
    return fformat(lev)+","+s

def cleannodeid(ns: str) -> str:
    """
    Standardize node id from "level,name" format.
    
    Args:
        ns: Node string in "level,name" format.
        
    Returns:
        Standardized node identifier.
    """
    a = ns.split(",")
    if len(a) < 2:
        error("missing comma in '"+ns+"', using empty node id")
        s = ""
    else:
        s = a[1]
    try:
        lev = float(a[0])
    except Exception:
        error("Level must be a number, using 0")
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

def level(words: List[str]) -> None:
    """
    Process a complete level command to create a game tree node.
    
    This is the main parsing function that handles the 'level' command and all
    its associated sub-commands (player, xshift, from, move, payoffs, arrow).
    Creates TikZ output for drawing the node and connecting lines.
    
    Args:
        words: List of command words starting with 'level'.
    """
    assert words[0] == "level"
    try:
        lev = float(words[1])
    except Exception:
        error("Level must be a number")
        return
    try:
        assert words[2] == "node"
    except Exception:
        error("Expected 'node' keyword")
        return
    try:
        s = words[3]
    except Exception:
        error("Expected node name")
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
    xfrom = 0.0  # Initialize to avoid unbound variable warnings
    yfrom = 0.0  # Initialize to avoid unbound variable warnings
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

def isetgen(words: List[str]) -> None:
    """
    Process 'iset' command to generate information set visualization.
    
    Creates TikZ code to draw information sets (connecting multiple nodes
    that belong to the same player and decision point).
    
    Args:
        words: List of command words starting with 'iset'.
    """
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
            if nodeid not in nodes:
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

def commandline(argv: List[str]) -> None:
    """
    Process command-line arguments to set global configuration.
    
    Sets global variables for ef_file, scale, and grid based on
    command-line arguments.
    
    Args:
        argv: List of command-line arguments (including script name).
    """
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
            except Exception:
                outs("% Command-line argument 'scale=x' needs x in 0.01 .. 100", stream0)
        elif arg == "grid":
            grid = True
        else:
            ef_file = arg
    return

def ef_to_tex(ef_file: str, scale_factor: float = 1.0, show_grid: bool = False) -> str:
    """
    Convert an extensive form (.ef) file to TikZ code.
    
    This function replicates the main processing logic but returns the TikZ code
    as a string instead of printing it to stdout.
    
    Args:
        ef_file: Path to the .ef file to process.
        scale_factor: Scale factor for the diagram (default: 1.0).
        show_grid: Whether to show grid lines (default: False).
        
    Returns:
        Complete TikZ code as a string.
    """
    global scale, grid
    
    # Save original state
    original_outstream = outstream.copy()
    original_stream0 = stream0.copy()
    original_nodes = nodes.copy()
    original_xshifts = xshifts.copy()
    original_playerdefined = playerdefined.copy()
    original_scale = scale
    original_grid = grid
    
    try:
        # Reset global state
        outstream.clear()
        stream0.clear()
        nodes.clear()
        xshifts.clear()
        for i in range(len(playerdefined)):
            playerdefined[i] = False
        
        # Set parameters
        scale = scale_factor
        grid = show_grid
        
        # Process the .ef file (same logic as main)
        lines = readfile(ef_file)

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
            if len(words) > 0:
                if words[0] == "player":
                    player(words)
                elif words[0] == "level":
                    level(words)
                elif words[0] == "iset":
                    isetgen(words)

        # Output nodes
        drawnodes()
        
        # end tikz picture - add to outstream so it comes after nodes
        outs("\\end{tikzpicture}", outstream)
        
        # Combine all output into a single string
        all_lines = stream0 + outstream
        return "\n".join(all_lines)
        
    finally:
        # Restore original state
        outstream.clear()
        outstream.extend(original_outstream)
        stream0.clear()
        stream0.extend(original_stream0)
        nodes.clear()
        nodes.update(original_nodes)
        xshifts.clear()
        xshifts.update(original_xshifts)
        for i in range(len(playerdefined)):
            playerdefined[i] = original_playerdefined[i]
        scale = original_scale
        grid = original_grid

def draw_tree(ef_file: str, scale_factor: float = 1.0, show_grid: bool = False, macros_file_path: str = "macros-drawtree.tex") -> str:
    """
    Generate complete TikZ code from an extensive form (.ef) file.
    
    This function combines ef_to_tex and create_tikz_from_file into a single
    streamlined call that goes directly from .ef file to complete TikZ code.
    
    Args:
        ef_file: Path to the .ef file to process.
        scale_factor: Scale factor for the diagram (default: 1.0).
        show_grid: Whether to show grid lines (default: False).
        macros_file_path: Path to the macros file (default: "macros-drawtree.tex").
        
    Returns:
        Complete TikZ code ready for use in Jupyter notebooks or LaTeX documents.
    """
    # Step 1: Generate the tikzpicture content using ef_to_tex logic
    tikz_picture_content = ef_to_tex(ef_file, scale_factor, show_grid)
    
    # Step 2: Read and process the macros file
    try:
        with open(macros_file_path, "r") as f:
            macros_content = f.read()
    except FileNotFoundError:
        print(f"Warning: Could not find macros file {macros_file_path}")
        macros_content = ""

    # Step 3: Extract macro definitions from the macros file
    macro_lines = []
    for line in macros_content.split("\n"):
        line = line.strip()
        if line and not line.startswith("%"):
            macro_lines.append(line)

    # Step 4: Combine everything into complete TikZ code
    tikz_code = """% TikZ code with q.tex styling using TikZ style definitions
% TikZ libraries required for game trees
\\usetikzlibrary{shapes}
\\usetikzlibrary{arrows.meta}

% Style settings to approximate q.tex formatting
\\tikzset{
    every node/.append style={font=\\rmfamily},
    every text node part/.append style={align=center},
    node distance=1.5mm,
    thick
}

% Macro definitions from macros-drawtree.tex
"""

    # Add macro definitions
    for macro in macro_lines:
        tikz_code += macro + "\n"

    tikz_code += f"\n% Game tree content from {ef_file}\n"
    tikz_code += tikz_picture_content

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

    outall(stream0)
    drawnodes()
    # end tikz picture
    outs("\\end{tikzpicture}")
    outall()

    quit("done.")
