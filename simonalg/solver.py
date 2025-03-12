from qiskit import ClassicalRegister, transpile

from simonalg.postprocessing import convert_to_basis_of_hidden_subgroup
from simonalg.utils.logging import log

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
        Implements the algorithm from the proof of Theorem 4 in https://ieeexplore.ieee.org/abstract/document/595153. For multi-shot
        quantum computer calls, we always take the bitstring that has been measured most often.
        """
        simon_circuit = self._simon_circuit
        input_register = simon_circuit.circuit_wrapper.get_registers()[0]
        working_indices = set(range(self._n)).difference(blocked_indices)

        for i in working_indices:
            log.info(f'Generating quantum circuit with the following parameters: Y={Y}, good_state_index={i}, blocked_indices={blocked_indices}')
            circuit = simon_circuit.generate_remove_zero_circuit(Y, i)
            log.debug(f'\n{circuit.draw(fold=-1)}')
            quantum_result = self._run_circuit(circuit, input_register)
            log.info(f'Raw quantum result is: {quantum_result}')

            measured_elements = list(quantum_result.keys())
            measured_elements.sort(key=lambda e: quantum_result[e], reverse=True)
            new_element = measured_elements[0]

            log.info(f'Picked the quantum result with highest count: {new_element}')
            blocked_indices.add(i)
            log.info(f'Added index {i} to blocked indices')
            if new_element[self._n - 1 - i] == '1':
                log.info(f'The quantum routine yielded a bitstring with 1 at index {i}')
                return (new_element, i)
            elif new_element != self._zerovec:
                string_indices_where_element_is_1 = filter(lambda i: (new_element[i] == '1'), range(len(new_element)))
                register_indices_where_element_is_1 = [self._n - 1 - index for index in string_indices_where_element_is_1]
                free_register_indices_where_element_is_1 = list(filter(lambda index: index not in blocked_indices, register_indices_where_element_is_1))
                blocking_index = free_register_indices_where_element_is_1[-1]

                blocked_indices.add(blocking_index)
                log.info(f'The quantum routine did not yield a bitstring with 1 at index {i}, but it yielded a different bitstring with 1 at index {blocking_index}')
                log.info(f'Added index {blocking_index} to blocked indices')
                return (new_element, blocking_index)
            log.info(f'The quantum routine yielded the zerovector for working index {i}')

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
        return [y[0] for y in Y]
            

    def solve(self):
        """
        Implements the algorithm from the proof of Theorem 5 in https://ieeexplore.ieee.org/abstract/document/595153.
        """
        log.info(f'[STARTED] Extended version of Simon\'s algorithm for hidden subgroup {self._simon_circuit._oracle._hidden_subgroup}')
        basis_of_orthogonal_subgroup = self.generate_basis_of_orthogonal_subgroup()
        log.info(f'Basis of orthogonal subgroup is {basis_of_orthogonal_subgroup}')
        basis_of_hidden_subgroup = convert_to_basis_of_hidden_subgroup(basis_of_orthogonal_subgroup, self._n)

        log.info(f'[FINISHED] Reconstruction of hidden subgroup {basis_of_hidden_subgroup}')
        return basis_of_hidden_subgroup
