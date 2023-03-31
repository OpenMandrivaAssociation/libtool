# libltdl is used by pulseaudio, pulseaudio is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define libname_orig libltdl
%define major 7
%define libname %mklibname ltdl %{major}
%define devname %mklibname -d ltdl

%define lib32name libltdl%{major}
%define dev32name libltdl-devel

# for the testsuite:
%define _disable_ld_no_undefined 1
%define _disable_ld_as_needed 1
# LTO kills the lt_libltdl_LTX_preloaded_symbols symbol
%define _disable_lto 1
%define _disable_rebuild_configure 1

%bcond_with bootstrap

Summary:	The GNU libtool, which simplifies the use of shared libraries
Name:		libtool
Version:	2.4.7
Release:	2
License:	GPLv2+
Group:		Development/Other
Url:		http://www.gnu.org/software/libtool/libtool.html
Source0:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source10:	libtool.rpmlintrc
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

# Pass --rtlib=* to the linker unmodified
# (must be applied after upstream patches because of conflicts)
Patch200:	libtool-2.4.6-pass-rtlib.patch
# If we put something on ldflags, we mean it to get through to ld!!!
# Just stop the insanity.
Patch201:	libtool-2.4.6-less-insane-linker-filtering.patch

BuildRequires:	help2man
BuildRequires:	texinfo
BuildRequires:	hostname
BuildRequires:	git-core
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

%if %{with compat32}
%package -n %{lib32name}
Group:		Development/C
Summary:	Shared library files for libtool (32-bit)
License:	LGPLv2.1+
BuildRequires:	libc6

%description -n %{lib32name}
Shared library files for libtool DLL library from the libtool package.

%package -n %{dev32name}
Group:		Development/C
Summary:	Development files for libtool (32-bit)
License:	LGPLv2.1+
Requires:	%{devname} = %{EVRD}
Requires:	%{lib32name} = %{EVRD}

%description -n %{dev32name}
Development headers, and files for development from the libtool package.
%endif

%prep
%autosetup -p1
#./bootstrap --force
cd libltdl
autoheader
aclocal
automake -a
autoconf

%build
# don't use configure macro - it forces libtoolize, which is bad -jgarzik
# Use configure macro but define __libtoolize to be /bin/true -Geoff
%define __libtoolize /bin/true
# And don't overwrite config.{sub,guess} in this package as well -- Abel
%define __cputoolize /bin/true

export CONFIGURE_TOP="$(pwd)"
%if %{with compat32}
mkdir build32
cd build32
%configure32
cd ..
%endif

mkdir build
cd build
%configure
cd ..


%if %{with compat32}
%make_build -C build32
%endif
%make_build -C build

# Do not use -nostdlib to build libraries, and so no need to hardcode gcc path (mdvbz#44616)
# (taken from debian, http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=206356)
# ([PIX] this is not done as a patch since the patch would be too big to maintain)
sed -i -e 's/^\(predep_objects\)=.*/\1=""/' \
       -e 's/^\(postdep_objects\)=.*/\1=""/' \
       -e 's/^\(compiler_lib_search_path\)=.*/\1=""/' \
       -e 's:^\(sys_lib_search_path_spec\)=.*:\1="/lib/ /usr/lib/ /usr/X11R6/lib/ /usr/local/lib/":' \
       -e 's/^\(archive_cmds=\".*\) -nostdlib /\1 /' \
       -e 's/^\(archive_expsym_cmds=\".*\) -nostdlib /\1 /' \
       build*/libtool

%check
set +x
echo ====================TESTING=========================
set -x
# all tests must pass here
# disabling icecream since some tests check the output of gcc
# Also disabling parallel make, as of 2.4.6 causes hangs on -j32 boxes
%if %{with compat32}
ICECC=no make -C build32 check VERBOSE=yes | tee make_check.log 2>&1 # || (cat make_check.log && false)
%endif
ICECC=no make -C build check VERBOSE=yes | tee make_check.log 2>&1 # || (cat make_check.log && false)
set +x
echo ====================TESTING END=====================
set -x

%install
%if %{with compat32}
%make_install -C build32
%endif
%make_install -C build

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

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libltdl.so.%{major}*

%files -n %{dev32name}
%{_prefix}/lib/*.so
%endif
