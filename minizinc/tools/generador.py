import os
import random
import numpy as np

# -------------------------------
# 1. Definición de parámetros fijos para Grupo 5
# -------------------------------

# Diámetros (mm) y sus capacidades (l/min) para Grupo 5: D2, D3, D5
DIAMETERS = [75, 100, 150]
CAPACITIES = {75: 795, 100: 1414, 150: 3181}

# Costos de instalación tipo a y tipo b según tabla del proyecto
COSTS_A = {75: 20, 100: 24, 150: 32}
COSTS_B = {75: 50, 100: 62, 150: 78}

print("=== GENERADOR DE INSTANCIAS - GRUPO 5 ===")
print(f"Diámetros disponibles: {DIAMETERS} mm")
print(f"Capacidades: {[CAPACITIES[d] for d in DIAMETERS]} l/min")
print(f"Costos tipo a: {[COSTS_A[d] for d in DIAMETERS]}")
print(f"Costos tipo b: {[COSTS_B[d] for d in DIAMETERS]}")
print("-" * 50)


# -------------------------------
# 2. Función para generar una sola instancia
# -------------------------------
def generate_instance(nP, nT, nC1, nC2, seed=None):
    """
    Genera una instancia de la red de tuberías para el Grupo 5:
    - nP: número de plantas (P)
    - nT: número de tanques (T)
    - nC1: número de nodos de transbordo (C1)
    - nC2: número de nodos finales (C2)
    - seed: semilla para reproducibilidad (opcional)
    
    Devuelve un diccionario con todos los datos necesarios para MiniZinc.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # 2.1. Crear índices de nodos en MiniZinc (1-based)
    P_idxs  = list(range(1, nP+1))
    T_idxs  = list(range(nP+1, nP+nT+1))
    C1_idxs = list(range(nP+nT+1, nP+nT+nC1+1))
    C2_idxs = list(range(nP+nT+nC1+1, nP+nT+nC1+nC2+1))
    
    total_nodes = nP + nT + nC1 + nC2
    
    # 2.2. Generar demanda: 0 para P y T, U(40,100) para C1 y C2
    demand = [0] * total_nodes
    for idx in C1_idxs + C2_idxs:
        demand[idx-1] = random.randint(40, 100)
    
    total_demand = sum(demand)
    
    # 2.3. Construir lista de arcos (i,j) entre columnas adyacentes
    arcs = []
    
    # P -> T (plantas a tanques)
    for i in P_idxs:
        for j in T_idxs:
            arcs.append((i, j))
    
    # T -> C1 (tanques a nodos de transbordo)
    for i in T_idxs:
        for j in C1_idxs:
            arcs.append((i, j))
    
    # C1 -> C2 (nodos transbordo a nodos finales)
    for i in C1_idxs:
        for j in C2_idxs:
            arcs.append((i, j))
    
    nA = len(arcs)
    
    # 2.4. Generar costos de transporte c_{ij} ∼ N(8,2), truncado a ≥0
    trans_cost = []
    for _ in range(nA):
        val = np.random.normal(8.0, 2.0)
        trans_cost.append(round(max(val, 0.1), 2))  # Mínimo 0.1 para evitar ceros
    
    # 2.5. Generar costos de instalación aleatorios (tipo a o b)
    install_cost = [[0]*len(DIAMETERS) for _ in range(nA)]
    cost_type_count = {"a": 0, "b": 0}
    
    for a in range(nA):
        for di, d in enumerate(DIAMETERS):
            if random.random() < 0.5:
                install_cost[a][di] = COSTS_A[d]
                cost_type_count["a"] += 1
            else:
                install_cost[a][di] = COSTS_B[d]
                cost_type_count["b"] += 1
    
    # 2.6. Información de la instancia generada
    instance_info = {
        "nP": nP, "nT": nT, "nC1": nC1, "nC2": nC2,
        "N": total_nodes, "nA": nA,
        "arcs": arcs, "demand": demand,
        "trans_cost": trans_cost, "install_cost": install_cost,
        "total_demand": total_demand,
        "cost_distribution": cost_type_count,
        "seed": seed
    }
    
    return instance_info


# -------------------------------
# 3. Función para convertir a formato DZN
# -------------------------------
def instance_to_dzn(inst, output_path):
    """
    Convierte la instancia a formato .dzn para MiniZinc.
    """
    nP, nT, nC1, nC2 = inst["nP"], inst["nT"], inst["nC1"], inst["nC2"]
    N, nA = inst["N"], inst["nA"]
    arcs = inst["arcs"]
    demand = inst["demand"]
    trans_cost = inst["trans_cost"]
    install_cost = inst["install_cost"]
    
    # Asegura que la carpeta de destino exista
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Construir listas arc_from y arc_to
    arc_from = [a[0] for a in arcs]
    arc_to   = [a[1] for a in arcs]
    
    # Formatear listas para MiniZinc
    def fmt_list(lst):
        return "[" + ", ".join(str(x) for x in lst) + "]"
    
    # install_cost como array2d(1..nA, 1..nD)
    flat_install = []
    for a in range(nA):
        for d_idx in range(len(DIAMETERS)):
            flat_install.append(str(install_cost[a][d_idx]))
    install_str = "[" + ", ".join(flat_install) + "]"
    
    # Escribir archivo .dzn con comentarios descriptivos
    with open(output_path, "w", encoding='utf-8') as f:
        f.write("% Instancia generada para Grupo 5\n")
        f.write(f"% Diámetros: {DIAMETERS} mm\n")
        f.write(f"% Capacidades: {[CAPACITIES[d] for d in DIAMETERS]} l/min\n")
        f.write(f"% Demanda total: {inst['total_demand']} l/min\n")
        f.write(f"% Costos tipo a: {inst['cost_distribution']['a']}, tipo b: {inst['cost_distribution']['b']}\n")
        if inst['seed']:
            f.write(f"% Semilla: {inst['seed']}\n")
        f.write("\n")
        
        # Parámetros de tamaño
        f.write(f"nP = {nP};\n")
        f.write(f"nT = {nT};\n")
        f.write(f"nC1 = {nC1};\n")
        f.write(f"nC2 = {nC2};\n")
        f.write(f"N = {N};\n\n")
        
        # Arcos
        f.write(f"nA = {nA};\n")
        f.write(f"arc_from = {fmt_list(arc_from)};\n")
        f.write(f"arc_to   = {fmt_list(arc_to)};\n\n")
        
        # Demandas
        f.write(f"demand = {fmt_list(demand)};\n\n")
        
        # Costos
        f.write(f"install_cost = array2d(1..{nA}, 1..{len(DIAMETERS)}, {install_str});\n")
        f.write(f"trans_cost   = {fmt_list(trans_cost)};\n")


# -------------------------------
# 4. Generador masivo con estadísticas
# -------------------------------
def generate_bulk_cases(out_dir="../data", n_pequenas=5, n_medianas=5, n_grandes=5):
    """
    Genera instancias según los rangos especificados en el proyecto:
    • Pequeñas: nP∈[1,2], nT∈[5,10], nC1∈[5,10], nC2∈[10,20]
    • Medianas: nP∈[3,4], nT∈[10,20], nC1∈[10,20], nC2∈[20,50]
    • Grandes: nP∈[5,7], nT∈[20,50], nC1∈[25,50], nC2∈[50,100]
    """
    os.makedirs(out_dir, exist_ok=True)
    
    def rand_range(a, b):
        return random.randint(a, b)
    
    estadisticas = {
        "pequenas": [], "medianas": [], "grandes": []
    }
    
    # 4.1 Instancias Pequeñas
    print(f"\nGenerando {n_pequenas} instancias PEQUEÑAS...")
    for k in range(1, n_pequenas + 1):
        nP  = rand_range(1, 2)
        nT  = rand_range(5, 10)
        nC1 = rand_range(5, 10)
        nC2 = rand_range(10, 20)
        seed = random.randint(1, 10**6)
        
        inst = generate_instance(nP, nT, nC1, nC2, seed=seed)
        
        nombre = f"pequena_{k:02d}.dzn"
        ruta = os.path.join(out_dir, nombre)
        instance_to_dzn(inst, ruta)
        
        estadisticas["pequenas"].append({
            "archivo": nombre,
            "nodos": inst["N"],
            "arcos": inst["nA"],
            "demanda_total": inst["total_demand"]
        })
        
        print(f"  ✓ {nombre}: {inst['N']} nodos, {inst['nA']} arcos, demanda={inst['total_demand']}")
    
    # 4.2 Instancias Medianas
    print(f"\nGenerando {n_medianas} instancias MEDIANAS...")
    for k in range(1, n_medianas + 1):
        nP  = rand_range(3, 4)
        nT  = rand_range(10, 20)
        nC1 = rand_range(10, 20)
        nC2 = rand_range(20, 50)
        seed = random.randint(1, 10**6)
        
        inst = generate_instance(nP, nT, nC1, nC2, seed=seed)
        
        nombre = f"mediana_{k:02d}.dzn"
        ruta = os.path.join(out_dir, nombre)
        instance_to_dzn(inst, ruta)
        
        estadisticas["medianas"].append({
            "archivo": nombre,
            "nodos": inst["N"],
            "arcos": inst["nA"],
            "demanda_total": inst["total_demand"]
        })
        
        print(f"  ✓ {nombre}: {inst['N']} nodos, {inst['nA']} arcos, demanda={inst['total_demand']}")
    
    # 4.3 Instancias Grandes
    print(f"\nGenerando {n_grandes} instancias GRANDES...")
    for k in range(1, n_grandes + 1):
        nP  = rand_range(5, 7)
        nT  = rand_range(20, 50)
        nC1 = rand_range(25, 50)
        nC2 = rand_range(50, 100)
        seed = random.randint(1, 10**6)
        
        inst = generate_instance(nP, nT, nC1, nC2, seed=seed)
        
        nombre = f"grande_{k:02d}.dzn"
        ruta = os.path.join(out_dir, nombre)
        instance_to_dzn(inst, ruta)
        
        estadisticas["grandes"].append({
            "archivo": nombre,
            "nodos": inst["N"],
            "arcos": inst["nA"],
            "demanda_total": inst["total_demand"]
        })
        
        print(f"  ✓ {nombre}: {inst['N']} nodos, {inst['nA']} arcos, demanda={inst['total_demand']}")
    
    # 4.4 Resumen estadístico
    print(f"\n" + "="*60)
    print(f"RESUMEN DE GENERACIÓN - GRUPO 5")
    print(f"="*60)
    print(f"Directorio: {out_dir}/")
    print(f"Total archivos: {n_pequenas + n_medianas + n_grandes}")
    
    for categoria, datos in estadisticas.items():
        if datos:
            nodos_promedio = sum(d["nodos"] for d in datos) / len(datos)
            arcos_promedio = sum(d["arcos"] for d in datos) / len(datos)
            demanda_promedio = sum(d["demanda_total"] for d in datos) / len(datos)
            
            print(f"\n{categoria.upper()}:")
            print(f"  - Cantidad: {len(datos)}")
            print(f"  - Nodos promedio: {nodos_promedio:.1f}")
            print(f"  - Arcos promedio: {arcos_promedio:.1f}")
            print(f"  - Demanda promedio: {demanda_promedio:.1f} l/min")


# -------------------------------
# 5. Función para generar instancia de prueba simple
# -------------------------------
def generate_test_instance(output_path="../minizinc/data/test_pequena.dzn"):
    """
    Genera una instancia de prueba pequeña para verificar el modelo.
    """
    print(f"\nGenerando instancia de prueba: {output_path}")
    
    # Instancia muy pequeña: 1 planta, 2 tanques, 2 transbordo, 3 finales
    inst = generate_instance(nP=1, nT=2, nC1=2, nC2=3, seed=12345)
    instance_to_dzn(inst, output_path)
    
    print(f"✓ Instancia de prueba generada:")
    print(f"  - Nodos: {inst['N']} (1P + 2T + 2C1 + 3C2)")
    print(f"  - Arcos: {inst['nA']}")
    print(f"  - Demanda total: {inst['total_demand']} l/min")
    print(f"  - Archivo: {output_path}")


# -------------------------------
# 6. Ejecución principal
# -------------------------------
if __name__ == "__main__":
    # Generar instancia de prueba pequeña
    generate_test_instance()
    
    # Generar conjunto completo de instancias
    generate_bulk_cases(
        out_dir="datos_dzn_grupo5",
        n_pequenas=5,    # Según especificación del proyecto
        n_medianas=5,
        n_grandes=5
    )
    print(f"   Usar con el modelo MiniZinc proporcionado.")
    print(f"   Comando ejemplo: minizinc modelo_grupo5.mzn datos_dzn_grupo5/pequena_01.dzn")