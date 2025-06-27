import os
import re
import ast
import matplotlib.pyplot as plt
import numpy as np

# Directorio base de los reportes
DATA_DIR = 'reportes'
SUBDIRS = ['grandes', 'medianas', 'pequeñas']
ORDEN_TAMANO = {'pequeñas': 0, 'medianas': 1, 'grandes': 2}

datos = []

# Recorrer subcarpetas (grandes, medianas, pequeñas)
for subdir in SUBDIRS:
    dir_path = os.path.join(DATA_DIR, subdir)
    for fname in sorted(os.listdir(dir_path)):
        if fname.endswith('.txt'):
            path = os.path.join(dir_path, fname)
            with open(path, 'r', encoding='utf-8') as f:
                meta = None
                tiempo = None
                objetivo = None
                for line in f:
                    if line.strip().startswith('Metadata:'):
                        meta_str = line.strip().replace('Metadata: ', '')
                        try:
                            meta = ast.literal_eval(meta_str)
                        except Exception:
                            meta = None
                    if 'COSTO TOTAL:' in line:
                        match = re.search(r'COSTO TOTAL:\s*\$([0-9]+)\.([0-9]+)', line)
                        if match:
                            objetivo = float(match.group(1) + '.' + match.group(2))
                    if 'Tiempo de resolución:' in line:
                        match = re.search(r'Tiempo de resolución:\s*([0-9.]+)', line)
                        if match:
                            tiempo = float(match.group(1))
                if meta:
                    datos.append({
                        'instancia': fname.replace('.txt',''),
                        'tamaño': meta.get('tamaño',''),
                        'numero': meta.get('numero',''),
                        'suministro_total': float(meta.get('suministro_total',0)),
                        'demanda_total': float(meta.get('demanda_total',0)),
                        'factor_holgura': float(meta.get('factor_holgura',0)),
                        'num_arcos': float(meta.get('num_arcos',0)),
                        'objetivo': objetivo,
                        'tiempo': tiempo
                    })

# --- INYECCIÓN DE DATOS CORREGIDOS MANUALMENTE ---
# Estos datos reflejan la tabla resumen corregida a mano en informe_proyecto.tex
# Si existe un dato con el mismo nombre de instancia, se reemplaza
correcciones = [
    # Pequeñas
    {'instancia': 'reporte_pequeña_1', 'tamaño': 'pequeñas', 'numero': 1, 'suministro_total': 682.82, 'demanda_total': 525.24, 'factor_holgura': 1.30, 'num_arcos': 36, 'objetivo': None, 'tiempo': 60.0},
    {'instancia': 'reporte_pequeña_2', 'tamaño': 'pequeñas', 'numero': 2, 'suministro_total': 849.58, 'demanda_total': 653.52, 'factor_holgura': 1.30, 'num_arcos': 40, 'objetivo': None, 'tiempo': 63.0},
    {'instancia': 'reporte_pequeña_3', 'tamaño': 'pequeñas', 'numero': 3, 'suministro_total': 1199.01, 'demanda_total': 922.32, 'factor_holgura': 1.30, 'num_arcos': 47, 'objetivo': None, 'tiempo': 9.0},
    {'instancia': 'reporte_pequeña_4', 'tamaño': 'pequeñas', 'numero': 4, 'suministro_total': 1076.49, 'demanda_total': 828.07, 'factor_holgura': 1.30, 'num_arcos': 51, 'objetivo': None, 'tiempo': 32.108},
    {'instancia': 'reporte_pequeña_5', 'tamaño': 'pequeñas', 'numero': 5, 'suministro_total': 1456.26, 'demanda_total': 1120.20, 'factor_holgura': 1.30, 'num_arcos': 76, 'objetivo': None, 'tiempo': 78.0},
    # Medianas
    {'instancia': 'reporte_mediana_1', 'tamaño': 'medianas', 'numero': 1, 'suministro_total': 2308.14, 'demanda_total': 1775.49, 'factor_holgura': 1.30, 'num_arcos': 87, 'objetivo': None, 'tiempo': 324.0},
    {'instancia': 'reporte_mediana_2', 'tamaño': 'medianas', 'numero': 2, 'suministro_total': 1062.81, 'demanda_total': 817.54, 'factor_holgura': 1.30, 'num_arcos': 60, 'objetivo': None, 'tiempo': 111.0},
    {'instancia': 'reporte_mediana_3', 'tamaño': 'medianas', 'numero': 3, 'suministro_total': 1607.10, 'demanda_total': 1236.24, 'factor_holgura': 1.30, 'num_arcos': 99, 'objetivo': None, 'tiempo': 447.0},
    {'instancia': 'reporte_mediana_4', 'tamaño': 'medianas', 'numero': 4, 'suministro_total': 1450.89, 'demanda_total': 1116.08, 'factor_holgura': 1.30, 'num_arcos': 88, 'objetivo': None, 'tiempo': 133.0},
    {'instancia': 'reporte_mediana_5', 'tamaño': 'medianas', 'numero': 5, 'suministro_total': 1456.26, 'demanda_total': 1120.20, 'factor_holgura': 1.30, 'num_arcos': 76, 'objetivo': None, 'tiempo': 105.0},
    # Grandes
    {'instancia': 'reporte_grande_1', 'tamaño': 'grandes', 'numero': 1, 'suministro_total': 5095.98, 'demanda_total': 3920.00, 'factor_holgura': 1.30, 'num_arcos': 186, 'objetivo': None, 'tiempo': 507.0},
    {'instancia': 'reporte_grande_2', 'tamaño': 'grandes', 'numero': 2, 'suministro_total': 3134.20, 'demanda_total': 2410.91, 'factor_holgura': 1.30, 'num_arcos': 130, 'objetivo': None, 'tiempo': 333.0},
    {'instancia': 'reporte_grande_3', 'tamaño': 'grandes', 'numero': 3, 'suministro_total': 4441.16, 'demanda_total': 3416.28, 'factor_holgura': 1.30, 'num_arcos': 183, 'objetivo': None, 'tiempo': 1163.0},
    {'instancia': 'reporte_grande_4', 'tamaño': 'grandes', 'numero': 4, 'suministro_total': 5757.96, 'demanda_total': 4429.22, 'factor_holgura': 1.30, 'num_arcos': 193, 'objetivo': None, 'tiempo': 507.0},
    {'instancia': 'reporte_grande_5', 'tamaño': 'grandes', 'numero': 5, 'suministro_total': 5280.20, 'demanda_total': 4061.69, 'factor_holgura': 1.30, 'num_arcos': 167, 'objetivo': None, 'tiempo': 1822.0},
]

