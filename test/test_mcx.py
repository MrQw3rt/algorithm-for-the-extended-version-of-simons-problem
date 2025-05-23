import unittest
from itertools import takewhile

from qiskit import QuantumRegister, AncillaRegister, QuantumCircuit

from utils import run_circuit_on_simulator
from simonalg.utils.grouptheory import generate_group_by_order
from simonalg.utils.circuit import mcx_halfchain, reverse_mcx_halfchain, optimized_mcx


class CustomMCXTest(unittest.TestCase):
    def assert_correct_halfchain(self, result):
        self.assertIs(len(result), 1)   # The halfchain circuit should not produce a superposition

        register_states = list(result.keys())[0]
        state_in, state_an = register_states.split(' ')

        def is_one(qbit):
            return qbit == '1'
        num_ancilla_ones = len(list(takewhile(is_one, reversed(state_an))))
        num_input_ones = len(list(takewhile(is_one, reversed(state_in))))

        # An anciliary qubit should be set to |1> iff all 'preceding' input qubits are |1>
        no_input_qubits_one = (num_ancilla_ones == 0) and (num_input_ones == 0)
        all_input_qubits_one = num_input_ones == len(state_in)
        self.assertTrue(
            no_input_qubits_one or 
            (num_input_ones == num_ancilla_ones + (2 if all_input_qubits_one else 1))
        )


    def assert_correct_reverse_halfchain(self, result, bitstring):
        # The reverse halfchain circuit should not produce a superposition
        self.assertIs(len(result), 1)

        register_states = list(result.keys())[0]
        state_in, state_an = register_states.split(' ')

        self.assertEqual(state_in, bitstring)
        self.assertEqual(state_an, '0' * len(state_an))


    def assert_correct_optimized_mcx(self, result, bitstring):
        self.assertIs(len(result), 1)   # The halfchain circuit should not produce a superposition

        register_states = list(result.keys())[0]
        state_in, state_an, state_out = register_states.split(' ')

        self.assertEqual(state_in, bitstring)
        self.assertEqual(state_an, '0' * len(state_an))
        self.assertEqual(
            state_out,
            ('1' if (state_in == '1' * len(state_in)) else '0') * len(state_out)
        )


    def test_halfchain_with_one_input(self):
        # For size one, we expect the halfchain circuit to do nothing
        input_register = QuantumRegister(1, 'in')
        ancilla_register = AncillaRegister(0, 'anc')
        circuit = QuantumCircuit(input_register, ancilla_register)

        circuit_before = circuit.copy()
        mcx_halfchain(circuit, input_register, ancilla_register)

        self.assertEqual(circuit_before, circuit)


    def test_halfchain_with_two_inputs(self):
        # For size two, we expect the halfchain circuit to do nothing
        input_register = QuantumRegister(2, 'in')
        ancilla_register = AncillaRegister(0, 'anc')
        circuit = QuantumCircuit(input_register, ancilla_register)

        circuit_before = circuit.copy()
        mcx_halfchain(circuit, input_register, ancilla_register)

        self.assertEqual(circuit_before, circuit)


    def test_halfchain_with_three_inputs(self):
        # Size 3 is a bit special, because we need only one ancilliary qubit
        for bitstring in generate_group_by_order(3):
            input_register = QuantumRegister(3, 'in')
            ancilla_register = AncillaRegister(1, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            mcx_halfchain(circuit, input_register, ancilla_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register])
            self.assert_correct_halfchain(result)


    def test_halfchain_with_four_inputs(self):
        # From size 4 onwards, the halfchain circuit follows a pattern
        for bitstring in generate_group_by_order(4):
            input_register = QuantumRegister(4, 'in')
            ancilla_register = AncillaRegister(2, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            mcx_halfchain(circuit, input_register, ancilla_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register])
            self.assert_correct_halfchain(result)


    def test_halfchain_with_five_inputs(self):
        for bitstring in generate_group_by_order(5):
            input_register = QuantumRegister(5, 'in')
            ancilla_register = AncillaRegister(3, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            mcx_halfchain(circuit, input_register, ancilla_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register])
            self.assert_correct_halfchain(result)


    def test_halfchain_with_six_inputs(self):
        for bitstring in generate_group_by_order(6):
            input_register = QuantumRegister(6, 'in')
            ancilla_register = AncillaRegister(4, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            mcx_halfchain(circuit, input_register, ancilla_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register])
            self.assert_correct_halfchain(result)


    def test_reverse_halfchain_with_one_input(self):
        # For size one, we expect the halfchain circuit to do nothing
        input_register = QuantumRegister(1, 'in')
        ancilla_register = AncillaRegister(0, 'anc')
        circuit = QuantumCircuit(input_register, ancilla_register)

        circuit_before = circuit.copy()
        mcx_halfchain(circuit, input_register, ancilla_register)
        reverse_mcx_halfchain(circuit, input_register, ancilla_register)

        self.assertEqual(circuit_before, circuit)


    def test_reverse_halfchain_with_two_inputs(self):
        # For size two, we expect the reverse halfchain circuit to do nothing
        input_register = QuantumRegister(2, 'in')
        ancilla_register = AncillaRegister(0, 'anc')
        circuit = QuantumCircuit(input_register, ancilla_register)

        circuit_before = circuit.copy()
        mcx_halfchain(circuit, input_register, ancilla_register)
        reverse_mcx_halfchain(circuit, input_register, ancilla_register)

        self.assertEqual(circuit_before, circuit)



    def test_reverse_halfchain_with_three_inputs(self):
        # Size 3 is a bit special, because we need only one ancilliary qubit
        for bitstring in generate_group_by_order(3):
            input_register = QuantumRegister(3, 'in')
            ancilla_register = AncillaRegister(1, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            mcx_halfchain(circuit, input_register, ancilla_register)
            reverse_mcx_halfchain(circuit, input_register, ancilla_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register])
            self.assert_correct_reverse_halfchain(result, bitstring)


    def test_reverse_halfchain_with_four_inputs(self):
        for bitstring in generate_group_by_order(4):
            input_register = QuantumRegister(4, 'in')
            ancilla_register = AncillaRegister(2, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            mcx_halfchain(circuit, input_register, ancilla_register)
            reverse_mcx_halfchain(circuit, input_register, ancilla_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register])
            self.assert_correct_reverse_halfchain(result, bitstring)


    def test_reverse_halfchain_with_five_inputs(self):
        for bitstring in generate_group_by_order(5):
            input_register = QuantumRegister(5, 'in')
            ancilla_register = AncillaRegister(3, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            mcx_halfchain(circuit, input_register, ancilla_register)
            reverse_mcx_halfchain(circuit, input_register, ancilla_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register])
            self.assert_correct_reverse_halfchain(result, bitstring)


    def test_reverse_halfchain_with_six_inputs(self):
        for bitstring in generate_group_by_order(6):
            input_register = QuantumRegister(6, 'in')
            ancilla_register = AncillaRegister(4, 'anc')
            circuit = QuantumCircuit(input_register, ancilla_register)
            circuit.initialize(bitstring, input_register)

            mcx_halfchain(circuit, input_register, ancilla_register)
            reverse_mcx_halfchain(circuit, input_register, ancilla_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register])
            self.assert_correct_reverse_halfchain(result, bitstring)


    def test_optimized_mcx_with_one_input(self):
        for bitstring in generate_group_by_order(1):
            input_register = QuantumRegister(1, 'in')
            ancilla_register = AncillaRegister(0, 'anc')
            output_register = QuantumRegister(3, 'out')
            circuit = QuantumCircuit(input_register, ancilla_register, output_register)
            circuit.initialize(bitstring, input_register)

            optimized_mcx(circuit, input_register, ancilla_register, output_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register, output_register])

            self.assert_correct_optimized_mcx(result, bitstring)


    def test_optimized_mcx_with_two_inputs(self):
        for bitstring in generate_group_by_order(2):
            input_register = QuantumRegister(2, 'in')
            ancilla_register = AncillaRegister(0, 'anc')
            output_register = QuantumRegister(3, 'out')
            circuit = QuantumCircuit(input_register, ancilla_register, output_register)
            circuit.initialize(bitstring, input_register)

            optimized_mcx(circuit, input_register, ancilla_register, output_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register, output_register])

            self.assert_correct_optimized_mcx(result, bitstring)


    def test_optimized_mcx_with_three_inputs(self):
        for bitstring in generate_group_by_order(3):
            input_register = QuantumRegister(3, 'in')
            ancilla_register = AncillaRegister(1, 'anc')
            output_register = QuantumRegister(1, 'out')
            circuit = QuantumCircuit(input_register, ancilla_register, output_register)
            circuit.initialize(bitstring, input_register)

            optimized_mcx(circuit, input_register, ancilla_register, output_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register, output_register])

            self.assert_correct_optimized_mcx(result, bitstring)


    def test_optimized_mcx_with_four_inputs(self):
        for bitstring in generate_group_by_order(4):
            input_register = QuantumRegister(4, 'in')
            ancilla_register = AncillaRegister(2, 'anc')
            output_register = QuantumRegister(2, 'out')
            circuit = QuantumCircuit(input_register, ancilla_register, output_register)
            circuit.initialize(bitstring, input_register)

            optimized_mcx(circuit, input_register, ancilla_register, output_register)

            result = run_circuit_on_simulator(circuit, [input_register, ancilla_register, output_register])

            self.assert_correct_optimized_mcx(result, bitstring)
            