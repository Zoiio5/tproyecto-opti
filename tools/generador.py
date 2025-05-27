import random
import numpy as np
import os
import json

class GeneradorInstanciasGrupo5:
    def __init__(self):
        self.diametros = ['D2', 'D3', 'D5']
        self.diametro_specs = {
            'D2': {'nominal_mm': 75, 'max_flujo': 795},
            'D3': {'nominal_mm': 100, 'max_flujo': 1414},
            'D5': {'nominal_mm': 150, 'max_flujo': 3181}
        }
        self.costos_instalacion = {
            'tipo_a': {'D2': 20, 'D3': 24, 'D5': 32},
            'tipo_b': {'D2': 50, 'D3': 62, 'D5': 78}
        }
        self.rangos_instancias = {
            'pequeñas':    {'plantas': (1, 2), 'tanques': (5, 10), 'transbordo': (5, 10), 'finales': (10, 20)},
            'medianas':    {'plantas': (3, 4), 'tanques': (10, 20), 'transbordo': (10, 20), 'finales': (20, 50)},
            'grandes':     {'plantas': (5, 7), 'tanques': (20, 50), 'transbordo': (25, 50), 'finales': (50, 100)}
        }

    def generar_demandas(self, num):
        return [round(random.uniform(40, 100), 2) for _ in range(num)]

    def generar_costos_transporte(self, m):
        return [round(max(0.1, np.random.normal(8, 2)), 2) for _ in range(m)]

    def generar_topologia(self, nP, nT, nC1, nC2):
        pt = [(f"P{p}", f"T{t}") for p in range(nP) for t in random.sample(range(nT), random.randint(1, min(3, nT)))]
        tc1 = [(f"T{t}", f"C1_{c}") for t in range(nT) for c in random.sample(range(nC1), random.randint(1, min(4, nC1)))]
        c1c2 = [(f"C1_{c}", f"C2_{f}") for f in range(nC2) for c in random.sample(range(nC1), random.randint(1, min(3, nC1)))]
        return pt, tc1, c1c2

    def generar_instancia(self, tam, idx):
        r = self.rangos_instancias[tam]
        nP, nT, nC1, nC2 = (random.randint(*r[k]) for k in ['plantas', 'tanques', 'transbordo', 'finales'])
        pt, tc1, c1c2 = self.generar_topologia(nP, nT, nC1, nC2)
        M = len(pt) + len(tc1) + len(c1c2)
        d1, d2 = self.generar_demandas(nC1), self.generar_demandas(nC2)
        trans = self.generar_costos_transporte(M)
        total = sum(d1) + sum(d2)
        sup = (total * 1.1) / nP

        def build_dict(conns, offs):
            return {f"{a}->{b}": trans[i + offs] for i, (a, b) in enumerate(conns)}

        c_pt = build_dict(pt, 0)
        c_tc1 = build_dict(tc1, len(pt))
        c_c1c2 = build_dict(c1c2, len(pt) + len(tc1))

        nodos = {
            'P': [f"P{i}" for i in range(nP)],
            'T': [f"T{i}" for i in range(nT)],
            'C1': [f"C1_{i}" for i in range(nC1)],
            'C2': [f"C2_{i}" for i in range(nC2)]
        }

        inst = {
            'metadata': {'tamaño': tam, 'numero': idx, 'grupo': 5},
            'nodos': nodos,
            'conexiones': {'pt': pt, 'tc1': tc1, 'c1c2': c1c2},
            'param': {
                'suministro': {f"P{i}": sup for i in range(nP)},
                'd1': {n: d for n, d in zip(nodos['C1'], d1)},
                'd2': {n: d for n, d in zip(nodos['C2'], d2)},
                'costos': {'pt': c_pt, 'tc1': c_tc1, 'c1c2': c_c1c2}
            }
        }
        return inst

    def guardar_dzn(self, instancia, ruta):
        """
        Genera un archivo .dzn compatible con el modelo MiniZinc.
        """
        # Indices de nodos
        node_idx = {}
        contador = 1
        for grupo in ['P', 'T', 'C1', 'C2']:
            for nodo in instancia['nodos'][grupo]:
                node_idx[nodo] = contador
                contador += 1

        # Arcos y costos de transporte
        arcos = instancia['conexiones']['pt'] + instancia['conexiones']['tc1'] + instancia['conexiones']['c1c2']
        arc_from = [node_idx[a] for (a,b) in arcos]
        arc_to   = [node_idx[b] for (a,b) in arcos]
        trans_costs = list(instancia['param']['costos']['pt'].values()) + \
                      list(instancia['param']['costos']['tc1'].values()) + \
                      list(instancia['param']['costos']['c1c2'].values())

        # Demandas: plantas y tanques = 0, C1 y C2 según inst['param']
        N = contador - 1
        demand = [0.0] * N
        for nodo,val in instancia['param']['d1'].items():
            demand[node_idx[nodo]-1] = val
        for nodo,val in instancia['param']['d2'].items():
            demand[node_idx[nodo]-1] = val

        # Costos de instalación: alternar tipo a/b para fila de cada arco
        install_costs = []
        for i in range(len(arcos)):
            tipo = 'tipo_a' if i % 2 == 0 else 'tipo_b'
            install_costs.append([ self.costos_instalacion[tipo][d] for d in self.diametros ])

        # Escritura del archivo
        with open(ruta, 'w') as f:
            # Parámetros de tamaño
            f.write(f"nP = {len(instancia['nodos']['P'])};")
            f.write(f"nT = {len(instancia['nodos']['T'])};")
            f.write(f"nC1 = {len(instancia['nodos']['C1'])};")
            f.write(f"nC2 = {len(instancia['nodos']['C2'])};")
            f.write(f"nA = {len(arcos)};")

            # Arcos
            f.write("arc_from = [ " + ", ".join(map(str, arc_from)) + " ];")
            f.write("arc_to   = [ " + ", ".join(map(str, arc_to)) + " ];")

            # Demandas
            f.write("demand = [ " + ", ".join(f"{d:.2f}" for d in demand) + " ];")

            # Install cost
            f.write("install_cost = array2d(1..nA,1..3,[")
            for row in install_costs:
                f.write("  " + ", ".join(f"{c:.2f}" for c in row) + ",")
            f.write("]);")

            # Transporte
            f.write("trans_cost = [ " + ", ".join(f"{c:.2f}" for c in trans_costs) + " ];")

# Generar todas las instancias .dzn
if __name__=='__main__':
    random.seed(42); np.random.seed(42)
    gen = GeneradorInstanciasGrupo5()
    for tam in ['pequeñas','medianas','grandes']:
        carpeta = f'instancias/{tam}'
        os.makedirs(carpeta, exist_ok=True)
        for i in range(1,6):
            inst = gen.generar_instancia(tam,i)
            ruta = os.path.join(carpeta,f"inst_{tam[:-1]}_{i}.dzn")
            gen.guardar_dzn(inst,ruta)
            print(f"Guardado: {ruta}")