# Reemplazar o agregar los datos corregidos, pero mantener también los datos extraídos de los reportes
for corr in correcciones:
    found = False
    for i, d in enumerate(datos):
        if d['instancia'] == corr['instancia']:
            # Fusionar: si el dato corregido es None, mantener el extraído
            for k, v in corr.items():
                if v is not None:
                    datos[i][k] = v
            found = True
            break
    if not found:
        datos.append(corr)

def es_valido(d):
    try:
        return (
            d['tamaño'] in ORDEN_TAMANO and
            str(d['numero']).strip() != '' and
            float(d['suministro_total']) > 0 and
            float(d['demanda_total']) > 0 and
            float(d['num_arcos']) > 0 and
            float(d['factor_holgura']) > 0
        )
    except Exception:
        return False

datos = [d for d in datos if es_valido(d)]
if not datos:
    print('No hay reportes válidos con datos completos para graficar.')
    exit(0)

datos.sort(key=lambda x: (ORDEN_TAMANO[x['tamaño']], int(x['numero'])))

instancias = [d['instancia'] for d in datos]
suministro = [d['suministro_total'] for d in datos]
demanda = [d['demanda_total'] for d in datos]
num_arcos = [d['num_arcos'] for d in datos]
tamaños = [d['tamaño'].capitalize() for d in datos]
objetivos = [d['objetivo'] for d in datos]
tiempos = [d['tiempo'] for d in datos]

# Gráfico Suministro vs Demanda
plt.figure(figsize=(10,6))
plt.bar(instancias, suministro, label='Suministro total', alpha=0.7)
plt.bar(instancias, demanda, label='Demanda total', alpha=0.7)
plt.ylabel('Cantidad')
plt.xlabel('Instancia')
plt.title('Suministro y Demanda por Instancia')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig('suministro_demanda.png')
plt.close()

# Gráfico Número de arcos
plt.figure(figsize=(10,6))
plt.bar(instancias, num_arcos, color='purple')
plt.ylabel('Número de arcos')
plt.xlabel('Instancia')
plt.title('Número de arcos por instancia')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('num_arcos.png')
plt.close()

# Gráfico Suministro/Demanda por tamaño
labels = sorted(set(tamaños), key=lambda x: ORDEN_TAMANO[x.lower()])
medias_suministro = [np.mean([d['suministro_total'] for d in datos if d['tamaño'].capitalize()==t]) for t in labels]
medias_demanda = [np.mean([d['demanda_total'] for d in datos if d['tamaño'].capitalize()==t]) for t in labels]

x = np.arange(len(labels))
width = 0.35
plt.figure(figsize=(8,5))
plt.bar(x-width/2, medias_suministro, width, label='Suministro promedio')
plt.bar(x+width/2, medias_demanda, width, label='Demanda promedio')
plt.ylabel('Cantidad promedio')
plt.xlabel('Tamaño de instancia')
plt.title('Promedio de Suministro y Demanda por Tamaño')
plt.xticks(x, labels)
plt.legend()
plt.tight_layout()
plt.savefig('promedio_suministro_demanda.png')
plt.close()

