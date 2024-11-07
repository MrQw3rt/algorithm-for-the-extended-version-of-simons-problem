def x_gate_where_bitstring_is_0(circuit, register, bitstring):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on
        - register is a main register of circuit, it is assumed to have as many qubits as bitstring has bits
        - bitstring
    This method applies an X-Gate on those qubits on register, where the corresponding bit in bitstring is a 0.
    """
    for s_index, bit in enumerate(bitstring):
            if bit == '0':
                circuit.x(register[register.size - s_index - 1])
                