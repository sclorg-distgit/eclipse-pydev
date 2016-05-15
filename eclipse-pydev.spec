%{?scl:%scl_package eclipse-pydev}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-scl-python-bytecompile[[:space:]].*$!!g')

%global release_version 4_5_5

%if 0%{?fedora} >= 24
%global droplets droplets
%else
%global droplets dropins
%endif

Epoch: 1
Summary: Eclipse Python development plug-in
Name:    %{?scl_prefix}eclipse-pydev
Version:          4.5.5
Release:          1.1%{?dist}
License:          EPL
URL:              http://pydev.org

Source0:          https://github.com/fabioz/Pydev/archive/pydev_%{release_version}.tar.gz

# Remove windows specific code that manipulates the windows registry
Patch0:           remove-winregistry.patch
Patch1:           remove-iInfo-error.patch

# Allow system jython interpreter to be configured in preferences
Patch2:           system-jython-interpreter.patch

# Fix native name
Patch3:           native-name.patch

# Remove fund-raising dialog
Patch4:           no-fund-raising-screen.patch

# Fix for failing to kill django processes
Patch5:           fix-process-killing.patch

# Fixes mysterious empty shell when checking editor prefs
Patch6:           remove-redundant-shell.patch

Requires: %{?scl_prefix}eclipse-platform
Requires: python
Requires: %{?scl_prefix_java_common}apache-commons-logging
Requires: %{?scl_prefix_java_common}snakeyaml
Requires: %{?scl_prefix_java_common}ws-commons-util
Requires: %{?scl_prefix_java_common}xmlrpc-common
Requires: %{?scl_prefix_java_common}xmlrpc-client
Requires: %{?scl_prefix_java_common}xmlrpc-server
Requires: %{?scl_prefix}jython >= 2.7
Requires: %{?scl_prefix}antlr32-java >= 3.2

BuildRequires:    %{?scl_prefix}tycho >= 0.22.0-15
BuildRequires:    %{?scl_prefix}tycho-extras
BuildRequires:    %{?scl_prefix}eclipse-p2-discovery
BuildRequires:    %{?scl_prefix}eclipse-mylyn-context-team >= 3.5.0
BuildRequires:    %{?scl_prefix}eclipse-mylyn-ide >= 3.5.0
BuildRequires:    %{?scl_prefix_java_common}apache-commons-logging
BuildRequires:    %{?scl_prefix_java_common}snakeyaml
BuildRequires:    %{?scl_prefix_java_common}ws-commons-util
BuildRequires:    %{?scl_prefix_java_common}xmlrpc-common
BuildRequires:    %{?scl_prefix_java_common}xmlrpc-client
BuildRequires:    %{?scl_prefix_java_common}xmlrpc-server
BuildRequires:    %{?scl_prefix}jython >= 2.7
BuildRequires:    %{?scl_prefix_java_common}lucene5
BuildRequires:    %{?scl_prefix_java_common}lucene5-analysis


%description
The eclipse-pydev package contains Eclipse plugins for
Python development.

%package  mylyn
Summary:  Pydev Mylyn Focused UI
Requires: %{?scl_prefix}eclipse-mylyn-context-team >= 3.5.0
Requires: %{?scl_prefix}eclipse-mylyn-ide >= 3.5.0
Requires: %{name} = %{epoch}:%{version}-%{release}

%description mylyn
Mylyn Task-Focused UI extensions for Pydev.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%setup -q -n Pydev-pydev_%{release_version}
%patch0
%patch1 -p1
%patch2 -p1
%patch3
%patch4
%patch5 -p1
%patch6 -p1

%mvn_package "::pom:" __noinstall
%mvn_package ":*.mylyn" mylyn
%mvn_package ":*.mylyn.*" mylyn
%mvn_package ":*" core

find -name 'Copy\ of\ opentype.gif' -exec rm -f '{}' \;

# remove bundled ctypes (used only under cygwin)
rm -r plugins/org.python.pydev/pysrc/third_party/wrapped_for_pydev

# remove pre-built artifacts
find -name '*.class' -delete
find -name '*.jar' -delete
find -name '*.dll' -delete
find -name '*.dylib' -delete
find -name '*.so' -delete
rm -rf plugins/org.python.pydev.jython/Lib
touch plugins/org.python.pydev.jython/Lib

# Link to system jython
# we must include all of jython's runtime dependencies on the classpath
pushd plugins/org.python.pydev.jython
build-jar-repository -s -p . \
  jython/jython guava jnr-constants jnr-ffi jnr-netdb jnr-posix jffi jline/jline jansi/jansi antlr32/antlr-runtime \
  objectweb-asm5/asm-5 objectweb-asm5/asm-commons-5 objectweb-asm5/asm-util-5 commons-compress icu4j \
  netty/netty-buffer netty/netty-codec netty/netty-common netty/netty-handler netty/netty-transport
for j in $(ls *.jar) ; do
  if [ -z "$js" ] ; then js="$j"; else js="${js},$j"; fi
done
sed -i -e 's/\r//' -e "s/^ jython\.jar/ $js/" META-INF/MANIFEST.MF
sed -i -e "s/ jython\.jar/ $js/" build.properties
popd

# links to other system jars
ln -sf %{_javadir_java_common}/commons-logging.jar \
       plugins/org.python.pydev.shared_interactive_console/commons-logging-1.1.1.jar

