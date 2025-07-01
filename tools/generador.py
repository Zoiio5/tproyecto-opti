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
            'pequeñas':    {'plantas': (2, 3), 'tanques': (5, 8), 'transbordo': (5, 8), 'finales': (8, 15)},
            'medianas':    {'plantas': (3, 5), 'tanques': (8, 15), 'transbordo': (8, 15), 'finales': (15, 30)},
            'grandes':     {'plantas': (4, 6), 'tanques': (15, 30), 'transbordo': (20, 35), 'finales': (30, 60)}
        }

    def generar_demandas_balanceadas(self, num, factor_demanda=0.7):
        """Genera demandas más conservadoras para garantizar satisfacibilidad"""
        base_demand = random.uniform(30, 80)  
        demands = []
        for _ in range(num):
            variation = random.uniform(0.8, 1.2)
            demand = round(base_demand * variation * factor_demanda, 2)
            demands.append(max(20, demand))  
        return demands

    def generar_costos_transporte(self, m):
        """Genera costos de transporte más razonables"""
        return [round(max(1.0, np.random.normal(8, 2)), 2) for _ in range(m)]

    def generar_topologia_conectada(self, nP, nT, nC1, nC2):
        """Genera una topología que garantiza conectividad completa"""
        pt = []

        for p in range(nP):
            pt.append((f"P{p}", f"T{random.randint(0, nT-1)}"))
        
 
        for t in range(nT):
            if not any(conn[1] == f"T{t}" for conn in pt):
                pt.append((f"P{random.randint(0, nP-1)}", f"T{t}"))
        
        tc1 = []

        for t in range(nT):
            tc1.append((f"T{t}", f"C1_{random.randint(0, nC1-1)}"))
        

        for c in range(nC1):
            if not any(conn[1] == f"C1_{c}" for conn in tc1):
                tc1.append((f"T{random.randint(0, nT-1)}", f"C1_{c}"))
        
        c1c2 = []

        for c in range(nC1):
            c1c2.append((f"C1_{c}", f"C2_{random.randint(0, nC2-1)}"))
        

        for f in range(nC2):
            if not any(conn[1] == f"C2_{f}" for conn in c1c2):
                c1c2.append((f"C1_{random.randint(0, nC1-1)}", f"C2_{f}"))

        return pt, tc1, c1c2

    def calcular_suministro_adecuado(self, d1, d2, nP, factor_holgura=1.3):
        """Calcula suministro con suficiente holgura para satisfacibilidad"""
        demanda_total = sum(d1) + sum(d2)
        suministro_por_planta = (demanda_total * factor_holgura) / nP
        return round(suministro_por_planta, 2)

    def validar_capacidades_flujo(self, pt, tc1, c1c2, demanda_total):
        """Verifica que las capacidades de flujo sean suficientes"""
        total_arcos = len(pt) + len(tc1) + len(c1c2)
        
        flujo_promedio = demanda_total / max(1, total_arcos * 0.7) 

        if flujo_promedio > self.diametro_specs['D3']['max_flujo']:
            print(f"Advertencia: Flujo promedio ({flujo_promedio:.2f}) podría exceder capacidades")
        
        return True

    def generar_instancia(self, tam, idx):
        r = self.rangos_instancias[tam]
        nP, nT, nC1, nC2 = (random.randint(*r[k]) for k in ['plantas', 'tanques', 'transbordo', 'finales'])
        
        factor_demanda = {'pequeñas': 0.6, 'medianas': 0.7, 'grandes': 0.8}[tam]
        d1 = self.generar_demandas_balanceadas(nC1, factor_demanda)
        d2 = self.generar_demandas_balanceadas(nC2, factor_demanda)
        
        
        pt, tc1, c1c2 = self.generar_topologia_conectada(nP, nT, nC1, nC2)
        

        demanda_total = sum(d1) + sum(d2)
        self.validar_capacidades_flujo(pt, tc1, c1c2, demanda_total)
        
        M = len(pt) + len(tc1) + len(c1c2)
        trans = self.generar_costos_transporte(M)
        
        
        sup = self.calcular_suministro_adecuado(d1, d2, nP)

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
                'tamaño': tam, 
                'numero': idx, 
                'grupo': 5,
                'demanda_total': round(demanda_total, 2),
                'suministro_total': round(sup * nP, 2),
                'factor_holgura': round((sup * nP) / demanda_total, 2),
                'num_arcos': M,
                'conectividad': {
                    'plantas_tanques': len(pt),
                    'tanques_transbordo': len(tc1),
                    'transbordo_finales': len(c1c2)
                }
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
        """
        Genera un archivo .dzn compatible con el modelo MiniZinc.
        Incluye parámetros adicionales para máximas capacidades.
        """

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

            f.write("trans_cost = [" + ", ".join(f"{c:.2f}" for c in trans_costs) + "];\n\n")


            f.write(f"% Metadata: {instancia['metadata']}\n")
            f.write(f"% Total supply: {sum(supply):.2f}\n")
            f.write(f"% Total demand: {sum(demand):.2f}\n")
            f.write(f"% Balance factor: {sum(supply)/max(sum(demand),1):.2f}\n")

    def generar_reporte_instancia(self, instancia, ruta_reporte):
        """Genera un reporte detallado de la instancia para análisis"""
        with open(ruta_reporte, 'w') as f:
            f.write("=== REPORTE DE INSTANCIA ===\n\n")
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
    random.seed(42)
    np.random.seed(42)
    gen = GeneradorInstanciasGrupo5()
    
    for tam in ['pequeñas','medianas','grandes']:
        carpeta = f'instancias/{tam}'
        carpeta_reportes = f'reportes/{tam}'
        os.makedirs(carpeta, exist_ok=True)
        os.makedirs(carpeta_reportes, exist_ok=True)
        
        print(f"\n=== Generando instancias {tam} ===")
        for i in range(1,6):
            inst = gen.generar_instancia(tam,i)
            
            ruta_dzn = os.path.join(carpeta, f"inst_{tam[:-1]}_{i}.dzn")
            gen.guardar_dzn(inst, ruta_dzn)
            

            ruta_reporte = os.path.join(carpeta_reportes, f"reporte_{tam[:-1]}_{i}.txt")
            gen.generar_reporte_instancia(inst, ruta_reporte)
            
            metadata = inst['metadata']
            print(f"  Instancia {i}: Factor holgura = {metadata['factor_holgura']:.2f}, "
                  f"Arcos = {metadata['num_arcos']}, "
                  f"Demanda = {metadata['demanda_total']:.2f}")
            print(f"  Guardado DZN: {ruta_dzn}")
            print(f"  Reporte: {ruta_reporte}")
    
    print(f"\n¡Generación completada! Todas las instancias tienen factores de holgura >= 1.3 para mejor satisfacibilidad.")
