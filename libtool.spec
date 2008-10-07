%define major	3
%define libname_orig	libltdl
%define libname		%mklibname ltdl %{major}

# allow --with bootstrap
%define bootstrap 0
%{?_with_bootstrap: %global bootstrap 1}

# define biarch platforms
%define biarches x86_64 ppc64 sparc64
%ifarch x86_64
%define alt_arch i586
%endif
%ifarch ppc64
%define alt_arch ppc
%endif
%ifarch sparc64
%define alt_arch sparc
%endif

# define fortran compiler
%if %{mdkversion} >= 200600
%define fortran_compiler gfortran
%else
%define fortran_compiler g77
%endif

Summary:	The GNU libtool, which simplifies the use of shared libraries
Name:		libtool
Version:	1.5.26
Release:	%mkrel 6
License:	GPL
Group:		Development/Other
URL:		http://www.gnu.org/software/libtool/libtool.html
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

Source:		ftp://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.gz
Source1:	%{SOURCE0}.sig
Source2:	libtool-cputoolize.sh

# (Abel) Patches please only modify ltmain.in and don't touch ltmain.sh
# otherwise ltmain.sh will not be regenerated, and patches will be lost
Patch0:		libtool-1.5.6-relink.patch
# Set sys_lib_dlsearch_path_spec correctly on lib64 systems:
Patch1:		libtool-1.5.26-lib64.patch
Patch2:		libtool-1.5.6-ltmain-SED.patch
Patch3:		libtool-1.5.6-libtoolize--config-only.patch
Patch4:		libtool-1.5.6-test-dependency.patch
Patch5:		libtool-1.5-testfailure.patch
Patch7:		libtool-1.5.20-fix-gcj-reload-cmd.patch
Patch10:	libtool-1.5.22-anygcc.patch

# disable ugly test. needed by link_all_depslibs patch
Patch11:	libtool-1.5.24-deplibs_test_disable.patch
# from debian, cf http://wiki.mandriva.com/en/Overlinking
Patch12:	libtool-1.5.24-link_all_deplibs.patch
# cf http://wiki.mandriva.com/en/2009-underlinking-overlinking
Patch13:	libtool-1.5.26-drop-ld-no-undefined-for-shared-lib-modules.patch

%ifarch %biarches
BuildRequires:	linux32
%endif
BuildRequires:	automake1.8
Buildrequires:	autoconf2.5
%if ! %{bootstrap}
BuildRequires:	gcc-%{fortran_compiler}
BuildRequires:	gcc-java
%endif
Requires:	%{name}-base = %{version}-%{release}

%description
The libtool package contains the GNU libtool, a set of shell scripts
which automatically configure UNIX and UNIX-like architectures to
generically build shared libraries.  Libtool provides a consistent,
portable interface which simplifies the process of using shared
libraries.

If you are developing programs which will use shared libraries, you
should install libtool.

%package base
Group:		Development/C
Summary:	Basic package for %{name}
Conflicts:	libtool < 1.5.20-4mdk
Requires:	file
# cputoolize uses sed
Requires: 	sed
Requires(post): info-install
Requires(preun): info-install

%description base
The libtool package contains the GNU libtool, a set of shell scripts
which automatically configure UNIX and UNIX-like architectures to
generically build shared libraries.  Libtool provides a consistent,
portable interface which simplifies the process of using shared
libraries.

If you are developing programs which will use shared libraries, you
should install libtool.

%package -n %{libname}
Group:		Development/C
Summary:	Shared library files for libtool
License:	LGPL
Provides:	%{libname_orig} = %{version}-%{release}
# old libextractor wrongly provided its own libltdl:
Conflicts:	%{_lib}extractor1 < 0.5.18a

%description -n %{libname}
Shared library files for libtool DLL library from the libtool package.

%package -n %{libname}-devel
Group:		Development/C
Summary:	Development files for libtool
License:	LGPL
Requires:	%{name} = %{version}
Requires:	%{libname} = %{version}
Provides:	%{libname_orig}-devel = %{version}-%{release}
Provides:	%{name}-devel

%description -n %{libname}-devel
Development headers, and files for development from the libtool package.

