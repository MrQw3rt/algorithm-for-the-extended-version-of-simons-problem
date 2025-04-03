from qiskit_ionq import IonQProvider
from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.solver import SimonSolver

API_KEY = 'YOUR_IONQ_API_KEY_GOES_HERE'
provider = IonQProvider(API_KEY)

simulator_backend = provider.get_backend("simulator")
simulator_backend.set_options(noise_model="aria-1")


hidden_subgroup = ['000', '001', '010', '011']
oracle = DefaultOracle(hidden_subgroup)

solver = SimonSolver(SimonCircuit(oracle), backend=simulator_backend)
hidden_subgroup_basis = solver.solve()
