import os
import sys
import platform
import subprocess
import importlib
from sysconfig import get_paths
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from distutils.sysconfig import get_config_var

import pybind11

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir, build_with_cuda):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.build_with_cuda = build_with_cuda

class Build(build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build extensions")
        super().run()

    def build_extension(self, ext):
        if isinstance(ext, CMakeExtension):
            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            include_path = get_paths()["include"]
            pybind11_include = pybind11.get_include()

            cmake_args = [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
                f"-DPYTHON_LIBRARY={get_config_var('LIBDIR')}",
                f"-DPYTHON_INCLUDE_PATH={include_path}",
                f"-DPYBIND11_INCLUDE_DIR={pybind11_include}",
                f"-DDIFFVG_CUDA={'1' if ext.build_with_cuda else '0'}"
            ]

            cfg = 'Debug' if self.debug else 'Release'
            build_args = ['--config', cfg]

            if platform.system() == "Windows":
                cmake_args += [
                    f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}",
                    f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"
                ]
                if sys.maxsize > 2**32:
                    cmake_args += ['-A', 'x64']
                build_args += ['--', '/m']
            else:
                cmake_args += [f"-DCMAKE_BUILD_TYPE={cfg}"]
                build_args += ['--', '-j8']

            env = os.environ.copy()
            env['CXXFLAGS'] = f'{env.get("CXXFLAGS", "")} -DVERSION_INFO="{self.distribution.get_version()}"'
            env['PYBIND11_INCLUDE_DIR'] = pybind11_include

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)
            subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
            subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
        else:
            super().build_extension(ext)

# === 自动检测是否需要 CUDA 构建 ===
torch_spec = importlib.util.find_spec("torch")
tf_spec = importlib.util.find_spec("tensorflow")
packages = []
build_with_cuda = False

if torch_spec is not None:
    packages.append('pydiffvg')
    import torch
    if torch.cuda.is_available():
        build_with_cuda = True

if tf_spec is not None and sys.platform != 'win32':
    packages.append('pydiffvg_tensorflow')
    if not build_with_cuda:
        import tensorflow as tf
        if hasattr(tf.test, "is_gpu_available"):
            build_with_cuda = tf.test.is_gpu_available(cuda_only=True)

if not packages:
    print("❌ Error: PyTorch or TensorFlow must be installed.")
    sys.exit(1)

# === 可通过环境变量覆盖 CUDA 构建选项 ===
if 'DIFFVG_CUDA' in os.environ:
    build_with_cuda = os.environ['DIFFVG_CUDA'] == '1'

# ✅ 定义 ext_modules 并传给 setup()
ext_modules = [CMakeExtension('diffvg', '.', build_with_cuda)]

setup(
    name='diffvg',
    version='0.0.1',
    install_requires=["svgpathtools"],
    description='Differentiable Vector Graphics',
    ext_modules=ext_modules,
    cmdclass=dict(build_ext=Build, install=install),
    packages=packages,
    zip_safe=False,
)


