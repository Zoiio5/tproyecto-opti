# Documentación del Proyecto

Este documento describe la estructura y el funcionamiento del proyecto, excluyendo las carpetas `minizinc/` y `minizinc-project/`.

## Estructura del Workspace

- **data/**
  - Contiene instancias de datos organizadas en subcarpetas por tamaño:
    - `instancias/grandes/`, `instancias/medianas/`, `instancias/pequeñas/`: Cada una incluye archivos `.dzn` que representan diferentes instancias del problema.
  - `README.md`: Explica el formato o uso de los datos.

- **models/**
  - `main.mzn`: Modelo principal de MiniZinc que define el problema de optimización.
  - `main.ozn`: Archivo de salida con soluciones u observaciones generadas por MiniZinc.

- **reportes/**
  - Almacena los resultados de las ejecuciones, organizados por tamaño de instancia:
    - Subcarpetas para `grandes/`, `medianas/` y `pequeñas/`, cada una con reportes `.txt` para cada instancia.

- **scripts/**
  - `run.sh`: Script de automatización para ejecutar modelos, instancias o experimentos de manera sencilla desde la terminal.

- **tools/**
  - `generador.py`: Script en Python para generar instancias o datos de entrada en formato `.dzn`.

## Funcionamiento y Uso

1. **Generación de Instancias**
   - Ejecuta el script `tools/generador.py` para crear archivos `.dzn` en las carpetas de datos. Estos archivos representan diferentes instancias del problema a resolver.

2. **Modelado y Resolución**
   - El modelo principal (`models/main.mzn`) define el problema de optimización. Utiliza los archivos `.dzn` generados como entrada.
   - Puedes automatizar la ejecución de múltiples instancias usando el script `scripts/run.sh`.

3. **Revisión de Resultados**
   - Los resultados de las ejecuciones se almacenan en la carpeta `reportes/`, organizados por tamaño y por instancia. Cada archivo `.txt` contiene el reporte correspondiente a una instancia resuelta.

## Requisitos

- Python 3.x (para ejecutar los scripts de generación de datos)
- MiniZinc (para ejecutar los modelos de optimización)

## Ejemplo de Uso

```bash
# Generar instancias de datos
python3 tools/generador.py

# Ejecutar el modelo sobre las instancias (puede requerir edición de run.sh)
bash scripts/run.sh
```

## Notas
- Asegúrate de tener instalados Python y MiniZinc en tu sistema.
- Consulta los archivos `README.md` en las subcarpetas para detalles adicionales sobre el formato de datos o instrucciones específicas.

---

Este documento proporciona una visión general clara para cualquier usuario que desee entender y utilizar el proyecto.

# MiniZinc Project

This project is designed to solve optimization problems using MiniZinc. The structure has been organized to streamline the workflow and focus on the essential components required for generating instances and running the MiniZinc model.

## Project Structure

- **generador.py**: A Python script that generates instances for the MiniZinc model. It creates the necessary data files based on specified parameters.

- **instancias_minizinc/**: This directory contains the generated `.dzn` files, which serve as data files for the MiniZinc model. Examples include `instancia_pequeñas_1.dzn`, `instancia_pequeñas_2.dzn`, etc.

- **resultados/**: This directory is used to save output results from the MiniZinc model runs.

## Usage

1. **Generate Instances**: Run the `generador.py` script to create the necessary data files for your MiniZinc model.
2. **Run MiniZinc Model**: Use the generated `.dzn` files with your MiniZinc model to solve the optimization problem.
3. **View Results**: Check the `resultados/` directory for the output from the MiniZinc model runs.

## Requirements

- Python 3.x
- MiniZinc

## License

This project is licensed under the MIT License.