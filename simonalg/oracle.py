import math
from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister

from .utils.grouptheory import generate_group_by_order, generate_cosets_for_subgroup
from .utils.circuit import x_gate_where_bitstring_is_0


class SimonOracle:
    def __init__(self, hidden_subgroup, ):
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
        input_register = QuantumRegister(self._n, 'x')
        output_register_size = math.floor(math.log2((2 ** self._n) // self._hidden_subgroup_order))
        output_register = QuantumRegister(output_register_size, 'y')
        ancilla_register = AncillaRegister(self._n - 2, 'anc')

        group = generate_group_by_order(self._n)
        cosets = generate_cosets_for_subgroup(group, self._hidden_subgroup)
        
        circuit = QuantumCircuit(input_register, output_register, ancilla_register)
        for c_index, coset in enumerate(cosets[1:]):
            for bitstring in coset:
                x_gate_where_bitstring_is_0(circuit, input_register, bitstring)

                output_value = format(c_index + 1, f'0{output_register_size}b')
                for o_index, bit in enumerate(output_value):
                    if bit == '1':
                        circuit.mcx(input_register, output_register[o_index], mode='v-chain', ancilla_qubits=ancilla_register)

                x_gate_where_bitstring_is_0(circuit, input_register, bitstring)
                
                circuit.barrier()

        return circuit

