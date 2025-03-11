from utils import BaseAssertions, construct_extended_simon_circuit_and_run_for_every_possible_index


class SimonBlockingclauseAndRemoveZero(BaseAssertions):
    
    def test_blockingclause_and_remove_zero_two_qubits_0(self):
        hidden_subgroup = ['00']
        blockingclauses = ['01']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index)


    def test_blockingclause_and_remove_zero_two_qubits_1(self):
        hidden_subgroup = ['00']
        blockingclauses = ['10']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index)


    def test_blockingclause_and_remove_zero_two_qubits_2(self):
        hidden_subgroup = ['00']
        blockingclauses = ['01', '10']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_only_all_zero_is_measured)


    def test_blockingclause_and_remove_zero_three_qubits_0(self):
        hidden_subgroup = ['000']
        blockingclauses = ['001']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index)


    def test_blockingclause_and_remove_zero_three_qubits_1(self):
        hidden_subgroup = ['000']
        blockingclauses = ['001', '010']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index)

    
    def test_blockingclause_and_remove_zero_three_qubits_2(self):
        hidden_subgroup = ['000']
        blockingclauses = ['001', '010','100']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_only_all_zero_is_measured)


    def test_blockingclause_and_remove_zero_four_qubits_0(self):
        hidden_subgroup = ['0000']
        blockingclauses = ['0001']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index)


    def test_blockingclause_and_remove_zero_four_qubits_1(self):
        hidden_subgroup = ['0000']
        blockingclauses = ['0001', '0010']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index)

    
    def test_blockingclause_and_remove_zero_four_qubits_2(self):
        hidden_subgroup = ['0000']
        blockingclauses = ['0001', '0010','0100']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_all_zero_not_measured_and_all_results_have_1_at_target_index)


    def test_blockingclause_and_remove_zero_four_qubits_3(self):
        hidden_subgroup = ['0000']
        blockingclauses = ['0001', '0010','0100', '1000']
        construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclauses, self.assert_only_all_zero_is_measured)




        