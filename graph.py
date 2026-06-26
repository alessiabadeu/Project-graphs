import networkx as nx
import matplotlib.pyplot as plt
import random

def create_graph():
    G = nx.Graph()
    us_airports = set()
    with open("airports.dat.txt", "r", encoding="utf-8") as f:

        for line in f:
            splited_line = line.strip().split(",")
            airport_code = splited_line[4].strip().replace('"','')
            airport_name = splited_line[1].strip().replace('"','') 
            airport_country = splited_line[3].strip().replace('"', '')
            if airport_country == "United States" and airport_code!="\\N": 
                G.add_node(airport_code, name=airport_name, country=airport_country)
                us_airports.add(airport_code)

    with open("routes.dat.txt","r", encoding="utf-8") as f:
        for line in f:
            splited_line = line.strip().split(",")
            origin = splited_line[2].strip().replace('"', '')
            destination = splited_line[4].strip().replace('"', '')

            if len(splited_line)>=4 and origin in us_airports and destination in us_airports:
                G.add_edge(origin,destination)
    
    return G

def find_hubs(G):
    centrality = nx.betweenness_centrality(G)
    hubs = sorted(centrality.items(), key = lambda x: x[1], reverse=True)[:10]
    return hubs

def attack(G, nodes, alpha):

    load = nx.betweenness_centrality(G) 
    capacity = {n: alpha * load[n] for n in G.nodes()}  

    G_temp = G.copy()
    G_temp.remove_nodes_from(nodes)

    print("Removed nodes:", nodes)

    nodes = []
    iteration = 0

    while True:
        iteration += 1
        load = nx.betweenness_centrality(G_temp)

        failed = []
        for n in G_temp.nodes():
            if load[n] > capacity[n]:
                failed.append(n)

        nodes.append(G_temp.number_of_nodes()) 

        if not failed: 
            break

        G_temp.remove_nodes_from(failed)

    nodes.append(G_temp.number_of_nodes())
    
    return G_temp, nodes

def Sandy(G, alpha):
    return attack(G, ["JFK", "LGA", "EWR"], alpha)

def Harvey(G, alpha):
    return attack(G, ["IAH", "HOU"], alpha)

def PolarVortex(G, alpha):
    return attack(G, ["ORD", "MSP"], alpha)

def analyze_cascade(G, G_temp):
    initial_nodes = G.number_of_nodes()

    print("Final nodes:",G_temp.number_of_nodes())

    print("Failed airports:",initial_nodes - G_temp.number_of_nodes())

    largest_component = max(nx.connected_components(G_temp),key=len) 

    S = len(largest_component)
    print("Largest component size:", S)
    print("Normalized S:",S / initial_nodes) 

    E_before = nx.global_efficiency(G)
    E_after = nx.global_efficiency(G_temp)

    print("Efficiency before:",E_before)
    print("Efficiency after:",E_after)

def plot_cascade(nodes_over_time, nodes):
    plt.plot(nodes_over_time, marker='o')

    plt.xlabel("Iteration")
    plt.ylabel("Remaining nodes")
    plt.title(f"Cascade failure after removing {nodes}")
    plt.grid(True)

    plt.show()

def plot_comparison(nodes_targeted, nodes_random, label_targeted, alpha):
    plt.figure(figsize=(10, 5))
    plt.plot(nodes_targeted, marker='o', markersize=4, color='red',   label=f"Targeted attack ({label_targeted})")
    plt.plot(nodes_random,   marker='s', markersize=4, color='green', label="Random failure")

    plt.xlabel("Iteration")
    plt.ylabel("Remaining nodes")
    plt.title(f"Cascade failure: Targeted vs Random (α={alpha})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def random_attack(G, alpha):
    random_node = random.choice(list(G.nodes()))
    return attack(G, [random_node], alpha)

def main():
    G =create_graph()

    G_temp, nodes_over_time1 = attack(G, ["ANC"], 1.1)
    analyze_cascade(G, G_temp)

    G_temp, nodes_over_time2 = random_attack(G, 1.1)
    analyze_cascade(G, G_temp)

    plot_comparison(nodes_over_time1, nodes_over_time2, "DEN", 1.2)

    G_temp, nodes_over_time = Sandy(G, 1.1)
    analyze_cascade(G, G_temp)
    plot_cascade(nodes_over_time, "Sandy")

    G_temp, nodes_over_time = Harvey(G, 1.2)
    analyze_cascade(G, G_temp)
    plot_cascade(nodes_over_time, "Harvey")

    G_temp, nodes_over_time = PolarVortex(G, 1.2)
    analyze_cascade(G, G_temp)
    plot_cascade(nodes_over_time, "PolarVortex")

main()