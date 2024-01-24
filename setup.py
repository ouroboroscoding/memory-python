from setuptools import setup

with open('README.md', 'r') as oF:
	long_description=oF.read()

setup(
	name='memory-oc',
	version='1.0.0',
	description='A session library using redis',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://ouroboroscoding.com/memory/',
	project_urls={
		'Documentation': 'https://ouroboroscoding.com/memory/',
		'Source': 'https://github.com/ouroboroscoding/memory-python',
		'Tracker': 'https://github.com/ouroboroscoding/memory-python/issues'
	},
	keywords=['session','redis'],
	author='Chris Nasr - Ouroboros Coding Inc.',
	author_email='chris@ouroboroscoding.com',
	license='MIT',
	packages=['memory'],
	python_requires='>=3.10',
	install_requires=[
		'jobject>=1.0.2,<1.1',
		'jsonb>=1.0.0,<1.1',
		'namedredis>=1.0.1,<1.1'
	],
	zip_safe=True
)