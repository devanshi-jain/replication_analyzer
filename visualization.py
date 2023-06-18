import networkx as nx
import matplotlib.pyplot as plt
import mplcursors

# Create an empty directed graph
graph = nx.DiGraph()

# Add nodes
graph.add_nodes_from(['A', 'B', 'C', 'D', 'E'])

# Add edges
graph.add_edges_from([('A', 'B'), ('A', 'C'), ('C', 'A'), ('B', 'D'), ('C', 'D'), ('D', 'E')])

print(graph)

# Draw the graph
pos = nx.spring_layout(graph)  # Layout algorithm for node positioning
# if one pointing to is more negative then make red
nodes = nx.draw(graph, pos, with_labels=True, node_size=500, node_color='lightgreen', edge_color='gray')

def update_annot(sel):
    node_index = sel.target.index
    node_name = list(graph.nodes)[node_index]
    node_attr = graph.nodes[node_name]
    text = node_name + ' is the name'
    sel.annotation.set_text(text)
    sel.annotation.get_bbox_patch().set(fc="white")

cursor = mplcursors.cursor(nodes, hover=True)
cursor.connect('add', update_annot)

#zoom feature
# Press move feature on graph + CTRL button

# Display the graph
plt.show()

