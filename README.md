# Algorithm for Extended Version of Simon's Problem

## Setup

### Using a Virtual Environment (Recommended)

In the project root, run
```
$ python3 -m venv .venv
$ source .venv/bin/activate
```
To install the necessary packages, run
```
(.venv) $ pip3 install -r requirements.txt
```
You can always exit the virtual environment with 
```
(.venv) $ deactivate
```

### Using global Environment (Not Recommended)

Simply run
```
$ pip3 install -r requirements.txt
```
Note that the above command installs `qiskit` and `qiskit-aer` system-wide!


## Run Test Suite

To verify that everything works, you can run the test suite for the `solver` class:
```
(.venv) $ python3 -m unittest discover -s ./test -p test_solver.py
```
You can also run the entire test suite via the command
```
(.venv) $ python3 -m unittest discover -v -s ./test
```
Depending on your hardware, executing the entire test suite can take a couple of minutes.


## Quickstart

The following Python code serves as a minimal example.

```python
from qiskit_aer import AerSimulator

from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.solver import SimonSolver

hidden_subgroup = ['000', '001', '010', '011']
oracle = DefaultOracle(hidden_subgroup)

solver = SimonSolver(SimonCircuit(oracle), AerSimulator())
hidden_subgroup_basis = solver.solve()

print(hidden_subgroup_basis)
```
* The `hidden_subgroup` is given as a list of bitstrings. It is assumed that **all** bitstrings that make up the hidden subgroup are contained in the list. Use the `expand_group` method from the `simonalg.utils.grouptheory` module if you only want to specify a generating set.
* The `DefaultOracle` class automatically constructs a quantum circuit that implements a valid oracle for the hidden subgroup. For a guide on how to program your own oracle implementation, refer to [here](#oracles).
* The `SimonCircuit` class capsules functionality for creating quantum circuits needed for the extended version of Simon's problem. For details, please refer to the [implementation](./simonalg/simon_circuit.py).
* The `SimonSolver` class implements the functionality from the algorithm for the extended version of Simon's problem (Theorem 5 in [the paper by Brassard and Høyer](https://ieeexplore.ieee.org/abstract/document/595153)). For details, have a look at the [implementation](./simonalg/solver.py).

You can experiment with different hidden subgroups. You can of course also use Qiskit backends other than the `AerSimulator` from the example code. If you use a simulator, be aware that for $n \geq 4$, depending on your hardware, the simulations can get very slow, since the implementation requires many ancillary qubits.


## Writing your own Oracles


### Circuit Wrapper

This class keeps track of all the needed quantum registers. Let $H \subseteq G = \{0,1\}^n$ and let $\rho$ with $\rho : \{0,1\}^n \rightarrow \{0,1\}^m$ be a function fulfilling the promise from the extended version of Simon's problem. Then we use four quantum registers in total:
* `input_register` holds the input values for $\rho$ and is always of size $n$.
* `output_register` holds the output values for $\rho$. For $H$, there are $|G| / |H|$ cosets of $H$ in $G$. We can assign each coset a number in the range from $|G| / |H|$ and we can express $|G| / |H|$ numbers in binary notation using only $log_2(|G|/|H|)$ qubits, which is the default register size of the output_register. Should you want to program an oracle by yourself which needs more output qubits than this default number (e.g. the [CosetRepresentativeOracle](./simonalg/oracle.py)), use the `custom_output_register_size` parameter from the `CircuitWrapper` constructor.
* `blockingcause_register` is needed for the internal workings of the algorithm for the extended version of Simon's problem. While not intended, you can use this register as ancilla qubits for you custom oracle implementation, but you **must** reset **all** used qubits back to |0> after you used them.
* `ancilla_register` holds qubits needed to simulate multi-controlled gates. Its size defaults to the size of all other registers combined minus 1, which is the minimum size required by the algorithm. Should you need more ancilla qubits, use the `custom_ancilla_register_size` parameter from the `CircuitWrapper` constructor. Make sure to reset **all** ancilla qubits to |0> after you used them.

Implementation details of this class can be found [here](./simonalg/utils/circuit.py).


### Oracles

Any custom oracle implementation is just a class that has the `_hidden_subgroup` field populated (needed by the `SimonCircuit` class) and that  implements the `generate_circuit` method. Here is a template:
```python
class CustomOracle:
    def __init__(self, hidden_subgroup):
            self._hidden_subgroup = hidden_subgroup


    def generate_circuit(self, circuit_wrapper):
        input_register, output_register, _, ancilla_register = circuit_wrapper.get_registers()
        circuit = circuit_wrapper.generate_new_circuit()
        """
        TODO generate the circuit implementing the oracle here
        """
        return circuit
```
You need to make sure that the `circuit_wrapper` has sufficient qubits for the oracle implementation!


### Workflow

From start to finish, the workflow for solving the extended version of Simon's problem for your own custom oracle is as follows:

* Come up with an oracle. For example, we might pick $n = 3$ and $H = \{000, 001, 100, 101\}$. We easily calculate that the cosets of $H$ are $\{000, 001, 100, 101\}$ and $\{010, 011, 110, 111\}$. We realize that none of the bitstrings in the first coset have a $1$ at the middle qubit, but all of the bitstrings in the second coset do. Hence, it is enough to have one output qubit (which corresponds to default) and to perform a CNOT operation with the middle qubit in the input register as control and the single output qubit as target. The implementation would look something like this:
    ```python
    class SimpleOracle:
        def __init__(self, hidden_subgroup):
            self._hidden_subgroup = hidden_subgroup


        def generate_circuit(self, circuit_wrapper):
            input_register, output_register, _, ancilla_register = circuit_wrapper.get_registers()
            circuit = circuit_wrapper.generate_new_circuit()

            circuit.cx(input_register[1], output_register[0])

            return circuit
    ```
* Wrap into `SimonCircuit`. We want to use the oracle in the context of the extended version of Simon's algorithm, hence we wrap it like this:
    ```python
    hidden_subgroup = ['000', '001', '100', '101']
    simon_circuit = SimonCircuit(SimpleOracle(hidden_subgroup), custom_output_register_size=None, custom_ancilla_register_size=None)
    ```
  Note that in case our oracle would need additional qubits, we would use the `custom_output_register_size` and `custom_ancilla_register_size` parameters from the `SimonCircuit` constructor here!
* Last, we wrap everything in a `SimonSolver` object.
    ```python
    solver = SimonSolver(simon_circuit, AerSimulator())
    ```
    At this step, we could also use any other Qiskit backend than `AerSimulator`!

The entire script then has this form:
```python
from qiskit_aer import AerSimulator

from simonalg.simon_circuit import SimonCircuit
from simonalg.solver import SimonSolver

class SimpleOracle:
    def generate_circuit(self, circuit_wrapper):
        input_register, output_register, _, ancilla_register = circuit_wrapper.get_registers()
        circuit = circuit_wrapper.generate_new_circuit()

        circuit.cx(input_register[1], output_register[0])

        return circuit

hidden_subgroup = ['000', '001', '100', '101']
simon_circuit = SimonCircuit(SimpleOracle(hidden_subgroup), custom_output_register_size=None, custom_ancilla_register_size=None)
solver = SimonSolver(simon_circuit, AerSimulator())

hidden_subgroup_basis = solver.solve()
print(hidden_subgroup_basis)
```

## Logging

By default, the `SimonSolver` class writes logs to `stdout` at `INFO` level. The corresponding logger config is [here](./simonalg/utils/logging.py). You can switch the logger off like this:
```python
from simonalg.utils.logging import log
log.disabled = True
```
At `DEBUG` level, the `SimonSolver` class will additionally print out the generated quantum circuits. You can set the logger to `DEBUG` like this:
```python
from simonalg.utils.logging import log
log.setLevel('DEBUG')
```
* **Attention** most quantum circuits will be wider than your terminal and won't be displayed correctly there. I recommend piping logs containing quantum circuits into a text file, since
  there everything will be formatted correctly.
