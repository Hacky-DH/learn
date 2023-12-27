#include <iostream>
#include <vector>

using namespace std;

struct CSRMatrix {
  vector<int> indptr;   // 每行非零元素的起始索引
  vector<int> indices;  // 非零元素的列索引
};

vector<CSRMatrix> splitCSR(const vector<int>& indptr,
                           const vector<int>& indices,
                           const vector<int>& split_sizes) {
  vector<CSRMatrix> result;
  int row_start = 0;
  int col_start = 0;
  for (int rs : split_sizes) {
    col_start = 0;
    for (int cs : split_sizes) {
      CSRMatrix sub_matrix;
      sub_matrix.indptr.reserve(rs + 1);
      sub_matrix.indptr.push_back(0);
      int nnz_count = 0;
      for (int i = row_start; i < row_start + rs; ++i) {
        for (int j = indptr[i]; j < indptr[i + 1]; ++j) {
          int col = indices[j];
          if (col >= col_start && col < col_start + cs) {
            sub_matrix.indices.push_back(col - col_start);
            ++nnz_count;
          }
        }
        sub_matrix.indptr.push_back(nnz_count);
      }
      result.push_back(sub_matrix);
      col_start += cs;
    }
    row_start += rs;
  }
  return result;
}

// 打印CSR矩阵的函数
void printCSR(const CSRMatrix& csr) {
  cout << "indptr = {";
  for (size_t i = 0; i < csr.indptr.size(); ++i) {
    cout << csr.indptr[i] << (i < csr.indptr.size() - 1 ? ", " : "");
  }
  cout << "};\nindices = {";
  for (size_t i = 0; i < csr.indices.size(); ++i) {
    cout << csr.indices[i] << (i < csr.indices.size() - 1 ? ", " : "");
  }
  cout << "};" << endl;
}

int main() {
  vector<int> indptr = {0, 2, 4, 6, 8, 12};
  vector<int> indices = {0, 1, 2, 3, 2, 3, 4, 3, 3, 2, 0, 1};
  vector<int> split_sizes = {3, 2};

  vector<CSRMatrix> split_csrs = splitCSR(indptr, indices, split_sizes);
  for (size_t i = 0; i < split_csrs.size(); ++i) {
    cout << "CSR " << i + 1 << ":\n";
    printCSR(split_csrs[i]);
  }

  return 0;
}
/*
对于
vector<int> indptr = {0, 2, 4, 6, 8, 12};
vector<int> indices = {0, 1, 2, 3, 2, 3, 4, 3, 3, 2, 0, 1};
vector<int> split_sizes = {3, 2};
输出
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

对于
vector<int> indptr = {0, 2, 4, 6, 8, 12};
vector<int> indices = {0, 1, 2, 3, 2, 3, 4, 3, 3, 2, 0, 1};
vector<int> split_sizes = {2, 1, 2};
输出
CSR 1:
indptr = {0, 2, 2};
indices = {0, 1};
CSR 2:
indptr = {0, 0, 1};
indices = {0};
CSR 3:
indptr = {0, 0, 1};
indices = {0};
CSR 4:
indptr = {0, 0};
indices = {};
CSR 5:
indptr = {0, 1};
indices = {0};
CSR 6:
indptr = {0, 1};
indices = {0};
CSR 7:
indptr = {0, 0, 2};
indices = {0, 1};
CSR 8:
indptr = {0, 0, 1};
indices = {0};
CSR 9:
indptr = {0, 2, 3};
indices = {1, 0, 0};

对于
vector<int> indptr = {0, 1, 2, 3, 4};
vector<int> indices = {2, 3, 1, 0};
vector<int> split_sizes = {2, 2};
输出
CSR 1:
indptr = {0, 0, 0};
indices = {};
CSR 2:
indptr = {0, 1, 2};
indices = {0, 1};
CSR 3:
indptr = {0, 1, 2};
indices = {1, 0};
CSR 4:
indptr = {0, 0, 0};
indices = {};
*/
