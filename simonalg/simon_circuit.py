from .utils.circuit import CircuitWrapper


class SimonCircuit():
    def __init__(self, oracle):
        self._oracle = oracle
        self.circuit_wrapper = CircuitWrapper(self._oracle._hidden_subgroup)


    def generate_standard_simon_circuit(self):
        circuit = self.circuit_wrapper.circuit
        input_register = self.circuit_wrapper.input_register

        circuit.h(input_register)

        self._oracle.apply_to_circuit(self.circuit_wrapper)

        circuit.h(input_register)
