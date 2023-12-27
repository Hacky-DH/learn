# 通过行列切分CSR格式

设计一个算法将一个大csr格式切分为多个小csr格式。
例如一个5x5的大矩阵，csr如下：

```
indptr = [0, 2, 4, 6, 8, 12]
indices = [0, 1, 2, 3, 2, 3, 4, 3, 3, 2, 0, 1]
```

split_sizes=[3, 2]表示切分成4个小矩阵：左上角3x3矩阵，右上角3x2矩阵，左下角2x3矩阵和右下角2x2矩阵。

切分后的csr为

```
CSR 1:
indptr = {0, 2, 3, 4};
indices = {0, 1, 2, 2};
CSR 2:
indptr = {0, 0, 1, 2};
indices = {0, 0};
CSR 3:
indptr = {0, 0, 3};
indices = {2, 0, 1};
CSR 4:
indptr = {0, 2, 3};
indices = {1, 0, 0};
```

实现了C++版本，pytorch版本，cuda版本

测评数据待更新
