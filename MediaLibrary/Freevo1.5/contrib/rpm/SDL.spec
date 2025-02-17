%define name SDL
%define version 1.2.6
%define release 2_freevo

Summary: Simple DirectMedia Layer
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
Patch0: %{name}-%{version}-nokeyboard.patch
URL: http://www.libsdl.org/
Copyright: LGPL
Group: System Environment/Libraries
BuildRoot: /var/tmp/%{name}-buildroot
Prefix: %{_prefix}
Provides: libSDL-1.1.so.0

%description
This is the Simple DirectMedia Layer, a generic API that provides low
level access to audio, keyboard, mouse, and display framebuffer across
multiple platforms.

%package devel
Summary: Libraries, includes and more to develop SDL applications.
Group: Development/Libraries
Requires: %{name}

%description devel
This is the Simple DirectMedia Layer, a generic API that provides low
level access to audio, keyboard, mouse, and display framebuffer across
multiple platforms.

This is the libraries, include files and other resources you can use
to develop SDL applications.


%prep
rm -rf ${RPM_BUILD_ROOT}

%setup -q 
%patch0 -p1

%build
CFLAGS="$RPM_OPT_FLAGS" ./configure --prefix=%{prefix} --disable-video-svga --disable-video-ggi --disable-video-aalib --disable-debug --enable-dlopen --enable-esd-shared --enable-arts-shared --enable-video-directfb
make

%install
rm -rf $RPM_BUILD_ROOT
make install prefix=$RPM_BUILD_ROOT/%{prefix}
ln -s libSDL-1.2.so.0 $RPM_BUILD_ROOT/%{prefix}/lib/libSDL-1.1.so.0

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README-SDL.txt COPYING CREDITS BUGS
%{prefix}/lib/lib*.so.*

%files devel
%defattr(-,root,root)
%doc README README-SDL.txt COPYING CREDITS BUGS WhatsNew docs.html
%doc docs/index.html docs/html
%{prefix}/bin/*-config
%{prefix}/lib/lib*.a
%{prefix}/lib/lib*.la
%{prefix}/lib/lib*.so
%{prefix}/include/SDL/
%{prefix}/man/man3/*
%{prefix}/share/aclocal/*

%changelog
* Mon Sep 29 2003 TC Wan <tcwan@cs.usm.my>
- Enabled alsa and directfb support, added nokeyboard patch

* Wed Jan 19 2000 Sam Lantinga <slouken@libsdl.org>
- Re-integrated spec file into SDL distribution
- 'name' and 'version' come from configure 
- Some of the documentation is devel specific
- Removed SMP support from %build - it doesn't work with libtool anyway

* Tue Jan 18 2000 Hakan Tandogan <hakan@iconsult.com>
- Hacked Mandrake sdl spec to build 1.1

* Sun Dec 19 1999 John Buswell <johnb@mandrakesoft.com>
- Build Release

* Sat Dec 18 1999 John Buswell <johnb@mandrakesoft.com>
- Add symlink for libSDL-1.0.so.0 required by sdlbomber
- Added docs

* Thu Dec 09 1999 Lenny Cartier <lenny@mandrakesoft.com>
- v 1.0.0

* Mon Nov  1 1999 Chmouel Boudjnah <chmouel@mandrakesoft.com>
- First spec file for Mandrake distribution.

# end of file
