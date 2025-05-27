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