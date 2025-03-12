import unittest

from qiskit import QuantumRegister, AncillaRegister, QuantumCircuit
import numpy as np


from utils import run_circuit_without_measurement
from simonalg.utils.grouptheory import generate_group_by_order
from simonalg.utils.circuit import conditional_phase_shift_by_zero_vec


class CPHByZeroVecTest(unittest.TestCase):
    def run_circuit_and_assert_correct_conditional_phaseshift(self, circuit, bitstring):
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
        expected_phase = np.complex128(0+1j) if ('1' not in bitstring) else 1
        self.assertEqual(phase, expected_phase)


    def test_cph_by_zero_vec_two_qubits(self):
        input_register_size = 2
        for bitstring in generate_group_by_order(input_register_size):
            input_register = QuantumRegister(input_register_size, 'in')
            ancilla_register = AncillaRegister(input_register_size - 1, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            conditional_phase_shift_by_zero_vec(circuit, input_register, ancilla_register)
            circuit.save_statevector()

            self.run_circuit_and_assert_correct_conditional_phaseshift(circuit, bitstring)



    def test_cph_by_zero_vec_three_qubits(self):
        input_register_size = 3
        for bitstring in generate_group_by_order(input_register_size):
            input_register = QuantumRegister(input_register_size, 'in')
            ancilla_register = AncillaRegister(input_register_size - 1, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            conditional_phase_shift_by_zero_vec(circuit, input_register, ancilla_register)
            circuit.save_statevector()

            self.run_circuit_and_assert_correct_conditional_phaseshift(circuit, bitstring)


    def test_cph_by_zero_vec_four_qubits(self):
        input_register_size = 4
        for bitstring in generate_group_by_order(input_register_size):
            input_register = QuantumRegister(input_register_size, 'in')
            ancilla_register = AncillaRegister(input_register_size - 1, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            conditional_phase_shift_by_zero_vec(circuit, input_register, ancilla_register)
            circuit.save_statevector()

            self.run_circuit_and_assert_correct_conditional_phaseshift(circuit, bitstring)



    def test_cph_by_zero_vec_five_qubits(self):
        input_register_size = 5
        for bitstring in generate_group_by_order(input_register_size):
            input_register = QuantumRegister(input_register_size, 'in')
            ancilla_register = AncillaRegister(input_register_size - 1, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            conditional_phase_shift_by_zero_vec(circuit, input_register, ancilla_register)
            circuit.save_statevector()

            self.run_circuit_and_assert_correct_conditional_phaseshift(circuit, bitstring)
