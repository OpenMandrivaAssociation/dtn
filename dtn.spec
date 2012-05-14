%define	major %{version}
%define libname	%mklibname dtn %{major}
%define develname %mklibname -d dtn

Summary:	Delay Tolerant Networking reference implementation
Name:		dtn
Version:	2.6.0
Release:	3
License:	Apache License
Group:		System/Servers
URL:		https://sourceforge.net/projects/dtn/
Source0:	http://kent.dl.sourceforge.net/sourceforge/dtn/%{name}-%{version}.tgz
Source1:	dtnd.init
Source2:	dtnd.logrotate
Source3:	dtnd.sysconfig
Patch0:		dtn-2.6.0-gcc43_glibc28_fixes.diff
Patch1:		dtn-2.6.0-soname_fixes.diff
Patch2:		dtn-2.6.0-str-fmt.patch
Patch3:		dtn-2.6.0-gcc43.patch
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	autoconf
BuildRequires:	db-devel
BuildRequires:	doxygen
BuildRequires:	google-perftools-devel
BuildRequires:	libbluez-devel
BuildRequires:	libexpat-devel
BuildRequires:	libtool
BuildRequires:	oasys-devel
BuildRequires:	openssl-devel
BuildRequires:	python
BuildRequires:	python-devel
BuildRequires:	swig
BuildRequires:	tcl tcl-devel
BuildRequires:	xerces-c28-devel
BuildRequires:	zlib-devel
Requires:	tcl
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This package contains the reference implementation of the Delay Tolerant
Networking (DTN) architecture. This includes the DTN daemon (dtnd) as well as
several example applications that use the DTN protocols. 

The Delay-Tolerant Networking Research Group (DTNRG) is concerned with how to
address the architectural and protocol design principles arising from the need
to provide interoperable communications with and among extreme and
performance-challenged environments where continuous end-to-end connectivity
cannot be assumed. Examples of such environments include spacecraft,
military/tactical, some forms of disaster response, underwater, and some forms
of ad-hoc sensor/actuator networks.

%package -n	python-dtnapi
Summary:	Delay Tolerant Networking reference implementation
Group:		Development/Python

%description -n	python-dtnapi
This package contains the Python interface for DTN.

%package -n	%{libname}
Summary:	Delay Tolerant Networking reference implementation libraries
Group:          System/Libraries

%description -n	%{libname}
This package contains the reference implementation of the Delay Tolerant
Networking (DTN) architecture. This includes the DTN daemon (dtnd) as well as
several example applications that use the DTN protocols. 

The Delay-Tolerant Networking Research Group (DTNRG) is concerned with how to
address the architectural and protocol design principles arising from the need
to provide interoperable communications with and among extreme and
performance-challenged environments where continuous end-to-end connectivity
cannot be assumed. Examples of such environments include spacecraft,
military/tactical, some forms of disaster response, underwater, and some forms
of ad-hoc sensor/actuator networks.

This package contains the shared libraries for DTN.

%package -n	%{develname}
Summary:	Static library and header files for the DTN libraries
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}

%description -n	%{develname}
This package contains the reference implementation of the Delay Tolerant
Networking (DTN) architecture. This includes the DTN daemon (dtnd) as well as
several example applications that use the DTN protocols. 

The Delay-Tolerant Networking Research Group (DTNRG) is concerned with how to
address the architectural and protocol design principles arising from the need
to provide interoperable communications with and among extreme and
performance-challenged environments where continuous end-to-end connectivity
cannot be assumed. Examples of such environments include spacecraft,
military/tactical, some forms of disaster response, underwater, and some forms
of ad-hoc sensor/actuator networks.

This package contains the static DTN library and its header files.

%prep

%setup -q -n dtn-%{version}
%patch0 -p1
%patch1 -p0
%patch2 -p0
%patch3 -p0

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;


# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# lib64 fixes
perl -pi -e "s|/lib\b|/%{_lib}|g" aclocal/*

mkdir -p Mandriva
install -m0755 %{SOURCE1} Mandriva/dtnd.init
install -m0644 %{SOURCE2} Mandriva/dtnd.logrotate
install -m0644 %{SOURCE3} Mandriva/dtnd.sysconfig

%build
%serverbuild

sh build-configure.sh

# build it against the shared oasys libs, ugly but works...
perl -pi -e "s|OASYS_VERSION\.a|OASYS_VERSION\.so|g" *

export EXTLIB_CFLAGS="%{optflags}"
export EXTLIB_LDFLAGS="-Wl,--as-needed -Wl,--no-undefined"

%configure2_5x \
    --bindir=%{_sbindir} \
    --with-openssl

%make

rm -f oasys; make doxygen

%install
rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}/var/lib/dtn/bundles
install -d %{buildroot}/var/lib/dtn/db
install -d %{buildroot}/var/lib/dtn/dtnperf
install -d %{buildroot}/var/lib/dtn/dtncpd-incoming
install -d %{buildroot}/var/log/dtnd

install -m0755 daemon/dtnd %{buildroot}%{_sbindir}/
install -m0755 tools/dtnd-control %{buildroot}%{_sbindir}/
install -m0755 apps/dtncat/dtncat %{buildroot}%{_sbindir}/
install -m0755 apps/dtncp/dtncp %{buildroot}%{_sbindir}/
install -m0755 apps/dtncpd/dtncpd %{buildroot}%{_sbindir}/
install -m0755 apps/dtnping/dtnping %{buildroot}%{_sbindir}/
install -m0755 apps/dtnrecv/dtnrecv %{buildroot}%{_sbindir}/
install -m0755 apps/dtnsend/dtnsend %{buildroot}%{_sbindir}/
install -m0755 apps/dtntunnel/dtntunnel %{buildroot}%{_sbindir}/

install -m0755 Mandriva/dtnd.init %{buildroot}%{_initrddir}/dtnd
install -m0644 Mandriva/dtnd.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/dtnd
install -m0644 Mandriva/dtnd.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/dtnd
install -m0644 daemon/dtn.conf %{buildroot}%{_sysconfdir}/dtn.conf

install -m0644 applib/libdtnapi-%{version}.a %{buildroot}%{_libdir}/
install -m0644 applib/libdtnapi++-%{version}.a %{buildroot}%{_libdir}/

pushd applib/python
    INCDIR="%{_includedir}" LIBDIR="%{_libdir}" VERSION="%{version}" python setup.py install --root=%{buildroot}
popd

# fix attribs
rm -rf doc/doxygen/man/man3
find doc/ -type f | xargs chmod 644

rm -rf devel
cp -rp doc/doxygen/html devel
rm -rf doc/manual/man

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%pre
%_pre_useradd dtnd /var/lib/dtn /bin/false

%postun
%_postun_userdel dtnd

%post
echo "Initializing DTN persistent data store..."
%{_sbindir}/dtnd --init-db -o /var/log/dtnd/dtnd.log
%_post_service dtnd

%preun
%_preun_service dtnd

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CONTRIBUTING README RELEASE-NOTES STATUS TCA_README
%doc doc/manual doc/*.txt doc/*.html sim/conf/*.conf
%attr(0755,root,root) %{_initrddir}/dtnd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/dtn.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/clevent.xsd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/router.xsd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/dtnd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/dtnd
%attr(0755,root,root) %{_sbindir}/dtncat
%attr(0755,root,root) %{_sbindir}/dtncp
%attr(0755,root,root) %{_sbindir}/dtncpd
%attr(0755,root,root) %{_sbindir}/dtnd
%attr(0755,root,root) %{_sbindir}/dtnd-control
%attr(0755,root,root) %{_sbindir}/dtnhttpproxy
%attr(0755,root,root) %{_sbindir}/dtnping
%attr(0755,root,root) %{_sbindir}/dtnrecv
%attr(0755,root,root) %{_sbindir}/dtnsend
%attr(0755,root,root) %{_sbindir}/dtntraceroute
%attr(0755,root,root) %{_sbindir}/dtntunnel
%attr(0755,root,root) %{_sbindir}/num2sdnv
%attr(0755,root,root) %{_sbindir}/sdnv2num
%attr(0755,dtnd,dtnd) %dir /var/lib/dtn
%attr(0755,dtnd,dtnd) %dir /var/lib/dtn/bundles
%attr(0755,dtnd,dtnd) %dir /var/lib/dtn/db
%attr(0755,dtnd,dtnd) %dir /var/lib/dtn/dtnperf
%attr(0755,dtnd,dtnd) %dir /var/lib/dtn/dtncpd-incoming
%attr(0755,dtnd,dtnd) %dir /var/log/dtnd

%files -n python-dtnapi
%defattr(-,root,root,0755)
%{py_platsitedir}/_dtnapi.so
%{py_platsitedir}/dtnapi-*-py*.egg-info
%{py_platsitedir}/dtnapi.py*
            
%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libdtnapi-%{version}.so
%{_libdir}/libdtnapi++-%{version}.so
%{_libdir}/libdtntcl-%{version}.so

%files -n %{develname}
%defattr(-,root,root)
%doc devel 
%{_libdir}/libdtnapi.so
%{_libdir}/libdtnapi++.so
%{_libdir}/libdtntcl.so
%{_libdir}/libdtnapi-%{version}.a
%{_libdir}/libdtnapi++-%{version}.a
