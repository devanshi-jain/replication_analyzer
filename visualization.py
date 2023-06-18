import networkx as nx
import matplotlib.pyplot as plt
import mplcursors

# Create an empty directed graph
graph = nx.DiGraph()

# Add nodes
graph.add_nodes_from(['A', 'B', 'C', 'D', 'E'])

# Add edges
graph.add_edges_from([('A', 'B'), ('A', 'C'), ('C', 'A'), ('B', 'D'), ('C', 'D'), ('D', 'E')])

# Draw the graph
pos = nx.spring_layout(graph)  # Layout algorithm for node positioning
nx.draw(graph, pos, with_labels=True, node_size=500, node_color='lightblue', edge_color='gray')

# Display the graph

cursor = mplcursors.cursor(hover=True)
cursor.connect("add", lambda sel: sel.annotation.set_text(
    f"add info here"))
plt.show()

