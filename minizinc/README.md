# MiniZinc Pipeline Project

This project implements a MiniZinc model for solving a pipeline problem involving plants, tanks, and nodes. The goal is to minimize the total cost of installation and transportation.

## Project Structure

- `src/pipeline.mzn`: Contains the MiniZinc model defining parameters, sets, arrays, decision variables, constraints, and the objective function.
- `data/instance.dzn`: Provides the data for the MiniZinc model, specifying values for parameters such as the number of plants, tanks, nodes, arcs, demands, installation costs, and transportation costs.

## Running the Model

To run the MiniZinc model, follow these steps:

1. Ensure you have MiniZinc installed on your machine. You can download it from the [MiniZinc website](https://www.minizinc.org/software.html).

2. Open a terminal and navigate to the project directory.

3. Run the MiniZinc model using the following command:

   ```
   minizinc src/pipeline.mzn data/instance.dzn
   ```

4. Review the output for the results of the optimization, including the total costs and the configuration of the pipeline.

## Environment Setup

Make sure to have the following dependencies installed:

- MiniZinc (version 2.4 or higher recommended)
- Any additional libraries or tools required for your specific use case (if applicable).

## License

This project is licensed under the MIT License. See the LICENSE file for more details.