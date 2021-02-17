import io

from setuptools import setup

setup(
    name='depthai_mock',
    version='0.0.2',
    description='The tool that allows you to record and playback the DepthAI generated frames',
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/luxonis/depthai-mock',
    keywords="depthai mock record tool development",
    author='Luxonis',
    author_email='support@luxonis.com',
    license='MIT',
    packages=['depthai_mock'],
    entry_points ={
        'console_scripts': [
            'depthai_mock=depthai_mock.cli:record_depthai_mockups'
        ],
    },
    install_requires=[
        "depthai==0.4.1.1"
    ],
    include_package_data=True,
    project_urls={
        "Bug Tracker": "https://github.com/luxonis/depthai-mock/issues",
        "Source Code": "https://github.com/luxonis/depthai-mock",
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
