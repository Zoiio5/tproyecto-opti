import random
import numpy as np
import os
import subprocess

class GeneradorPenaliza:
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

    def generar_instancia_penaliza(self, idx=1):
        nP, nT, nC1, nC2 = 2, 5, 5, 8
        d1 = [random.uniform(60, 80) for _ in range(nC1)]
        d2 = [random.uniform(60, 80) for _ in range(nC2)]
        demanda_total = sum(d1) + sum(d2)
        sup = round((demanda_total * 0.8) / nP, 2)
        pt = [(f"P{p}", f"T{t}") for p in range(nP) for t in range(nT)]
        tc1 = [(f"T{t}", f"C1_{c}") for t in range(nT) for c in range(nC1)]
        c1c2 = [(f"C1_{c}", f"C2_{f}") for c in range(nC1) for f in range(nC2)]
        M = len(pt) + len(tc1) + len(c1c2)
        trans = [round(max(1.0, np.random.normal(6, 1.5)), 2) for _ in range(M)]
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
            'metadata': {
                'tamaño': 'pequeña',
                'numero': idx,
                'grupo': 5,
                'demanda_total': round(demanda_total, 2),
                'suministro_total': round(sup * nP, 2),
                'factor_holgura': round((sup * nP) / demanda_total, 2),
                'num_arcos': M
            },
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
        node_idx = {}
        contador = 1
        for grupo in ['P', 'T', 'C1', 'C2']:
            for nodo in instancia['nodos'][grupo]:
                node_idx[nodo] = contador
                contador += 1
        arcos = instancia['conexiones']['pt'] + instancia['conexiones']['tc1'] + instancia['conexiones']['c1c2']
        arc_from = [node_idx[a] for (a,b) in arcos]
        arc_to   = [node_idx[b] for (a,b) in arcos]
        trans_costs = list(instancia['param']['costos']['pt'].values()) + \
                      list(instancia['param']['costos']['tc1'].values()) + \
                      list(instancia['param']['costos']['c1c2'].values())
        N = contador - 1
        supply = [0.0] * N
        for nodo in instancia['nodos']['P']:
            supply[node_idx[nodo]-1] = instancia['param']['suministro'][nodo]
        demand = [0.0] * N
        for nodo,val in instancia['param']['d1'].items():
            demand[node_idx[nodo]-1] = val
        for nodo,val in instancia['param']['d2'].items():
            demand[node_idx[nodo]-1] = val
        max_capacity = [self.diametro_specs[d]['max_flujo'] for d in self.diametros]
        install_costs = []
        for i in range(len(arcos)):
            tipo = 'tipo_a' if i % 2 == 0 else 'tipo_b'
            install_costs.append([self.costos_instalacion[tipo][d] for d in self.diametros])
        with open(ruta, 'w') as f:
            f.write(f"nP = {len(instancia['nodos']['P'])};\n")
            f.write(f"nT = {len(instancia['nodos']['T'])};\n")
            f.write(f"nC1 = {len(instancia['nodos']['C1'])};\n")
            f.write(f"nC2 = {len(instancia['nodos']['C2'])};\n")
            f.write(f"nA = {len(arcos)};\n")
            f.write(f"nD = {len(self.diametros)};\n\n")
            f.write("arc_from = [" + ", ".join(map(str, arc_from)) + "];\n")
            f.write("arc_to = [" + ", ".join(map(str, arc_to)) + "];\n\n")
            f.write("supply = [" + ", ".join(f"{s:.2f}" for s in supply) + "];\n")
            f.write("demand = [" + ", ".join(f"{d:.2f}" for d in demand) + "];\n\n")
            f.write("max_capacity = [" + ", ".join(f"{c}" for c in max_capacity) + "];\n\n")
            f.write("install_cost = array2d(1..nA, 1..nD, [\n")
            for i, row in enumerate(install_costs):
                f.write("  " + ", ".join(f"{c}" for c in row))
                if i < len(install_costs) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")
            f.write("]);\n\n")
            f.write("trans_cost = [" + ", ".join(f"{c:.2f}" for c in trans_costs) + "];\n")
            # No escribir nada después de la última instrucción para evitar errores de sintaxis

    def generar_reporte_instancia(self, instancia, ruta_reporte):
        with open(ruta_reporte, 'w') as f:
            f.write("=== REPORTE DE INSTANCIA PENALIZA ===\n\n")
            f.write(f"Metadata: {instancia['metadata']}\n\n")
            f.write("BALANCE OFERTA-DEMANDA:\n")
            supply_total = sum(instancia['param']['suministro'].values())
            demand_total = sum(instancia['param']['d1'].values()) + sum(instancia['param']['d2'].values())
            f.write(f"  Suministro total: {supply_total:.2f}\n")
            f.write(f"  Demanda total: {demand_total:.2f}\n")
            f.write(f"  Factor de holgura: {supply_total/demand_total:.2f}\n\n")
            f.write("CONECTIVIDAD:\n")
            f.write(f"  Plantas -> Tanques: {len(instancia['conexiones']['pt'])} conexiones\n")
            f.write(f"  Tanques -> Transbordo: {len(instancia['conexiones']['tc1'])} conexiones\n")
            f.write(f"  Transbordo -> Finales: {len(instancia['conexiones']['c1c2'])} conexiones\n\n")

if __name__=='__main__':
    random.seed(123)
    np.random.seed(123)
    gen = GeneradorPenaliza()
    n_inst = 10
    carpeta = 'instancias/penalizacion'
    carpeta_reportes = 'reportes/penalizacion'
    os.makedirs(carpeta, exist_ok=True)
    os.makedirs(carpeta_reportes, exist_ok=True)
    for i in range(1, n_inst+1):
        inst = gen.generar_instancia_penaliza(i)
        ruta_dzn = os.path.join(carpeta, f'inst_penaliza_{i}.dzn')
        gen.guardar_dzn(inst, ruta_dzn)
        salida_sol = os.path.join(carpeta_reportes, f'sol_penaliza_{i}.txt')
        comando = [
            'minizinc', '--solver', 'org.gecode.gecode', '--output-to-file', salida_sol,
            'models/main.mzn', ruta_dzn
        ]
        try:
            subprocess.run(comando, check=True)
        except Exception as e:
            with open(salida_sol, 'w') as f:
                f.write(f'Error ejecutando MiniZinc: {e}\n')
        print(f'Instancia penaliza generada: {ruta_dzn}\nReporte solución: {salida_sol}')
