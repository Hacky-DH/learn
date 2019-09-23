import torch
from datetime import datetime

def multinomial(probs, n_samples):
    # O(lgn)
    return torch.multinomial(probs, n_samples, True)

def alias(probs, n_samples):
    # alias method, both on CPU and GPU
    # just works in pytorch 1.2
    alias_table, prob_table = torch._multinomial_alias_setup(probs)
    return torch._multinomial_alias_draw(prob_table, alias_table, n_samples)


probs = torch.rand(10)

start = datetime.now()
multinomial(probs, 10)
print("multinomial {}".format(datetime.now()-start))

start = datetime.now()
alias(probs, 10)
print("alias {}".format(datetime.now()-start))
