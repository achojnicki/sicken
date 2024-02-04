from wikipedia import page
from json import dump

articles=[
	'Video Game',
	'Japanese Animation',
	'Computer',
	'Language',
	'Programming Language',
	'Music',
	'Games',
	'Artifical Intelligence',
	'Software',
	'Love',
	'Microcontroller',
	'Arduino',
	'Python (programming language)',
]


if __name__=="__main__":
	results=[]

	for a in articles:
		p=page(a, auto_suggest=False)
		d={
			"title":p.title,
			"content": p.content
		}
		results.append(d)

	with open('output.json','w') as file:
		dump(results, file)

