import numpy as np


class AliasSample(object):
    """ A probability distribution for discrete weighted random variables and its probability/alias
    tables for efficient sampling via Vose's Alias Method (a good explanation of which can be found at
    http://www.keithschwarz.com/darts-dice-coins/).

    Compute utility lists for non-uniform sampling from discrete distributions.
    """

    def __init__(self, dist):
        """dist (list or numpy array)"""
        self.dist = dist
        self.alias_initialisation()

    def alias_initialisation(self):
        """ Construct probability and alias tables for the distribution. """
        n = len(self.dist)
        self.prob = np.zeros(n)  # probability list
        self.alias = np.zeros(n, dtype=np.int)  # alias list
        smaller = [] # stack for probabilities smaller than 1
        larger = [] # stack for probabilities greater than or equal to 1

        # Construct and sort the scaled probabilities into their appropriate stacks
        for i, p in enumerate(self.dist):
            self.prob[i] = n * p
            if self.prob[i] < 1.0:
                smaller.append(i)
            else:
                larger.append(i)

        # Construct the probability and alias tables
        while smaller and larger:
            small = smaller.pop()
            large = larger.pop()
            self.alias[small] = large
            self.prob[large] = self.prob[large] + self.prob[small] - 1.0
            if self.prob[large] < 1.0:
                smaller.append(large)
            else:
                larger.append(large)

    def alias_generation(self):
        """
        Draw sample from a non-uniform discrete distribution using alias sampling.
        """
        n = len(self.dist)
        ind = np.random.randint(n)
        if np.random.rand() < self.prob[ind]:
            return ind
        else:
            return self.alias[ind]

    def __call__(self):
        return self.alias_generation()

    def sample_n(self, size):
        """ Return a sample of size n from the distribution."""
        # Ensure a non-negative integer as been specified
        n = int(size)
        if n <= 0:
            raise ValueError("The number of samples must be a non-negative integer: %d" % n)
        return [self.alias_generation() for i in range(n)]


def main():
    import numpy as np
    p = np.random.rand(10)
    # probability sum is 1
    p = p/p.sum()
    print(p)
    # [0.03746718 0.14211218 0.16262279 0.08387829 0.03669862 0.11052032
    #  0.03956142 0.10498392 0.19045631 0.09169898]
    al = AliasSample(p)
    print(al.prob, al.alias)
    # [0.37467183 1.         0.57887818 0.8387829  0.36698618 0.73919552
    #  0.39561416 0.63399234 0.58415317 0.91698977] [2 0 1 2 8 2 8 5 7 8]
    # sample
    for x in range(1, 10):
        print(al(), end=' ')
    # 5 6 1 3 8 5 2 4 8

def plot():
    import matplotlib.pyplot as plt

    probs = np.random.uniform(0.0, 1.0, [10])
    probs /= np.sum(probs)
    idxs = np.arange(0, 10)

    sampler = AliasSample(probs)
    collect = list()
    for it in range(10000):
        collect.append(sampler())
        
    plt.figure()
    plt.subplot(121)
    plt.bar(idxs, probs)
    plt.title('true distribution')
    plt.subplot(122)
    plt.hist(collect, bins=10, density=True)
    plt.title('sampled distribution')
    plt.show()
