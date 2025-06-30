import random
import numpy as np
import os
import json
import subprocess
import time

class GeneradorProblematico:
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

    def generar_instancia_infactible_demanda(self, idx=1):
        """Genera instancia infactible por demanda imposible de satisfacer"""
        nP, nT, nC1, nC2 = 2, 3, 4, 6
        
        # Demandas que exceden capacidad máxima posible
        capacidad_maxima_arco = max(self.diametro_specs[d]['max_flujo'] for d in self.diametros)
        num_arcos_estimado = nP * nT + nT * nC1 + nC1 * nC2
        capacidad_teorica_maxima = capacidad_maxima_arco * num_arcos_estimado
        
        # Demanda 200% mayor que la capacidad teórica máxima
        demanda_objetivo = capacidad_teorica_maxima * 2.0
        d1 = [round(demanda_objetivo / (nC1 + nC2), 2) for _ in range(nC1)]
        d2 = [round(demanda_objetivo / (nC1 + nC2), 2) for _ in range(nC2)]
        
        # Suministro mínimo (para que el problema no sea trivial)
        sup = round(sum(d1 + d2) * 0.1 / nP, 2)
        
        return self._crear_instancia_base(idx, nP, nT, nC1, nC2, d1, d2, sup, "INFACTIBLE_DEMANDA")

    def generar_instancia_cuello_botella(self, idx=1):
        """Genera instancia con cuellos de botella extremos"""
        nP, nT, nC1, nC2 = 4, 1, 6, 10  # Solo 1 nodo intermedio T
        
        # Demandas altas que deben pasar por el único nodo T
        d1 = [round(random.uniform(500, 800), 2) for _ in range(nC1)]
        d2 = [round(random.uniform(600, 900), 2) for _ in range(nC2)]
        
        # Suministro distribuido pero insuficiente para el cuello de botella
        sup = round(sum(d1 + d2) * 0.8 / nP, 2)
        
        return self._crear_instancia_base(idx, nP, nT, nC1, nC2, d1, d2, sup, "CUELLO_BOTELLA")

    def generar_instancia_costos_prohibitivos(self, idx=1):
        """Genera instancia con costos que impiden soluciones viables"""
        nP, nT, nC1, nC2 = 3, 4, 5, 7
        
        # Demandas moderadas
        d1 = [round(random.uniform(80, 150), 2) for _ in range(nC1)]
        d2 = [round(random.uniform(100, 180), 2) for _ in range(nC2)]
        
        # Suministro adecuado
        sup = round(sum(d1 + d2) * 1.1 / nP, 2)
        
        return self._crear_instancia_base(idx, nP, nT, nC1, nC2, d1, d2, sup, "COSTOS_PROHIBITIVOS")

    def generar_instancia_topologia_imposible(self, idx=1):
        """Genera instancia con topología que aísla nodos críticos"""
        nP, nT, nC1, nC2 = 3, 5, 6, 8
        
        # Demandas altas en nodos que serán aislados
        d1 = [round(random.uniform(200, 400), 2) for _ in range(nC1)]
        d2 = [round(random.uniform(300, 500), 2) for _ in range(nC2)]
        
        # Suministro suficiente si hubiera conectividad
        sup = round(sum(d1 + d2) * 1.2 / nP, 2)
        
        return self._crear_instancia_base(idx, nP, nT, nC1, nC2, d1, d2, sup, "TOPOLOGIA_IMPOSIBLE", fragmentar=True)

    def generar_instancia_complejidad_extrema(self, idx=1):
        """Genera instancia extremadamente compleja para el solver"""
        nP, nT, nC1, nC2 = 6, 10, 15, 25  # Problema muy grande
        
        # Patrones de demanda complejos y variables
        d1 = [round(random.uniform(10, 500), 2) for _ in range(nC1)]
        d2 = [round(random.uniform(20, 600), 2) for _ in range(nC2)]
        
        # Suministro en el límite exacto
        sup = round(sum(d1 + d2) * 1.001 / nP, 2)  # Apenas suficiente
        
        return self._crear_instancia_base(idx, nP, nT, nC1, nC2, d1, d2, sup, "COMPLEJIDAD_EXTREMA")

    def generar_instancia_restricciones_conflictivas(self, idx=1):
        """Genera instancia con restricciones que entran en conflicto"""
        nP, nT, nC1, nC2 = 2, 3, 4, 6
        
        # Demandas que requieren capacidades específicas conflictivas
        d1 = [round(random.uniform(800, 1200), 2) for _ in range(nC1)]  # Requieren D5
        d2 = [round(random.uniform(50, 100), 2) for _ in range(nC2)]    # Pueden usar D2
        
        # Suministro ajustado para crear tensión
        sup = round(sum(d1 + d2) * 1.05 / nP, 2)
        
        return self._crear_instancia_base(idx, nP, nT, nC1, nC2, d1, d2, sup, "RESTRICCIONES_CONFLICTIVAS")

    def _crear_instancia_base(self, idx, nP, nT, nC1, nC2, d1, d2, sup, tipo, fragmentar=False):
        """Crea la estructura base de una instancia"""
        # Generar conexiones completas inicialmente
        pt = [(f"P{p}", f"T{t}") for p in range(nP) for t in range(nT)]
        tc1 = [(f"T{t}", f"C1_{c}") for t in range(nT) for c in range(nC1)]
        c1c2 = [(f"C1_{c}", f"C2_{f}") for c in range(nC1) for f in range(nC2)]
        
        # Aplicar fragmentación específica según el tipo de problema
        if fragmentar or tipo == "TOPOLOGIA_IMPOSIBLE":
            # Eliminar conexiones críticas para aislar nodos
            if len(pt) > 2:
                pt = random.sample(pt, max(1, len(pt) // 3))  # Eliminar 2/3 de conexiones P-T
            
            if len(tc1) > 2:
                tc1 = random.sample(tc1, max(1, len(tc1) // 2))  # Eliminar 1/2 de conexiones T-C1
            
            # Aislar completamente algunos nodos C2 de alta demanda
            if nC2 > 3:
                nodos_aislados = random.sample(range(nC2), min(3, nC2 // 2))
                c1c2 = [arc for arc in c1c2 if not any(arc[1] == f'C2_{n}' for n in nodos_aislados)]
                print(f"Nodos C2 aislados: {[f'C2_{n}' for n in nodos_aislados]}")
        
        M = len(pt) + len(tc1) + len(c1c2)
        
        # Generar costos según el tipo de problema
        if tipo == "COSTOS_PROHIBITIVOS":
            # Costos extremadamente altos
            trans = [round(random.uniform(5000, 20000), 2) for _ in range(M)]
        elif tipo == "RESTRICCIONES_CONFLICTIVAS":
            # Costos que favorecen capacidades pequeñas pero necesitamos grandes
            trans = [round(random.uniform(1, 5), 2) for _ in range(M)]  # Muy baratos
        else:
            # Costos normales con variabilidad
            trans = [round(max(0.5, np.random.normal(8, 3)), 2) for _ in range(M)]
        
        def build_dict(conns, offs):
            return {(a, b): trans[i + offs] for i, (a, b) in enumerate(conns)}
        
        c_pt = build_dict(pt, 0)
        c_tc1 = build_dict(tc1, len(pt))
        c_c1c2 = build_dict(c1c2, len(pt) + len(tc1))
        
        nodos = {
            'P': [f"P{i}" for i in range(nP)],
            'T': [f"T{i}" for i in range(nT)],
            'C1': [f"C1_{i}" for i in range(nC1)],
            'C2': [f"C2_{i}" for i in range(nC2)]
        }
        
        demanda_total = sum(d1) + sum(d2)
        suministro_total = sup * nP
        
        return {
            'metadata': {
                'tamaño': self._clasificar_tamaño(M, nP + nT + nC1 + nC2),
                'numero': idx,
                'tipo_problema': tipo,
                'demanda_total': round(demanda_total, 2),
                'suministro_total': round(suministro_total, 2),
                'factor_holgura': round(suministro_total / demanda_total, 2) if demanda_total > 0 else 0,
                'num_arcos': M,
                'nodos_totales': nP + nT + nC1 + nC2,
                'densidad_conexion': round(M / ((nP + nT + nC1 + nC2) ** 2), 4),
                'es_problematico': True,
                'razon_problematico': self._explicar_problema(tipo, demanda_total, suministro_total, M)
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

    def _clasificar_tamaño(self, num_arcos, num_nodos):
        """Clasifica el tamaño del problema"""
        if num_arcos > 200 or num_nodos > 40:
            return 'muy_grande'
        elif num_arcos > 100 or num_nodos > 25:
            return 'grande'
        elif num_arcos > 50 or num_nodos > 15:
            return 'mediana'
        else:
            return 'pequeña'

    def _explicar_problema(self, tipo, demanda_total, suministro_total, num_arcos):
        """Explica por qué la instancia debería ser problemática"""
        explicaciones = {
            'INFACTIBLE_DEMANDA': f'Demanda ({demanda_total:.1f}) excede capacidad física máxima teórica',
            'CUELLO_BOTELLA': f'Topología con cuello de botella extremo, solo 1 nodo intermedio',
            'COSTOS_PROHIBITIVOS': f'Costos de transporte extremadamente altos (>5000)',
            'TOPOLOGIA_IMPOSIBLE': f'Nodos críticos aislados sin conectividad',
            'COMPLEJIDAD_EXTREMA': f'Problema muy grande ({num_arcos} arcos) con margen mínimo',
            'RESTRICCIONES_CONFLICTIVAS': f'Demandas requieren capacidades conflictivas'
        }
        return explicaciones.get(tipo, 'Problema diseñado para ser difícil')

    def validar_numero(self, num):
        """Valida y formatea números para MiniZinc"""
        if isinstance(num, (int, float)):
            if abs(num - round(num)) < 1e-10:  # Es prácticamente un entero
                return str(int(round(num)))
            else:
                return f"{num:.2f}"
        return str(num)

    def guardar_dzn(self, instancia, ruta):
        """Guarda la instancia en formato .dzn para MiniZinc"""
        # Crear mapeo de nodos a índices
        node_idx = {}
        contador = 1
        for grupo in ['P', 'T', 'C1', 'C2']:
            for nodo in instancia['nodos'][grupo]:
                node_idx[nodo] = contador
                contador += 1
        
        # Crear listas de arcos
        arcos = (instancia['conexiones']['pt'] + 
                instancia['conexiones']['tc1'] + 
                instancia['conexiones']['c1c2'])
        
        arc_from = [node_idx[a] for (a, b) in arcos]
        arc_to = [node_idx[b] for (a, b) in arcos]
        
        # Costos de transporte
        trans_costs = (list(instancia['param']['costos']['pt'].values()) + 
                      list(instancia['param']['costos']['tc1'].values()) + 
                      list(instancia['param']['costos']['c1c2'].values()))
        
        N = contador - 1
        
        # Arrays de suministro y demanda
        supply = [0.0] * N
        demand = [0.0] * N
        
        for nodo in instancia['nodos']['P']:
            supply[node_idx[nodo]-1] = instancia['param']['suministro'][nodo]
        
        for nodo, val in instancia['param']['d1'].items():
            demand[node_idx[nodo]-1] = val
        
        for nodo, val in instancia['param']['d2'].items():
            demand[node_idx[nodo]-1] = val
        
        # Capacidades máximas por diámetro
        max_capacity = [self.diametro_specs[d]['max_flujo'] for d in self.diametros]
        
        # Costos de instalación por arco y diámetro
        install_costs = []
        for i in range(len(arcos)):
            tipo = 'tipo_a' if i % 2 == 0 else 'tipo_b'
            install_costs.append([self.costos_instalacion[tipo][d] for d in self.diametros])
        
        # Escribir archivo .dzn
        try:
            with open(ruta, 'w', encoding='utf-8') as f:
                # Comentario de metadata
                f.write(f"% Instancia problemática tipo: {instancia['metadata']['tipo_problema']}\n")
                f.write(f"% Razón: {instancia['metadata']['razon_problematico']}\n")
                f.write(f"% Demanda total: {instancia['metadata']['demanda_total']}\n")
                f.write(f"% Suministro total: {instancia['metadata']['suministro_total']}\n")
                f.write(f"% Factor holgura: {instancia['metadata']['factor_holgura']}\n\n")
                
                # Parámetros básicos
                f.write(f"nP = {len(instancia['nodos']['P'])};\n")
                f.write(f"nT = {len(instancia['nodos']['T'])};\n")
                f.write(f"nC1 = {len(instancia['nodos']['C1'])};\n")
                f.write(f"nC2 = {len(instancia['nodos']['C2'])};\n")
                f.write(f"nA = {len(arcos)};\n")
                f.write(f"nD = {len(self.diametros)};\n\n")
                
                # Arrays de arcos
                f.write("arc_from = [" + ", ".join(str(x) for x in arc_from) + "];\n")
                f.write("arc_to = [" + ", ".join(str(x) for x in arc_to) + "];\n\n")
                
                # Arrays de suministro y demanda
                f.write("supply = [" + ", ".join(self.validar_numero(s) for s in supply) + "];\n")
                f.write("demand = [" + ", ".join(self.validar_numero(d) for d in demand) + "];\n\n")
                
                # Capacidades máximas
                f.write("max_capacity = [" + ", ".join(str(c) for c in max_capacity) + "];\n\n")
                
                # Costos de instalación
                f.write("install_cost = array2d(1..nA, 1..nD, [\n")
                for i, row in enumerate(install_costs):
                    f.write("  " + ", ".join(str(c) for c in row))
                    if i < len(install_costs) - 1:
                        f.write(",\n")
                    else:
                        f.write("\n")
                f.write("]);\n\n")
                
                # Costos de transporte
                f.write("trans_cost = [" + ", ".join(self.validar_numero(c) for c in trans_costs) + "];\n")
                
            print(f"Archivo .dzn creado: {ruta}")
            
        except Exception as e:
            print(f"Error escribiendo archivo .dzn: {e}")
            raise

    def guardar_metadata_json(self, instancia, ruta):
        """Guarda metadata en JSON para análisis"""
        try:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(instancia['metadata'], f, indent=2, ensure_ascii=False)
            print(f"Metadata guardada: {ruta}")
        except Exception as e:
            print(f"Error guardando metadata: {e}")

    def ejecutar_minizinc_con_timeout(self, ruta_dzn, ruta_sol, timeout_segundos=120):
        """Ejecuta MiniZinc con timeout para detectar problemas"""
        comando = [
            'minizinc', 
            '--solver', 'org.gecode.gecode',
            '--output-to-file', ruta_sol,
            '--time-limit', str(timeout_segundos * 1000),  # MiniZinc usa milisegundos
            '--statistics',
            'models/main.mzn',  # Asume que tienes tu modelo en models/main.mzn
            ruta_dzn
        ]
        
        try:
            print(f"Ejecutando MiniZinc con timeout de {timeout_segundos}s...")
            inicio = time.time()
            
            resultado = subprocess.run(comando, 
                                     capture_output=True, 
                                     text=True, 
                                     timeout=timeout_segundos + 10)
            
            tiempo_total = time.time() - inicio
            
            # Analizar resultado
            analisis = {
                'tiempo_ejecutado': round(tiempo_total, 2),
                'codigo_retorno': resultado.returncode,
                'timeout_alcanzado': tiempo_total >= timeout_segundos,
                'es_problematico': False
            }
            
            if resultado.returncode != 0:
                analisis['es_problematico'] = True
                analisis['razon'] = 'Error de ejecución o infactible'
            elif tiempo_total >= timeout_segundos * 0.9:
                analisis['es_problematico'] = True
                analisis['razon'] = 'Timeout o muy lento'
            elif '=====UNSATISFIABLE=====' in resultado.stdout:
                analisis['es_problematico'] = True
                analisis['razon'] = 'Infactible'
            elif '=====UNKNOWN=====' in resultado.stdout:
                analisis['es_problematico'] = True
                analisis['razon'] = 'No pudo resolver'
            
            # Escribir resultado completo
            with open(ruta_sol, 'w', encoding='utf-8') as f:
                f.write(f"=== ANÁLISIS AUTOMÁTICO ===\n")
                f.write(f"Tiempo: {analisis['tiempo_ejecutado']}s\n")
                f.write(f"Problemático: {analisis['es_problematico']}\n")
                if 'razon' in analisis:
                    f.write(f"Razón: {analisis['razon']}\n")
                f.write(f"\n=== SALIDA MINIZINC ===\n")
                f.write(resultado.stdout)
                if resultado.stderr:
                    f.write(f"\n=== ERRORES ===\n")
                    f.write(resultado.stderr)
            
            return analisis
            
        except subprocess.TimeoutExpired:
            analisis = {
                'tiempo_ejecutado': timeout_segundos,
                'timeout_alcanzado': True,
                'es_problematico': True,
                'razon': 'Timeout forzado'
            }
            with open(ruta_sol, 'w', encoding='utf-8') as f:
                f.write("=== TIMEOUT FORZADO ===\n")
                f.write(f"Excedió {timeout_segundos} segundos\n")
            return analisis
            
        except Exception as e:
            analisis = {
                'error': str(e),
                'es_problematico': True,
                'razon': f'Error de ejecución: {e}'
            }
            with open(ruta_sol, 'w', encoding='utf-8') as f:
                f.write(f"=== ERROR ===\n{e}\n")
            return analisis

    def ejecutar_experimento_completo(self, num_instancias_por_tipo=2):
        """Ejecuta experimento completo con diferentes tipos de instancias problemáticas"""
        
        tipos_generadores = [
            ("infactible_demanda", self.generar_instancia_infactible_demanda),
            ("cuello_botella", self.generar_instancia_cuello_botella),
            ("costos_prohibitivos", self.generar_instancia_costos_prohibitivos),
            ("topologia_imposible", self.generar_instancia_topologia_imposible),
            ("complejidad_extrema", self.generar_instancia_complejidad_extrema),
            ("restricciones_conflictivas", self.generar_instancia_restricciones_conflictivas)
        ]
        
        carpeta_dzn = 'instancias/problematicas'
        carpeta_metadata = 'metadata/problematicas'
        carpeta_resultados = 'resultados/problematicas'
        
        for carpeta in [carpeta_dzn, carpeta_metadata, carpeta_resultados]:
            os.makedirs(carpeta, exist_ok=True)
        
        resumen_experimento = []
        
        print(f"{'='*80}")
        print(f"GENERANDO INSTANCIAS PROBLEMÁTICAS PARA MINIZINC")
        print(f"{'='*80}")
        
        for tipo, generador in tipos_generadores:
            print(f"\n{'-'*60}")
            print(f"Tipo: {tipo.upper().replace('_', ' ')}")
            print(f"{'-'*60}")
            
            for i in range(1, num_instancias_por_tipo + 1):
                print(f"\n--- Instancia {tipo}_{i} ---")
                
                try:
                    # Generar instancia
                    instancia = generador(i)
                    
                    # Rutas de archivos
                    archivo_dzn = os.path.join(carpeta_dzn, f'{tipo}_{i}.dzn')
                    archivo_metadata = os.path.join(carpeta_metadata, f'{tipo}_{i}.json')
                    archivo_resultado = os.path.join(carpeta_resultados, f'{tipo}_{i}_resultado.txt')
                    
                    # Guardar archivos
                    self.guardar_dzn(instancia, archivo_dzn)
                    self.guardar_metadata_json(instancia, archivo_metadata)
                    
                    # Probar con MiniZinc
                    analisis = self.ejecutar_minizinc_con_timeout(archivo_dzn, archivo_resultado, 60)
                    
                    # Registrar resultado
                    resultado_completo = {
                        'archivo_dzn': f'{tipo}_{i}.dzn',
                        'tipo': tipo,
                        'metadata': instancia['metadata'],
                        'analisis_minizinc': analisis
                    }
                    
                    resumen_experimento.append(resultado_completo)
                    
                    # Mostrar resumen
                    print(f"✓ Generado: {archivo_dzn}")
                    print(f"  Tamaño: {instancia['metadata']['tamaño']}")
                    print(f"  Arcos: {instancia['metadata']['num_arcos']}")
                    print(f"  Nodos: {instancia['metadata']['nodos_totales']}")
                    print(f"  Problemático: {analisis['es_problematico']}")
                    if 'razon' in analisis:
                        print(f"  Razón: {analisis['razon']}")
                    print(f"  Tiempo: {analisis.get('tiempo_ejecutado', 'N/A')}s")
                    
                except Exception as e:
                    print(f"✗ Error procesando {tipo}_{i}: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Guardar resumen final
        archivo_resumen = os.path.join(carpeta_resultados, 'resumen_experimento.json')
        with open(archivo_resumen, 'w', encoding='utf-8') as f:
            json.dump(resumen_experimento, f, indent=2, ensure_ascii=False)
        
        # Estadísticas finales
        total = len(resumen_experimento)
        problematicos = sum(1 for r in resumen_experimento if r['analisis_minizinc']['es_problematico'])
        
        print(f"\n{'='*80}")
        print(f"RESUMEN FINAL")
        print(f"{'='*80}")
        print(f"Total instancias: {total}")
        print(f"Problemáticas: {problematicos}")
        print(f"Éxito: {problematicos/total*100:.1f}%")
        print(f"\nArchivos generados:")
        print(f"  .dzn: {carpeta_dzn}")
        print(f"  metadata: {carpeta_metadata}")
        print(f"  resultados: {carpeta_resultados}")
        print(f"\nPara usar en MiniZinc IDE: abrir archivos .dzn desde {carpeta_dzn}")

if __name__ == '__main__':
    # Configurar semillas
    random.seed(42)
    np.random.seed(42)
    
    generador = GeneradorProblematico()
    
    # Ejecutar experimento
    generador.ejecutar_experimento_completo(num_instancias_por_tipo=3)