from .utils.grouptheory import generate_group_by_order, generate_cosets_for_subgroup
from .utils.circuit import x_gate_where_bitstring_is_0, optimized_mcx


class SimonOracle:
    def __init__(self, hidden_subgroup):
        """
        Parameters:
            - hidden_subgroup is a list of state vectors of the form ['000', '001']. This is supposed to be the entire hidden subgroup.
              It is assumed that the list of state vectors is non-empty.
        """
        self._hidden_subgroup = hidden_subgroup
        self._hidden_subgroup_order = len(self._hidden_subgroup)
        self._n = len(hidden_subgroup[0])
    

    def apply_to_circuit(self, circuit_wrapper):
        """
        Parameters:
             - circuit_wrapper is the circuit to which we apply (append) the oracle circuit
        Generates a circuit implementing the oracle. If f is the oracle function, |x> is an n-qubit register and |y> is an m-qubit register,
        the circuit performs the calculation |x>|y> -> |x>|y XOR f(y)>. The generated oracle circuit is appended to the circuit from circuit_wrapper.
        """
        circuit, input_register, output_register, _, ancilla_register = circuit_wrapper.get()

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
