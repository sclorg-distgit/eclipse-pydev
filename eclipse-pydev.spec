%{?scl:%scl_package eclipse-pydev}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-scl-python-bytecompile[[:space:]].*$!!g')
%global __jar_repack %{nil}
%global release_version 5_1_2

%global droplets droplets

Epoch: 1
Summary: Eclipse Python development plug-in
Name:    %{?scl_prefix}eclipse-pydev
Version:          5.1.2
Release:          1.%{baserelease}%{?dist}
License:          EPL
URL:              http://pydev.org

Source0:           https://github.com/fabioz/Pydev/archive/pydev_%{release_version}.tar.gz

# Remove windows specific code that manipulates the windows registry
Patch0:           remove-winregistry.patch
Patch1:           remove-iInfo-error.patch

# Allow system jython interpreter to be configured in preferences
Patch2:           system-jython-interpreter.patch

# Fix native name
Patch3:           native-name.patch

# Fix for failing to kill django processes
Patch4:           fix-process-killing.patch

# Fix valid encoding detection failure
Patch5:           encoding-tolerance.patch

# Remove fund-raising dialog
Patch6:           no-fund-raising-screen.patch

Requires: %{?scl_prefix}eclipse-platform
Requires: python
Requires: %{?scl_prefix_java_common}apache-commons-logging
Requires: %{?scl_prefix_java_common}snakeyaml
Requires: %{?scl_prefix_java_common}ws-commons-util
Requires: %{?scl_prefix_java_common}xmlrpc-common
Requires: %{?scl_prefix_java_common}xmlrpc-client
Requires: %{?scl_prefix_java_common}xmlrpc-server
Requires: %{?scl_prefix}jython >= 2.7.1
Requires: %{?scl_prefix}antlr32-java >= 3.2-12
Requires: python-django
BuildRequires:    %{?scl_prefix}tycho
BuildRequires:    %{?scl_prefix}tycho-extras
BuildRequires:    %{?scl_prefix}eclipse-mylyn >= 3.16.0
BuildRequires:    %{?scl_prefix}eclipse-p2-discovery
BuildRequires:    %{?scl_prefix_java_common}apache-commons-logging
BuildRequires:    %{?scl_prefix_java_common}snakeyaml
BuildRequires:    %{?scl_prefix_java_common}ws-commons-util
BuildRequires:    %{?scl_prefix_java_common}xmlrpc-common
BuildRequires:    %{?scl_prefix_java_common}xmlrpc-client
BuildRequires:    %{?scl_prefix_java_common}xmlrpc-server
BuildRequires:    %{?scl_prefix}jython >= 2.7.1
BuildRequires:    %{?scl_prefix_java_common}lucene5
BuildRequires:    %{?scl_prefix_java_common}lucene5-analysis

%description
The eclipse-pydev package contains Eclipse plugins for
Python development.

%package  mylyn
Summary:  Pydev Mylyn Focused UI
Requires: %{name} = %{epoch}:%{version}-%{release}

%description mylyn
Mylyn Task-Focused UI extensions for Pydev.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n Pydev-pydev_%{release_version}
%patch0
%patch1 -p1
%patch2 -p1
%patch3
%patch4 -p1
%patch5 -p1
%patch6

%mvn_package "::pom:" __noinstall
%mvn_package ":*.mylyn" mylyn
%mvn_package ":*.mylyn.*" mylyn
%mvn_package ":*" core

# Remove bundled ctypes (used only under cygwin)
rm -r plugins/org.python.pydev/pysrc/third_party/wrapped_for_pydev
# Remove bundled pep8 and lib2to3
rm -r plugins/org.python.pydev/pysrc/third_party/pep8/lib2to3

# Remove pre-built artifacts
find -name '*.class' -delete
find -name '*.jar' -delete
find -name '*.dll' -delete
find -name '*.dylib' -delete
find -name '*.so' -delete
rm -rf plugins/org.python.pydev.jython/Lib
mkdir -p plugins/org.python.pydev.jython/Lib

# Link to system jython
# we must include all of jython's runtime dependencies on the classpath
pushd plugins/org.python.pydev.jython
build-jar-repository -s -p . \
  jython/jython guava jnr-constants jnr-ffi jnr-netdb jnr-posix jffi jline/jline jansi/jansi antlr32/antlr-runtime-3.2 \
  objectweb-asm5/asm-5 objectweb-asm5/asm-commons-5 objectweb-asm5/asm-util-5 commons-compress icu4j \
  netty/netty-buffer netty/netty-codec netty/netty-common netty/netty-handler netty/netty-transport
for j in $(ls *.jar) ; do
  if [ -z "$js" ] ; then js="$j"; else js="${js},$j"; fi
done
sed -i -e 's/\r//' -e "s/^ jython\.jar/ $js/" META-INF/MANIFEST.MF
sed -i -e "s/ jython\.jar/ $js/" build.properties
popd

