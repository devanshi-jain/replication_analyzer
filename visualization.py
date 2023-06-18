import networkx as nx
import matplotlib.pyplot as plt
import mplcursors
from mpl_interactions import ioff, panhandler, zoom_factory


# Create an empty directed graph
graph = nx.DiGraph()

# Add nodes
graph.add_nodes_from(['A', 'B', 'C', 'D', 'E'])

# Add edges
graph.add_edges_from([('A', 'B'), ('A', 'C'), ('C', 'A'), ('B', 'D'), ('C', 'D'), ('D', 'E')])

print(graph)

# Draw the graph
pos = nx.spring_layout(graph)  # Layout algorithm for node positioning
nx.draw(graph, pos, with_labels=True, node_size=500, node_color='lightblue', edge_color='gray')

# arrow features
cursor = mplcursors.cursor(hover=True)
@cursor.connect("add")

def _(sel):
    sel.annotation.set_text(f"add info here")
    sel.annotation.get_bbox_patch().set(fc="white")

#zoom feature
# Press move feature on graph + CTRL button

# Display the graph
plt.show()

