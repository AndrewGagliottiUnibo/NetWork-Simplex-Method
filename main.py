from copy import deepcopy
import utilities


class NetSimplex:

    # Inizializza un oggetto grafo
    def __init__(self, type=1):
        self.G = utilities.create_graph(type)
        self.G1 = {"node": [], "arc": []}
        self.T = {"node": [], "arc": []}
        self.L = []
        self.T1 = []
        self.neighborhood = []
        self.reverse = False

#-----------------------------Operazioni sugli archi-----------------------------
    # Recupera il valore dell'arco
    def get_arc(self, graph, i, j):
        for arc in graph["arc"]:
            if arc["sp"] == i and arc["ep"] == j:
                return arc
        return None

    # Funzione strutturale
    def reverse_arcs(self, graph):
        G = deepcopy(graph)
        for arc in G["arc"]:
            if (arc["sp"] > arc["ep"]):
                app = arc["sp"]
                arc["sp"] = arc["ep"]
                arc["ep"] = app

    # Rimuove un arco
    def remove_arc(self, graph, i):
        for arc in graph["arc"]:
            if (arc["sp"] == i or arc["ep"] == i):
                graph["arc"].remove(arc)

    # Direzione dell'arco
    def is_foward(self, i, j):
        if (i < j):
            return True
        else:
            return False

    # Direzione dell'arco
    def is_backward(self, i, j):
        return not self.is_foward()

#-----------------------------Operazioni sui potenziali-----------------------------
    # Recupera i potenziali
    def get_potential(self, graph, point):
        node = self.get_node(graph, point)
        return node["potential"]

    # Aggiorna i potenziali
    def update_potential(self, graph, point, change):
        node = self.get_node(graph, point)
        node["potential"] = change

#-----------------------------Operazioni sui nodi-----------------------------
    # Recupera i nodi
    def get_node(self, graph, point):
        return graph["node"][point-1]
        print("Node not found")

    # Rimuove i nodi
    def remove_node(self, graph, point):
        graph["node"].remove(self.get_node(graph, point))
        self.remove_arc(graph, point)

    # Recupera il precedente
    def get_pred(self, graph, point):
        return self.get_node(graph, point)["pred"]
        print("Pred not found")

    # Recupera la profondità
    def get_depth(self, graph, point):
        node = self.get_node(graph, point)
        return node["depth"]

    # Imposta la profondità
    def set_depth(self, graph, node, depth):
        node = self.get_node(graph, node["point"])
        node["depth"] = depth

    # Imposta il precedente
    def set_pred(self, graph, point, pred):
        node = self.get_node(graph, point)
        node["pred"] = pred

    # Analizza la profondità di un nodo
    def compute_depth(self, graph, node):
        if (node["point"] == 1):
            self.set_depth(graph, node, 0)
        else:
            pred = self.get_pred(graph, node["point"])
            depth_pred = self.get_depth(graph, pred)
            self.set_depth(graph, node, depth_pred+1)

    # Analizza il precedente e il flusso
    def compute_pred_and_thread(self, graph):
        G = deepcopy(graph)
        self.reverse_arcs(G)
        self.dfs(G, 1, thread=True, reverse=True)
        self.G["node"] = deepcopy(G["node"])

#-----------------------------Operazioni sui flussi-----------------------------
    # Recupera il flusso
    def get_thread(self, graph, point):
        node = self.get_node(graph, point)
        return node["thread"]

    # Imposta il flusso
    def set_thread(self, graph, point, thread):
        node = self.get_node(graph, point)
        node["thread"] = thread

#-----------------------------Operazioni sui costi-----------------------------
    # Analizza i costi
    def compute_cost(self, graph):
        if (isinstance(graph, dict)):
            for arc in graph["arc"]:
                pi_i = self.get_potential(self.T, arc["sp"])
                pi_j = self.get_potential(self.T, arc["ep"])
                c_ij = self.get_arc(self.G, arc["sp"], arc["ep"])["cost"]

                arc["cost"] = c_ij - pi_i + pi_j
        else:
            for arc in graph:
                pi_i = self.get_potential(self.T, arc["sp"])
                pi_j = self.get_potential(self.T, arc["ep"])
                c_ij = self.get_arc(self.G, arc["sp"], arc["ep"])["cost"]
                
                arc["cost"] = c_ij - pi_i + pi_j

