# webdot.spec.  Generated from webdot.spec.in by configure.
                                                                                
Name:           webdot
Summary:        A CGI graph server script that uses tcldot from graphviz-tcl.
Version:        2.30

%define truerelease 1
%{?distroagnostic: %define release %{truerelease}}
%{!?distroagnostic: %define release %{truerelease}%{?dist}}

Release: %{?release}

Group:          Applications/Multimedia
License:        BSD-style
URL:            http://www.graphviz.org/
Requires:       graphviz-tcl >= 2.9 graphviz-gd ghostscript tcl >= 8.4 httpd
Source:         http://www.graphviz.org/pub/graphviz/development/SOURCES/%{name}-%{version}.tar.gz
BuildArchitectures: noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
A cgi-bin program that produces clickable graphs in web pages
when provided with an href to a .dot file.  Uses Tcldot from the
graphviz-tcl rpm.

%prep
# %setup -n %{name}-%{version}
%setup -q

#define cgibindir  #(rpm -ql httpd | grep -v doc | grep '/cgi-bin$')
#define htmldir    #(rpm -ql httpd | grep -v doc | grep '/html$')
#define httpdconf  #(rpm -ql httpd | grep -v doc | grep '/httpd\\\.conf$')
%define cgibindir  /var/www/cgi-bin
%define htmldir    /var/www/html
%define httpdconf  /etc/httpd/conf/httpd.conf

%define apacheuser %(grep -i '^user ' %{httpdconf} | awk '{print $2}')
%define apachegroup %(grep -i '^group ' %{httpdconf} | awk '{print $2}')

%define cachedir   /var/cache/webdot
%define tclshbin   %(which tclsh)
%define libtcldot  %{_libdir}/graphviz/tcl/libtcldot.so
%define gsbin      %(which gs)
%define ps2epsibin %(which ps2epsi)

%install
mkdir -p $RPM_BUILD_ROOT/%{cgibindir}
mkdir -p $RPM_BUILD_ROOT/%{htmldir}
mkdir -p $RPM_BUILD_ROOT/%{cachedir}
cp cgi-bin/webdot $RPM_BUILD_ROOT/%{cgibindir}/
cp cgi-bin/webdot.tclet $RPM_BUILD_ROOT/%{cgibindir}/
cp -r html/webdot $RPM_BUILD_ROOT/%{htmldir}/
%{?suse_check}

%files
%attr(755,root,root) %{cgibindir}/webdot
%attr(755,root,root) %{cgibindir}/webdot.tclet
%attr(-,root,root) %{htmldir}/webdot/
%attr(700,%{apacheuser},%{apachegroup}) %{cachedir}/

%post
cat > %{cgibindir}/webdot.new << '__EOF__'
#!%{tclshbin}
set LIBTCLDOT "%{libtcldot}"
set CACHE_ROOT "%{cachedir}"
set GS "%{gsbin}"
set PS2EPSI "%{ps2epsibin}"
set LOCALHOSTONLY 1
__EOF__
cat %{cgibindir}/webdot >> %{cgibindir}/webdot.new
mv -f %{cgibindir}/webdot.new %{cgibindir}/webdot
chmod +x %{cgibindir}/webdot
chown %{apacheuser}:%{apachegroup} %{cachedir}
chmod 700 %{cachedir}

%clean
rm -rf $RPM_BUILD_ROOT
