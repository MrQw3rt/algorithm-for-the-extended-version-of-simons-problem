"""
Contains the CircuitWrapper class, which is used to keep track over all the used quantum circuits.
Furthermore, there are utility methods for constructing circuits for many quantum operations
needed in the extended version of Simon's algorithm.
"""

import math
from functools import reduce

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from qiskit.transpiler.passes import RemoveBarriers


class CircuitWrapper():
    """
    This class keeps track of all the needed quantum registers. 
    Have a look at the README for more information.
    """
    def __init__(self,
                 hidden_subgroup,
                 custom_output_register_size=None,
                 custom_ancilla_register_size=None
                 ):
        """
        Parameters:
            - hidden_subgroup is the hidden subgroup for the current instance of Simon's problem. 
              The group is assumed to be complete (i.e. a list containing all elements of the 
              hidden subgroup).
            - custom_output_register_size should be used for custom oracle implementations where 
              the oracle's output needs more qubits than the strict lower bound 
              log(2^n)//hidden_subgroup_order.
            - custom_ancilla_register_size should be used for custom oracle implementations that 
              need more ancilla qubits than the strict lower bound (total_number_of_qubits - 1) 
              needed for the multi-controlled CNOT gates.
        Returns an empty circuit with the exact number of qubits needed for running an instance of 
        Simon's problem.
        """
        n = len(hidden_subgroup[0])
        hidden_subgroup_order = len(hidden_subgroup)

        input_register_size = n
        self.input_register = QuantumRegister(n, 'in')

        coset_count = math.floor(math.log2((2 ** n) // hidden_subgroup_order))
        default_output_register_size = coset_count if hidden_subgroup_order < 2 ** n else 1
        output_register_size = custom_output_register_size or default_output_register_size
        self.output_register = QuantumRegister(output_register_size, 'out')

        blockingclause_register_size = default_output_register_size
        self.blockingclause_register = QuantumRegister(blockingclause_register_size, 'bloc')

        default_ancilla_register_size = sum([
            input_register_size, output_register_size, blockingclause_register_size, -1
        ])
        ancilla_register_size = custom_ancilla_register_size or default_ancilla_register_size
        self.ancilla_register = QuantumRegister(ancilla_register_size, 'anc')


    def get_registers(self):
        """
        Returns a 4-tuple of registers (input, output, blocking, ancilla)
        """
        return (
            self.input_register,
            self.output_register,
            self.blockingclause_register,
            self.ancilla_register
        )


    def generate_new_circuit(self, init_vector=None):
        """
        Parameters:
            - init_vector is optional. If present, the input_register of the generated circuit 
              will be initialized with this vector. init_vector is assumed to have exactly the 
              same length as all elements in hidden_subgroup.
        """
        circuit = QuantumCircuit(
            self.input_register,
            self.output_register,
            self.blockingclause_register,
            self.ancilla_register
        )
        if init_vector:
            circuit.initialize(init_vector, self.input_register)
        return circuit


def x_gate_where_bitstring_is_0(circuit, register, bitstring):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on
        - register is a main register of circuit, it is assumed to have as many qubits 
          as bitstring has bits
        - bitstring
    This method applies an X-Gate on those qubits on register, where the corresponding 
    bit in bitstring is a 0.
    """
    for s_index, bit in enumerate(bitstring):
        if bit == '0':
            circuit.x(register[register.size - s_index - 1])


def mcx_halfchain(circuit, input_register, ancilla_register):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding (all) control qubits for MCX.
        - ancilla_register holds ancilla qubits for MCX, it is assumed that we have at least two 
          fewer ancilla qubits than input qubits.
    For an n-qubit input, the halfchain circuit prepares the first (n-1) steps for an n-qubit 
    controlled X gate. The gate is described in Lemma 13 of the thesis. After the halfchain circuit 
    was applied, when we apply a CCX gate with the last input qubit and the last ancilliary qubit as
    controls, the effect is as if the CCX gate was controlled by all input qubits.
    """
    input_register_size = len(input_register)
    if input_register_size <= 2:
        return

    circuit.ccx(input_register[0], input_register[1], ancilla_register[0])
    for i in range(2, input_register_size - 1):
        circuit.ccx(input_register[i], ancilla_register[i - 2], ancilla_register[i - 1])


def reverse_mcx_halfchain(circuit, input_register, ancilla_register):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding (all) control qubits for MCX.
        - ancilla_register holds ancilla qubits for MCX, it is assumed that we have at least two
          fewer ancilla qubits than input qubits.
    Reverses the effects of the mcx_halfchain circuit.
    """
    input_register_size = len(input_register)
    if input_register_size <= 2:
        return

    for i in range(input_register_size - 2, 1, -1):
        circuit.ccx(input_register[i], ancilla_register[i - 2], ancilla_register[i - 1])
    circuit.ccx(input_register[0], input_register[1], ancilla_register[0])


def optimized_mcx(circuit, input_register, ancilla_register, target_qubits):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding (all) control qubits for MCX.
        - ancilla_register holds ancilla qubits for MCX, all ancilla qubits are assumed to 
          be in state |0>. We assume that there is exactly one fewer ancilla qubit than input 
          qubits.
        - target_qubits are the the target qubits for MCX.
    Executes MCX for each target_qubit where the control qubits are all qubits in input_register. 
    """
    mcx_halfchain(circuit, input_register, ancilla_register)

    in_register_size = input_register.size
    for target_qubit in target_qubits:
        if in_register_size == 1:
            circuit.cx(input_register[0], target_qubit)
        elif in_register_size == 2:
            circuit.ccx(input_register[0], input_register[1], target_qubit)
        else:
            circuit.ccx(
                input_register[in_register_size - 1],
                ancilla_register[in_register_size - 3],
                target_qubit
            )

    reverse_mcx_halfchain(circuit, input_register, ancilla_register)


def conditional_phase_shift_by_index(circuit, input_register, ancilla_register, index):
    """
    Parameters:
        - circuit is the quantum circuit currently being worked on.
        - input_register is the register holding inputs (e.g. for a Simon oracle).
        - ancilla_register holds at least one qubit.
        - index is the index of the input register, which we use to decide whether to perform the
          phase shift or not.
    Implements the operater S_A from https://ieeexplore.ieee.org/abstract/document/595153, Lemma 8,
    where the operator Chi is like Chi_i in Theorem 4.
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
    Implements the operator S_{0} from https://ieeexplore.ieee.org/abstract/document/595153, 
    Lemma 8. It shifts the phase of the quantum state by i precisely if the input register is 
    the all-zero vector.
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
        circuit.ccx(
            input_register[in_register_size - 1],
            ancilla_register[ancilla_register.size - 2],
            ancilla_target
        )
        circuit.s(ancilla_target)
        circuit.ccx(
            input_register[in_register_size - 1],
            ancilla_register[ancilla_register.size - 2],
            ancilla_target
        )
        reverse_mcx_halfchain(circuit, input_register, ancilla_register)

    circuit.x(input_register)


def conditional_phase_shift_by_zero_vec_entire_register(circuit, registers, ancilla_register):
    """
    Parameters:
        - circuit is the quantum circuit to which to append the phase shift gates.
        - registers is a list of registers that serve as 'control' for the phase
          shift. 
        - ancilla_register holds ancilla qubits used for the simulation of multi-controlled
          gates.
    Generates a quantum circuit that shifts the phase iff all qubits in registers hold 
    the value |0>.
    """
    def append_qubits(register, accumulator_list):
        for qubit in register:
            accumulator_list.append(qubit)
        return accumulator_list
    virtual_input_register = list(reduce(lambda a,b: append_qubits(b, a), registers, []))

    conditional_phase_shift_by_zero_vec(circuit, virtual_input_register, ancilla_register)


def remove_barriers_and_transpile_for_backend(circuit, backend):
    """
    Parameters:
        - circuit the quantum circuit we want to remove all barriers on.
        - backend the quantum computer backend we want to transpile the circuit for.
    Returns a new quantum circuit transpiled for backend.
    """
    circuit_without_barriers = RemoveBarriers()(circuit)
    return transpile(circuit_without_barriers, backend)


def run_circuit_and_measure_registers(circuit, registers, sampler):
    """
    Parameters:
        - circuit is the quantum circuit which we want to run.
        - registers are the quantum registers, which we would like to measure.
        - sampler is a SamplerV2 object used for running the circuit. Use this to
          customize the quantum computer backend or other options like the number of shots.
    Runs circuit on the backend referred to by sampler and returns the result of measuring
    registers as a counts dict. In the counts dict, registers are separated by a whitespace
    and registers are arranged in the order they are given in in the registers parameter.
    """
    total_measured_qubit_count = sum([len(r) for r in registers])
    classical_register = ClassicalRegister(total_measured_qubit_count, 'measure')
    circuit.add_register(classical_register)
    creg_size = len(classical_register)

    register_boundaries = []
    offset = 0
    for register in registers:
        register_length = len(register)
        register_boundaries.append((offset, offset + register_length))
        for i in range(register.size):
            circuit.measure(
                register[i], classical_register[creg_size - 1 - offset - (register_length - 1 - i)]
            )
        offset += register_length

    backend = sampler.backend()
    transpiled_circuit = remove_barriers_and_transpile_for_backend(circuit, backend)
    job = sampler.run([transpiled_circuit])

    def split_into_registers(key, boundaries):
        return ' '.join([key[b[0]:b[1]] for b in boundaries])

    raw_result_data = job.result()[0].data.measure.get_counts()
    return dict((split_into_registers(key, register_boundaries),raw_result_data[key])
            for key in raw_result_data.keys())
