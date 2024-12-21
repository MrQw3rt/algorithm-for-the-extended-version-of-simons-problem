import unittest
import numpy as np

from functools import reduce

from simonalg.oracle import SimonOracle
from simonalg.simon_circuit import SimonCircuit

from utils import run_circuit, run_circuit_without_measurement
from simonalg.utils.grouptheory import generate_group_by_order, generate_orthogonal_group, is_in_orthogonal_group


def format_statevector(sv, input_register, output_register):
    def format_item(item):
        state = item[0]
        amplitude = item[1]
        return f'|{state[-len(input_register):]}>|{state[-len(input_register) - len(output_register):-len(input_register)]}>', amplitude

    results = [format_item(item) for item in sv.items()]
    results.sort(key=lambda tuple: tuple[0])
    results = list(filter(lambda t: np.absolute(t[1]) > 1e-8, results))

    results_string = '\n'.join([f'\t{t[0]}: {t[1]}' for t in results])
    return results_string


def log_statevectors(result, input_register, output_register):
    strings = [(t[0], format_statevector(t[1].to_dict(), input_register, output_register)) for t in result.items()]
    strings.sort(key=lambda t: t[0])
    
    strings = [f'{t[0]}\n{t[1]}' for t in strings]
    res = '\n'.join(strings)
    print()
    print('Statevectors:')
    print(res)


