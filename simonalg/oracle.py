from .utils.grouptheory import generate_group_by_order, generate_cosets_for_subgroup
from .utils.circuit import x_gate_where_bitstring_is_0, optimized_mcx


class DefaultOracle:
    def __init__(self, hidden_subgroup):
        """
        Parameters:
            - hidden_subgroup is a list of state vectors of the form ['000', '001']. This is supposed to be the entire hidden subgroup.
              It is assumed that the list of state vectors is non-empty.
        """
        self._hidden_subgroup = hidden_subgroup
        self._hidden_subgroup_order = len(self._hidden_subgroup)
        self._n = len(hidden_subgroup[0])
        

    def generate_circuit(self, circuit_wrapper):
        """
        Parameters:
             - circuit_wrapper is the circuit to which we apply (append) the oracle circuit
        Generates a circuit implementing the oracle. If f is the oracle function, |x> is an n-qubit register and |y> is an m-qubit register,
        the circuit performs the calculation |x>|y> -> |x>|y XOR f(y)>. The generated oracle circuit is appended to the circuit from circuit_wrapper.
        """
        input_register, output_register, _, ancilla_register = circuit_wrapper.get_registers()
        circuit = circuit_wrapper.generate_new_circuit()

        group = generate_group_by_order(self._n)
        cosets = generate_cosets_for_subgroup(group, self._hidden_subgroup)
        for c_index, coset in enumerate(cosets[1:]):
            for bitstring in coset:
                output_value = format(c_index + 1, f'0{output_register.size}b')

                x_gate_where_bitstring_is_0(circuit, input_register, bitstring)
                
                target_qubits = [output_register[i] for i in filter(lambda o_index: output_value[o_index] == '1', range(output_register.size))]
                optimized_mcx(circuit, input_register, ancilla_register, target_qubits)

                x_gate_where_bitstring_is_0(circuit, input_register, bitstring)
                
                circuit.barrier()

        return circuit
    

class CosetRepresentativeOracle():
    def __init__(self, hidden_subgroup):
        """
        Parameters:
            - hidden_subgroup is a list of state vectors of length 2 of the form ['000', '001']. This is supposed to be the entire hidden subgroup.
              It is assumed that the list of state vectors is non-empty.
        Generates a circuit implementing an oracle for the standard version of Simon's problem. That is, the
        hidden subgroup is of order 2.
        """
        self._hidden_subgroup = hidden_subgroup
        self._hidden_subgroup_order = len(self._hidden_subgroup)
        self._n = len(hidden_subgroup[0])

    
    def generate_circuit(self, circuit_wrapper):
        """
        Parameters:
            - circuit_wrapper is the circuit to which we apply (append) the oracle circuit
        Generates a circuit implementing the oracle by performing the state transition |x>|y> -> |x>|y XOR (s XOR x)>
        if x_i = 1 where i is the least significant index where the secret string s from the hidden subgroup is 1.
        Otherwise, the oracle performs the state change |x>|y> -> |x>|y XOR x>.
        The generated oracle circuit is appended to the circuit from circuit_wrapper.
        """
        input_register, output_register, _, _ = circuit_wrapper.get_registers()
        circuit = circuit_wrapper.generate_new_circuit()
        input_register_size = len(input_register)

        s = list(filter(lambda h: h != '0' * self._n, self._hidden_subgroup))[0]
        def map_to_indices_with_1(bitstring):
            return set(filter(lambda index: bitstring[self._n - index - 1] == '1', range(0, self._n)))
        indices_where_s_is_1 = map_to_indices_with_1(s)
        least_significant_index_where_s_is_1 = min(indices_where_s_is_1)

        for i in range(input_register_size):
            circuit.cx(input_register[i], output_register[i])
        for i in indices_where_s_is_1:
            circuit.cx(input_register[least_significant_index_where_s_is_1], output_register[i])

        return circuit