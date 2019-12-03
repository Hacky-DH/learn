kimport os

def cpu_count():
    r'''
    consider run in docker
    '''
    quota = '/sys/fs/cgroup/cpu/cpu.cfs_quota_us'
    period = '/sys/fs/cgroup/cpu/cpu.cfs_period_us'
    share = '/sys/fs/cgroup/cpu/cpu.shares'
    avail_cpu = -1
    if os.path.isfile(quota):
        cpu_quota = int(open(quota).read().rstrip())
        if os.path.isfile(period):
            cpu_period = int(open(period).read().rstrip())
            avail_cpu = cpu_quota // cpu_period
    elif os.path.isfile(share):
        cpu_shares = int(open(share).read().rstrip())
        avail_cpu = cpu_shares // 1024
    return avail_cpu if avail_cpu > 0 else os.cpu_count()
