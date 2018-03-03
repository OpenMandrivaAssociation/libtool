%define libname_orig libltdl
%define major 7
%define libname %mklibname ltdl %{major}
%define devname %mklibname -d ltdl

# for the testsuite:
%define _disable_ld_no_undefined 1
%define _disable_ld_as_needed 1
# LTO kills the lt_libltdl_LTX_preloaded_symbols symbol
%define _disable_lto 1
%define _disable_rebuild_configure 1

%bcond_with bootstrap

Summary:	The GNU libtool, which simplifies the use of shared libraries
Name:		libtool
Version:	2.4.6
Release:	7
License:	GPLv2+
Group:		Development/Other
Url:		http://www.gnu.org/software/libtool/libtool.html
Source0:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source1:	libtool.rpmlintrc
# deprecated: introduced in July 2003
# (cf http://lists.mandriva.com/cooker-amd64/2003-12/msg00046.php)
# but is not needed anymore since Sept 2003 change in rpm "Make "x86_64" the
# canonical arch on amd64"

# (Abel) Patches please only modify ltmain.in and don't touch ltmain.sh
# otherwise ltmain.sh will not be regenerated, and patches will be lost

# (cjw) when a library that is produced in the build is also linked against, 
#       make sure that the library in the rpm install dir is used for relinking 
#	even if (an older version of) the lib is installed on the system
Patch0:		relink.patch
#
Patch1:		libtool-2.2.10-rpath.patch
Patch2:		ltmain-SED.patch
# Support /usr/bin/ld == LLD
Patch3:		libtool-2.4.6-lld.patch
# (bero) any compiler actually worth using (definitely including clang and gcc)
# knows better than libtool what its standard libraries are.
Patch4:		libtool-2.4.6-no-bogus-nostdlib.patch
Patch12:	do-not-link-against-deplibs.patch
Patch13:	drop-ld-no-undefined-for-shared-lib-modules.patch
Patch14:	fix-checking-libltdl-is-installed-installable.patch
# (cjw) do not use CFLAGS when running gcj
Patch16:	libtool-2.2.6-use-gcjflags-for-gcj.patch
# (cjw) in the libltdl install test, use --enable-ltdl-install to make sure 
#       the library is built even if it is installed on the system
Patch17:	libtool-2.2.6b-libltdl-install-test-fix.patch
#Patch19:	libtool-2.4.2-drop-soname-for-modules.patch
# (fwang) detect libltdl.so rather than libltdl.la, as we will delete them
Patch20:	libtool-2.4.2-use-so-to-detect-libltdl.patch

# (tpg) upstream git
Patch100:	0000-libtool-fix-GCC-linking-with-specs.patch
Patch101:	0001-bootstrap-fix-race-in-temporary-Makefile.patch
Patch105:	0005-libool.m4-add-ARFLAGS-variable.patch
Patch106:	0006-ARFLAGS-use-cr-instead-of-cru-by-default.patch
Patch107:	0007-maint-relax-sc_prohibit_test_dollar-check.patch
Patch113:	0013-gl-tests-new-tests-for-func_quote-family.patch
Patch114:	0014-syntax-check-fix-sed-syntax-errors.patch
Patch117:	0017-m4-libtool.m4-export-AIX-TLS-symbols.patch
Patch118:	0018-gl-tests-make-the-failure-more-readable.patch
Patch119:	0019-libtool-fix-GCC-clang-linking-with-fsanitize.patch
Patch122:	0022-libltdl-handle-ENOMEM-sooner.patch
Patch126:	0026-libtoolize-exec-automake-and-autoconf-only-with-help.patch
Patch127:	0027-m4-libtool.m4-FreeBSD-elftoolchain-strip-support.patch
Patch128:	0028-libtool-pass-through-fuse-ld-flags.patch
Patch129:	0029-tests-fix-objdir-hardcoding-check-with-CFLAGS-g3.patch
Patch130:	0030-libtool-set-file_list_spec-to-on-OS-2.patch
Patch132:	0032-libltdl-handle-ENOMEM-in-lt_dlloader_remove.patch

BuildRequires:	help2man
BuildRequires:	texinfo
%if ! %{with bootstrap}
BuildRequires:	gcc-gfortran
%ifarch %{ix86} x86_64
BuildRequires:	quadmath-devel
%endif
%endif
Requires:	%{name}-base = %{EVRD}

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
Requires:	file

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
License:	LGPLv2.1+
Provides:	%{libname_orig} = %{EVRD}

%description -n %{libname}
Shared library files for libtool DLL library from the libtool package.

%package -n %{devname}
Group:		Development/C
Summary:	Development files for libtool
License:	LGPLv2.1+
Requires:	%{name} = %{EVRD}
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Provides:	%{libname_orig}-devel = %{EVRD}

%description -n %{devname}
Development headers, and files for development from the libtool package.

%prep
%setup -q
%apply_patches
#./bootstrap --force

%build
# don't use configure macro - it forces libtoolize, which is bad -jgarzik
# Use configure macro but define __libtoolize to be /bin/true -Geoff
%define __libtoolize /bin/true
# And don't overwrite config.{sub,guess} in this package as well -- Abel
%define __cputoolize /bin/true

%configure --disable-static
%make

# lame & ugly, trying to fix up relative paths that's made their way into libtool..
DIRS=$(cat libtool|grep compiler_lib_search_dirs|grep -F ..|uniq|cut -d'"' -f2)
PATHS=$(cat libtool|grep compiler_lib_search_path|grep -F ..|uniq|cut -d'"' -f2)
for i in $DIRS; do pushd $i; ABSOLUTE="$ABSOLUTE $PWD"; popd; done
ABSOLUTE=$(echo $ABSOLUTE | sed -e 's#%{_libdir} /%{_lib}#/%{_lib}#g' -e 's#%{_libdir} %{_libdir}#%{_libdir}#g')
sed -e 's#compiler_lib_search_dirs=\"$DIRS\"#compiler_lib_search_dirs=\"$ABSOLUTE\"#g' -i libtool
for i in $ABSOLUTE; do SEARCH=$(echo $SEARCH -L$i); done
sed -e 's#compiler_lib_search_path=\"$PATHS\"#compiler_lib_search_path=\"$SEARCH\"#g' -i libtool

#%%check
#pushd    build-%{_target_cpu}-%{_target_os}
#set +x
#echo ====================TESTING=========================
#set -x
## all tests must pass here
## disabling icecream since some tests check the output of gcc
#ICECC=no %make check
#set +x
#echo ====================TESTING END=====================
#set -x
#
#popd

%install
%makeinstall_std

# Let's retain compatibility with pathname hardcodes from earlier...
mv %{buildroot}%{_datadir}/libtool/build-aux %{buildroot}%{_datadir}/libtool/config
ln -s config %{buildroot}%{_datadir}/libtool/build-aux

%files
%doc AUTHORS NEWS README THANKS TODO
%{_bindir}/libtool
%{_mandir}/man1/libtool.1*

%files base
%{_bindir}/libtoolize
%{_mandir}/man1/libtoolize.*
%{_infodir}/libtool.info*
%{_datadir}/libtool
%{_datadir}/aclocal/*.m4

%files -n %{libname}
%{_libdir}/libltdl.so.%{major}*

%files -n %{devname}
%doc libltdl/README
%{_includedir}/*
%{_libdir}/*.so
