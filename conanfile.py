from conans import ConanFile, tools

class ZLibConan(ConanFile):
    name = 'zlib'

    source_version = '1.2.8'
    package_version = '1'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-1@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://zlib.net/'
    license = 'http://zlib.net/zlib_license.html'
    description = 'A compression library'
    source_dir = 'zlib-%s' % source_version
    install_dir = '_install'

    def source(self):
        tools.get('http://www.zlib.net/fossils/zlib-%s.tar.gz' % self.source_version,
                  sha256='36658cb768a54c1d4dec43c3116c27ed893e88b02ecfcb44f2166f9c0b7f2a0d')

    def build(self):
        with tools.chdir(self.source_dir):
            self.run('CC=%s CFLAGS="-Oz -mmacosx-version-min=10.10" LDFLAGS="-mmacosx-version-min=10.10 -Wl,-headerpad_max_install_names -Wl,-install_name,@rpath/libz.dylib" ./configure --prefix=../%s --archs="-arch x86_64" --64'
                     % (self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                        self.install_dir))
            self.run('make')
            self.run('make install')

    def package(self):
        self.copy('*.h', src='%s/include' % self.install_dir, dst='include/zlib')
        self.copy('libz.dylib', src='%s/lib' % self.install_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['z']