ln -sf %{_javadir_java_common}/ws-commons-util.jar \
       plugins/org.python.pydev.shared_interactive_console/ws-commons-util-1.0.2.jar

ln -sf %{_javadir_java_common}/xmlrpc-client.jar \
       plugins/org.python.pydev.shared_interactive_console/xmlrpc-client-3.1.3.jar

ln -sf %{_javadir_java_common}/xmlrpc-common.jar \
       plugins/org.python.pydev.shared_interactive_console/xmlrpc-common-3.1.3.jar

ln -sf %{_javadir_java_common}/xmlrpc-server.jar \
       plugins/org.python.pydev.shared_interactive_console/xmlrpc-server-3.1.3.jar

ln -sf %{_javadir_java_common}/snakeyaml.jar \
       plugins/org.python.pydev.shared_core/libs/snakeyaml-1.11.jar

ln -sf %{_javadir_java_common}/lucene5/lucene-core-5.jar \
       plugins/org.python.pydev.shared_core/libs/lucene-core-5.2.1.jar

ln -sf %{_javadir_java_common}/lucene5/lucene-analyzers-common-5.jar \
       plugins/org.python.pydev.shared_core/libs/lucene-analyzers-common-5.2.1.jar


# Fix encodings
iconv -f CP1252 -t UTF-8 LICENSE.txt > LICENSE.txt.utf
mv LICENSE.txt.utf LICENSE.txt
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
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
%mvn_install

# fix perms on native lib
find ${RPM_BUILD_ROOT} -name attach_linux.so -exec chmod +x {} \;

# deal with linked deps
installDir=${RPM_BUILD_ROOT}/%{_libdir}/eclipse/dropins/pydev-core
pushd $installDir/eclipse/plugins

file=`find . -name commons-logging-1.1.1.jar`
rm $file
ln -sf %{_javadir_java_common}/commons-logging.jar $file

file=`find . -name ws-commons-util-1.0.2.jar`
rm $file
ln -sf %{_javadir_java_common}/ws-commons-util.jar $file

file=`find . -name xmlrpc-client-3.1.3.jar`
rm $file
ln -sf %{_javadir_java_common}/xmlrpc-client.jar $file

file=`find . -name xmlrpc-common-3.1.3.jar`
rm $file
ln -sf %{_javadir_java_common}/xmlrpc-common.jar $file

file=`find . -name xmlrpc-server-3.1.3.jar`
rm $file
ln -sf %{_javadir_java_common}/xmlrpc-server.jar $file

file=`find . -name snakeyaml-1.11.jar`
rm $file
ln -sf %{_javadir_java_common}/snakeyaml.jar $file

file=`find . -name lucene-core-5.2.1.jar`
rm $file
ln -sf %{_javadir_java_common}/lucene5/lucene-core-5.jar $file

file=`find . -name lucene-analyzers-common-5.2.1.jar`
rm $file
ln -sf %{_javadir_java_common}/lucene5/lucene-analyzers-common-5.jar $file
popd

# Symlink system jython and libs
pushd $installDir/eclipse/plugins/org.python.pydev.jython_*
rm -rf Lib
ln -sf %{_datadir}/jython/Lib
build-jar-repository -s -p . \
  jython/jython guava jnr-constants jnr-ffi jnr-netdb jnr-posix jffi jline/jline jansi/jansi antlr32/antlr-runtime \
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
%doc LICENSE.txt README.txt

%files mylyn -f .mfiles-mylyn
%doc LICENSE.txt

%changelog
* Mon Apr 04 2016 Mat Booth <mat.booth@redhat.com> - 1:4.5.5-1.1
- Fix redundant empty shell when checking editor prefs, rhbz#1311099

* Tue Mar 29 2016 Sopot Cela <scela@redhat.com> - 1:4.5.5-1
- Update to upstream 4.5.5

* Mon Feb 29 2016 Mat Booth <mat.booth@redhat.com> - 1:4.5.4-0.2.git3694021.3
- Rebuild 2016-02-29

* Wed Feb 17 2016 Sopot Cela <scela@redhat.com> - 1:4.5.4-0.2.git3694021.2
- Fix antlr dependency 

* Wed Feb 17 2016 Sopot Cela <scela@redhat.com> - 1:4.5.4-0.2.git3694021.1
- Fix snakeyaml, dependency issues and update fedora-compliant version

* Wed Feb 17 2016 Sopot Cela <scela@redhat.com> - 1:4.5.4-0.1.git3694021
- Upgrade to pre 4.5.4 release

* Wed Oct 21 2015 Mat Booth <mat.booth@redhat.com> - 1:4.1.0-2.5
- Fix for failing to kill django processes
- rhbz#1264446

* Wed Aug 12 2015 Mat Booth <mat.booth@redhat.com> - 1:4.1.0-2.4
- Add all necessary symlinks for jython
- Don't bother users with upstream project fund-raising screen
- rhbz#1251408

* Fri Jul 17 2015 Mat Booth <mat.booth@redhat.com> - 1:4.1.0-2.3
- Fix perms on native lib to fix binary stripping
- Generate debuginfo

* Thu Jul 09 2015 Mat Booth <mat.booth@redhat.com> - 1:4.1.0-2.2
- Avoid dependencies on packages from maven30 collection

* Wed Jul 08 2015 Mat Booth <mat.booth@redhat.com> - 1:4.1.0-2.1
- Import latest from Fedora

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