#-----------------------------Operazioni sul routing-----------------------------
    # Recupera il path tra due nodi
    def get_path(self, graph, i, j, path):
        if (not len(path)):
            path.append(j)
        if (i == j):
            return path
        else:
            pred_j = self.get_pred(graph, j)
            path.append(pred_j)
            if (pred_j == i):
                return path
            else:
                self.get_path(graph, i, pred_j, path)
        return path

#
# START TODO
#
    # procedure to identify cyle (return apex)
    def identify_cycle(self, graph, k, l):
        i = k
        j = l
        while (i != j):
            depth_i = self.get_depth(graph, i)
            depth_j = self.get_depth(graph, j)
            if (depth_i > depth_j):
                i = self.get_pred(graph, i)
            elif (depth_j > depth_i):
                j = self.get_pred(graph, j)
            else:
                i = self.get_pred(graph, i)
                j = self.get_pred(graph, j)
        # apex
        return i

    def compute_potentials(self, graph):
        root = self.get_node(graph, 1)
        root["potential"] = 0
        j = self.get_thread(graph, 1)
        while (j != 1):
            i = self.get_pred(graph, j)
            pi_i = self.get_potential(graph, i)
            if (self.is_foward(i, j)):
                arc = self.get_arc(graph, i, j)
                if (arc is not None):
                    cost = arc["cost"]
                    self.update_potential(graph, j, (pi_i - cost))
            else:
                arc = self.get_arc(graph, j, i)
                if (arc is not None):
                    cost = arc["cost"]
                    self.update_potential(graph, j, (pi_i + cost))
            j = self.get_thread(graph, j)

    def update_potentials(self, graph, entering, leaving):
        # root node + other nodes
        T1 = deepcopy(graph)

        # no root node
        T2 = deepcopy(graph)
        T2["node"].remove(self.get_node(T2, 1))
        self.remove_arc(T2, 1)

        # (k,l) entering arc
        k = entering["sp"]
        l = entering["ep"]

        # (p,q) exiting arc
        p = leaving["sp"]
        q = leaving["ep"]

        found = False
        for n in T2["node"]:
            if n["point"] == q:
                found = True
                y = q
                break
        if (not found):
            y = p

        found = False
        for n in T1["node"]:
            if n["point"] == k:
                found = True
                change = -entering["cost"]
                break
        if (not found):
            change = entering["cost"]

        pi_y = self.get_potential(graph, y)
        self.update_potential(graph, y, (pi_y+change))
        z = self.get_thread(graph, y)
        while (self.get_depth(graph, z) > self.get_depth(graph, y)):
            pi_z = self.get_potential(graph, z)
            self.update_potential(graph, z, (pi_z+change))
            z = self.get_thread(graph, z)
#
# END TODO
#

#-----------------------------Operazioni sulla struttura-----------------------------
    # Crea la struttura dello spanning tree
    def get_spanning_tree_stucture(self, graph):
        G = deepcopy(graph)
        self.dfs(G, 1, reverse=False)

        for n in G["node"]:
            if (n["point"] != graph["node"][0]["point"]):
                i = n["pred"]
                j = n["point"]
                arc = self.get_arc(G, i, j)
                if (arc is not None):
                    self.T["arc"].append(arc)
                    G["arc"].remove(arc)
        self.T["node"] = deepcopy(G["node"])

        self.L = deepcopy(G["arc"])
        del G
        return self.T, self.L

