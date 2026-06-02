
def get_resolutions(test):
   if test=='sedov':
      return ['256','512','1024']
   else:
      print('Add resolutions for benchmark:', test)
      exit(1)

def get_weak_scaling_config(test):
   if test=='sedov':
      nodes = [1,8,64]
      resos = get_resolutions(test)
   else:
      print('Add weak scaling configuration for benchmark:', test)
      exit(1)
   return nodes, resos
