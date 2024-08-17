from setuptools import setup, find_packages

setup(
    name='django_restful_toolbox',
    version='0.1',
    packages=['django_restful_toolbox'],
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
        'djangorestframework>=3.12.4',
        'markdown>=3.3.4',
    ],
    description='A custom Django renderer package.',
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