#
# START TODO
#
    def optimal(self):
        for arc in self.L:
            if (arc["cost"] < 0):
                return False
        return True

    # First eligible arc pivot rule
    def get_entering_arc(self):
        if (len(self.L)):
            for i in range(len(self.L)):
                if (self.L[i]["cost"] < 0):
                    return self.L.pop(i)
        else:
            return False

    # entering arc = (k,l)
    def get_leaving_arc(self, graph, entering_arc):
        l = entering_arc["ep"]
        pred_l = self.get_pred(graph, l)
        return self.get_arc(graph, pred_l, l)

    # returns all the nodes reachable from a given node
    def get_neighborhood(self, graph, point):
        neighborhood = []
        for arc in graph["arc"]:
            if (arc["sp"] == point):
                neighborhood.append(arc["ep"])
                neighborhood.reverse()
        return neighborhood

    # performs DFS and set thread of all nodes
    def dfs(self, graph, start, thread=False, reverse=False):
        visited = [start]
        stack = [start]
        if reverse:
            self.reverse_arcs(graph)

        while len(stack):
            v = stack.pop(0)
            for u in self.get_neighborhood(graph, v):
                if u not in visited:
                    stack.insert(0, u)
                    visited.append(u)
                    self.set_pred(graph, u, v)
            if thread:
                if (len(stack)):
                    self.set_thread(graph, v, stack[0])
                else:
                    self.set_thread(graph, v, 1)

    def update_tree(self):
        self.T["node"] = deepcopy(self.T1["node"])
        self.G["node"] = deepcopy(self.T1["node"])
        self.G1 = deepcopy(self.G)
#
# END TODO
#

def main():
    j = 0
    M = NetSimplex(6)

    # compute predecessors and threads indices
    M.compute_pred_and_thread(M.G)

    # draw initial graph
    utilities.draw_graph(M.G, name=str(j)+".svg", title="Initial Graph")
    j += 1

    # get initial feasible spanning tree structure
    M.get_spanning_tree_stucture(M.G)

    # draw spanning tree
    utilities.draw_graph(M.G, arcs=M.T["arc"], L=M.L, spanning=1, name=str(
        j)+".svg", title="Initial Spanning Tree Structure")
    j += 1

    # compute depth
    for node in M.T["node"]:
        M.compute_depth(M.T, node)

    # compute initial potentials
    M.compute_potentials(M.T)

    # compute cost
    M.compute_cost(M.L)

    i = 0
    while (not M.optimal()):
        # select an entering arc
        entering = M.get_entering_arc()

        # add the entering arc to the tree
        arc = M.get_arc(M.G, entering["sp"], entering["ep"])
        M.T["arc"].append(arc)

        # select the leaving arc
        leaving = M.get_leaving_arc(M.T, entering)

        # draw graph highlighting the entering and the leaving edge
        utilities.draw_graph(M.G, L=M.L, arcs=M.T["arc"], entering=entering, leaving=leaving, spanning=1,
                             name=str(j)+".svg",
                             title="Iteration: " + str(i) + "\nEntering arc (green) and Leaving arc (red)")
        j += 1

        # update T
        M.T["arc"].remove(leaving)

        # update L
        M.L.append(leaving)

        M.compute_pred_and_thread(M.T)

        for node in M.T["node"]:
            M.compute_depth(M.T, node)

        # update potentials
        M.update_potentials(M.T, entering, leaving)

        # draw the updated graph
        utilities.draw_graph(M.G, L=M.L, arcs=M.T["arc"], spanning=1,
                             name=str(j) + ".svg",
                             title="Iteration: " + str(i) + "\nUpdated Structure.")
        j += 1

        # compute cost
        M.compute_cost(M.L)

        # logs
        # '''
        print("*"*100)
        print("ITERATION:", i)

        print("\n")
        print("=" * 100)
        print("ENTERING ARC:", entering)
        print("LEAVING ARC:", leaving)
        print("=" * 100)
        print("\n")

        utilities.print_structure(M.T, M.L)
        print("\n")

        print("END OF ITERATION", i)
        print("*" * 100)
        i += 1

    print("\n")
    print("*"*100)
    print("SHORTEST PATH THREE FOUND")
    print("*" * 100)
    utilities.print_structure(M.T)
    # draw the SPT
    utilities.draw_graph(M.T, spanning=1,
                         name=str(j)+".svg",
                         title="Shortest Path Tree")

    # '''
if __name__ == "__main__":
    main()
