import unittest

from simonalg.oracle import SimonOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.utils.grouptheory import is_in_orthogonal_group

from utils import run_circuit


class SimonStandardTest(unittest.TestCase):
    def run_circuit_and_assert_all_measurments_are_in_hbot(self, hidden_subgroup):
        oracle = SimonOracle(hidden_subgroup)
        simon_circuit = SimonCircuit(oracle)

        circuit = simon_circuit.generate_standard_simon_circuit()
        input_register, _, blockingclause_register, ancilla_register = simon_circuit.circuit_wrapper.get_registers()
        result = run_circuit(circuit, [input_register, blockingclause_register, ancilla_register])

        register_states = [k.split(' ') for k in result.keys()]
        for input_register_state, blockingclause_register_state, ancilla_register_state in register_states:
            self.assertTrue(is_in_orthogonal_group(input_register_state, hidden_subgroup))
            self.assertEqual(ancilla_register_state, '0' * len(ancilla_register))
            self.assertEqual(blockingclause_register_state, '0' * len(blockingclause_register))


    def test_simonalg_two_qubits_hsgorder_1(self):
        hidden_subgroup = ['00']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_two_qubits_hsgorder_two_1(self):
        hidden_subgroup = ['00', '01']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)
        

    def test_simonalg_two_qubits_hsgorder_two_2(self):
        hidden_subgroup = ['00', '10']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_two_qubits_hsgorder_two_3(self):
        hidden_subgroup = ['00', '11']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_two_1(self):
        hidden_subgroup = ['000', '010']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_two_2(self):
        hidden_subgroup = ['000', '011']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_four_1(self):
        hidden_subgroup = ['000', '100', '010', '110']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)


    def test_simonalg_three_qubits_hsgorder_four_2(self):
        hidden_subgroup = ['000', '100', '111', '011']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)

    
    def test_simonalg_three_qubits_hsgorder_eight_1(self):
        hidden_subgroup = ['000', '001', '010', '011', '100', '101', '110', '111']
        self.run_circuit_and_assert_all_measurments_are_in_hbot(hidden_subgroup)

