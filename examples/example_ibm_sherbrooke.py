from qiskit_ibm_runtime import SamplerV2, QiskitRuntimeService

from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.solver import SimonSolver

hidden_subgroup = ['000', '001', '010', '011']
oracle = DefaultOracle(hidden_subgroup)


API_TOKEN = 'TODO_YOUR_IBM_API_KEY_GOES_HERE'
service = QiskitRuntimeService(token=API_TOKEN, channel='ibm_quantum')
backend = service.backend('ibm_sherbrooke')

solver = SimonSolver(SimonCircuit(oracle), sampler=SamplerV2(backend))
hidden_subgroup_basis = solver.solve()
