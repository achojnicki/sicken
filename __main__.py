from sicken_concurrent import SickenConcurrent
from modules.sicken.paths import Paths

if __name__=="__main__":
	paths=Paths()
	sc=SickenConcurrent(paths)
	sc.start()