import unittest

from simonalg.oracle import SimonOracle
from simonalg.utils.grouptheory import generate_group_by_order, generate_cosets_for_subgroup
from simonalg.utils.circuit import generate_circuit_setup


from utils import run_circuit


class CustomMCXTest(unittest.TestCase):
    def run_circuit_for_oracle(self, hidden_subgroup):
        n = len(hidden_subgroup[0])
        group = generate_group_by_order(n)
        cosets = generate_cosets_for_subgroup(group, hidden_subgroup)

        results = {}
        for bitstring in group:
            init_circuit, input_register, output_register, ancilla_register = generate_circuit_setup(n, len(hidden_subgroup))
            init_circuit.initialize(bitstring, input_register)

            oracle = SimonOracle(hidden_subgroup)
            oracle_circuit = oracle.generate_default_circuit()

            full_circuit = init_circuit.compose(oracle_circuit)

            result = run_circuit(full_circuit, [input_register, output_register, ancilla_register])
        
            self.assertIs(len(result), 1)
            register_states = list(result.keys())[0]

            res_in, res_out, res_an = register_states.split(' ')
            self.assertEqual(res_in, bitstring)
            self.assertEqual(res_an, '0' * len(ancilla_register))

            results[bitstring] = res_out

        coset_results = []
        for coset in cosets:
            coset_mappings = [results[bitstring] for bitstring in coset]
            self.assertTrue(all(r == coset_mappings[0] for r in coset_mappings))    # Check that oracle behaves constant on a coset
            coset_results.append(coset_mappings[0])
        
        self.assertEqual(len(coset_results), len(set(coset_results)))   # Check that oracle behaves different for each coset


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
        



        