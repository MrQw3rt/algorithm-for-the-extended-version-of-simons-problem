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


    def get_new_orthogonal_subgroup_element(self, Y=[], blocked_indices=set()):
        """
        Parameters:
            - Y is the list of orthogonal subgroup elements we have already sampled.
            - blocked_indices are those indices for which we already executed a quantum circuit
              and where we are hence guaranteed to not find a fresh element of the basis of the
              orthogonal subgroup.
        Implements the algorithm from the proof of Theorem 4 in https://ieeexplore.ieee.org/abstract/document/595153.
        """
        simon_circuit = self._simon_circuit
        input_register = simon_circuit.circuit_wrapper.get_registers()[0]
        working_indices = set(range(self._n)).difference(blocked_indices)

        for i in working_indices:
            log.info(f'Generating quantum circuit with the following parameters: Y={Y}, index={i}, blocked_indices={blocked_indices}')
            circuit = simon_circuit.generate_remove_zero_circuit(Y, i)
            log.debug(f'Generated quantum circuit is: \n{circuit}')
            quantum_result = self._run_circuit(circuit, input_register)
            log.info(f'Raw quantum result is: {quantum_result}')

            new_element = list(quantum_result.keys())[0]
            log.info(f'Picked the following quantum result: {new_element}')
            if new_element[self._n - 1 - i] == '1':
                blocked_indices.add(i)
                log.info(f'Added index {i} to blocked indices')
                return new_element
            elif new_element != self._zerovec:
                index_where_element_is_1 = list(filter(lambda i: new_element[i] == '1', range(len(new_element))))[-1]
                blocked_indices.add(index_where_element_is_1)
                log.info(f'Added index {index_where_element_is_1} to blocked indices')
                return new_element

        log.info('Quantum algorithm returned the zerovector for all working indices')
        return self._zerovec
    

    def generate_basis_of_orthogonal_subgroup(self):
        """
        Implements the first stage of the algorithm from the proof of Theorem 5 in https://ieeexplore.ieee.org/abstract/document/595153.
        """
        Y = []
        blocked_indices = set()
        
        done = False
        while not done:
            orthogonal_subgroup_element = self.get_new_orthogonal_subgroup_element(Y=Y, blocked_indices=blocked_indices)
            if orthogonal_subgroup_element != self._zerovec:
                Y.append(orthogonal_subgroup_element)
            else:
                done = True
        return Y
            

    def solve(self):
        """
        Implements the algorithm from the proof of Theorem 5 in https://ieeexplore.ieee.org/abstract/document/595153.
        """
        basis_of_orthogonal_subgroup = self.generate_basis_of_orthogonal_subgroup()
        log.info(f'Basis of orthogonal subgroup is {basis_of_orthogonal_subgroup}')
        basis_of_hidden_subgroup = convert_to_basis_of_hidden_subgroup(basis_of_orthogonal_subgroup, self._n)

        return basis_of_hidden_subgroup
