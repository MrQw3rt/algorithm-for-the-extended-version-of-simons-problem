import unittest

from qiskit import QuantumRegister, AncillaRegister, QuantumCircuit
import numpy as np


from simonalg.utils.grouptheory import generate_group_by_order
from simonalg.utils.circuit import conditional_phase_shift_by_index
from utils import run_circuit_without_measurement


class CPHByIndexTest(unittest.TestCase):
    def run_circuit_and_assert_correct_conditional_phaseshift(self, circuit, bitstring, index):
        result = run_circuit_without_measurement(circuit).get_statevector(circuit).to_dict()

        # the circuit should not create a superposition
        self.assertIs(len(result), 1)
        (state, phase) = list(result.items())[0]
        ancilla_register_size = len(state) - len(bitstring)
        ancilla_state = state[:ancilla_register_size]
        input_state = state[ancilla_register_size:]

        # ancilla qubits must be reset
        self.assertEqual(ancilla_state, '0' * ancilla_register_size)
        # the value in the input register should not be changed
        self.assertEqual(input_state, bitstring)

        # the phase shift should only be performed if input register is 1 at index
        expected_phase = np.complex128(0+1j) if bitstring[len(bitstring) - 1 - index] == '1' else 1
        self.assertEqual(phase, expected_phase)


    def test_conditional_phaseshift_bitstring_size_2(self):
        input_register_size = 2
        for index in range(input_register_size):
            for bitstring in generate_group_by_order(input_register_size):
                input_register = QuantumRegister(input_register_size, 'in')
                ancilla_register = AncillaRegister(1, 'anc')

                circuit = QuantumCircuit(input_register, ancilla_register)
                circuit.initialize(bitstring, input_register)

                conditional_phase_shift_by_index(circuit, input_register, ancilla_register, index)

                circuit.save_statevector()
                self.run_circuit_and_assert_correct_conditional_phaseshift(circuit, bitstring, index)


    def test_conditional_phaseshift_bitstring_size_3(self):
        input_register_size = 3
        for index in range(input_register_size):
            for bitstring in generate_group_by_order(input_register_size):
                input_register = QuantumRegister(input_register_size, 'in')
                ancilla_register = AncillaRegister(1, 'anc')

                circuit = QuantumCircuit(input_register, ancilla_register)
                circuit.initialize(bitstring, input_register)

                conditional_phase_shift_by_index(circuit, input_register, ancilla_register, index)

                circuit.save_statevector()
                self.run_circuit_and_assert_correct_conditional_phaseshift(circuit, bitstring, index)
                    

    def test_conditional_phaseshift_bitstring_size_4(self):
        input_register_size = 4
        for index in range(input_register_size):
            for bitstring in generate_group_by_order(input_register_size):
                input_register = QuantumRegister(input_register_size, 'in')
                ancilla_register = AncillaRegister(1, 'anc')

                circuit = QuantumCircuit(input_register, ancilla_register)
                circuit.initialize(bitstring, input_register)

                conditional_phase_shift_by_index(circuit, input_register, ancilla_register, index)

                circuit.save_statevector()
                self.run_circuit_and_assert_correct_conditional_phaseshift(circuit, bitstring, index)
                