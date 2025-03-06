import unittest
import logging
logging.basicConfig(level=logging.DEBUG)

from qiskit_aer import AerSimulator

from simonalg.oracle import DefaultOracle, CosetRepresentativeOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.solver import SimonSolver
from simonalg.utils.grouptheory import expand_group

class SimonSolverTest(unittest.TestCase):
    def run_solver_with_AerSimulator_and_assert_success(self, hidden_subgroup, oracle_constructor=DefaultOracle, custom_output_register_size=None):
        oracle = oracle_constructor(hidden_subgroup)

        solver = SimonSolver(SimonCircuit(oracle, custom_output_register_size=custom_output_register_size), AerSimulator())
        recovered_hidden_subgroup = expand_group(solver.solve(), solver._n)
        recovered_hidden_subgroup.sort()

        self.assertListEqual(hidden_subgroup, recovered_hidden_subgroup)


    def test_standard_oracle_hidden_subgroup_order_1_1(self):
        hidden_subgroup = ['00']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup)


    def test_standard_oracle_hidden_subgroup_order_1_2(self):
        hidden_subgroup = ['000']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup)


    def test_cosetrepresentative_oracle_hidden_subgroup_order_2_1(self):
        hidden_subgroup = ['0000', '1100']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup, oracle_constructor=CosetRepresentativeOracle, custom_output_register_size=4)


    def test_cosetrepresentative_oracle_hidden_subgroup_order_2_2(self):
        hidden_subgroup = ['0000', '0011']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup, oracle_constructor=CosetRepresentativeOracle, custom_output_register_size=4)


    def test_standard_oracle_hidden_subgroup_order_4_1(self):
        hidden_subgroup = ['000', '001', '010', '011']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup)


    def test_standard_oracle_hidden_subgroup_order_4_2(self):
        hidden_subgroup = ['000', '010', '100', '110']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup)


    def test_standard_oracle_hidden_subgroup_order_4_3(self):
        hidden_subgroup = ['000', '001', '110', '111']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup)


    def test_standard_oracle_hidden_subgroup_order_8_1(self):
        hidden_subgroup = ['000', '001', '010', '011', '100', '101', '110', '111']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup)


    def test_standard_oracle_hidden_subgroupt_order_8_2(self):
        hidden_subgroup = ['0000', '0010', '0101', '0111', '1001', '1011', '1100', '1110']
        self.run_solver_with_AerSimulator_and_assert_success(hidden_subgroup)

