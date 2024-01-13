from pprint import pprint



class Pagen:
	def __init__(self):
		pass

	def tabulate(self, amount=1):
		d=""
		for a in range(amount):
			d+="\t"
		return d

	def generate_title(self, title, indent=0):
		return f"{self.tabulate(indent)}{title}:\n"

	def generate_points(self, data, indent=2):
		points=""
		for point in data:
			index=data.index(point)+1
			if 'description' not in point:
				points+=f"{self.tabulate(indent)}{index}. {point['point']}\n"

			if 'description' in point:
				points+=f"{self.tabulate(indent)}{index}. {point['point']}:\n{self.tabulate(indent+1)}{point['description']}\n\n"
		
		points+='\n'
		return points

	def generate_bullets(self, data, indent=2):
		bullets=""
		for bullet in data:
			if 'description' not in bullet:
				bullets+=f"{self.tabulate(indent)}• {bullet['bullet']}\n"

			elif 'description' in bullet:
				bullets+=f"{self.tabulate(indent)}• {bullet['bullet']}:\n{self.tabulate(indent+1)}{bullet['description']}\n\n"
		bullets+='\n'
		return bullets

	def generate_categories(self, data, indent=2):
		categories=""
		categories+=self.generate_title('Categories', indent=1)

		for category in data:
			categories+=f"{self.tabulate(indent)}• {category}\n"
		categories+='\n'
		return categories

	def generate_paragraphs(self, data, indent=2):
		paragraphs=""
		for paragraph in data:
			paragraph=paragraph['paragraph'].replace("\n",f"\n{self.tabulate(indent)}",)
			paragraphs+=f"{self.tabulate(indent)}{paragraph}\n\n"
		return paragraphs

	def __call__(self, data):
		result=""
		result+=self.generate_title(data['title'])
		

		for main_content in data['content']:
			result+=self.generate_title(main_content['title'], indent=1)
			if main_content['type']=='paragraphs':
				result+=self.generate_paragraphs(main_content['content'])

			elif main_content['type']=='points':
				result+=self.generate_points(main_content['content'])

			elif main_content['type']=='bullets':
				result+=self.generate_bullets(main_content['content'])
		
		if 'categories' in data and data['categories']:
			result+=self.generate_categories(data['categories'])
		return result
