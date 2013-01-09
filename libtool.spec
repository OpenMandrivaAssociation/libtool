%define libname_orig libltdl
%define major	7
%define libname	%mklibname ltdl %{major}
%define devname	%mklibname -d ltdl

# for the testsuite:
%define _disable_ld_no_undefined 1
%define _disable_ld_as_needed 1

%bcond_with	bootstrap

%define arch_has_java 1
%ifarch %{arm} %{mips}
%define arch_has_java 0
%endif
%if %{with bootstrap}
%define arch_has_java 0
%endif

Summary:	The GNU libtool, which simplifies the use of shared libraries
Name:		libtool
Version:	2.4.2
Release:	10
License:	GPLv2+
Group:		Development/Other
URL:		http://www.gnu.org/software/libtool/libtool.html

Source0:	ftp://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source1:	%{SOURCE0}.sig

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
# (abondrov) pass -fuse-ld= flag to allow switching between bfd and gold
Patch3:		libtool-2.4.2-fuse-ld.patch
Patch12:	do-not-link-against-deplibs.patch
Patch13:	drop-ld-no-undefined-for-shared-lib-modules.patch
Patch14:	fix-checking-libltdl-is-installed-installable.patch
# (cjw) do not use CFLAGS when running gcj
Patch16:	libtool-2.2.6-use-gcjflags-for-gcj.patch
# (cjw) in the libltdl install test, use --enable-ltdl-install to make sure 
#       the library is built even if it is installed on the system
Patch17:	libtool-2.2.6b-libltdl-install-test-fix.patch
# (cjw) mdemo-dryrun test may fail because file sizes are incorrect in 'before' 
#       file list
Patch18:	libtool-2.4-dryrun-sleepmore.patch
#Patch19:	libtool-2.4.2-drop-soname-for-modules.patch
# (fwang) detect libltdl.so rather than libltdl.la, as we will delete them
Patch20:	libtool-2.4.2-use-so-to-detect-libltdl.patch

BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	help2man
%if ! %{with bootstrap}
BuildRequires:	gcc-gfortran
%endif
%if %{arch_has_java}
BuildRequires:	gcc-java
BuildRequires:	pkgconfig(libgcj-4.7)
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

%package	base
Group:		Development/C
Summary:	Basic package for %{name}
Requires:	file

%description	base
The libtool package contains the GNU libtool, a set of shell scripts
which automatically configure UNIX and UNIX-like architectures to
generically build shared libraries.  Libtool provides a consistent,
portable interface which simplifies the process of using shared
libraries.

If you are developing programs which will use shared libraries, you
should install libtool.

%package -n	%{libname}
Group:		Development/C
Summary:	Shared library files for libtool
License:	LGPLv2.1+
Provides:	%{libname_orig} = %{EVRD}

%description -n	%{libname}
Shared library files for libtool DLL library from the libtool package.

%package -n	%{devname}
Group:		Development/C
Summary:	Development files for libtool
License:	LGPLv2.1+
Requires:	%{name} = %{EVRD}
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Provides:	%{libname_orig}-devel = %{EVRD}

%description -n	%{devname}
Development headers, and files for development from the libtool package.

%prep
%setup -q
%apply_patches
./bootstrap

%build
# don't use configure macro - it forces libtoolize, which is bad -jgarzik
# Use configure macro but define __libtoolize to be /bin/true -Geoff
%define __libtoolize /bin/true
# And don't overwrite config.{sub,guess} in this package as well -- Abel
%define __cputoolize /bin/true

%configure2_5x --disable-static
%make

# lame & ugly, trying to fix up relative paths that's made their way into libtool..
DIRS=$(cat libtool|grep compiler_lib_search_dirs|grep -F ..|uniq|cut -d'"' -f2)
PATHS=$(cat libtool|grep compiler_lib_search_path|grep -F ..|uniq|cut -d'"' -f2)
for i in $DIRS; do pushd $i; ABSOLUTE="$ABSOLUTE $PWD"; popd; done
ABSOLUTE=$(echo $ABSOLUTE | sed -e 's#%{_libdir} /%{_lib}#/%{_lib}#g' -e 's#%{_libdir} %{_libdir}#%{_libdir}#g')
sed -e "s#compiler_lib_search_dirs=\"$DIRS\"#compiler_lib_search_dirs=\"$ABSOLUTE\"#g" -i libtool
for i in $ABSOLUTE; do SEARCH=$(echo $SEARCH -L$i); done
sed -e "s#compiler_lib_search_path=\"$PATHS\"#compiler_lib_search_path=\"$SEARCH\"#g" -i libtool

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

