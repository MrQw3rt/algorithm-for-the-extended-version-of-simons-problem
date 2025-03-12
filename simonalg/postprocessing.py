"""
Contains functionality to convert the vectors sampled by the quantum part of Simon's algorithm
into a basis for the hidden subgroup.
"""

from functools import reduce

from sympy.polys.matrices import DM
from sympy import GF


def bitstrings_to_vectors(bitstrings):
    """
    Converts the list of bitstrings into a list of numerical vectors.
    """
    def bitstring_to_vector(bitstring):
        return reduce(lambda a,b: a + [1 if b == '1' else 0], bitstring, [])
    return [bitstring_to_vector(b) for b in bitstrings]


def vectors_to_bitstrings(vectors):
    """
    Converts the list of numerical vectors into a list of bitstrings.
    """
    return [reduce(lambda acc, bit: acc + f'{bit}', list(r), '') for r in vectors.tolist()]


def get_basis_of_nullspace_mod_2(basis_elements):
    """
    Parameters:
        - basis_elements is a list of numerical vectors.
    Interprets the basis_elements as rows of a matrix and returns the kernel of that matrix.
    """
    parity_check_matrix = DM(basis_elements, GF(2))
    return parity_check_matrix.nullspace().to_Matrix()


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

    hidden_subgroup_basis = get_basis_of_nullspace_mod_2(numerical_vectors)
    return vectors_to_bitstrings(hidden_subgroup_basis)
