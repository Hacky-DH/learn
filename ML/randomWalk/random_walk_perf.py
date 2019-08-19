import torch
import torch_geometric
from timeit import default_timer

'''
cpu: Intel(R) Xeon(R) CPU E5-2683 v4 @ 2.10GHz
cuda:Tesla P40 22919MiB
from /proc/driver/nvidia/gpus and nvidia-smi -q
example result:
nodes 1522362, vertex 30425676, walk length 100
load data done, elapsed 0.5166s
cpu:
random walk with cpp(no pq), elapsed 35.6593s
gpu:
random walk with cpp(no pq), elapsed 0.0250s
pytorch version
load data done, elapsed 0.5219s
cpu:(100 nodes)
random walk with pytorch(no pq), elapsed 3.8387s all >=16.2h
gpu:(100 nodes)
random walk with pytorch(no pq), elapsed 1.7894s all >=7.5h
'''

dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
cpu = torch.device('cpu')
default_walk_length = 100
# data from torch.save torch_geometric.data.data.Data
data_path = 'graph/small/output/torch_geometric/data.pt'


class Timer(object):
    def __init__(self):
        self.start = 0

    def __enter__(self):
        self.start = default_timer()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def elapsed(self):
        return default_timer() - self.start

    @property
    def elapsed_str(self):
        return 'elapsed {:.4f}s'.format(self.elapsed)


def random_walk_cb(data, cb, desc, walk_length=default_walk_length):
    row = data.edge_index[0].long()
    col = data.edge_index[1].long()
    start = torch.arange(data.num_nodes, device=row.device)
    with Timer() as t:
        out = cb(row, col, start, walk_length)
        print(desc + ', ' + t.elapsed_str)
        return out


def random_walk_pytorch_(row, col, start, walk_length, num_nodes=None):
    if num_nodes is None:
        num_nodes = max(row.max(), col.max()).item() + 1
    start = start.flatten()
    # get out-degree of all nodes
    zero = torch.zeros(num_nodes, dtype=row.dtype, device=row.device)
    one = torch.ones(row.size(0), dtype=row.dtype, device=row.device)
    deg = zero.scatter_add_(0, row, one)
    # cumsum of degree, insert 0 to first index
    cum_deg = torch.cat([torch.zeros(1, dtype=row.dtype, device=row.device), deg.cumsum(0)], 0)
    rnd = torch.rand([start.size(0), walk_length], device=row.device)
    out = torch.full([start.size(0), walk_length + 1], -1, dtype=row.dtype, device=row.device)
    for n in range(start.size(0)):
        cur = start[n]
        out[n, 0] = cur
        for l in range(1, walk_length + 1):
            cur = col[cum_deg[cur] + (rnd[n, l - 1] * deg[cur]).long()]
            out[n, l] = cur
    return out


def random_walk_pytorch_nopq(data, walk_length=default_walk_length):
    """
    random walk with pytorch
    Note: not support return-para p and in-out-para q
    data: torch_geometric.data.data.Data
    """
    return random_walk_cb(data,
                          random_walk_pytorch_,
                          'random walk with pytorch(no pq)',
                          walk_length)


def random_walk_cpp_nopq(data, walk_length=default_walk_length):
    """
    random walk with cpp
    Note: not support return-para p and in-out-para q
    data: torch_geometric.data.data.Data
    """
    from torch_cluster import random_walk
    return random_walk_cb(data,
                          random_walk,
                          'random walk with cpp(no pq)',
                          walk_length)


def main():
    with Timer() as t:
        data = torch.load(data_path, map_location=cpu)
        print('load data done, ' + t.elapsed_str)

    print('cpu:')
    random_walk_cpp_nopq(data)

    print('gpu:')
    data_gpu = data.to(dev)
    random_walk_cpp_nopq(data_gpu)

    # need too long time
    # random_walk_pytorch_nopq(data_gpu)
    # random_walk_pytorch_nopq(data)


main()
