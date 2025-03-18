from sicken.Sicken_VTube import Animation_Seq
from math import ceil

import numpy as np

class generators(Animation_Seq):
	def _generate_speak_range(self, words, data):
		seq=[]
		for word_index in range(0,len(words)):
			frame=self._frame
			print(words[word_index]['word'])
			start=words[word_index]['start']
			end=words[word_index]['end']
			duration=end-start
			word_len=len(words[word_index]['word'])

			print(f'start: {start}, end: {end}, duration: {duration}, word_len: {word_len}')
			for letter in words[word_index]['word']:
				iters=(duration/word_len)/frame
				
				if letter.lower() in data:
					if iters>1:
						path=np.linspace(
							seq[-1] if len(seq)>0 else 0,
							data[letter.lower()],
							ceil(iters)
						)
					else:
						path=[data[letter.lower()]]
					print(f'path: {path}')

					for repeat in range(0,ceil(iters)):
						seq.append(int(path[repeat]))

				else:
					for repeats in range(0,ceil(iters)):
						seq.append(seq[-1])

				print(f'\tletter: {letter} iters: {iters}, seq[-1]:{seq[-1]}')

			if (len(words)-1)>word_index:
				pause_duration=words[word_index+1]['start']-words[word_index]['end']
				print(f"pause_duration: {pause_duration}")
				if pause_duration>frame:
					iters=pause_duration*frame
					print(f'\titers" {iters}')
					for repeats in range(0, ceil(iters)):
						seq.append(0)

		seq.append(0)
		return seq

	def _generate_wink_range(self, start, stop, step):
		l=list(range(start,stop-(step*2),-step))+list(range(stop, start+step,step))
		return l

	def _generate_possessed_look_range(self, start, stop, step):
		l=list(range(start,stop,step))

		x=ceil(int(self._duration/self._frame))
		for _ in range(x):
			l.append(stop)

		l=l+list(range(stop,start,-step))
		l+=[start]
		return l

	def _generate_angry_range(self, start, stop, step):
		l=list(range(start,stop+(step*2),step))

		x=ceil(int(self._duration/self._frame))
		for _ in range(x):
			l.append(stop)

		l.append(start)
		return l

	def _generate_surprise_sign_range(self, start, stop, step):
		l=list(range(start,stop+(step*2),step))

		x=ceil(int(self._duration/self._frame))
		for _ in range(x):
			l.append(stop)

		l.append(start)
		return l

	def _generate_music_notes_range(self, start, stop, step):
		l=list(range(start,stop+(step*2),step))

		x=ceil(int(self._duration/self._frame))
		for _ in range(x):
			l.append(stop)

		l.append(start)
		return l

	def _generate_sweat_range(self, start, stop, step):
		l=list(range(start,stop+(step*2),step))

		x=ceil(int(self._duration/self._frame))
		for _ in range(x):
			l.append(stop)

		l.append(start)
		return l

	def _generate_angry_range(self, start, stop, step):
		l=list(range(start,stop+(step*2),step))

		x=ceil(int(self._duration/self._frame))
		for _ in range(x):
			l.append(stop)

		l.append(start)
		return l

	def _generate_shock_range(self, start, stop, step):
		l=list(range(start,stop,step))

		x=ceil(int(self._duration/self._frame))
		for _ in range(x):
			l.append(stop)

		l=l+list(range(stop,start,-step))
		l.append(start)
		return l

	def _generate_shock_sign_range(self, start, stop, step):
		l=list(range(start,stop+(step*2),step))

		return l

	def _generate_tilt_left_range(self, start, stop, step):
		l=list(range(start,stop+step,step))+list(range(stop, start-step,-step))+[0]
		return l

	def _generate_tilt_right_range(self, start, stop, step):
		l=list(range(start, stop+step,-step))+list(range(stop,start+step,step))+[0]
		return l

	def _generate_nod_range(self, start, stop, step):
		return list(range(start, stop, step))+list(range(stop, -stop, -step))+list(range(-stop, start, step))+[0]
