from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from qiskit_ibm_runtime import SamplerV2

from simonalg.oracle import DefaultOracle
from simonalg.simon_circuit import SimonCircuit
from simonalg.solver import SimonSolver
from simonalg.utils.logging import log

log.setLevel('DEBUG')

hidden_subgroup = ['000', '001', '010', '011']
oracle = DefaultOracle(hidden_subgroup)

solver = SimonSolver(SimonCircuit(oracle), sampler=SamplerV2(FakeSherbrooke()))
hidden_subgroup_basis = solver.solve()
