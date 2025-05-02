    def build_extension(self, ext):
        if isinstance(ext, CMakeExtension):
            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            include_path = get_paths()["include"]
            pybind11_include = pybind11.get_include()

            cmake_args = [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
                f"-DPYTHON_LIBRARY={get_config_var('LIBDIR')}",
                f"-DPYTHON_INCLUDE_PATH={include_path}",
                f"-DDIFFVG_CUDA={'1' if ext.build_with_cuda else '0'}"
            ]

            # 👇 将 pybind11 路径传给 CMake
            env = os.environ.copy()
            env['PYBIND11_INCLUDE_DIR'] = pybind11_include

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

            env['CXXFLAGS'] = f'{env.get("CXXFLAGS", "")} -DVERSION_INFO="{self.distribution.get_version()}"'

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)
            subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
            subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
        else:
            super().build_extension(ext)
