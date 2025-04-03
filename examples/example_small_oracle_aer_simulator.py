from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import SamplerV2

from simonalg.simon_circuit import SimonCircuit
from simonalg.solver import SimonSolver

class SimpleOracle:
    def __init__(self, hidden_subgroup):
        self._hidden_subgroup = hidden_subgroup


    def generate_circuit(self, circuit_wrapper):
        input_register, output_register, _, _ = circuit_wrapper.get_registers()
        circuit = circuit_wrapper.generate_new_circuit()

        circuit.cx(input_register[1], output_register[0])

        return circuit


hidden_subgroup = ['000', '001', '100', '101']
simon_circuit = SimonCircuit(SimpleOracle(hidden_subgroup))
solver = SimonSolver(simon_circuit, SamplerV2(AerSimulator()))

hidden_subgroup_basis = solver.solve()
