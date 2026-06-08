
def get_resolutions(test):
    if test=='sedov':
        return ['256','512','1024']
    elif test=='sedov-amr':
        return ['lvl5-8','lvl5-10']
    else:
        print('ERROR: Add resolutions for benchmark:', test)
        exit(1)

def get_weak_scaling_config(test):
    if test=='sedov':
        nodes = [1,8,64]
        resos = get_resolutions(test)
    elif test=='sedov-amr':
        nodes = [1,2]
        resos = get_resolutions(test)
    else:
        print('ERROR: Add weak scaling configuration for benchmark:', test)
        exit(1)
    return nodes, resos

def get_weak_scaling_config2(test):
    if test=='sedov':
        weak_scaling_map = {
            '256': 1,
            '512': 8,
            '1024': 64}
    elif test=='sedov-amr':
        weak_scaling_map = {
            'lvl5-8': 1,
            'lvl5-10': 2}
    else:
        print('ERROR: Add weak scaling configuration for benchmark:', test)
        exit(1)
    return weak_scaling_map