# Gráfico Función Objetivo por instancia (solo si hay datos válidos)
objetivos_validos = [o for o in objetivos if o is not None]
if len(objetivos_validos) == len(objetivos):
    plt.figure(figsize=(10,6))
    plt.plot(instancias, objetivos, marker='o', color='green')
    plt.ylabel('Costo total (función objetivo)')
    plt.xlabel('Instancia')
    plt.title('Función objetivo (costo total) por instancia')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('funcion_objetivo_por_instancia.png')
    plt.close()
else:
    print('Advertencia: No se pudo graficar función objetivo por instancia (faltan datos en algunos reportes)')

# Gráfico Función Objetivo promedio por tamaño (solo si hay datos válidos)
medias_objetivo = []
for t in labels:
    valores = [d['objetivo'] for d in datos if d['tamaño'].capitalize()==t and d['objetivo'] is not None]
    medias_objetivo.append(np.mean(valores) if valores else np.nan)
if all([not np.isnan(m) for m in medias_objetivo]):
    plt.figure(figsize=(8,5))
    plt.bar(labels, medias_objetivo, color='orange')
    plt.ylabel('Costo total promedio')
    plt.xlabel('Tamaño de instancia')
    plt.title('Función objetivo promedio por tamaño de instancia')
    plt.tight_layout()
    plt.savefig('funcion_objetivo_promedio.png')
    plt.close()
else:
    print('Advertencia: No se pudo graficar función objetivo promedio por tamaño (faltan datos)')

# Gráfico Tiempos de resolución por instancia
plt.figure(figsize=(10,6))
plt.plot(instancias, tiempos, marker='o', color='red')
plt.ylabel('Tiempo de resolución (s)')
plt.xlabel('Instancia')
plt.title('Tiempo de resolución por instancia')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('tiempos_resolucion.png')
plt.close()

# Gráfico Tiempos de resolución promedio por tamaño (corregido para filtrar None)
medias_tiempo = []
for t in labels:
    valores = [d['tiempo'] for d in datos if d['tamaño'].capitalize()==t and d['tiempo'] is not None]
    medias_tiempo.append(np.mean(valores) if valores else np.nan)
plt.figure(figsize=(8,5))
plt.bar(labels, medias_tiempo, color='teal')
plt.ylabel('Tiempo promedio (s)')
plt.xlabel('Tamaño de instancia')
plt.title('Tiempo de resolución promedio por tamaño de instancia')
plt.tight_layout()
plt.savefig('tiempos_resolucion_promedio.png')
plt.close()

print('¡Gráficos generados exitosamente!')

# Al final del script, generar un archivo .tex con las inclusiones de los gráficos generados
with open('graficos_informe.tex', 'w', encoding='utf-8') as f:
    f.write('% Gráficos generados automáticamente\n')
    if os.path.exists('suministro_demanda.png'):
        f.write('\\begin{figure}[H]\n')
        f.write('\\centering\n')
        f.write('\\includegraphics[width=0.8\\textwidth]{suministro_demanda.png}\n')
        f.write('\\caption{Suministro y demanda por instancia}\n')
        f.write('\\end{figure}\n\n')
    if os.path.exists('num_arcos.png'):
        f.write('\\begin{figure}[H]\n')
        f.write('\\centering\n')
        f.write('\\includegraphics[width=0.8\\textwidth]{num_arcos.png}\n')
        f.write('\\caption{Número de arcos por instancia}\n')
        f.write('\\end{figure}\n\n')
    if os.path.exists('promedio_suministro_demanda.png'):
        f.write('\\begin{figure}[H]\n')
        f.write('\\centering\n')
        f.write('\\includegraphics[width=0.7\\textwidth]{promedio_suministro_demanda.png}\n')
        f.write('\\caption{Promedio de suministro y demanda por tamaño de instancia}\n')
        f.write('\\end{figure}\n\n')
    if os.path.exists('tiempos_resolucion.png'):
        f.write('\\begin{figure}[H]\n')
        f.write('\\centering\n')
        f.write('\\includegraphics[width=0.7\\textwidth]{tiempos_resolucion.png}\n')
        f.write('\\caption{Tiempos de resolución por instancia}\n')
        f.write('\\end{figure}\n\n')
    if os.path.exists('tiempos_resolucion_promedio.png'):
        f.write('\\begin{figure}[H]\n')
        f.write('\\centering\n')
        f.write('\\includegraphics[width=0.7\\textwidth]{tiempos_resolucion_promedio.png}\n')
        f.write('\\caption{Tiempos de resolución promedio por tamaño de instancia}\n')
        f.write('\\end{figure}\n\n')
print('Archivo graficos_informe.tex generado para inclusión automática en el informe.')
