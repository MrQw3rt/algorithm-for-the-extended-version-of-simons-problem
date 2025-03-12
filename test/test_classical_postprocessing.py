import unittest

from simonalg.postprocessing import convert_to_basis_of_hidden_subgroup
from simonalg.utils.grouptheory import expand_group


class PostProcessingTest(unittest.TestCase):
    def test_hidden_subgroup_trivial(self):
        # The trivial subgroup has an empty generating set.
        res = convert_to_basis_of_hidden_subgroup(['001', '010', '100'], 3)
        self.assertListEqual(res, [])


    def test_hidden_subgroup_size_2(self):
        # Hidden subgroup is ['000', '001'].
        res = convert_to_basis_of_hidden_subgroup(['010', '100'], 3)
        self.assertListEqual(res, ['001'])


    def test_hidden_subgroup_size_4(self):
        # Hidden subgroup is ['000', '001', '010', '011']
        res = convert_to_basis_of_hidden_subgroup(['100'], 3)
        self.assertListEqual(expand_group(res, 3), ['000', '001', '010', '011'], 3)


    def test_hidden_subgroup_size_8(self):
        # Hidden subgroup is ['000', '001', '010', '011', '100', '101', '110', '111']
        res = convert_to_basis_of_hidden_subgroup([], 3)
        self.assertListEqual(expand_group(res, 3), expand_group(res, 3))
