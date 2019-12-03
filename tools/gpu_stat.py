#!/bin/env python
def get_gpu_status(dev_id):
    r'''
    return res.gpu res.memory
    '''
    try:
        import py3nvml.py3nvml as nv
        nv.nvmlInit()
        assert dev_id >= 0 and dev_id < nv.nvmlDeviceGetCount()
        handle = nv.nvmlDeviceGetHandleByIndex(dev_id)
        return nv.nvmlDeviceGetUtilizationRates(handle)
    except:
        print('WARNING: could not get status of cuda {}'.format(dev_id))
    return None
