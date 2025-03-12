import unittest

from utils import construct_extended_simon_circuit_and_run_for_every_possible_index, BaseAssertions
from simonalg.utils.grouptheory import generate_group_by_order


class SimonRemoveAllZeroTest(BaseAssertions):


    def test_remove_all_zero_vector_for_two_qubits_0(self):
        # Case oracle is bijective
        hidden_subgroup = ['00']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_two_qubits_1(self):
        hidden_subgroup = ['00', '01']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index,
            log_circuit_and_statevector=True
        )


    def test_remove_all_zero_vector_for_two_qubits_2(self):
        hidden_subgroup = ['00', '10']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_two_qubits_3(self):
        # Case hidden subgroup is entire group G
        hidden_subgroup = generate_group_by_order(2)
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_only_all_zero_is_measured
        )


    def test_remove_all_zero_vector_for_three_qubits_0(self):
        # Case oracle is bijective
        hidden_subgroup = ['000']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_three_qubits_1(self):
        hidden_subgroup = ['000', '001']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_three_qubits_2(self):
        hidden_subgroup = ['000', '010']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_three_qubits_3(self):
        hidden_subgroup = ['000', '100']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_three_qubits_4(self):
        hidden_subgroup = ['000', '111']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_three_qubits_5(self):
        # Case hidden subgroup is entire group G
        hidden_subgroup = generate_group_by_order(3)
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_only_all_zero_is_measured
        )


    def test_remove_all_zero_vector_for_four_qubits_0(self):
        # Case oracle is bijective
        hidden_subgroup = ['0000']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_four_qubits_1(self):
        hidden_subgroup = ['0000', '1100']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_four_qubits_2(self):
        hidden_subgroup = ['0000', '1001']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_four_qubits_3(self):
        hidden_subgroup = ['0000', '1101']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_four_qubits_4(self):
        hidden_subgroup = ['0000', '1111']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_four_qubits_5(self):
        # Case hidden subgroup is entire group G
        hidden_subgroup = generate_group_by_order(4)
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_only_all_zero_is_measured
        )


    @unittest.skip('This takes too long to simulate on a laptop!')
    def test_remove_all_zero_vector_for_five_qubits_0(self):
        # Case oracle is bijective
        hidden_subgroup = ['00000']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_five_qubits_1(self):
        hidden_subgroup = ['00000', '00001', '00010', '00011']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_five_qubits_2(self):
        hidden_subgroup = ['00000', '10000', '01000', '11000']
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index
        )


    def test_remove_all_zero_vector_for_five_qubits_3(self):
        # Case hidden subgroup is entire group G
        hidden_subgroup = generate_group_by_order(5)
        construct_extended_simon_circuit_and_run_for_every_possible_index(
            hidden_subgroup,
            [],
            self.assert_only_all_zero_is_measured
        )
