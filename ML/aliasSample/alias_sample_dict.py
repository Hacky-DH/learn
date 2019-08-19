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
    p = np.random.rand(10)
    p = p/p.sum() # probability sum is 1
    print(p)
    # array([0.0361911 , 0.12752677, 0.12804291, 0.1754963 , 0.13940683,
    #    0.01704452, 0.10762277, 0.01283925, 0.151209  , 0.10462055])
    al = AliasSample(p)
    print(al.table_prob, al.table_alias)
    """
    example:
    ({7: 0.1283924746822515,
      9: 0.17459801256180785,
      8: 0.6866879879400214,
      6: 0.7629156984356447,
      5: 0.17044515944072064,
      4: 0.3274291515105685,
      0: 0.3619110396008491,
      3: 0.4443032100142974,
      2: 0.7247323461975472,
      1: 1.0},
    {7: 9, 9: 8, 8: 6, 6: 4, 5: 4, 4: 3, 0: 3, 3: 2, 2: 1})
    """
    # sample
    for x in range(1,10):
        print(al(), end=' ')
    # 2 6 8 3 1 6 0 1 4 
