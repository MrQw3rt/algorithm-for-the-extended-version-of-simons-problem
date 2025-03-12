import unittest

from utils import run_circuit
from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.utils.grouptheory import is_in_orthogonal_group


class SimonStandardTest(unittest.TestCase):
    def run_circuit_and_assert_all_measurments_are_in_hbot(self, hidden_subgroup):
        oracle = DefaultOracle(hidden_subgroup)
        simon_circuit = SimonCircuit(oracle)

        circuit = simon_circuit.generate_standard_simon_circuit()
        registers = simon_circuit.circuit_wrapper.get_registers()
        input_register, _, blockingclause_register, ancilla_register = registers
        result = run_circuit(circuit, [input_register, blockingclause_register, ancilla_register])

        register_states = [k.split(' ') for k in result.keys()]
        for reg_tuple in register_states:
            input_register_state, blockingclause_register_state, ancilla_register_state = reg_tuple
            self.assertTrue(is_in_orthogonal_group(input_register_state, hidden_subgroup))
            self.assertEqual(ancilla_register_state, '0' * len(ancilla_register))
            self.assertEqual(blockingclause_register_state, '0' * len(blockingclause_register))


    def run_circuit_and_assert_it_is_its_own_inverse(self, hidden_subgroup):
        oracle = DefaultOracle(hidden_subgroup)
        simon_circuit = SimonCircuit(oracle)

        circuit = simon_circuit.generate_standard_simon_circuit()
        registers = simon_circuit.circuit_wrapper.get_registers()
        input_register, output_register, blockingclause_register, ancilla_register = registers
        result = run_circuit(
            circuit.compose(circuit),
            [input_register, output_register, blockingclause_register, ancilla_register]
        )

        self.assertIs(len(result), 1)
        state = list(result.keys())[0]

        state_pure = state.replace(' ', '')
        self.assertEqual(state_pure, '0' * len(state_pure))


    def test_simonalg_two_qubits_hsgorder_1(self):
        hidden_subgroup = ['00']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_two_qubits_hsgorder_two_1(self):
        hidden_subgroup = ['00', '01']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_two_qubits_hsgorder_two_1a(self):
        hidden_subgroup = ['00', '01']
        self.run_circuit_and_assert_it_is_its_own_inverse(hidden_subgroup)


    def test_simonalg_two_qubits_hsgorder_two_2(self):
        hidden_subgroup = ['00', '10']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_two_qubits_hsgorder_two_2a(self):
        hidden_subgroup = ['00', '10']
        self.run_circuit_and_assert_it_is_its_own_inverse(hidden_subgroup)


    def test_simonalg_two_qubits_hsgorder_two_3(self):
        hidden_subgroup = ['00', '11']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_two_qubits_hsgorder_two_3a(self):
        hidden_subgroup = ['00', '11']
        self.run_circuit_and_assert_it_is_its_own_inverse(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_two_1(self):
        hidden_subgroup = ['000', '010']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_two_1a(self):
        hidden_subgroup = ['000', '010']
        self.run_circuit_and_assert_it_is_its_own_inverse(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_two_2(self):
        hidden_subgroup = ['000', '011']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_two_2a(self):
        hidden_subgroup = ['000', '011']
        self.run_circuit_and_assert_it_is_its_own_inverse(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_four_1(self):
        hidden_subgroup = ['000', '100', '010', '110']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_four_1a(self):
        hidden_subgroup = ['000', '100', '010', '110']
        self.run_circuit_and_assert_it_is_its_own_inverse(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_four_2(self):
        hidden_subgroup = ['000', '100', '111', '011']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_four_2a(self):
        hidden_subgroup = ['000', '100', '111', '011']
        self.run_circuit_and_assert_it_is_its_own_inverse(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_eight_1(self):
        hidden_subgroup = ['000', '001', '010', '011', '100', '101', '110', '111']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_eight_1a(self):
        hidden_subgroup = ['000', '001', '010', '011', '100', '101', '110', '111']
        self.run_circuit_and_assert_it_is_its_own_inverse(hidden_subgroup)