# Symlinks to other system jars
ln -sf $(build-classpath commons-logging) \
       plugins/org.python.pydev.shared_interactive_console/commons-logging-1.1.1.jar
ln -sf $(build-classpath ws-commons-util) \
       plugins/org.python.pydev.shared_interactive_console/ws-commons-util-1.0.2.jar
ln -sf $(build-classpath xmlrpc-client) \
       plugins/org.python.pydev.shared_interactive_console/xmlrpc-client-3.1.3.jar
ln -sf $(build-classpath xmlrpc-common) \
       plugins/org.python.pydev.shared_interactive_console/xmlrpc-common-3.1.3.jar
ln -sf $(build-classpath xmlrpc-server) \
       plugins/org.python.pydev.shared_interactive_console/xmlrpc-server-3.1.3.jar
ln -sf $(build-classpath snakeyaml) \
       plugins/org.python.pydev.shared_core/libs/snakeyaml-1.11.jar
ln -sf $(build-classpath lucene5/lucene-core-5) \
       plugins/org.python.pydev.shared_core/libs/lucene-core-5.2.1.jar
ln -sf $(build-classpath lucene5/lucene-analyzers-common-5) \
       plugins/org.python.pydev.shared_core/libs/lucene-analyzers-common-5.2.1.jar

# Fix encodings
iconv -f CP1252 -t UTF-8 LICENSE.txt > LICENSE.txt.utf
mv LICENSE.txt.utf LICENSE.txt
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
# build native part first
pushd plugins/org.python.pydev/pysrc/pydevd_attach_to_process/linux &>/dev/null
g++ %{optflags} -shared -o attach_linux.so -fPIC -nostartfiles attach_linux.c
mv attach_linux.so ../attach_linux.so
popd &>/dev/null

# build everything else
%mvn_build -j -f -- -DforceContextQualifier=$(date +%Y%m%d%H00)
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install

# fix perms on native lib
find ${RPM_BUILD_ROOT} -name attach_linux.so -exec chmod +x {} \;

# Have to re-symlink embedded system jars
installDir=${RPM_BUILD_ROOT}/%{_libdir}/eclipse/%{droplets}/pydev-core
pushd $installDir/eclipse/plugins
for f in commons-logging \
         ws-commons-util \
         xmlrpc-client \
         xmlrpc-common \
         xmlrpc-server \
         snakeyaml \
         lucene5/lucene-core-5 \
         lucene5/lucene-analyzers-common-5 ; do
  file=$(find . -name $(basename $f)*.jar)
  rm $file
  ln -sf $(build-classpath $f) $file
done
popd

# Symlink system jython and libs
sed -i -e '/Lib/s/%%dir//' .mfiles-core
pushd $installDir/eclipse/plugins/org.python.pydev.jython_*
rm -rf Lib
ln -sf %{_datadir}/jython/Lib
build-jar-repository -s -p . \
  jython/jython guava jnr-constants jnr-ffi jnr-netdb jnr-posix jffi jline/jline jansi/jansi antlr32/antlr-runtime-3.2 \
  objectweb-asm5/asm-5 objectweb-asm5/asm-commons-5 objectweb-asm5/asm-util-5 commons-compress icu4j \
  netty/netty-buffer netty/netty-codec netty/netty-common netty/netty-handler netty/netty-transport
popd

# convert .py$ files from mode 0644 to mode 0755
sixFourFourfiles=$(find ${RPM_BUILD_ROOT} -name '*\.py' -perm 0644 | xargs)
if [ ${sixFourFourfiles:-0} -ne 0 ]; then
  chmod 0755 ${sixFourFourfiles}
fi
%{?scl:EOF}


%files -f .mfiles-core
%doc LICENSE.txt
%doc README.txt

%files mylyn -f .mfiles-mylyn
%doc LICENSE.txt

%changelog
* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 1:5.1.2-1.2
- Prevent bytecode compilation inside the SCL
- Always use droplets location
- Fixup references to asm 5 and lucene 5
- Patch out fund raising screen
- Remove pep/autopep8 symlinking for now

* Fri Jul 29 2016 Mat Booth <mat.booth@redhat.com> - 1:5.1.2-1.1
- Auto SCL-ise package for rh-eclipse46 collection

* Fri Jun 24 2016 Mat Booth <mat.booth@redhat.com> - 1:5.1.2-1
- Update to release 5.1.2
- Remove bundled third-party libs rhbz#1339362
- Fix valid encoding detection failure rhbz#1327642
- Improve system jython integration
- Make symlinking jars more portable

* Fri Jun 17 2016 Alexander Kurtakov <akurtako@redhat.com> 1:5.1.1-1
- Update to upstream 5.1.1.

* Wed May 18 2016 Sopot Cela <scela@redhat.com> 1:5.0.0-1
- Update to upstream 5.0.0

* Wed May 04 2016 Sopot Cela <scela@redhat.com> 1:4.6.0-1
- Update to upstream 4.6.0