class SimonRemoveAllZeroTest(unittest.TestCase):

    def construct_circuit(self, hidden_subgroup, index):
        oracle = SimonOracle(hidden_subgroup)
        simon_circuit = SimonCircuit(oracle)

        input_register, output_register, _, _ = simon_circuit.circuit_wrapper.get_registers()
        rmz_circuit = simon_circuit.generate_remove_zero_circuit([], index)
        return rmz_circuit, input_register, output_register

    def construct_circuit_and_run(self, hidden_subgroup, index, orthogonal_subgroup, log_circuit=False):
        rmz_circuit, input_register, _ = self.construct_circuit(hidden_subgroup, index)
        print()
        print()
        print('Running circuit for hidden subgroup ', hidden_subgroup)
        print('Orthogonal group is ', orthogonal_subgroup)
        print('Index is ', index)
        if log_circuit:
            print('Generated Circuit:')
            print(rmz_circuit)

        result = run_circuit(rmz_circuit, [input_register])
        print('Results: ', result)

        return list(result.keys())


    def assert_all_zero_not_measured(self, measurements):
        n = len(measurements[0])
        allzero = '0' * n
        self.assertTrue(all([bitstring != allzero for bitstring in measurements]))


    def assert_all_measurements_have_1_at_index(self, measurements, index):
        n = len(measurements[0])
        self.assertTrue(all([bitstring[n - index - 1] == '1' for bitstring in measurements]))


    def assert_all_measurements_are_in_orthogonal_group(self, measurements, hidden_subgroup):
        self.assertTrue(all([is_in_orthogonal_group(bitstring, hidden_subgroup) for bitstring in measurements]))


    def run_circuit_for_each_index_that_can_be_1(self, hidden_subgroup, log_circuit_and_statevector=False):
        n = len(hidden_subgroup[0])
        group = generate_group_by_order(n)
        orthogonal_subgroup = generate_orthogonal_group(group, hidden_subgroup)

        def map_to_indices_with_1(bitstring):
            return set(filter(lambda index: bitstring[n - index - 1] == '1', range(0, n)))
        orthogonal_group_mapped = [map_to_indices_with_1(bitstring) for bitstring in orthogonal_subgroup]
        indices_that_can_be_1 = reduce(lambda a,b: a.union(b), orthogonal_group_mapped, set())
        for index in indices_that_can_be_1:
            measurements = self.construct_circuit_and_run(hidden_subgroup, index, orthogonal_subgroup, log_circuit=log_circuit_and_statevector)
            if log_circuit_and_statevector:
                sv_circuit, sv_input_register, sv_output_register = self.construct_circuit(hidden_subgroup, index)
                result_sv = run_circuit_without_measurement(sv_circuit).data(0)
                log_statevectors(result_sv, sv_input_register, sv_output_register)

            
            self.assert_all_zero_not_measured(measurements)
            self.assert_all_measurements_have_1_at_index(measurements, index)
            self.assert_all_measurements_are_in_orthogonal_group(measurements, hidden_subgroup)

    
    def run_circuit_for_all_zero_orthogonal_group(self, hidden_subgroup, log_circuit_and_statevector=False):
        n = len(hidden_subgroup[0])
        group = generate_group_by_order(n)
        orthogonal_subgroup = generate_orthogonal_group(group, hidden_subgroup)

        indices_that_can_be_1 = range(n)
        for index in indices_that_can_be_1:
            measurements = self.construct_circuit_and_run(hidden_subgroup, index, orthogonal_subgroup, log_circuit=log_circuit_and_statevector)
            if log_circuit_and_statevector:
                sv_circuit, input_register, output_register = self.construct_circuit(hidden_subgroup, index)
                result_sv = run_circuit_without_measurement(sv_circuit).data(0)
                log_statevectors(result_sv, input_register, output_register)

            self.assertTrue(len(measurements) == 1)
            self.assertTrue(measurements[0] == n * '0')


    def test_remove_all_zero_vector_for_two_qubits_0(self):
        # Case oracle is bijective
        hidden_subgroup = ['00']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_two_qubits_1(self):
        hidden_subgroup = ['00', '01']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup, log_circuit_and_statevector=True)


    def test_remove_all_zero_vector_for_two_qubits_2(self):
        hidden_subgroup = ['00', '10']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)

    
    def test_remove_all_zero_vector_for_two_qubits_3(self):
        # Case hidden subgroup is entire group G
        hidden_subgroup = generate_group_by_order(2)
        self.run_circuit_for_all_zero_orthogonal_group(hidden_subgroup)


    def test_remove_all_zero_vector_for_three_qubits_0(self):
        # Case oracle is bijective
        hidden_subgroup = ['000']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_three_qubits_1(self):
        hidden_subgroup = ['000', '001']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)

    
    def test_remove_all_zero_vector_for_three_qubits_2(self):
        hidden_subgroup = ['000', '010']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_three_qubits_3(self):
        hidden_subgroup = ['000', '100']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_three_qubits_4(self):
        hidden_subgroup = ['000', '111']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_three_qubits_5(self):
        # Case hidden subgroup is entire group G
        hidden_subgroup = generate_group_by_order(3)
        self.run_circuit_for_all_zero_orthogonal_group(hidden_subgroup)


    def test_remove_all_zero_vector_for_four_qubits_0(self):
        # Case oracle is bijective
        hidden_subgroup = ['0000']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_four_qubits_1(self):
        hidden_subgroup = ['0000', '1100']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_four_qubits_2(self):
        hidden_subgroup = ['0000', '1001']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_four_qubits_3(self):
        hidden_subgroup = ['0000', '1101']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_four_qubits_4(self):
        hidden_subgroup = ['0000', '1111']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_four_qubits_5(self):
        # Case hidden subgroup is entire group G
        hidden_subgroup = generate_group_by_order(4)
        self.run_circuit_for_all_zero_orthogonal_group(hidden_subgroup)


    @unittest.skip('This takes too long to simulate on a laptop!')
    def test_remove_all_zero_vector_for_five_qubits_0(self):
        # Case oracle is bijective
        hidden_subgroup = ['00000']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_five_qubits_1(self):
        hidden_subgroup = ['00000', '00001', '00010', '00011']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_five_qubits_2(self):
        hidden_subgroup = ['00000', '10000', '01000', '11000']
        self.run_circuit_for_each_index_that_can_be_1(hidden_subgroup)


    def test_remove_all_zero_vector_for_five_qubits_3(self):
        # Case hidden subgroup is entire group G
        hidden_subgroup = generate_group_by_order(5)
        self.run_circuit_for_all_zero_orthogonal_group(hidden_subgroup)

