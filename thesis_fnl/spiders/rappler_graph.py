import networkx as nx
import pygraphviz


try:
    import pygraphviz
except ImportError:
    raise ImportError('read_dot() requires pygraphviz ',
                      'http://pygraphviz.github.io/')
A=pygraphviz.AGraph(file="rappler.dot")
return from_agraph(A)
