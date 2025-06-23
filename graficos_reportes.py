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
