from .oracle import DefaultOracle

oracle = DefaultOracle(['000'])
circuit = oracle.generate_default_circuit()
print(circuit)