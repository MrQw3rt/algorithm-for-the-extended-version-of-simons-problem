import logging
log = logging.getLogger(__name__)

from qiskit import ClassicalRegister, transpile

from simonalg.postprocessing import convert_to_basis_of_hidden_subgroup


class SimonSolver:
    def __init__(self, simon_circuit, backend):
        self._simon_circuit = simon_circuit
        self._backend = backend
        self._n = len(simon_circuit.circuit_wrapper.input_register)
        self._zerovec = '0' * self._n


    def _run_circuit(self, circuit, input_register):
        classical_register = ClassicalRegister(input_register.size)
        circuit.add_register(classical_register)
        for i in range(input_register.size):
            circuit.measure(input_register[i], classical_register[i])
            
        transpiled_circuit = transpile(circuit, self._backend)
        result = self._backend.run(transpiled_circuit).result()

        return result.get_counts(transpiled_circuit)


    def get_new_orthogonal_subgroup_element(self, y=[], blocked_indices=set()):
        simon_circuit = self._simon_circuit
        input_register = simon_circuit.circuit_wrapper.get_registers()[0]
        working_indices = set(range(self._n)).difference(blocked_indices)

        for i in working_indices:
            log.info(f'Generating quantum circuit with the following parameters: y={y}, index={i}')
            circuit = simon_circuit.generate_remove_zero_circuit(y, i)
            log.debug(f'Generated quantum circuit is: \n{circuit}')
            quantum_result = self._run_circuit(circuit, input_register)
            log.info(f'Raw quantum result is: {quantum_result}')

            blocked_indices.add(i)
            new_element = list(quantum_result.keys())[0]
            log.info(f'Picked quantum result is: {new_element}')
            if new_element != self._zerovec:
                return new_element
        return self._zerovec
    

    def generate_basis_of_orthogonal_subgroup(self):
        y = []
        blocked_indices = set()
        
        done = False
        while not done:
            orthogonal_subgroup_element = self.get_new_orthogonal_subgroup_element(y=y, blocked_indices=blocked_indices)
            if orthogonal_subgroup_element != self._zerovec:
                y.append(orthogonal_subgroup_element)
            else:
                done = True
        return y
            

    def solve(self):
        basis_of_orthogonal_subgroup = self.generate_basis_of_orthogonal_subgroup()
        log.info(f'Basis of orthogonal subgroup is {basis_of_orthogonal_subgroup}')
        basis_of_hidden_subgroup = convert_to_basis_of_hidden_subgroup(basis_of_orthogonal_subgroup, self._n)

        return basis_of_hidden_subgroup
