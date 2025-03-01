from functools import reduce

from .utils.circuit import CircuitWrapper, conditional_phase_shift_by_zero_vec, conditional_phase_shift_by_zero_vec_entire_register
from qiskit.quantum_info import Operator
from qiskit import QuantumRegister


class SimonCircuit():
    def __init__(self, oracle, custom_output_register_size=None, custom_ancilla_register_size=None):
        self._oracle = oracle
        self.circuit_wrapper = CircuitWrapper(self._oracle._hidden_subgroup, custom_output_register_size=custom_output_register_size, custom_ancilla_register_size=custom_ancilla_register_size)


    def generate_standard_simon_circuit(self):
        """
        Generates the quantum circuit proposed by Simon in https://epubs.siam.org/doi/abs/10.1137/S0097539796298637.
        """
        input_register = self.circuit_wrapper.input_register

        hadamard_circuit_1 = self.circuit_wrapper.generate_new_circuit()
        hadamard_circuit_1.h(input_register)

        oracle_circuit = self._oracle.generate_circuit(self.circuit_wrapper)

        hadamard_circuit_2 = self.circuit_wrapper.generate_new_circuit()
        hadamard_circuit_2.h(input_register)

        return self._compose_circuits([hadamard_circuit_1, oracle_circuit, hadamard_circuit_2])


    def add_blocking_clauses_for_bitstrings(self, bitstrings):
        """
        Parameters:
            - bitstrings are the bitstrings we would like to remove from a superposition. All elements
              are assumed to be non-zero and of equal length as the bitstrings of the oracle's hidden subgroup.
        Modifies the circuit according to https://ieeexplore.ieee.org/abstract/document/595153, Lemma 7.
        """
        blockingclause_circuits = [self.generate_blockingclause_circuit(bitstring, blocking_index) for blocking_index, bitstring in enumerate(bitstrings)]
        return self._compose_circuits(blockingclause_circuits)


    def generate_blockingclause_circuit(self, bitstring, blocking_index):
        """
        Parameters:
            - bitstring is the bitstring we would like to remove from a superposition. bitstring is assumed to be
              non-zero and of equal length as the bitstrings of the oracle's hidden subgroup.
            - blocking_index is a technical parameter specifying which control qubit from the blockingclause_register
              to use.
        Modifies the circuit according to https://ieeexplore.ieee.org/abstract/document/595153, Lemma 6.
        """
        indices_where_bitstring_is_1 = list(filter(lambda i: bitstring[i] == '1', range(len(bitstring))))
        j = indices_where_bitstring_is_1[0]

        circuit = self.circuit_wrapper.generate_new_circuit()
        input_register, _, blockingclause_register, _ = self.circuit_wrapper.get_registers()

        blocking_qubit = blockingclause_register[len(blockingclause_register) - 1 - blocking_index]

        circuit.cx(input_register[len(input_register) - 1 - j], blocking_qubit)
        for i in indices_where_bitstring_is_1:
            circuit.cx(blocking_qubit, input_register[len(input_register) - 1 - i])

        circuit.h(blocking_qubit)

        return circuit
    

    # TODO unused right now
    def generate_demo_forward_circuit(self):
        forward_circuit = self.circuit_wrapper.generate_new_circuit()
        input_register, output_register, blockingclause_register, ancilla_register = self.circuit_wrapper.get_registers()

        forward_circuit.h(input_register[1])
        forward_circuit.h(output_register[0])
        forward_circuit.ccx(input_register[1], output_register[0], ancilla_register[0])
        forward_circuit.z(ancilla_register[0])
        forward_circuit.ccx(input_register[1], output_register[0], ancilla_register[0])

        return forward_circuit


    # TODO unused right now 
    def generate_new_demo_forward_circuit(self):
        circuit_wrapper = CircuitWrapper(['000', '110'])
        circuit_wrapper.output_register = QuantumRegister(3)

        input_register, output_register, _, ancilla_register = circuit_wrapper.get_registers()

        # STANDARD SIMON
        forward_circuit = circuit_wrapper.generate_new_circuit()
        forward_circuit.h(input_register)

        forward_circuit.cx(input_register[0], output_register[0])
        forward_circuit.cx(input_register[1], output_register[1])
        forward_circuit.cx(input_register[2], output_register[2])

        forward_circuit.cx(input_register[1], output_register[1])
        forward_circuit.cx(input_register[1], output_register[2])

        forward_circuit.h(input_register)
        forward_circuit.save_statevector(label='0_forward')

        # CONDITIONAL PHASESHIFT BY INDEX
        phaseshift_circuit = circuit_wrapper.generate_new_circuit()
        phaseshift_circuit.s(input_register[0])
        phaseshift_circuit.save_statevector(label='1_phaseshift_by_index')

        # BACKWARD CIRCUIT
        backward_circuit = circuit_wrapper.generate_new_circuit()
        backward_circuit.h(input_register)

        backward_circuit.cx(input_register[1], output_register[2])
        backward_circuit.cx(input_register[1], output_register[1])

        backward_circuit.cx(input_register[2], output_register[2])
        backward_circuit.cx(input_register[1], output_register[1])
        backward_circuit.cx(input_register[0], output_register[0])

        backward_circuit.h(input_register)
        backward_circuit.save_statevector(label='2_backward')

        # PHASESHIFT BY ZEROVEC
        phaseshift_z = circuit_wrapper.generate_new_circuit()
        conditional_phase_shift_by_zero_vec(phaseshift_z, input_register, ancilla_register)
        phaseshift_z.save_statevector(label='3_phaseshift_by_zerovec')

        # STANDARD_SIMON
        forward_circuit_2 = circuit_wrapper.generate_new_circuit()

        forward_circuit_2.h(input_register)

        forward_circuit_2.cx(input_register[0], output_register[0])
        forward_circuit_2.cx(input_register[1], output_register[1])
        forward_circuit_2.cx(input_register[2], output_register[2])

        forward_circuit_2.cx(input_register[1], output_register[1])
        forward_circuit_2.cx(input_register[1], output_register[2])

        forward_circuit_2.h(input_register)
        forward_circuit_2.save_statevector(label='4_final_forward')

        return reduce(lambda a,b: a.compose(b), [
            forward_circuit,
            phaseshift_circuit,
            backward_circuit,
            phaseshift_z,
            forward_circuit_2
        ], circuit_wrapper.generate_new_circuit()), input_register


    def generate_remove_zero_circuit(self, bitstrings, index):
        def generate_forward_circuit():
            standard_simon_circuit = self.generate_standard_simon_circuit()
            blockingclause_circuit = self.add_blocking_clauses_for_bitstrings(bitstrings)
            return self._compose_circuits([standard_simon_circuit, blockingclause_circuit])
        
        first_forward_circuit = generate_forward_circuit()
        first_forward_circuit.save_statevector(label='1_forward')

        phaseshift_by_index_circuit = self.generate_phaseshift_by_index_circuit(index)
        phaseshift_by_index_circuit.save_statevector(label='2_phaseshift_by_index')

        backward_circuit = generate_forward_circuit().inverse()
        backward_circuit.save_statevector(label='3_backward')

        phaseshift_by_all_zero_vec_circuit = self.generate_phaseshift_by_zero_vec_circuit()
        phaseshift_by_all_zero_vec_circuit.save_statevector(label='4_phaseshift_by_zerovec')

        second_forward_circuit = generate_forward_circuit()
        second_forward_circuit.save_statevector(label='5_final_forward')
         
        return self._compose_circuits([
            first_forward_circuit,
            phaseshift_by_index_circuit,
            backward_circuit,
            phaseshift_by_all_zero_vec_circuit,
            second_forward_circuit
        ])
    

    # TODO unused, remove later
    def generate_remove_zero_operator(self, bitstrings, index):
        standard_simon_circuit = self.generate_standard_simon_circuit()
        blockingclause_circuit = self.add_blocking_clauses_for_bitstrings(bitstrings)

        forward_operator = Operator(self._compose_circuits([standard_simon_circuit, blockingclause_circuit]))
        backward_operator = forward_operator.adjoint()

        phaseshift_by_index_operator = Operator(self.generate_phaseshift_by_index_circuit(index))
        phaseshift_by_all_zero_vec_operator = Operator(self.generate_phaseshift_by_zero_vec_circuit())

        return forward_operator.compose(phaseshift_by_index_operator).compose(backward_operator).compose(phaseshift_by_all_zero_vec_operator).compose(forward_operator)


    def generate_phaseshift_by_index_circuit(self, index):
        """
        Parameters:
            - index an integer in [0, input_register size)
        Generates a circuit that shifts the global phase by i if the qubit at index 'index' is |1>.
        """
        circuit = self.circuit_wrapper.generate_new_circuit()
        input_register, _, _, _ = self.circuit_wrapper.get_registers()
        circuit.s(input_register[index])

        return circuit


    def generate_phaseshift_by_zero_vec_circuit(self):
        """
        Generates a circuit that shifts the global phase by i if the input register holds
        the all-zero bitstring.
        """
        circuit = self.circuit_wrapper.generate_new_circuit()
        input_register, output_register, blockingclause_register, ancilla_register = self.circuit_wrapper.get_registers()
        
        working_registers = [input_register, output_register, blockingclause_register]
        conditional_phase_shift_by_zero_vec_entire_register(circuit, working_registers, ancilla_register)

        return circuit


    def _compose_circuits(self, circuits):
        """
        Parameters:
            - circuits is a list of circuits which we want to compose.
        Returns a quantum circuit that is composed of the quantum circuits in circuits. The circuits get
        concatenated in the order in which they are inserted in the list.
        """
        return reduce(lambda a,b: a.compose(b), circuits, self.circuit_wrapper.generate_new_circuit())