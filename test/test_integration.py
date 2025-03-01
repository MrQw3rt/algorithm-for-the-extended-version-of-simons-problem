import unittest

from qiskit import ClassicalRegister, transpile
from qiskit_aer import AerSimulator

from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.postprocessing import convert_to_basis_of_hidden_subgroup
from simonalg.utils.grouptheory import expand_group


class SimonIterator:
    def __init__(self, simon_circuit, backend, known_strings=[], blocked_indices=set()):
        self._simon_circuit = simon_circuit
        self._backend = backend
        self._y = known_strings
        self._blocked_indices = blocked_indices


    def _run_circuit(self, circuit, input_register):
        classical_register = ClassicalRegister(input_register.size)
        circuit.add_register(classical_register)
        for i in range(input_register.size):
            circuit.measure(input_register[i], classical_register[i])
            
        transpiled_circuit = transpile(circuit, self._backend)
        result = self._backend.run(transpiled_circuit).result()

        return result.get_counts(transpiled_circuit)


    def __iter__(self):
        return self


    def __next__(self):
        simon_circuit = self._simon_circuit
        input_register = simon_circuit.circuit_wrapper.get_registers()[0]
        n = len(input_register)
        zerovec = '0' * n
        working_indices = set(range(n)).difference(self._blocked_indices)

        for i in working_indices:
            circuit = simon_circuit.generate_remove_zero_circuit(self._y, i)
            quantum_result = self._run_circuit(circuit, input_register)      

            y = list(quantum_result.keys())[0]
            if y != zerovec:
                self._y.append(y)
                self._blocked_indices.add(i)
                return y

        raise StopIteration


class Integration(unittest.TestCase):
    def test_first(self):

        hidden_subgroup = ['000', '001', '010', '011']
        oracle = DefaultOracle(hidden_subgroup)

        iterator = SimonIterator(SimonCircuit(oracle), AerSimulator())
        orthogonal_subgroup_basis = list(iterator)

        hidden_subgroup_basis = convert_to_basis_of_hidden_subgroup(orthogonal_subgroup_basis, 3)

        print()
        print(hidden_subgroup_basis)
        print(expand_group(hidden_subgroup_basis, 3))