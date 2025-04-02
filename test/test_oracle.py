import unittest

from utils import run_circuit_on_simulator

from simonalg.oracle import DefaultOracle
from simonalg.utils.grouptheory import generate_group_by_order, generate_cosets_for_subgroup
from simonalg.utils.circuit import CircuitWrapper


class OracleTest(unittest.TestCase):
    def run_circuit_for_oracle(self, hidden_subgroup):
        n = len(hidden_subgroup[0])
        group = generate_group_by_order(n)
        cosets = generate_cosets_for_subgroup(group, hidden_subgroup)

        results = {}
        for bitstring in group:
            circuit_wrapper = CircuitWrapper(hidden_subgroup)
            registers = circuit_wrapper.get_registers()
            input_register, output_register, blockingclause_register, ancilla_register = registers

            init_circuit = circuit_wrapper.generate_new_circuit(init_vector=bitstring)

            oracle = DefaultOracle(hidden_subgroup)
            oracle_circuit = oracle.generate_circuit(circuit_wrapper)

            result = run_circuit_on_simulator(
                 init_circuit.compose(oracle_circuit),
                [input_register, output_register, blockingclause_register, ancilla_register]
            )

            self.assertIs(len(result), 1)
            register_states = list(result.keys())[0]

            res_in, res_out, res_bc, res_an = register_states.split(' ')
            #[res_in, res_out, res_bc, res_an] = result

            self.assertEqual(res_in, bitstring)
            self.assertEqual(res_bc, '0' * len(blockingclause_register))
            self.assertEqual(res_an, '0' * len(ancilla_register))

            results[bitstring] = res_out

        coset_results = []
        for coset in cosets:
            coset_mappings = [results[bitstring] for bitstring in coset]
            # Check that oracle behaves constant on a coset
            self.assertTrue(all(r == coset_mappings[0] for r in coset_mappings))
            coset_results.append(coset_mappings[0])

        # Check that oracle behaves different for each coset
        self.assertEqual(len(coset_results), len(set(coset_results)))


    def test_oracle_tow_qubits_1(self):
        self.run_circuit_for_oracle(['00'])


    def test_oracle_two_qubits_2(self):
        self.run_circuit_for_oracle(['00', '01'])


    def test_oracle_two_qubits_3(self):
        self.run_circuit_for_oracle(['00', '10'])


    def test_oracle_two_qubits_4(self):
        self.run_circuit_for_oracle(['00', '01'])


    def test_oracle_two_qubits_5(self):
        self.run_circuit_for_oracle(['00', '11'])


    def test_oracle_three_qubits_1(self):
        self.run_circuit_for_oracle(['000', '001'])


    def test_oracle_three_qubits_2(self):
        self.run_circuit_for_oracle(['000', '111'])


    def test_oracle_three_qubits_3(self):
        self.run_circuit_for_oracle(['000', '001', '010', '011'])


    def test_oracle_three_qubits_4(self):
        self.run_circuit_for_oracle(['000', '100', '101', '001'])


    def test_oracle_three_qubits_5(self):
        self.run_circuit_for_oracle(['000', '001', '010', '011', '100', '101', '110', '111'])
        