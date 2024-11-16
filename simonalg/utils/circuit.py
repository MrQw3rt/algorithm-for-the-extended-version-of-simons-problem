import math

from qiskit import QuantumRegister, AncillaRegister, QuantumCircuit


class RegisterNames():
    INPUT = 'in'
    OUTPUT = 'out'
    ANCILLA = 'anc'
    BLOCKING = 'bloc'


class CircuitWrapper():
    def __init__(self, hidden_subgroup):
        """
        Parameters:
            - hidden_subgroup is the hidden subgroup for the current instance of Simon's problem. The group is assumed
              to be complete (i.e. a list containing all elements of the hidden subgroup).
        Returns an empty circuit with the exact number of qubits needed for running an instance of Simon's problem.
        """ 
        n = len(hidden_subgroup[0])
        hidden_subgroup_order = len(hidden_subgroup)
        
        self.input_register = QuantumRegister(n, RegisterNames.INPUT)
        output_register_size = math.floor(math.log2((2 ** n) // hidden_subgroup_order)) if hidden_subgroup_order < 2 ** n else 1
        self.output_register = QuantumRegister(output_register_size, RegisterNames.OUTPUT)
        self.ancilla_register = AncillaRegister(n - 1, RegisterNames.ANCILLA)
        self.blockingclause_register = QuantumRegister(output_register_size, RegisterNames.BLOCKING)


    def get_registers(self):
        return self.input_register, self.output_register, self.blockingclause_register, self.ancilla_register
    

    def generate_new_circuit(self, init_vector=None):
        """
        Parameters:
            - init_vector is optional. If present, the input_register of the generated circuit will be initialized with
              this vector. init_vector is assumed to have exactly the same length as all elements in hidden_subgroup.
        """
        circuit = QuantumCircuit(self.input_register, self.output_register, self.blockingclause_register, self.ancilla_register)
        if init_vector:
            circuit.initialize(init_vector, self.input_register)
        return circuit


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
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding (all) control qubits for MCX.
        - ancilla_register holds ancilla qubits for MCX, it is assumed that we have at least two fewer ancilla qubits than input qubits.
    For an n-qubit input, the halfchain circuit prepares the first (n-1) steps for an n-qubit controlled X gate. The gate is
    described in Lemma 13 of the thesis. After the halfchain circuit was applied, when we apply a CCX gate with the last input
    qubit and the last ancilliary qubit as controls, the effect is as if the CCX gate was controlled by all input qubits.
    """
    input_register_size = input_register.size
    ancilla_register_size = ancilla_register.size
    if input_register_size <= 2:
        return
    
    if ancilla_register_size + 2 < input_register.size:
        raise Exception(f'Ancilla register is too small: an input register of size {input_register_size} requires at least {input_register_size} + 2 ancilla qubits!')

    circuit.ccx(input_register[0], input_register[1], ancilla_register[0])
    for i in range(2, input_register.size - 1):
        circuit.ccx(input_register[i], ancilla_register[i - 2], ancilla_register[i - 1])


def reverse_mcx_halfchain(circuit, input_register, ancilla_register):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding (all) control qubits for MCX.
        - ancilla_register holds ancilla qubits for MCX, it is assumed that we have at least two fewer ancilla qubits than input qubits.
    Reverses the effects of the mcx_halfchain circuit.
    """
    if input_register.size <= 2:
        return
    
    for i in range(input_register.size - 2, 1, -1):
        circuit.ccx(input_register[i], ancilla_register[i - 2], ancilla_register[i - 1])
    circuit.ccx(input_register[0], input_register[1], ancilla_register[0])


def optimized_mcx(circuit, input_register, ancilla_register, target_qubits):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding (all) control qubits for MCX.
        - ancilla_register holds ancilla qubits for MCX, all ancilla qubits are assumed to be in state |0>.
          We assume that there is exactly one fewer ancilla qubit than input qubits.
        - target_qubits are the the target qubits for MCX.
    Executes MCX for each target_qubit where the control qubits are all qubits in input_register. 
    """
    mcx_halfchain(circuit, input_register, ancilla_register)
    circuit.barrier()

    in_register_size = input_register.size
    for target_qubit in target_qubits:
        if in_register_size == 1:
            circuit.cx(input_register[0], target_qubit)
        elif in_register_size == 2:
            circuit.ccx(input_register[0], input_register[1], target_qubit)
        else:
            circuit.ccx(input_register[in_register_size - 1], ancilla_register[in_register_size - 3], target_qubit)
    
    circuit.barrier()
    reverse_mcx_halfchain(circuit, input_register, ancilla_register)


def conditional_phase_shift_by_index(circuit, input_register, ancilla_register, index):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding inputs (e.g. for a Simon oracle).
        - ancilla_register holds at least one qubit.
        - index is the index of the input register, which we use to decide whether to perform the phase shift or not.
    Implements the operater S_A from https://ieeexplore.ieee.org/abstract/document/595153, Lemma 8, where the operator
    Chi is like Chi_i in Theorem 4.
    """
    control_qubit = input_register[index]
    target_qubit = ancilla_register[0]
    
    circuit.cx(control_qubit, target_qubit)
    circuit.s(target_qubit)
    circuit.cx(control_qubit, target_qubit)


def conditional_phase_shift_by_zero_vec(circuit, input_register, ancilla_register):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding inputs (e.g. for a Simon oracle).
        - ancilla_register holds ancilla qubits for both MCX and the conditional phase shift.
          We must have at least as many ancilla qubits as input qubits (n-1 for MCX and one
          for the phase shift).
    Implements the operator S_{0} from https://ieeexplore.ieee.org/abstract/document/595153, Lemma 8. It
    shifts the phase of the quantum state by i precisely if the input register is the all-zero vector.
    """
    ancilla_target = ancilla_register[len(ancilla_register) - 1]
    in_register_size = len(input_register)

    circuit.x(input_register)

    if in_register_size == 1:
        circuit.s(input_register[0])
    elif in_register_size == 2:
        circuit.ccx(input_register[0], input_register[1], ancilla_target)
        circuit.s(ancilla_target)
        circuit.ccx(input_register[0], input_register[1], ancilla_target)
    else:
        mcx_halfchain(circuit, input_register, ancilla_register)
        circuit.ccx(input_register[in_register_size - 1], ancilla_register[ancilla_register.size - 2], ancilla_target)
        circuit.s(ancilla_target)
        circuit.ccx(input_register[in_register_size - 1], ancilla_register[ancilla_register.size - 2], ancilla_target)
        reverse_mcx_halfchain(circuit, input_register, ancilla_register)

    circuit.x(input_register)