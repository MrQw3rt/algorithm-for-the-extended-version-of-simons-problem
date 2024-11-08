from qiskit import ClassicalRegister, transpile
from qiskit_aer import AerSimulator

def run_circuit(circuit, measured_registers):
    for register in reversed(measured_registers):   # Reversed in order to preserve the register order in the output
        classical_register = ClassicalRegister(register.size)
        circuit.add_register(classical_register)
        for i in range(register.size):
            circuit.measure(register[i], classical_register[i])

    simulator = AerSimulator()
    transpiled_circuit = transpile(circuit, simulator)
    result = simulator.run(transpiled_circuit).result()

    return result.get_counts(transpiled_circuit)