%files
%doc AUTHORS NEWS README THANKS TODO
%{_bindir}/libtool
%{_mandir}/man1/libtool.1.*

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
%doc tests/demo
%{_includedir}/*
%{_libdir}/*.so


%changelog
* Wed Jun 06 2012 Andrey Bondrov <abondrov@mandriva.org> 2.4.2-6
+ Revision: 802932
- Drop some legacy junk

* Tue Mar 20 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 2.4.2-5
+ Revision: 785868
- drop patch removing soname for modules for now
- drop *.la

* Fri Mar 16 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 2.4.2-4
+ Revision: 785398
- only drop soname for modules if -avoid-version is specified

* Mon Mar 12 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 2.4.2-3
+ Revision: 784475
- fix typo in libtool-2.4.2-drop-soname-for-modules.patch

* Sun Mar 11 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 2.4.2-2
+ Revision: 784080
- try fix relative library path mess.. (ugly.. :p)
- drop buildrequires on locales-de
- drop ancient conflicts
- don't bother shipping 'ChangeLog*', 'NEWS' should be sufficient
- drop 'INSTALL'
- in stead of dropping --no-undefined, override it with --warn-unresolved-symbols
- drop dead cputoolize script
- drop dead libtool 1.5 fix for #44616
- detect libltdl.so rather than libltdl.la (P20, from Funda)
- do parallel build
- ditch biarch build, no longer required
- replace lib64 patch with rpath patch from Fedora
- use %%configure2_5x for 32 bit biarch as well
- run bootstrap in %%prep
- make dependencies versioned
- drop excessive provides
- add version to license
- cleanups
- do not build modules with soname (P19)

* Sun Nov 20 2011 Matthew Dawkins <mattydaw@mandriva.org> 2.4.2-1
+ Revision: 732050
- removed p19 upstreamed,
- removed dup docs
- switched to apply_patches
- new version 2.4.2
- removed mkrel & BuildRoot
- removed clean section
- removed old ldconfig scriptlets
- removed defattr
- removed old Conflicts
- added build cond arch_has_java from mga
- changed devel macro from libname_devel to develname

* Sat May 21 2011 Oden Eriksson <oeriksson@mandriva.com> 2.4-3
+ Revision: 676960
- deactivate the tests for now.
- mass rebuild
- P19: attempt to fix so that the demo tests passes
- mass rebuild

  + Funda Wang <fwang@mandriva.org>
    - fix multiarch usage

* Sat Dec 18 2010 Christiaan Welvaart <spturtle@mandriva.org> 2.4-1mdv2011.0
+ Revision: 622767
- 2.4

* Mon Aug 02 2010 Funda Wang <fwang@mandriva.org> 2.2.10-1mdv2011.0
+ Revision: 564939
- new version 2.2.10

* Sat Jan 30 2010 Christiaan Welvaart <spturtle@mandriva.org> 2.2.6b-2mdv2010.1
+ Revision: 498615
- patch0: ignore / as inst-prefix dir (fixes bug #57319)

* Sat Nov 28 2009 Christiaan Welvaart <spturtle@mandriva.org> 2.2.6b-1mdv2010.1
+ Revision: 470775
- 2.2.6b
- drop obsolete patches 7 and 15
- patch17: fix libltdl install test for non-minimal build env

* Sat Nov 21 2009 Christiaan Welvaart <spturtle@mandriva.org> 2.2.6-10mdv2010.1
+ Revision: 468578
- patch16: fix gcj compilation checks in configure scripts: use GCJFLAGS instead of CFLAGS (replaces previous workaround)

* Fri Nov 20 2009 Anssi Hannula <anssi@mandriva.org> 2.2.6-9mdv2010.1
+ Revision: 467716
- workaround gcj flags detection in configure by disabling -Wformat, and
  remove then unneeded -fPIC workaround added in previous release (fixes
  creation of java convenience libraries that broke with the previous
  workaround)

* Thu Nov 19 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.6-8mdv2010.1
+ Revision: 467567
- use -fPIC for x86_64 for now...

  + Pascal Terjan <pterjan@mandriva.org>
    - Fix tests

  + Funda Wang <fwang@mandriva.org>
    - rebuild

* Sun Mar 15 2009 Anssi Hannula <anssi@mandriva.org> 2.2.6-6mdv2009.1
+ Revision: 355430
- apply lib64.patch to the correct file (it has been applied to a test
  file since libtool was updated to 2.x)

* Sun Mar 15 2009 Anssi Hannula <anssi@mandriva.org> 2.2.6-5mdv2009.1
+ Revision: 355373
- readd lib64.patch, not fixed upstream after all (duh)
- drop lib64.patch, fixed upstream

* Wed Jan 28 2009 Pixel <pixel@mandriva.com> 2.2.6-3mdv2009.1
+ Revision: 334853
- add patch14: fix checking libltdl is installed (#47357)

* Wed Jan 28 2009 Pixel <pixel@mandriva.com> 2.2.6-2mdv2009.1
+ Revision: 334757
- libltdl-devel obsoletes libltdl3-devel

* Tue Jan 27 2009 Pixel <pixel@mandriva.com> 2.2.6-1mdv2009.1
+ Revision: 334330
- new version: 2.2.6a
- libltdl's major is now 7
- do not use major in libltdl-devel subpackage
  (to follow mandriva library policy)
- ensure we can't build when the major is wrong
- for the testsuite to succeed:
  o disable icrecream during the tests
  o disable ld --as-needed and --no-undefined
- rediff patch0, patch1, patch2, patch7, patch12, patch13
- drop patch4, patch5, patch11 (tests related patches, now unneeded)
- no need to clean demo/ since all the build is done in build-xxx
- partially drop cputoolize, keeping it only for transition

* Tue Oct 07 2008 Pixel <pixel@mandriva.com> 1.5.26-6mdv2009.1
+ Revision: 291169
- drop anygcc patch, which is not doing anything useful, and fixed differently
- do not use -nostdlib to build libraries, and so no need to hardcode gcc path (#44616)

* Wed Aug 06 2008 Thierry Vignaud <tv@mandriva.org> 1.5.26-5mdv2009.0
+ Revision: 264933
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Wed Jun 04 2008 Anssi Hannula <anssi@mandriva.org> 1.5.26-4mdv2009.0
+ Revision: 214898
- update lib64.patch:
  o do not hardcode build-time library search path
    (sys_lib_search_path_spec), as libtool fetches it from gcc
  o apply lib64 change to run-time library search path
    (sys_lib_dlsearch_path_spec) even when /etc/ld.so.conf does not exist

* Mon May 26 2008 Pixel <pixel@mandriva.com> 1.5.26-3mdv2009.0
+ Revision: 211318
- discard ld option "--no-undefined" when building shared library modules

* Wed May 07 2008 Pixel <pixel@mandriva.com> 1.5.26-2mdv2009.0
+ Revision: 202855
- do not build shared files with all deplibs (cf http://wiki.mandriva.com/en/Overlinking)

* Thu Apr 17 2008 Oden Eriksson <oeriksson@mandriva.com> 1.5.26-1mdv2009.0
+ Revision: 195285
- 1.5.26

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Oct 14 2007 Christiaan Welvaart <spturtle@mandriva.org> 1.5.24-1mdv2008.1
+ Revision: 98132
- 1.5.24
- rediff patch1
- drop patch6 - almost completely included upstream
- drop patches 8 and 9 - merged upstream

* Sun Sep 30 2007 Anssi Hannula <anssi@mandriva.org> 1.5.22-3mdv2008.0
+ Revision: 94045
- add conflicts with old libextractor1 for smooth upgrade

* Tue Sep 18 2007 Anssi Hannula <anssi@mandriva.org> 1.5.22-2mdv2008.0
+ Revision: 89730
- rebuild due to package loss


* Mon Jan 29 2007 Per Øyvind Karlsen <pkarlsen@mandriva.com> 1.5.22-1mdv2007.0
+ Revision: 114816
- new release: 1.5.22
- detect gcc path at runtime instead of requiring specific version (P10 from fedora)
- regenerate P6
- fix link.test check
- use new %%check stage for checks
- license for libraries is LGPL, not GPL

* Thu Jan 04 2007 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.20-11mdv2007.1
+ Revision: 104146
- recognize cell spu targets

* Sat Nov 11 2006 Anssi Hannula <anssi@mandriva.org> 1.5.20-10mdv2007.1
+ Revision: 83259
- fix gcc_version define when gcc is not present
- rebuild for gcc 4.1.2
- Import libtool

* Fri Jun 02 2006 Gustavo Pichorim Boiko <boiko@mandriva.com> 1.5.20-9mdk
- Added requires for sed (it is needed for cputoolize)

* Thu May 18 2006 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.20-8mdk
- rebuild for 4.1.1

* Wed Apr 26 2006 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.5.20-7mdk
- patch7: fix incremental linking for GCJ tag
- add a conflicts to fix upgrade

* Thu Feb 16 2006 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.20-6mdk
- rebuild for 4.0.3

* Wed Nov 23 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.5.20-5mdk
- fix filelist for biarch architectures

* Fri Nov 18 2005 Abel Cheung <deaddog@mandriva.org> 1.5.20-4mdk
- Revert previous crappy revert that make people's life difficult

* Wed Nov 16 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.20-3mdk
- revert change of lame coward who does not even know how to use --define

* Fri Nov 04 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.20-1mdk
- 1.5.20
- buildrequires gfortran and gcj
- allow definition of custom gcc_version

* Sat Aug 13 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.18-1mdk
- 1.5.18
- readd the strict gcc requirement, it's still need to match with
  current env compiler

* Mon Jun 20 2005 Stefan van der Eijk <stefan@eijk.nu> 1.5.12-8mdk
- remove construction like bug 6574

* Fri Jun 03 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.12-7mdk
- rebuild for 4.0.1

* Sat May 07 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.12-6mdk
- rebuild once more in a clean environment this time

* Thu May 05 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.5.12-5mdk
- rebuild

* Sun Feb 27 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.5.12-4mdk
- fix bug in Patch0 affecting packages with multiple inst_prefixed lib paths

* Wed Feb 23 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.5.12-3mdk
- make libtool script multiarch, other lib64 fixes

* Fri Feb 11 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.5.12-2mdk
- really pass thread flags

* Thu Feb 10 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.5.12-1mdk
- 1.5.12
- /usr/bin/libtool is compiler dependent

* Wed Jul 28 2004 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.5.6-4mdk
- Patch10: demo-nopic test not suitable on x86_64

* Tue Jun 22 2004 Abel Cheung <deaddog@deaddog.org> 1.5.6-3mdk
- Fix patch16 to include more compatibility hack
- Fix Provides (thx gb)

* Sat May 22 2004 Abel Cheung <deaddog@deaddog.org> 1.5.6-2mdk
- Patch16: Libtool sucks, changing the variable that defines ".so"
  extension all the time

* Mon May 03 2004 Abel Cheung <deaddog@deaddog.org> 1.5.6-1mdk
- THE BIG MOVE
- Updated P2(relink), P3(lib64), P4(add x86_64 to host_cpu), P8($SED),
  P12(libtoolize --config-only), P14(test dependency)
- Disable or drop other obsolete patches (some are kept in case they might
  be useful later)
- Patch15: Shamelessly copied from fedora RPM, fix test cases
- Please check if test suite fails for non-IA32 archs

* Wed Feb 11 2004 Abel Cheung <deaddog@deaddog.org> 1.4.3-10mdk
- Yet another more extra additional (...) fix to relink patch, hopefully final
- Patch14: demo-conf.test is a prerequisite of demo-conf.test

