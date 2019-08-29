#include <iostream>
#include <cstdio>
#include <vector>
#include <omp.h>

// https://www.ibm.com/developerworks/cn/aix/library/au-aix-openmp-framework/index.html
// env OMP_NUM_THREADS sets the number of threads

int main() {
        int num_threads=5;
        int idx = 100;
        #pragma omp parallel private(idx) num_threads(num_threads)
        {
                printf("thread=%d, private idx=%d\n", omp_get_thread_num(), idx);
        }
        #pragma omp parallel firstprivate(idx) num_threads(num_threads)
        {
                printf("thread=%d, first private idx=%d\n", omp_get_thread_num(), idx);
        }

        std::vector<int> vec(100);
        #pragma omp parallel for
        for (int i = 0; i < 100; ++i)
                vec[i] = i + 2;
        printf("vec %d", vec[5]);
        return 0;
}
