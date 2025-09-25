from setuptools import setup, find_packages
import os

# 获取项目根目录
root_dir = os.path.abspath(os.path.dirname(__file__))

# 读取requirements.txt文件
with open(os.path.join(root_dir, 'requirements.txt'), 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

# 项目元数据
setup(
    name="photo-watermark",
    version="1.0.0",
    description="一个简单易用的图片水印工具",
    long_description="""图片水印工具

这是一个用于给图片添加水印的桌面应用程序，支持文本水印，可自定义透明度、位置等参数。
支持批量处理图片，提供水印模板功能。
""",
    author="",
    author_email="",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'photo-watermark=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
    license='MIT',
)

# 主入口函数（如果setup.py被直接运行）
def main():
    import main
    main.main()

if __name__ == '__main__':
    main()