import unittest
import numpy as np

from simonalg.oracle import SimonOracle
from simonalg.simon_circuit import SimonCircuit

from utils import run_circuit, run_circuit_without_measurement


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
    print(res)


class SimonRemoveAllZeroTest(unittest.TestCase):
    def run_custom_circuit(self):
        circuit, input_register = SimonCircuit(SimonOracle(['000', '110'])).generate_new_demo_forward_circuit()
        result = run_circuit(circuit, [input_register])
        print('RMZ Result: ', result)


    def run_remove_all_zero_circuit(self, hidden_subgroup, index):
        oracle = SimonOracle(hidden_subgroup)
        simon_circuit = SimonCircuit(oracle)

        rmz_circuit = simon_circuit.generate_remove_zero_circuit([], index)
        sv_circuit = rmz_circuit.copy()

        input_register, output_register, blockingclause_register, ancilla_register = simon_circuit.circuit_wrapper.get_registers()
        result = run_circuit(rmz_circuit, [input_register])
        
        result_nm = run_circuit_without_measurement(sv_circuit).data(0)
        
        print()
        
        log_statevectors(result_nm, input_register, output_register)
        
        print()
        print('Measurement Result: ', result)

        print()
        print(rmz_circuit)


    def test_remove_all_zero_vector_for_two_qubits(self):
        hidden_subgroup = ['00', '01']
        self.run_remove_all_zero_circuit(hidden_subgroup, 1)

    def test_tmp(self):
        self.run_custom_circuit()
