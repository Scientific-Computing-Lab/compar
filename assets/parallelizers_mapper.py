from compilers.par4all import Par4all
from compilers.autopar import Autopar
from compilers.cetus import Cetus
from compilers.dummy import Dummy


parallelizers = dict()
parallelizers[Autopar.NAME] = Autopar
parallelizers[Cetus.NAME] = Cetus
parallelizers[Par4all.NAME] = Par4all
parallelizers[Dummy.NAME] = Dummy
