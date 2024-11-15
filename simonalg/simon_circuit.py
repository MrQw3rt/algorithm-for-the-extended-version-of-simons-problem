from .utils.circuit import CircuitWrapper


class SimonCircuit():
    def __init__(self, oracle):
        self._oracle = oracle
        self.circuit_wrapper = CircuitWrapper(self._oracle._hidden_subgroup)


    def generate_standard_simon_circuit(self):
        """
        Generates the quantum circuit proposed by Simon in https://epubs.siam.org/doi/abs/10.1137/S0097539796298637.
        """

        circuit = self.circuit_wrapper.circuit
        input_register = self.circuit_wrapper.input_register

        circuit.h(input_register)

        self._oracle.apply_to_circuit(self.circuit_wrapper)

        circuit.h(input_register)


    def add_blocking_clauses_for_bitstrings(self, bitstrings):
        """
        Parameters:
            - bitstrings are the bitstrings we would like to remove from a superposition. All elements
              are assumed to be non-zero and of equal length as the bitstrings of the oracle's hidden subgroup.
        Modifies the circuit according to https://ieeexplore.ieee.org/abstract/document/595153, Lemma 7.
        """
        for blocking_index, bitstring in enumerate(bitstrings):
            self.add_blocking_clause_for_bitstring(bitstring, blocking_index)


    def add_blocking_clause_for_bitstring(self, bitstring, blocking_index):
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

        circuit, input_register, _, blockingclause_register, _ = self.circuit_wrapper.get()

        blocking_qubit = blockingclause_register[len(blockingclause_register) - 1 - blocking_index]

        circuit.cx(input_register[len(input_register) - 1 - j], blocking_qubit)
        for i in indices_where_bitstring_is_1:
            circuit.cx(blocking_qubit, input_register[len(input_register) - 1 - i])

        circuit.h(blocking_qubit)
 
