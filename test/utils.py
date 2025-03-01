import numpy as np
from qiskit import ClassicalRegister, transpile
from qiskit_aer import AerSimulator

import unittest
from functools import reduce

from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.utils.grouptheory import generate_group_by_order, generate_orthogonal_group, is_in_orthogonal_group


def log_parameters(params):
    print()
    print()
    for message, object in params:
        print(message, object)


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


def run_circuit(circuit, measured_registers):
    for register in reversed(measured_registers):   # Reversed in order to preserve the register order in the output
        classical_register = ClassicalRegister(register.size)
        circuit.add_register(classical_register)
        for i in range(register.size):
            circuit.measure(register[i], classical_register[i])

    simulator = AerSimulator()
    transpiled_circuit = transpile(circuit, simulator)
    result = simulator.run(transpiled_circuit).result()

    return result.get_counts(transpiled_circuit)


def run_circuit_without_measurement(circuit):
    simulator = AerSimulator()
    transpiled_circuit = transpile(circuit, simulator)

    return simulator.run(transpiled_circuit).result()


def construct_extended_simon_circuit(hidden_subgroup, index, blockingclause_bitstrings=[]):
    oracle = DefaultOracle(hidden_subgroup)
    simon_circuit = SimonCircuit(oracle)

    input_register, output_register, _, _ = simon_circuit.circuit_wrapper.get_registers()
    rmz_circuit = simon_circuit.generate_remove_zero_circuit(blockingclause_bitstrings, index)
    return rmz_circuit, input_register, output_register


def construct_and_run_extended_simon_circuit(hidden_subgroup, index, orthogonal_subgroup, blockingclause_bitstrings=[], log_circuit=False):
    rmz_circuit, input_register, _ = construct_extended_simon_circuit(hidden_subgroup, index, blockingclause_bitstrings=blockingclause_bitstrings)
    log_parameters([
        ('Running circuit for hidden subgroup ', hidden_subgroup),
        ('Orthogonal group is ', orthogonal_subgroup),
        ('Index is ', index),
        ('Blockingclauses are ', blockingclause_bitstrings)
    ] + ([('Generated Circuit\n', rmz_circuit)] if log_circuit else []))

    result = run_circuit(rmz_circuit, [input_register])
    print('Results: ', result)

    return list(result.keys())


def find_indices_that_can_be_1(orthogonal_subgroup):
        n = len(orthogonal_subgroup[0])
        def map_to_indices_with_1(bitstring):
            return set(filter(lambda index: bitstring[n - index - 1] == '1', range(0, n)))
        orthogonal_group_mapped = [map_to_indices_with_1(bitstring) for bitstring in orthogonal_subgroup]
        return reduce(lambda a,b: a.union(b), orthogonal_group_mapped, set())


def construct_extended_simon_circuit_and_run_for_every_possible_index(hidden_subgroup, blockingclause_bitstrings, assert_fn, log_circuit_and_statevector=False):
    n = len(hidden_subgroup[0])
    group = generate_group_by_order(n)
    orthogonal_subgroup = generate_orthogonal_group(group, hidden_subgroup)

    all_indices_that_can_be_1 = find_indices_that_can_be_1(orthogonal_subgroup)
    indices_locked_by_bitstrings = []
    for bitstring in blockingclause_bitstrings:
        for index in find_indices_that_can_be_1([bitstring]):
            if len(indices_locked_by_bitstrings) == 0 or indices_locked_by_bitstrings[-1] < index:
                indices_locked_by_bitstrings.append(index)
                break
    indices_that_can_be_1_after_bitstrings = list(set(all_indices_that_can_be_1).difference(set(indices_locked_by_bitstrings)))
    if len(indices_that_can_be_1_after_bitstrings) == 0:
        indices_that_can_be_1_after_bitstrings = range(n)

    for index in indices_that_can_be_1_after_bitstrings:
        measurements = construct_and_run_extended_simon_circuit(hidden_subgroup, index, orthogonal_subgroup, blockingclause_bitstrings=blockingclause_bitstrings, log_circuit=log_circuit_and_statevector)
        if log_circuit_and_statevector:
            sv_circuit, sv_input_register, sv_output_register = construct_extended_simon_circuit(hidden_subgroup, index)
            result_sv = run_circuit_without_measurement(sv_circuit).data(0)
            log_statevectors(result_sv, sv_input_register, sv_output_register)

        params = { 
            'measurements': measurements, 
            'index': index, 
            'hidden_subgroup': hidden_subgroup, 
            'blockingclause_bitstrings': blockingclause_bitstrings 
        }
        assert_fn(params)


class BaseAssertions(unittest.TestCase):

    def assert_all_zero_not_measured(self, measurements):
        n = len(measurements[0])
        allzero = '0' * n
        self.assertTrue(all([bitstring != allzero for bitstring in measurements]))


    def assert_all_measurements_have_1_at_index(self, measurements, index):
        n = len(measurements[0])
        self.assertTrue(all([bitstring[n - index - 1] == '1' for bitstring in measurements]))


    def assert_all_measurements_are_in_orthogonal_group(self, measurements, hidden_subgroup):
        self.assertTrue(all([is_in_orthogonal_group(bitstring, hidden_subgroup) for bitstring in measurements]))


    def assert_all_zero_not_measured_and_all_results_have_1_at_target_index(self, params):
        measurements = params['measurements']
        index = params['index']
        hidden_subgroup = params['hidden_subgroup']

        self.assert_all_zero_not_measured(measurements)
        self.assert_all_measurements_have_1_at_index(measurements, index)
        self.assert_all_measurements_are_in_orthogonal_group(measurements, hidden_subgroup)


    def assert_only_all_zero_is_measured(self, params):
        measurements = params['measurements']
        n = len(measurements[0])
        self.assertTrue(len(measurements) == 1)
        self.assertTrue(measurements[0] == n * '0')