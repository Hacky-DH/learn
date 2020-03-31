import multiprocessing as mp
import torch
import torch.distributed as dist

init_method='tcp://127.0.0.1:1234'

def run(queue, rank):
    dist.init_process_group(
            backend='gloo',
            init_method=init_method,
            world_size=2,
            rank=rank)
    keys = torch.arange(0, 10, dtype=torch.long)
    if rank == 0:
        dist.send(keys, 1)
    else:
        out = torch.empty(10, dtype=torch.long)
        dist.recv(out, 0)
        assert out.equal(keys)
    dist.destroy_process_group()
    queue.put('done')

def main():
    ctx = mp.get_context('spawn')
    queue = ctx.Queue()
    c = ctx.Process(target=run, args=(queue, 0))
    c.start()
    c1 = ctx.Process(target=run, args=(queue, 1))
    c1.start()
    out = queue.get()
    assert out == 'done'
    c.join()
    c1.join()

if __name__ == '__main__':
    main()
