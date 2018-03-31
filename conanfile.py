from conans import ConanFile, tools
import platform

class ZLibConan(ConanFile):
    name = 'zlib'

    source_version = '1.2.8'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://zlib.net/'
    license = 'http://zlib.net/zlib_license.html'
    description = 'A compression library'
    source_dir = 'zlib-%s' % source_version
    install_dir = '_install'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.9@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://www.zlib.net/fossils/zlib-%s.tar.gz' % self.source_version,
                  sha256='36658cb768a54c1d4dec43c3116c27ed893e88b02ecfcb44f2166f9c0b7f2a0d')

        # zlib.h contains the license in the first block comment.
        # Truncate it at the end of that comment.
        self.run('sed "/\\*\\//q" %s/zlib.h > %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        with tools.chdir(self.source_dir):
            cflags = '-Oz'
            ldflags = '-Oz'

            if platform.system() == 'Darwin':
                cflags += ' -mmacosx-version-min=10.10'
                ldflags += ' -mmacosx-version-min=10.10 -Wl,-headerpad_max_install_names -Wl,-install_name,@rpath/libz.dylib'

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
                'CFLAGS': cflags,
                'LDFLAGS': ldflags,
            }
            with tools.environment_append(env_vars):
                self.run('./configure --prefix=../%s --archs="-arch x86_64" --64' % self.install_dir)
                self.run('make')
                self.run('make install')

        with tools.chdir(self.install_dir):
            if platform.system() == 'Linux':
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
