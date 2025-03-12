import unittest

from utils import run_circuit
from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.utils.grouptheory import is_in_orthogonal_group



class SimonBlockingclauseTest(unittest.TestCase):
    def run_circuit_with_blockingclause_and_assert_correct_behaviour(
        self,
        hidden_subgroup,
        blockingclauses
    ):
        oracle = DefaultOracle(hidden_subgroup)
        simon_circuit = SimonCircuit(oracle)

        standard_circuit = simon_circuit.generate_standard_simon_circuit()
        blockingclauses_circuit = simon_circuit.add_blocking_clauses(blockingclauses)

        input_register, _, _, ancilla_register = simon_circuit.circuit_wrapper.get_registers()
        result = run_circuit(
            standard_circuit.compose(blockingclauses_circuit),
            [input_register, ancilla_register]
        )

        # resulting bitstrings must all be in the orthogonal group of the hidden subgroup
        register_states = [k.split(' ') for k in result.keys()]
        for input_register_state, ancilla_register_state in register_states:
            self.assertTrue(is_in_orthogonal_group(input_register_state, hidden_subgroup))
            self.assertEqual(ancilla_register_state, '0' * len(ancilla_register))

        # we must not measure any bitstring from bitstrings again
        measured_bitstrings = {s[0] for s in register_states}
        for bitstring in [bc[0] for bc in blockingclauses]:
            self.assertNotIn(bitstring, measured_bitstrings)

        # all measured bitstrings should be 0 on the index j used in the blocking clause
        expected_zero_indices = [bc[1] for bc in blockingclauses]
        def zero_on_all_indices(bitstring):
            return all([bitstring[i == '0'] for i in expected_zero_indices])
        self.assertTrue([zero_on_all_indices(bitstring) for bitstring in measured_bitstrings])


    def test_blockingclause_two_qubits_1(self):
        hidden_subgroup = ['00', '01']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('10', 1)]
        )


    def test_blockingclause_two_qubits_2(self):
        hidden_subgroup = ['00', '10']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('01', 0)]
        )


    def test_blockingclause_two_qubits_3(self):
        hidden_subgroup = ['00', '11']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('11', 0)]
        )


    def test_blockingclauses_three_qubits_1(self):
        hidden_subgroup = ['000', '100']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('011', 0)]
        )


    def test_blockingclauses_three_qubits_2(self):
        hidden_subgroup = ['000', '100']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('001', 0)]
        )


    def test_blockingclauses_three_qubits_3(self):
        hidden_subgroup = ['000', '100']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('010', 1), ('001', 0)]
        )


    def test_blockingclauses_three_qubits_4(self):
        hidden_subgroup = ['000', '100']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('011', 1), ('001', 0)]
        )


    def test_blockingclauses_four_qubits_1(self):
        hidden_subgroup = ['0000', '0001']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('1000', 3)]
        )


    def test_blockingclauses_four_qubits_2(self):
        hidden_subgroup = ['0000', '0001']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('1000', 3), ('0110', 2)]
        )


    def test_blockingclauses_four_qubits_3(self):
        hidden_subgroup = ['0000', '0001']
        self.run_circuit_with_blockingclause_and_assert_correct_behaviour(
            hidden_subgroup,
            [('1000', 3), ('0110', 2), ('0010', 1)]
        )
