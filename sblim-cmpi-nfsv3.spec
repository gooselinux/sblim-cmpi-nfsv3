%define provider_dir %{_libdir}/cmpi
%define tog_pegasus_version 2:2.5.1

Summary:        SBLIM nfsv3 instrumentation
Name:           sblim-cmpi-nfsv3
Version:        1.1.0
Release:        1%{?dist}
License:        EPL
Group:          Applications/System
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL:            http://sourceforge.net/projects/sblim/
Source0:        http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2

BuildRequires:  tog-pegasus-devel >= %{tog_pegasus_version}
BuildRequires:  sblim-cmpi-base-devel
Requires:       tog-pegasus >= %{tog_pegasus_version}
Requires:       sblim-cmpi-base
Requires:       /etc/ld.so.conf.d
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
Standards Based Linux Instrumentation Nfsv3 Providers

%package devel
Summary:        SBLIM Nfsv3 Instrumentation Header Development Files
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       tog-pegasus >= %{tog_pegasus_version}

%description devel
SBLIM Base Nfsv3 Development Package

%package test
Summary:        SBLIM Nfsv3 Instrumentation Testcases
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       sblim-testsuite
Requires:       tog-pegasus >= %{tog_pegasus_version}

%description test
SBLIM Base Fsvol Testcase Files for SBLIM Testsuite

%prep
%setup -q

%build
%ifarch s390 s390x ppc ppc64
export CFLAGS="$RPM_OPT_FLAGS -fsigned-char"
%else
export CFLAGS="$RPM_OPT_FLAGS" 
%endif
%configure \
        TESTSUITEDIR=%{_datadir}/sblim-testsuite \
        CIMSERVER=pegasus \
        PROVIDERDIR=%{provider_dir}
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
mv $RPM_BUILD_ROOT/%{_libdir}/libLinux_NFSv3SystemConfigurationUtil.so $RPM_BUILD_ROOT/%{_libdir}/cmpi/
# remove unused libtool files
rm -f $RPM_BUILD_ROOT/%{_libdir}/*a
rm -f $RPM_BUILD_ROOT/%{provider_dir}/*a
# shared libraries
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/cmpi" > $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%files
%defattr(-,root,root,-)
%docdir %{_datadir}/doc/%{name}-%{version}
%{provider_dir}/*.so
%{_datadir}/%{name}
%{_datadir}/doc/%{name}-%{version}
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%files test
%defattr(-,root,root,-)
%{_datadir}/sblim-testsuite

%define NFSV3_SCHEMA %{_datadir}/%{name}/Linux_NFSv3SystemSetting.mof %{_datadir}/%{name}/Linux_NFSv3SystemConfiguration.mof
%define NFSV3_REGISTRATION %{_datadir}/%{name}/Linux_NFSv3SystemConfiguration.registration %{_datadir}/%{name}/Linux_NFSv3SystemSetting.registration

%pre
# If upgrading, deregister old version
if [ $1 -gt 1 ]; then
  %{_datadir}/%{name}/provider-register.sh -d \
  -t pegasus -r %{NFSV3_REGISTRATION} -m %{NFSV3_SCHEMA} > /dev/null 2>&1 || :;
fi

%post
/sbin/ldconfig
if [ $1 -ge 1 ]; then
# Register Schema and Provider - this is higly provider specific
  %{_datadir}/%{name}/provider-register.sh \
  -t pegasus -r %{NFSV3_REGISTRATION} -m %{NFSV3_SCHEMA} > /dev/null 2>&1 || :;
fi;

%preun
# Deregister only if not upgrading 
if [ $1 -eq 0 ]; then
  %{_datadir}/%{name}/provider-register.sh -d \
  -t pegasus -r %{NFSV3_REGISTRATION} -m %{NFSV3_SCHEMA} > /dev/null 2>&1 || :;
fi

%postun -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Wed Jun 30 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.1.0-1
- Update to sblim-cmpi-nfsv3-1.1.0

* Tue Sep 29 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.0.14-1
- Initial support
