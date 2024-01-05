
def merge_sub_csrs(sub_csrs, num_vertices):
    r'''
    \brief 通过graph的多个关系的子csr，合并成一个大的CSR

    \param sub_csrs dict key is (src, rel, dst), value is a tuple 
        (sub_csr_row, sub_csr_col, [])
    \param num_vertices dict(type=number) 

    \return tuple (csr_row, csr_col)
    '''
    vertices_start = dict()
    total_nodes = 0
    for t, num in num_vertices.items():
        vertices_start[t] = total_nodes
        total_nodes += num
    csr_row = torch.zeros(total_nodes + 1, dtype=torch.long)
    csr_col = []
    csr_col_indices = []
    for (src, rel, dst), (_, (row_indices, col_indices,
                              _)) in sub_csrs.items():
        row_start = vertices_start[src] + 1
        col_start = vertices_start[dst]
        # 计算csr_row并放到对应位置
        row_diff = torch.diff(row_indices)
        csr_row[row_start:row_start + len(row_diff)] += row_diff
        col_indices += col_start
        csr_col.append(col_indices)
        idx = torch.nonzero(row_diff).flatten()
        idx = torch.repeat_interleave(idx, row_diff[idx])
        csr_col_indices.append(idx + vertices_start[src])
    csr_row = torch.cumsum(csr_row, dim=0)
    csr_col_indices = torch.cat(csr_col_indices)
    csr_col_indices = torch.argsort(csr_col_indices)
    csr_col = torch.cat(csr_col)
    csr_col = csr_col[csr_col_indices]
    return csr_row, csr_col
