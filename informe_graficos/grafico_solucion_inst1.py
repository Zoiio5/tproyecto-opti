import networkx as nx
import matplotlib.pyplot as plt

# Nodos por tipo
plantas = [1, 2]
tanques = [3, 4, 5, 6, 7]
c1 = [8, 9, 10, 11, 12, 13, 14]
c2 = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

# Crear el grafo dirigido
g = nx.DiGraph()

# Añadir nodos con color por tipo
g.add_nodes_from(plantas, color='green', tipo='P')
g.add_nodes_from(tanques, color='blue', tipo='T')
g.add_nodes_from(c1, color='orange', tipo='C1')
g.add_nodes_from(c2, color='red', tipo='C2')

# Arcos activos (origen, destino, flujo, diámetro)
arcos_activos = [
    (1, 3, 84.62, 75),
    (1, 6, 82.0, 75),
    (1, 7, 66.0, 75),
    (2, 3, 36.38, 75),
    (2, 4, 145.24, 75),
    (2, 5, 81.0, 75),
    (3, 8, 25.0, 75),
    (3, 9, 24.0, 75),
    (4, 10, 26.0, 75),
    (5, 13, 19.0, 75),
    (6, 14, 20.0, 75),
    (3, 11, 20.0, 75),
    (4, 12, 22.0, 75),
    (3, 15, 27.0, 75),
    (4, 16, 31.0, 75),
    (5, 17, 29.0, 75),
    (6, 18, 32.0, 75),
    (7, 19, 34.0, 75),
    (3, 20, 25.0, 75),
    (4, 21, 35.0, 75),
    (5, 22, 33.0, 75),
    (6, 23, 30.0, 75),
    (7, 24, 32.0, 75),
    (4, 25, 31.24, 75)
]



# Posiciones: agrupar por tipo para visualización más clara
pos = {}
# Plantas
for i, n in enumerate(plantas):
    pos[n] = (i*2, 4)
# Tanques
for i, n in enumerate(tanques):
    pos[n] = (i*1.5, 3)
# C1
for i, n in enumerate(c1):
    pos[n] = (i*1.2, 2)
# C2
for i, n in enumerate(c2):
    pos[n] = (i*1.0, 1)

# Dibujar nodos
colors = [g.nodes[n]['color'] for n in g.nodes]
nx.draw_networkx_nodes(g, pos, node_color=colors, node_size=500)
nx.draw_networkx_labels(g, pos)

# Dibujar arcos activos
nx.draw_networkx_edges(g, pos, edgelist=[(o, d) for o, d, _, _ in arcos_activos], width=2, edge_color='black', arrows=True)

# Etiquetas de arcos (solo flujo, sin diámetro)
edge_labels = {(o, d): f"{flujo} l/min" for o, d, flujo, diam in arcos_activos}
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_size=8)

plt.title('Solución Instancia 1 - Arcos Activos y Flujos')
plt.axis('off')
plt.tight_layout()
plt.show()
