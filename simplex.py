import networkx as nx

# Initializing a new graph
G = nx.DiGraph()

# Adding nodes
G.add_node("1", demand=-10)
G.add_node("2", demand=0)
G.add_node("3", demand=0)
G.add_node("4", demand=0)
G.add_node("5", demand=10)

# Adding edges
G.add_edge("1", "2", weight=10, capacity=5)
G.add_edge("1", "3", weight=12, capacity=3)
G.add_edge("1", "4", weight=6, capacity=4)
G.add_edge("3", "2", weight=2, capacity=2)
G.add_edge("3", "4", weight=3, capacity=5)
G.add_edge("3", "5", weight=7, capacity=5)
G.add_edge("2", "5", weight=6, capacity=6)
G.add_edge("4", "5", weight=3, capacity=6)
flowCost, flowDict = nx.network_simplex(G)

# Objective function: Min 10
print("Flusso: ", flowDict)
print("Min z = ", flowCost)
