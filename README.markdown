irclinks.py
-----------

Maps out an IRC network by connecting to one of the servers, running
the LINKS command, and recursing until it queries the entire
network. The graph is dumped in [Graphviz](http://graphviz.org) format
for easy visualisation.

### Usage: 

python irclinks.py irc.somewhere.org a_file_name.dot
dot a_file_name.dot -Tpng > an_image_name.png