import networkx as nx
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import random

def rgb_to_hex(red, green, blue):
    color_hex = "#{:02x}{:02x}{:02x}".format(red, green, blue)
    return color_hex

def displayInteractableGraph(tree):
    labeling = {}
    pos = {}
    colors = []
    for node_name, node_attr in tree.nodes.items():
        # PI last name as label
        pos[node_name]=(node_attr["data"].xtier, node_attr["data"].tier)
        node_pi = node_attr["data"].author[0].split(',')[0]
        labeling[node_name] = node_pi
        node_val = node_attr["data"].val
        #delete this test
        # node_val = random.randint(-100, 100)
        print(node_val)
        color = "#D3D3D3"

        if node_val < 0: 
            color = rgb_to_hex(min(255, 150 + int(-node_val*50)), 150, 150)
        elif node_val > 0: 
            color = rgb_to_hex(150, min(255, 150 + int(node_val*50)), 150)
        colors.append(color)
        print(colors)

    nodes = nx.draw(tree, pos, with_labels = True, labels = labeling, node_size=800, font_size = 7, node_color=colors, edge_color='gray')
    def update_annot(sel):
        node_index = sel.target.index
        #number index
        node_name = list(tree.nodes)[node_index]
        node_attr = tree.nodes[node_name]
        node_title = node_attr["data"].title
        node_author = node_attr["data"].author
        node_doi = node_attr["data"].doi
        node_pi =node_author[0] 
        node_val = node_attr["data"].val

        text = node_title + "\n" + node_doi 
        sel.annotation.set_text(text)
        sel.annotation.get_bbox_patch().set(fc="white")

    cursor = mplcursors.cursor(nodes, hover=True)
    cursor.connect('add', update_annot)

    #zoom feature
    # Press move feature on graph + CTRL button
    plt.show()

    return 0 #successful exit!