from .oracle import SimonOracle

oracle = SimonOracle(['000'])
circuit = oracle.generate_default_circuit()
print(circuit)