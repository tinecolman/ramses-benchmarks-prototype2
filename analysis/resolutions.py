
def get_resolutions(test):
    if test=='sedov':
        return ['256','512','1024']
    elif test=='sedov-amr':
        return ['lvl5-10']
    elif test=='cosmo':
        return ['256','512','1024']
    elif test=='cosmo-amr':
        return ['lvl8-12']
    else:
        print('ERROR: Add resolutions for benchmark:', test)
        exit(1)

def get_weak_scaling_config(test):
    if test=='sedov':
        nodes = [1,8,64]
        resos = get_resolutions(test)
    elif test=='sedov-amr':
        nodes = [1]
        resos = get_resolutions(test)
    elif test=='cosmo':
        nodes = [1,8,64]
        resos = get_resolutions(test)
    elif test=='cosmo-amr':
        nodes = [1]
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
            'lvl5-10': 1}
    elif test=='cosmo':
        weak_scaling_map = {
            '256': 1,
            '512': 8,
            '1024': 64}
    elif test=='cosmo-amr':
        weak_scaling_map = {
            'lvl8-12': 1}
    else:
        print('ERROR: Add weak scaling configuration for benchmark:', test)
        exit(1)
    return weak_scaling_map