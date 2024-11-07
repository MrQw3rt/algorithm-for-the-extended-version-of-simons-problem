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

def mcx_halfchain(circuit, input_register, ancilla_register):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on
        - input_register is the register holding (all) control qubits for MCX
        - ancilla_register holds ancilla qubits for MCX, it is assumed that we have exactly one fewer ancilla qubit than
          control qubits
    For an n-qubit input, the halfchain circuit prepares the first (n-1) steps for an n-qubit controlled X gate. The gate is
    described in Lemma 13 of the thesis. After the halfchain circuit was applied, when we apply a CCX gate with the last input
    qubit and the last ancilliary qubit as controls, the effect is as if the CCX gate was controlled by all input qubits.
    """
    if input_register.size <= 2:
         return
    
    circuit.ccx(input_register[0], input_register[1], ancilla_register[0])
    for i in range(2, input_register.size - 1):
         circuit.ccx(input_register[i], ancilla_register[i - 2], ancilla_register[i - 1])
