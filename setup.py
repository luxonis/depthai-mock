from setuptools import setup

setup(
    name='depthai_mock',
    version='0.0.1',
    description='The tool that allows you to record and playback the DepthAI generated frames',
    url='https://github.com/luxonis/depthai-mock',
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
        "depthai==0.2.0.1"
    ],
    zip_safe=False
)
