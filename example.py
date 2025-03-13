from qiskit_aer import AerSimulator

from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.solver import SimonSolver

hidden_subgroup = ['000', '001', '010', '011']
oracle = DefaultOracle(hidden_subgroup)

solver = SimonSolver(SimonCircuit(oracle), AerSimulator())
hidden_subgroup_basis = solver.solve()
