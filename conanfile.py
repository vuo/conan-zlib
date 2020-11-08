from conans import ConanFile, CMake, tools
import os
import platform

class ZLibConan(ConanFile):
    name = 'zlib'

    source_version = '1.2.11'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://zlib.net/'
    license = 'http://zlib.net/zlib_license.html'
    description = 'A compression library'
    source_dir = 'zlib-%s' % source_version
    generators = 'cmake'

    build_dir = '_build'
    install_dir = '_install'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://www.zlib.net/zlib-%s.tar.gz' % self.source_version,
                  sha256='c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1')

        # zlib.h contains the license in the first block comment.
        # Truncate it at the end of that comment.
        self.run('sed "/\\*\\//q" %s/zlib.h > %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        cmake = CMake(self)
        cmake.definitions['CONAN_DISABLE_CHECK_COMPILER'] = True
        cmake.definitions['CMAKE_CXX_FLAGS'] = '-Oz -std=c++11 -stdlib=libc++'
        cmake.definitions['CMAKE_CXX_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang++'
        cmake.definitions['CMAKE_SHARED_LINKER_FLAGS'] = cmake.definitions['CMAKE_EXE_LINKER_FLAGS'] = '-stdlib=libc++'
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_dir)
        if platform.system() == 'Darwin':
            cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
            cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
            cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath

        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.',
                            args=['-Wno-dev', '--no-warn-unused-cli'])
            cmake.build()
            cmake.install()

        with tools.chdir(self.install_dir):
            if platform.system() == 'Darwin':
                self.run('install_name_tool -id @rpath/libz.dylib lib/libz.dylib')
            elif platform.system() == 'Linux':
                patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                self.run('%s --set-soname libz.so lib/libz.so' % patchelf)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src='%s/include' % self.install_dir, dst='include/zlib')
        self.copy('libz.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['z']
