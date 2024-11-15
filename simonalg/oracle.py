from .utils.grouptheory import generate_group_by_order, generate_cosets_for_subgroup
from .utils.circuit import x_gate_where_bitstring_is_0, optimized_mcx, generate_circuit_setup


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

    def generate_default_circuit(self):
        """
        Generates a circuit implementing the oracle. If f is the oracle function, |x> is an n-qubit register and |y> is an m-qubit register,
        the circuit performs the calculation |x>|y> -> |x>|y XOR f(y)>.
        """
        group = generate_group_by_order(self._n)
        cosets = generate_cosets_for_subgroup(group, self._hidden_subgroup)
        
        circuit, input_register, output_register, ancilla_register = generate_circuit_setup(self._n, len(self._hidden_subgroup))
        for c_index, coset in enumerate(cosets[1:]):
            for bitstring in coset:
                output_value = format(c_index + 1, f'0{output_register.size}b')

                x_gate_where_bitstring_is_0(circuit, input_register, bitstring)
                
                target_qubits = [output_register[i] for i in filter(lambda o_index: output_value[o_index] == '1', range(output_register.size))]
                optimized_mcx(circuit, input_register, ancilla_register, target_qubits)

                x_gate_where_bitstring_is_0(circuit, input_register, bitstring)
                
                circuit.barrier()

        return circuit