* Mon Apr 25 2016 Sopot Cela <scela@redhat.com> 1:4.5.5-3
- Patch so it builds with Neon

* Wed Apr 6 2016 Alexander Kurtakov <akurtako@redhat.com> 1:4.5.5-2
- Switch python* requires to python3.

* Fri Mar 25 2016 Alexander Kurtakov <akurtako@redhat.com> 1:4.5.5-1
- Update to upstream 4.5.5.

* Thu Feb 04 2016 Sopot Cela <scela@redhat.com> 1:4.5.4-0.2.git3694021
- Minor changelog correction

* Thu Feb 04 2016 Sopot Cela <scela@redhat.com> 1:4.5.4-0.1
- Upgrade to upstream 4.5.4

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:4.5.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 22 2016 Alexander Kurtakov <akurtako@redhat.com> 1:4.5.3-1
- Update to upstream 4.5.3.

* Tue Jan 19 2016 Alexander Kurtakov <akurtako@redhat.com> 1:4.5.1-1
- Update to upstream 4.5.1.

* Sun Nov 29 2015 Mat Booth <mat.booth@redhat.com> - 1:4.4.0-3
- Rebuild to fix broken antlr symlink

* Wed Oct 21 2015 Mat Booth <mat.booth@redhat.com> - 1:4.4.0-2
- Fix for failing to kill django processes
- rhbz#1264446

* Thu Oct 8 2015 Alexander Kurtakov <akurtako@redhat.com> 1:4.4.0-1
- Update to upstream 4.4.0.
- Disable brp-repack.

* Mon Sep 14 2015 Roland Grunberg <rgrunber@redhat.com> - 1:4.3.0-3
- Rebuild as an Eclipse p2 Droplet.

* Mon Aug 31 2015 Roland Grunberg <rgrunber@redhat.com> - 1:4.3.0-2
- Minor change to build as a droplet.

* Fri Aug 21 2015 akurtakov <akurtakov@localhost.localdomain> 1:4.3.0-1
- Update to upstream 4.3.0.
- Simplify BR/R to adapt new names and remove autogenerated ones now.

* Wed Aug 12 2015 Mat Booth <mat.booth@redhat.com> - 1:4.2.0-3
- Add all necessary symlinks for jython

* Mon Jul 20 2015 Mat Booth <mat.booth@redhat.com> - 1:4.2.0-2
- Fix perms on native lib to fix binary stripping
- Generate debuginfo

* Thu Jul 16 2015 Sopot Cela <scela@redhat.com> - 1:4.2.0-1
- Update to 4.2.0 release

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:4.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 27 2015 Alexander Kurtakov <akurtako@redhat.com> 1:4.1.0-1
- Update to upstream 4.1.0 release.

* Wed May 13 2015 Alexander Kurtakov <akurtako@redhat.com> 1:4.0.0-2
- Make mylyn subpackage archful as timestamps make diff and fail builds.

* Wed Apr 15 2015 Mat Booth <mat.booth@redhat.com> - 1:4.0.0-1
- Update to latest upstream release
- No longer necessary to symlink optparse
- Now archful package due to having a native component

* Mon Dec 8 2014 Alexander Kurtakov <akurtako@redhat.com> 1:3.7.1-2
- Build with xmvn.

* Thu Sep 18 2014 Alexander Kurtakov <akurtako@redhat.com> 1:3.7.1-1
- Update to upstream 3.7.1.

* Thu Jul 31 2014 Mat Booth <mat.booth@redhat.com> - 1:3.6.0-1
- Update to latest upstream release
- Require jython 2.7
- Remove no longer needed patches

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.5.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Jun 04 2014 Mat Booth <mat.booth@redhat.com> - 1:3.5.0-3
- Patch to allow system jython interpreter to be configured in preferences

* Mon Jun 02 2014 Mat Booth <mat.booth@redhat.com> - 1:3.5.0-2
- Patch to build with latest version of jython
- Install license files
- No longer need to package a portion of jython's lib dir

* Thu May 29 2014 Alexander Kurtakov <akurtako@redhat.com> 1:3.5.0-1
- Update to 3.5.0.

* Thu Mar 20 2014 Alexander Kurtakov <akurtako@redhat.com> 1:3.4.1-1
- Update to 3.4.1.

* Wed Feb 12 2014 Alexander Kurtakov <akurtako@redhat.com> 1:3.3.3-1
- Update to 3.3.3.

* Mon Dec 30 2013 Alexander Kurtakov <akurtako@redhat.com> 1:3.2.0-1
- Update to 3.2.0.

* Fri Dec 13 2013 Alexander Kurtakov <akurtako@redhat.com> 1:3.1.0-1
- Update to 3.1.0.

* Mon Nov 11 2013 Alexander Kurtakov <akurtako@redhat.com> 1:3.0-1
- Update to 3.0.
- Drop old changelog now that we move to tycho builds.
