TEMPLATE="{title}:\n{content}\n\nCategories:\n{categories}"
TEMPLATE_NO_CAT="{title}:\n{content}"

class Pagen:
	def __init__(self):
		pass

	def generate_numbered_points(self, data):
		points=""
		for point in data:
			index=data.index(point)+1
			if type(point) is str:
				points+=f"\t{index}. {point}\n"

			if type(point) is dict:
				points+=f"\t{index}. {point['title']}:\n\t\t{point['description']}\n\n"
		return points

	def generate_bullet_points(self, data):
		bullets=""
		for bullet in data:
			if type(bullet) is str:
				bullets+=f"\t• {bullet}\n"

			elif type(bullet) is dict:
				bullets+=f"\t• {bullet['title']}:\n\t\t{bullet['description']}\n\n"
		return bullets


	def __call__(self, data):
		if data['type'] == 'bullet':
			data['content']=self.generate_bullet_points(data['content'])
		elif data['type'] =='number':
			data['content']=self.generate_numbered_points(data['content'])

		elif data['type']=='paragraph':
			data['content']=data['content'].replace("\n","\n\t")
			data['content']=f"\t{data['content']}"

		if 'categories' in data and data['categories']:
			data['categories']=self.generate_bullet_points(data['categories'])
			page=TEMPLATE.format(
				title=data['title'],
				content=data['content'],
				categories=data['categories']
				)
		else:
			page=TEMPLATE_NO_CAT.format(
				title=data['title'],
				content=data['content'],
				)

		return page
