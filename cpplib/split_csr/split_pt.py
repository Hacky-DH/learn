
import torch


def splitCSR(indptr, indices, split_sizes):
    result = []
    row_start = 0
    indices_tensor = torch.tensor(indices)
    for rs in split_sizes:
        col_start = 0
        for cs in split_sizes:
            indptr_tensor = torch.tensor(indptr[row_start:row_start + rs + 1])
            # 计算当前块的列范围
            row_index = torch.arange(row_start, row_start + rs)
            row_indices = row_index.repeat_interleave(indptr_tensor[1:] -
                                                      indptr_tensor[:-1])
            col_indices = indices_tensor[indptr_tensor[0]:indptr_tensor[-1]]
            # 选择当前块的行列索引
            mask = (col_indices >= col_start) & (col_indices < col_start + cs)
            row_indices = row_indices[mask] - row_start
            col_indices = col_indices[mask] - col_start
            # 计算row_indices
            _, row_counts = torch.unique(row_indices, return_counts=True)
            row_cum_sum = torch.cumsum(row_counts, dim=0)
            pre_zero = torch.zeros(rs - row_cum_sum.numel() + 1,
                                   dtype=row_cum_sum.dtype)
            row_indices = torch.cat([pre_zero, row_cum_sum])
            sub_matrix = {'indptr': row_indices, 'indices': col_indices}
            result.append(sub_matrix)
            col_start += cs
        row_start += rs
    return result


indptr = [0, 2, 4, 6, 8, 12]
indices = [0, 1, 2, 3, 2, 3, 4, 3, 3, 2, 0, 1]
split_sizes = [3, 2]
res = splitCSR(indptr, indices, split_sizes)
print(res)

indptr = [0, 1, 2, 3, 4]
indices = [2, 3, 1, 0]
split_sizes = [2, 2]
res = splitCSR(indptr, indices, split_sizes)
print(res)

'''
[{'indptr': tensor([0, 2, 3, 4]), 'indices': tensor([0, 1, 2, 2])}, {'indptr': tensor([0, 0, 1, 2]), 'indices': tensor([0, 0])}, {'indptr': tensor([0, 0, 3]), 'indices': tensor([2, 0, 1])}, {'indptr': tensor([0, 2, 3]), 'indices': tensor([1, 0, 0])}]
[{'indptr': tensor([0, 0, 0]), 'indices': tensor([], dtype=torch.int64)}, {'indptr': tensor([0, 1, 2]), 'indices': tensor([0, 1])}, {'indptr': tensor([0, 1, 2]), 'indices': tensor([1, 0])}, {'indptr': tensor([0, 0, 0]), 'indices': tensor([], dtype=torch.int64)}]
'''
