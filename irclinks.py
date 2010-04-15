#!/usr/bin/python

import socket, random, re, time, cgi

def getlinks(hostname, via = None):
    sock = socket.socket()
    sock.settimeout(3)
    nick = "x" + str(random.getrandbits(23))

    if via is None:
        sock.connect((hostname, 6667))
        sock.send("USER " + nick + " * * :x\nNICK " + nick + "\n")
        time.sleep(0.5)
        sock.send("LINKS\n")
        time.sleep(0.5)
        sock.send("QUIT\n")
    else:
        sock.connect((via, 6667))
        sock.send("USER " + nick + " * * :x\nNICK " + nick + "\n")
        time.sleep(0.5)
        sock.send("LINKS "+hostname+" *\n")
        time.sleep(0.5)
        sock.send("QUIT\n")

        

    data = ""
    while len(data) < 2**16:
        s = sock.recv(4096)
        if len(s) == 0: break
        data += s
    for resp in data.split("\n"):
        g = re.match(r"^[^ ]*? 364 .*? (.*?) (.*?) :?(?:\d+ )?(.*?)\s*$", resp)
        if g:
            yield g.groups()

def buildgraph(firsthost):
    unqueried = set([firsthost]) # hosts still to be queried
    places = {} # locations of hosts
    edges = set()

    while len(unqueried) != 0:
        h = unqueried.pop()
        try:
            print "Querying %s... (%d hosts still to query)" % (h,len(unqueried))
            for dst, src, dstloc in getlinks(h, via=firsthost):
                if dst not in places:
                    places[dst] = dstloc
                    unqueried.add(dst)
                elif places[dst] != dstloc:
                    print "Conflicting locations for %s: %r and %r" % (dst, places[dst], dstloc)
                edges.add((src,dst))
        except Exception,e:
            print "Error querying %s: %s" % (h,e)
    return places, edges

def mkdot(places, conns, outfile):
    outfile.write("digraph{\nsplines=1;\n")
    nodenames = {}
    nidx = 0
    for p in places:
        nodenames[p] = "n" + str(nidx)
        txt = places[p]
        txt = "".join([c for c in txt if ord(c) >= 32]) # strip ascii control chars
        # random guess at encoding
        try:
            txt = unicode(txt, 'utf8')
        except UnicodeDecodeError:
            txt = unicode(txt, 'iso-8859-1')
        txt = cgi.escape(txt).encode('ascii','xmlcharrefreplace')
        txt = txt.replace("|","&#124;")
        outfile.write(nodenames[p] + " [shape=Mrecord;label=<{<font point-size=\"11\">%s</font>|<font point-size=\"8\">%s</font>}>];\n" % (p, txt))
        nidx += 1

    skipped = set()
    for (src, dst) in conns:
        if (src, dst) in skipped: continue
        if src == dst: continue
        if (dst,src) in conns:
            bidir = "dir=both"
            skipped.add((dst,src))
        else:
            bidir = "dir=forward"
        outfile.write(nodenames[src] + " -> " + nodenames[dst] + " [" + bidir + "];\n")
    outfile.write("}\n")


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) != 2:
        print '''Usage: %s <IRC host> <out filename>'''
    else:
        p,c = buildgraph(args[0])
        mkdot(p,c, open(args[1], "w"))
