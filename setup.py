import setuptools

with open("readme.org", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="i2p-chee",
	version="0.0.0",
	author="chee",
	author_email="chee@snoot.club",
	description="save them",
	long_description=long_description,
	long_description_content_type="text/org",
	url="https://git.snoot.club/chee/i2p",
	packages=setuptools.find_packages(),
	python_requires=">= 3.6",
	entry_points={
		'console_scripts': [
			"i2p = i2p.__main__:main"
		]
	}
)
