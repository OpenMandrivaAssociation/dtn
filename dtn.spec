%define snap 20060831

Summary:	Delay Tolerant Networking reference implementation
Name:		dtn
Version:	2.2.1
Release:	%mkrel 0.%{snap}.1
License:	BSD-like
Group:		System/Servers
URL:		http://www.dtnrg.org/
#Source0:	http://www.dtnrg.org/docs/code/%{name}_%{version}.tar.bz2
Source0:	dtn_%{version}-20060831.tar.bz2
Source1:	dtnd.init
Source2:	dtnd.logrotate
Source3:	dtnd.sysconfig
Patch0:		dtn_2.2.1-localstatedir.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	libtool
#BuildRequires:	MySQL-devel
#BuildRequires:	postgresql-devel
Requires:	tcl
BuildRequires:	tcl libtcl-devel
BuildRequires:	db4-devel
BuildRequires:	libbluez-devel
BuildRequires:	libexpat-devel
BuildRequires:	doxygen
ExclusiveArch:	i686 i586
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

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

%prep

%setup -q -n DTN2
%patch0 -p1


find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

mkdir -p Mandriva
install -m0755 %{SOURCE1} Mandriva/dtnd.init
install -m0644 %{SOURCE2} Mandriva/dtnd.logrotate
install -m0644 %{SOURCE3} Mandriva/dtnd.sysconfig

# fix version
echo "%{version}" > version.dat

%build

#export CPPFLAGS="-I%{_includedir}/mysql -I%{_includedir}/pgsql"

pushd oasys
    sh build-configure.sh
popd

sh build-configure.sh

%configure2_5x \
    --bindir=%{_sbindir} \
    --with-dbver=4.2 \
    --with-bluez \
    --disable-atomic-asm

#    --with-mysql\
#    --with-postgres \

make OPTIMIZE="%{optflags}" WARN="-Wall -fpermissive -fPIC"

make doxygen

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_localstatedir}/dtn/bundles
install -d %{buildroot}%{_localstatedir}/dtn/db
install -d %{buildroot}%{_localstatedir}/dtn/dtnperf
install -d %{buildroot}%{_localstatedir}/dtn/dtncpd-incoming
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

# fix attribs
rm -rf doc/doxygen/man/man3
find doc/ -type f | xargs chmod 644

rm -rf devel
cp -rp doc/doxygen/html devel
rm -rf doc/manual/man
cp oasys/README README.oasys
cp oasys/TODO TODO.oasys

%pre
%_pre_useradd dtnd %{_localstatedir}/dtn /bin/false

%postun
%_postun_userdel dtnd

%post
echo "Initializing DTN persistent data store..."
%{_sbindir}/dtnd --init-db -o /var/log/dtnd/dtnd.log
%_post_service dtnd

%preun
%_preun_service dtnd

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CONTRIBUTING README RELEASE-NOTES STATUS TCA_README oasys/LICENSE README.oasys TODO.oasys
%doc devel doc/manual doc/*.txt doc/*.html doc/*.cc sim/conf/send-one-bundle.conf
%attr(0755,root,root) %{_initrddir}/dtnd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/dtn.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/dtnd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/dtnd

%attr(0755,root,root) %{_sbindir}/dtnd
%attr(0755,root,root) %{_sbindir}/dtnd-control
%attr(0755,root,root) %{_sbindir}/dtncat
%attr(0755,root,root) %{_sbindir}/dtncp
%attr(0755,root,root) %{_sbindir}/dtncpd
%attr(0755,root,root) %{_sbindir}/dtnping
%attr(0755,root,root) %{_sbindir}/dtnrecv
%attr(0755,root,root) %{_sbindir}/dtnsend
%attr(0755,root,root) %{_sbindir}/dtntunnel

%attr(0755,dtnd,dtnd) %dir %{_localstatedir}/dtn
%attr(0755,dtnd,dtnd) %dir %{_localstatedir}/dtn/bundles
%attr(0755,dtnd,dtnd) %dir %{_localstatedir}/dtn/db
%attr(0755,dtnd,dtnd) %dir %{_localstatedir}/dtn/dtnperf
%attr(0755,dtnd,dtnd) %dir %{_localstatedir}/dtn/dtncpd-incoming
%attr(0755,dtnd,dtnd) %dir /var/log/dtnd


