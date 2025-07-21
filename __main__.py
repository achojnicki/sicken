from concurrent import sickenconcurrent
from modules.sicken.paths import Paths

if __name__=="__main__":
	
	paths=Paths()
	sc=sickenconcurrent(paths)
	sc.start()