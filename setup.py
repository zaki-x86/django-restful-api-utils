from setuptools import setup, find_packages

setup(
    name='rest_framework_toolbox',
    version='0.41',
    packages= find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
        'djangorestframework>=3.12.4',
        'markdown>=3.3.4',
    ],
    extra_require={
        'dev': [
            'twine>=3.4.1',
            'wheel>=0.37.1',
        ],
        
    },
    description='A custom toolbox with ready to use utilities.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mohamed Zaki',
    author_email='zaki.x86@gmail.com',
    url='https://github.com/zaki-x86/django_restful_toolbox.git',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
    license=open('LICENSE').read(),
    zip_safe=False,
)

