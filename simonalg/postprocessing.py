from sympy.polys.matrices import DM
from sympy import GF

from functools import reduce


def bitstrings_to_vectors(bitstrings):
    def bitstring_to_vector(bitstring):
        return reduce(lambda a,b: a + [1 if b == '1' else 0], bitstring, [])
    return [bitstring_to_vector(b) for b in bitstrings]


def vectors_to_bitstrings(results):
    return [reduce(lambda acc, bit: acc + f'{bit}', list(r), '') for r in results.tolist()]


def get_basis_of_nullspace_mod_2(basis_elements):
    A = DM(basis_elements, GF(2))
    return A.nullspace().to_Matrix()


def convert_to_basis_of_hidden_subgroup(orthogonal_subgroup_basis, n):
    """
    Parameters:
        - orthogonal_subgroup_basis is the basis of the group orthogonal to the hidden subgroup.
          This is the collection of bitstrings sampled by the quantum part of Simon's algorithm.
    Converts the basis of the orthogonal subgroup into a basis of the hidden subgroup as described
    in Section 10.4.1 of 'Quantum Computation and Quantum Information' by Nielsen and Chuang.
    """
    if len(orthogonal_subgroup_basis) == 0:
        orthogonal_subgroup_basis = ['0' * n]
    numerical_vectors = bitstrings_to_vectors(orthogonal_subgroup_basis)

    """
    The matrix where numerical_vectors are the columns is the generator matrix of the linear code specified 
    the orthogonal subgroup. Hence, the transpose of that matrix, A, is the parity check matrix of the corresponding
    dual code, which is the code specified by the hidden subgroup itself.
    """
    A = DM(numerical_vectors, GF(2))
    """
    By definition of the parity check matrix, its kernel forms a basis of the underlying code.
    Hence, the kernel of A is the basis of the hidden subgroup.
    """
    hidden_subgroup_basis = A.nullspace().to_Matrix()
    return vectors_to_bitstrings(hidden_subgroup_basis)