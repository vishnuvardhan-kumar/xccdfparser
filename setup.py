import setuptools

with open("README.md", "r") as file_obj:
    long_description = file_obj.read()

setuptools.setup(
    name="xccdfparser",
    version="1.5.1",
    author="Vishnuvardhan Kumar",
    author_email="vishnukumar1997@gmail.com",
    description="Parse XCCDF files and produce human-readable outputs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=['lxml', 'IPy'],
    entry_points={
          'console_scripts': [
              'xccdfparser = xccdfparser.main:main'
          ]
      },
    data_files=[('test', ['xccdfparser/tests/test/sample.json',
                          'xccdfparser/tests/test/sample.xml']
                 ),
                ('', ['tox.ini', 'LICENSE',
                      'requirements.txt', 'test-requirements.txt'])
                ],
    classifiers=(
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
