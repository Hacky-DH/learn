# nsys profile --trace=cuda,nvtx --capture-range=cudaProfilerApi --capture-range-end=stop --sample=cpu --output=profile_report%n python profile_demo.py

import torch.nn as nn

import torch


# 1. 准备阶段：模型定义与数据初始化
# 此时分析器尚未启动记录
model = nn.Sequential(
    nn.Linear(1024, 4096),
    nn.ReLU(),
    nn.Linear(4096, 1024)
).cuda()

data = torch.randn(128, 1024).cuda()

# Warmup：预热 GPU，排除 CUDA Context 初始化和缓存影响
print("Warming up...")
for _ in range(5):
    _ = model(data)

# 2. 核心分析阶段：手动开启记录
print("Starting Profiler...")
torch.cuda.cudart().cudaProfilerStart()

# 这一段代码会被 Nsight Systems 记录
for i in range(3):
    # 进阶技巧：添加 NVTX 标签，在可视化界面中显示名称
    torch.cuda.nvtx.range_push(f"Iteration_{i}")

    torch.cuda.nvtx.range_push(f"Fwd_{i}")
    output = model(data)
    loss = output.sum()
    torch.cuda.nvtx.range_pop()

    torch.cuda.nvtx.range_push(f"Bwd_{i}")
    loss.backward()
    torch.cuda.nvtx.range_pop()

    torch.cuda.nvtx.range_pop()

# 手动停止记录
torch.cuda.cudart().cudaProfilerStop()
print("Profiler Stopped.")

# 3. 结束阶段：后续计算
# 这里的代码不会出现在分析报告中
final_output = model(data)
print("Done.")
