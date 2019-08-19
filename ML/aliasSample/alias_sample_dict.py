import random


class AliasSample(object):
    """ A probability distribution for discrete weighted random variables and its probability/alias
    tables for efficient sampling via Vose's Alias Method (a good explanation of which can be found at
    http://www.keithschwarz.com/darts-dice-coins/).
    """

    def __init__(self, dist):
        """(dict)"""
        self.dist = dist
        self.alias_initialisation()
        self.table_prob_list = list(self.table_prob)

    def alias_initialisation(self):
        """ Construct probability and alias tables for the distribution. """
        # Initialise variables
        n = len(self.dist)
        self.table_prob = {}  # probability table
        self.table_alias = {}  # alias table
        scaled_prob = {}  # scaled probabilities
        small = []  # stack for probabilities smaller that 1
        large = []  # stack for probabilities greater than or equal to 1

        # Construct and sort the scaled probabilities into their appropriate stacks
        for o, p in self.dist.items():
            scaled_prob[o] = p * n

            if scaled_prob[o] < 1.0:
                small.append(o)
            else:
                large.append(o)

        # Construct the probability and alias tables
        while small and large:
            s = small.pop()
            l = large.pop()

            self.table_prob[s] = scaled_prob[s]
            self.table_alias[s] = l

            scaled_prob[l] = (scaled_prob[l] + scaled_prob[s]) - 1.0

            if scaled_prob[l] < 1:
                small.append(l)
            else:
                large.append(l)

        # The remaining outcomes (of one stack) must have probability 1
        while large:
            self.table_prob[large.pop()] = 1.0

        while small:
            self.table_prob[small.pop()] = 1.0

    def alias_generation(self):
        """ Return a random outcome from the distribution. """
        # Determine which column of table_prob to inspect
        col = random.choice(self.table_prob_list)

        # Determine which outcome to pick in that column
        if self.table_prob[col] >= random.uniform(0, 1):
            return col
        else:
            return self.table_alias[col]

    def __call__(self):
        return self.alias_generation()

    def sample_n(self, size):
        """ Return a sample of size n from the distribution."""
        # Ensure a non-negative integer as been specified
        n = int(size)
        if n <= 0:
            raise ValueError("Please enter a non-negative integer for the number of samples desired: %d" % n)

        return [self.alias_generation() for i in range(n)]


def main():
    import numpy as np
    p = np.random.rand(10)
    # probability sum is 1
    p = p/p.sum()
    # convert to dict
    pd = {i:d for i, d in enumerate(p)}
    print(pd)
    """
    {0: 0.11943376886817711,
     1: 0.007560149547964362,
     2: 0.1267330778938664,
     3: 0.1185252153459745,
     4: 0.11221417387355175,
     5: 0.052940832744314964,
     6: 0.08467942267626706,
     7: 0.13664483265297844,
     8: 0.12427719579381807,
     9: 0.11699133060308733}
    """
    al = AliasSample(pd)
    print(al.table_prob, al.table_alias)
    """
    example:
    {6: 0.8467942267626706, 
     5: 0.5294083274431496, 
     9: 0.5461158602366933,
     8: 0.788887818174874, 
     1: 0.07560149547964362, 
     7: 0.23093764018430174, 
     4: 0.3530793789198192, 
     3: 0.5383315323795643, 
     2: 0.8056623113182284, 
     0: 1.0} 
     {6: 9, 5: 9, 9: 8, 8: 7, 1: 7, 7: 4, 4: 3, 3: 2, 2: 0}
    """
    # sample
    for x in range(1,10):
        print(al(), end=' ')
    # 3 9 4 2 0 5 6 3 4
