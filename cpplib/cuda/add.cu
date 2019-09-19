/*
 * use CUDA C++ compiler to compile
 * nvcc add.cu -o add_cuda
 *
 * profile: nvprof ./add_cuda
 * on Tesla P40 
 * one thread add call takes 201.23ms
 * one thread block 1024 threads takes 3.6280ms
 * many thread blocks takes 2.9605ms 
 *
 * see help https://devblogs.nvidia.com/even-easier-introduction-cuda/
*/
#include <iostream>
#include <math.h>

#define THREADS 1024
#define BLOCKS(N) (N + THREADS - 1) / THREADS

// CUDA Kernel function to add the elements of two arrays on the GPU
__global__ void add(int n, float *x, float *y)
{
  // the following two lines is just for 1 block many threads
  //int index = threadIdx.x;
  //int stride = blockDim.x;
  // for many blocks and many threads
  int index = blockIdx.x * blockDim.x + threadIdx.x;
  int stride = blockDim.x * gridDim.x;
  for (int i = index; i < n; i += stride)
      y[i] = x[i] + y[i];
}


int main(void)
{
  int N = 1<<20; // 1M elements

  // Allocate Unified Memory -- accessible from CPU or GPU
  float *x, *y;
  cudaMallocManaged(&x, N*sizeof(float));
  cudaMallocManaged(&y, N*sizeof(float));

  // initialize x and y arrays on the host
  for (int i = 0; i < N; i++) {
    x[i] = 1.0f;
    y[i] = 2.0f;
  }

  // Run kernel on 1M elements on the GPU
  // launch one GPU thread
  // add<<<1, 1>>>(N, x, y);
  // launch 1024 threads
  // add<<<1, THREADS>>>(N, x, y);
  // launch many blocks for each block have 1024 threads
  add<<<BLOCKS(N), THREADS>>>(N, x, y);

  // Wait for GPU to finish before accessing on host
  cudaDeviceSynchronize();

  // Check for errors (all values should be 3.0f)
  float maxError = 0.0f;
  for (int i = 0; i < N; i++)
    maxError = fmax(maxError, fabs(y[i]-3.0f));
  std::cout << "Max error: " << maxError << std::endl;

  // Free memory
  cudaFree(x);
  cudaFree(y);

  return 0;
}
