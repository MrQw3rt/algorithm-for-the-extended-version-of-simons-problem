"""
Contains the SimonCircuit class, which capsules functionality for generating the circuits needed
for the implementation of Simon's algorithm.
"""

from functools import reduce

from qiskit_aer.library import save_statevector

from .utils.circuit import CircuitWrapper, conditional_phase_shift_by_zero_vec_entire_register


class SimonCircuit():
    """
    Capsules functionality for generating the circuits for the implementation of Simon's algorithm.
    """
    def __init__(self, oracle, custom_output_register_size=None, custom_ancilla_register_size=None):
        self._oracle = oracle
        self.circuit_wrapper = CircuitWrapper(
            self._oracle._hidden_subgroup,
            custom_output_register_size=custom_output_register_size,
            custom_ancilla_register_size=custom_ancilla_register_size
        )


    def generate_standard_simon_circuit(self):
        """
        Generates the quantum circuit proposed by Simon in 
        https://epubs.siam.org/doi/abs/10.1137/S0097539796298637.
        """
        input_register = self.circuit_wrapper.input_register

        hadamard_circuit_1 = self.circuit_wrapper.generate_new_circuit()
        hadamard_circuit_1.h(input_register)

        oracle_circuit = self._oracle.generate_circuit(self.circuit_wrapper)

        hadamard_circuit_2 = self.circuit_wrapper.generate_new_circuit()
        hadamard_circuit_2.h(input_register)

        return self._compose_circuits([hadamard_circuit_1, oracle_circuit, hadamard_circuit_2])


    def add_blocking_clauses(self, blockingclauses):
        """
        Parameters:
            - blockingclauses are tuples of the form (bitstring, j) where bitstring is the bistring
              we would like to remove from a superposition and j is the index where bitstring is 1 
              according to Lemma 6 of https://ieeexplore.ieee.org/abstract/document/595153. 
              bitstring is assumed to be of equal length as the bitstrings of the oracle's hidden 
              subgroup.
        Modifies the circuit according to https://ieeexplore.ieee.org/abstract/document/595153, 
        Lemma 7.
        """
        blockingclause_circuits = [self.generate_blockingclause_circuit(bitstring, blocking_index)
            for blocking_index, bitstring in enumerate(blockingclauses)]
        return self._compose_circuits(blockingclause_circuits)


    def generate_blockingclause_circuit(self, blockingclause, blocking_index):
        """
        Parameters:
            - blockingclause is a tuple of the form (bitstring, j) where bitstring is the bistring
              we would like to remove from a superposition and j is the index where bitstring is 1 
              according to Lemma 6 of https://ieeexplore.ieee.org/abstract/document/595153. 
              bitstring is assumed to be of equal length as the bitstrings of the oracle's hidden 
              subgroup.
            - blocking_index is a technical parameter specifying which control qubit from the 
              blockingclause_register to use.
        Modifies the circuit according to https://ieeexplore.ieee.org/abstract/document/595153,
        Lemma 6.
        """
        bitstring, j = blockingclause
        indices_where_bitstring_is_1 = list(
            filter(lambda i: bitstring[i] == '1', range(len(bitstring)))
        )

        circuit = self.circuit_wrapper.generate_new_circuit()
        input_register, _, blockingclause_register, _ = self.circuit_wrapper.get_registers()

        blocking_qubit = blockingclause_register[len(blockingclause_register) - 1 - blocking_index]

        circuit.cx(input_register[j], blocking_qubit)
        for i in indices_where_bitstring_is_1:
            circuit.cx(blocking_qubit, input_register[len(input_register) - 1 - i])

        circuit.h(blocking_qubit)

        return circuit


    def generate_remove_zero_circuit(self, blockingclauses, index, for_aer_simulator=False):
        """
        Parameters:
            - blockingclauses are tuples of the form (bitstring, j) where bitstring is the bistring
              we would like to remove from a superposition and j is the index where bitstring is 1 
              according to Lemma 6 of https://ieeexplore.ieee.org/abstract/document/595153. 
              bitstring is assumed to be of equal length as the bitstrings of the oracle's hidden 
              subgroup.
            - index specifies which states to mark for amplitude amplification. All states with a 
              1 at index are 'good' states and the rest are the 'bad' states. We assume 
              0 <= index < len(bitstring) for each bitstring in bitstrings.
            - for_aer_simulator is a technical parameter used for testing/debugging. If set to True,
              after each amplitude amplification step, the statevector will be logged. This is only
              available when using the AER-Simulator and does not work with any 'productive' 
              backend.
        Implements the quantum algorithm Q_i from 
        https://ieeexplore.ieee.org/abstract/document/595153, Theorem 4.
        """
        def generate_forward_circuit():
            standard_simon_circuit = self.generate_standard_simon_circuit()
            blockingclause_circuit = self.add_blocking_clauses(blockingclauses)
            return self._compose_circuits([standard_simon_circuit, blockingclause_circuit])

        first_forward_circuit = generate_forward_circuit()
        phaseshift_by_index_circuit = self.generate_phaseshift_by_index_circuit(index)
        backward_circuit = generate_forward_circuit().inverse()
        phaseshift_by_all_zero_vec_circuit = self.generate_phaseshift_by_zero_vec_circuit()
        second_forward_circuit = generate_forward_circuit()

        labels = [
            '1_forward', 
            '2_phaseshift_by_index', 
            '3_backward', 
            '4_phaseshift_by_zerovec', 
            '5_final_forward'
        ]
        circuits = [
            first_forward_circuit,
            phaseshift_by_index_circuit,
            backward_circuit,
            phaseshift_by_all_zero_vec_circuit,
            second_forward_circuit
        ]
        for circuit, label in zip(circuits, labels):
            if for_aer_simulator:
                save_statevector(circuit, label=label)
            else:
                circuit.barrier(label=label)

        return self._compose_circuits(circuits)


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
        registers = self.circuit_wrapper.get_registers()
        input_register, output_register, blockingclause_register, ancilla_register = registers

        working_registers = [input_register, output_register, blockingclause_register]
        conditional_phase_shift_by_zero_vec_entire_register(
            circuit, working_registers, ancilla_register
        )

        return circuit


    def _compose_circuits(self, circuits):
        """
        Parameters:
            - circuits is a list of circuits which we want to compose.
        Returns a quantum circuit that is composed of the quantum circuits in circuits. The circuits 
        get concatenated in the order in which they are inserted in the list.
        """
        def compose(a, b):
            return a.compose(b)
        return reduce(compose, circuits, self.circuit_wrapper.generate_new_circuit())
