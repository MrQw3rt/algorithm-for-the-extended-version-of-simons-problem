"""
Contains the SimonSolver class, the 'solve' method of which implements
the algorithm from the proof of Theorem 5 in https://ieeexplore.ieee.org/abstract/document/595153.
"""

from simonalg.postprocessing import convert_to_basis_of_hidden_subgroup
from simonalg.utils.logging import log
from simonalg.utils.circuit import run_circuit_and_measure_registers


class ValidationException(Exception):
    pass


class SimonSolver:
    """
    Encapsules functionality to solve an instance of the extended version of Simon's problem.
    Contains implementations for Theorem 4 and Theorem 5 of 
    https://ieeexplore.ieee.org/abstract/document/595153.
    """
    def __init__(self, simon_circuit, sampler=None, backend=None, validate_new_elements=True):
        """
        Parameters:
            - simon_circuit an instance of the SimonCircuit class.
            - sampler is a SamplerV2 object used for running the circuit via the Primitives V2 API. 
              See https://docs.quantum.ibm.com/api/qiskit/primitives for details. This is needed 
              if you want to execute quantum circuits on IBM hardware.
            - backend is a Qiskit Backend object used for running the circuit via the backend.run
              API. See https://docs.quantum.ibm.com/api/qiskit/providers for details. In principle, 
              the backend.run API is deprecated but some non-IBM providers have not migrated yet. 
              Use this if you want to execute quantum circuits on e.g. IonQ hardware.
            - validate_new_elements set this to True if you want to check whether
              all bitstrings sampled by the quantum routine are linearly independent after
              each quantum circuit run. Intended to be used when testing on noisy NISQ hardware.
              If sampled vectors are not linearly independent, an exception is thrown and the
              solver aborts.
        The solver expects either sampler of backend to be present, but not both.
        """
        self._simon_circuit = simon_circuit
        self._sampler = sampler
        self._backend = backend
        self._n = len(simon_circuit.circuit_wrapper.input_register)
        self._zerovec = '0' * self._n
        self._validate_new_elements = validate_new_elements


    def _run_circuit(self, circuit, input_register):
        return run_circuit_and_measure_registers(
            circuit, [input_register], sampler=self._sampler, backend=self._backend
        )


    def _get_most_probable_result(self, quantum_result):
        measured_elements = list(quantum_result.keys())
        measured_elements.sort(key=lambda e: quantum_result[e], reverse=True)
        return measured_elements[0]


    def _get_good_state_index(self, new_element, blocked_indices):
        string_indices_where_element_is_1 = filter(
            lambda i: (new_element[i] == '1'), range(len(new_element))
        )
        register_indices_where_element_is_1 = [self._n - 1 - index
                                               for index in string_indices_where_element_is_1]
        free_register_indices_where_element_is_1 = list(filter(
            lambda index: index not in blocked_indices, register_indices_where_element_is_1
        ))
        return free_register_indices_where_element_is_1[-1]


    def _validate_new_element(self, new_element, blocked_indices):
        is_zero_on_all_blocked_indices = all(
            new_element[self._n - 1 - bi] == '0' for bi in blocked_indices
        )
        if is_zero_on_all_blocked_indices:
            return

        log.error(
                'Measured an element that should have been blocked. '
                'This is most likely due to a noisy quantum backend. Aborting the algorithm.'
            )
        raise ValidationException(
            f'Bitstring {new_element} was measured despite '
            'blocked indices {blocked_indices}.'
        )


    def get_new_orthogonal_subgroup_element(self, y=None, blocked_indices=None):
        """
        Parameters:
            - Y is the list of orthogonal subgroup elements we have already sampled.
            - blocked_indices are those indices for which we already executed a quantum circuit
              and where we are hence guaranteed to not find a fresh element of the basis of the
              orthogonal subgroup.
        Implements the algorithm from the proof of Theorem 4 in 
        https://ieeexplore.ieee.org/abstract/document/595153. For multi-shot quantum computer calls, 
        we always take the bitstring that has been measured most often.
        """
        if y is None:
            y = []
        if blocked_indices is None:
            blocked_indices = set()

        simon_circuit = self._simon_circuit
        input_register = simon_circuit.circuit_wrapper.get_registers()[0]
        working_indices = set(range(self._n)).difference(blocked_indices)

        for i in working_indices:
            log.info(
                'Generating quantum circuit with the following parameters:'
                ' Y=%s, good_state_index=%d, blocked_indices=%s',
                y, i, blocked_indices
            )
            circuit = simon_circuit.generate_remove_zero_circuit(y, i)
            log.debug('\n%s', circuit.draw(fold=-1))
            quantum_result = self._run_circuit(circuit, input_register)
            log.info('Raw quantum result is: %s', quantum_result)

            new_element = self._get_most_probable_result(quantum_result)
            log.info('Picked the quantum result with highest count: %s', new_element)
            if self._validate_new_elements:
                self._validate_new_element(new_element, blocked_indices)

            blocked_indices.add(i)
            log.info('Added index %d to blocked indices', i)

            if new_element[self._n - 1 - i] == '1':
                log.info('The quantum routine yielded a bitstring with 1 at index %s', i)
                return (new_element, i)
            if new_element != self._zerovec:
                blocking_index = self._get_good_state_index(new_element, blocked_indices)
                blocked_indices.add(blocking_index)
                log.info(
                    'The quantum routine did not yield a bitstring with 1 at index %d, '
                    'but it yielded a different bitstring with 1 at index %d', 
                    i, blocking_index
                )
                log.info('Added index %d to blocked indices', blocking_index)
                return (new_element, blocking_index)
            log.info('The quantum routine yielded the zerovector for working index %d', i)

        log.info('Quantum algorithm returned the zerovector for all working indices')
        return self._zerovec


    def generate_basis_of_orthogonal_subgroup(self):
        """
        Implements the first stage of the algorithm from the proof of Theorem 5 
        in https://ieeexplore.ieee.org/abstract/document/595153.
        """
        y = []
        blocked_indices = set()

        done = False
        while not done:
            orthogonal_subgroup_element = self.get_new_orthogonal_subgroup_element(
                y=y, blocked_indices=blocked_indices
            )
            if orthogonal_subgroup_element != self._zerovec:
                y.append(orthogonal_subgroup_element)
            else:
                done = True
        return [y[0] for y in y]


    def solve(self):
        """
        Implements the algorithm from the proof of Theorem 5 in 
        https://ieeexplore.ieee.org/abstract/document/595153.
        """
        log.info('[STARTED] Extended version of Simon\'s algorithm')
        try:
            basis_of_orthogonal_subgroup = self.generate_basis_of_orthogonal_subgroup()
        except ValidationException:
            log.error('[ABORTED]')
            return None

        log.info('Basis of orthogonal subgroup is %s', basis_of_orthogonal_subgroup)
        basis_of_hidden_subgroup = convert_to_basis_of_hidden_subgroup(
            basis_of_orthogonal_subgroup, self._n
        )

        log.info('[FINISHED] Reconstruction of hidden subgroup %s', basis_of_hidden_subgroup)
        return basis_of_hidden_subgroup