%prep
%setup -q
%patch0 -p1 -b .relink
%patch1 -p1 -b .lib64
%patch2 -p1 -b .ltmain-SED
%patch3 -p1 -b .libtoolize--config-only
%patch4 -p1 -b .test-dependency
%patch5 -p1
%patch7 -p1 -b .gcj-reload
%patch10 -p1 -b .anygcc
%patch11 -p1 -b .uglytest
%patch12 -p1 -b .overlinking
%patch13 -p1 -b .underlinking

./bootstrap

%build
# don't use configure macro - it forces libtoolize, which is bad -jgarzik
# Use configure macro but define __libtoolize to be /bin/true -Geoff
%define __libtoolize /bin/true
# And don't overwrite config.{sub,guess} in this package as well -- Abel
%define __cputoolize /bin/true

# build alt-arch libtool first
# NOTE: don't bother to make libtool biarch capable within the same
# "binary", use the multiarch facility to dispatch to the right script.
%ifarch %biarches
mkdir -p build-%{alt_arch}-%{_target_os}
pushd    build-%{alt_arch}-%{_target_os}
linux32 ../configure --prefix=%{_prefix} --build=%{alt_arch}-%{_real_vendor}-%{_target_os}%{?_gnu}
linux32 make
popd
%endif

mkdir -p build-%{_target_cpu}-%{_target_os}
pushd    build-%{_target_cpu}-%{_target_os}
CONFIGURE_TOP=.. %configure2_5x
make

# Do not use -nostdlib to build libraries, and so no need to hardcode gcc path (mdvbz#44616)
# (taken from debian, http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=206356)
# ([PIX] this is not done as a patch since the patch would be too big to maintain)
sed -i -e 's/^\(predep_objects\)=.*/\1=""/' \
       -e 's/^\(postdep_objects\)=.*/\1=""/' \
       -e 's/^\(compiler_lib_search_path\)=.*/\1=""/' \
       -e 's:^\(sys_lib_search_path_spec\)=.*:\1="/lib/ /usr/lib/ /usr/X11R6/lib/ /usr/local/lib/":' \
       -e 's/^\(archive_cmds=\".*\) -nostdlib /\1 /' \
       -e 's/^\(archive_expsym_cmds=\".*\) -nostdlib /\1 /' \
       libtool

popd

%check
pushd    build-%{_target_cpu}-%{_target_os}
set +x
echo ====================TESTING=========================
set -x
#ifarch ia64
# - ia64: SIGILL when running hellodl
#make check || echo make check failed
#else
# all tests must pass here
make check
#endif
set +x
echo ====================TESTING END=====================
set -x

make -C demo clean
popd

%install
rm -fr %{buildroot}
%makeinstall_std -C build-%{_target_cpu}-%{_target_os}

sed -e "s,@prefix@,%{_prefix}," -e "s,@datadir@,%{_datadir}," %{SOURCE2} \
  > %{buildroot}%{_bindir}/cputoolize
chmod 755 %{buildroot}%{_bindir}/cputoolize

# biarch support
%ifarch %biarches
%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/libtool
install -m 755 build-%{alt_arch}-%{_target_os}/libtool $RPM_BUILD_ROOT%{_bindir}/libtool
linux32 /bin/sh -c '%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/libtool'
%endif

%clean
rm -fr %{buildroot}

%post base
%_install_info %{name}.info

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%preun base
%_remove_install_info %{name}.info

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root)
%doc AUTHORS INSTALL NEWS README
%doc THANKS TODO ChangeLog*
%{_bindir}/libtool
%ifarch %biarches
%define alt_multiarch_bindir %(linux32 /bin/rpm --eval %%multiarch_bindir)
%{multiarch_bindir}
%{multiarch_bindir}/libtool
%{alt_multiarch_bindir}
%{alt_multiarch_bindir}/libtool
%endif

%files base
%defattr(-,root,root)
%doc AUTHORS INSTALL NEWS README
%doc THANKS TODO ChangeLog*
%{_bindir}/cputoolize
%{_bindir}/libtoolize
%{_infodir}/libtool.info*
%{_datadir}/libtool
%{_datadir}/aclocal/*.m4

%files -n %{libname}
%defattr(-,root,root)
%doc libltdl/README
%{_libdir}/*.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%doc demo
%{_includedir}/*
%{_libdir}/*.a
%{_libdir}/*.so
%{_libdir}/*.la


