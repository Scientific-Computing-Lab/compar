from compilers.par4all import Par4all
from compilers.autopar import Autopar
from compilers.cetus import Cetus


parallelizers = dict()
parallelizers[Autopar.NAME] = Autopar
parallelizers[Cetus.NAME] = Cetus
parallelizers[Par4all.NAME] = Par4all
