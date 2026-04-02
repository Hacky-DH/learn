# ENABLE_PROFILE=1 nsys profile --trace=cuda,nvtx --capture-range=cudaProfilerApi --capture-range-end=stop --sample=none --output=profile_report%n python profile_demo.py

import os

import torch.nn as nn

import torch


# 获取环境变量，默认关闭
ENABLE_PROFILE = os.getenv("ENABLE_PROFILE", "0") == "1"


class CUDAProfiler:
    """封装 CUDA 分析工具的工具类"""

    @staticmethod
    def start():
        if ENABLE_PROFILE:
            torch.cuda.cudart().cudaProfilerStart()

    @staticmethod
    def stop():
        if ENABLE_PROFILE:
            torch.cuda.cudart().cudaProfilerStop()

    @staticmethod
    def range_push(name: str):
        if ENABLE_PROFILE:
            torch.cuda.nvtx.range_push(name)

    @staticmethod
    def range_pop():
        if ENABLE_PROFILE:
            torch.cuda.nvtx.range_pop()

    # 上下文管理器（自动处理 push/pop）
    class scope:
        def __init__(self, name: str):
            self.name = name

        def __enter__(self):
            CUDAProfiler.range_push(self.name)

        def __exit__(self, exc_type, exc_val, exc_tb):
            CUDAProfiler.range_pop()


# 1. 准备阶段：模型定义与数据初始化
# 此时分析器尚未启动记录
model = nn.Sequential(
    nn.Linear(1024, 4096), nn.ReLU(), nn.Linear(4096, 1024)
).cuda()

data = torch.randn(128, 1024).cuda()

# Warmup：预热 GPU，排除 CUDA Context 初始化和缓存影响
print("Warming up...")
for _ in range(5):
    _ = model(data)

# 2. 核心分析阶段：手动开启记录
print("Starting Profiler...")
CUDAProfiler.start()

# 这一段代码会被 Nsight Systems 记录
for i in range(3):
    # 添加 NVTX 标签，在可视化界面中显示名称
    with CUDAProfiler.scope(f"Iteration_{i}"):
        with CUDAProfiler.scope("Forward"):
            output = model(data)

        with CUDAProfiler.scope("Backward"):
            loss = output.sum()
            loss.backward()

# 手动停止记录
CUDAProfiler.stop()
print("Profiler Stopped.")

# 3. 结束阶段：后续计算
# 这里的代码不会出现在分析报告中
final_output = model(data)
print("Done.")
