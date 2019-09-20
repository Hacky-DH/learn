/*
 * get infomation of GPU
 * nvcc info.cu -o info
*/
#include <cstdio>

int main() {
    int dev = 0;
    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, dev);
    printf("GPU: %s\n", prop.name);
    printf("SM num: %d\n", prop.multiProcessorCount);
    printf("max threads per thread block: %d\n", prop.maxThreadsPerBlock);
    printf("max threads per SM: %d\n", prop.maxThreadsPerMultiProcessor);
    printf("total memory: %.2f GB\n", prop.totalGlobalMem/1024./1024/1024);
    printf("shared memory per SM: %.2f KB\n", prop.sharedMemPerMultiprocessor/1024.);
    printf("shared memory per thread block: %.2f KB\n", prop.sharedMemPerBlock/1024.);
    printf("max threads dim: %d,%d,%d\n", prop.maxThreadsDim[0], prop.maxThreadsDim[1], prop.maxThreadsDim[2]);
    return 0;
}
