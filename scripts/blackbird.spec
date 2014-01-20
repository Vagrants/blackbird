%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define name blackbird
%define version 0.3.5
%define unmangled_version %{version}
%define release 1%{dist}
%define blackbird_user bbd
%define blackbird_uid 187
%define blackbird_group bbd
%define blackbird_gid 187
%define log_dir %{_var}/log/blackbird
%define pid_dir %{_var}/run/blackbird
%define include_cfg_dir %{_sysconfdir}/blackbird/conf.d
%define plugins /opt/blackbird/plugins/

Summary: Daemon monitoring each middleware by using ZABBIX-SENDER
Name: %{name}
Version: %{version}
Release: %{release}
Source: %{name}-%{unmangled_version}.tar.gz
License: WTFPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: ARASHI, Jumpei <jumpei.arashi@arashike.com>
Packager: ARASHI, Jumpei <jumpei.arashi@arashike.com>
Requires: python-argparse python-configobj python-daemon python-ipaddr python-lockfile python-setuptools
Url: https://github.com/Vagrants/blackbird.git
BuildRequires: python-setuptools

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/blackbird
mkdir -p $RPM_BUILD_ROOT/opt/blackbird
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/init.d
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig

install -dm 0755 $RPM_BUILD_ROOT%{log_dir}
install -dm 0755 $RPM_BUILD_ROOT%{pid_dir}
install -dm 0755 $RPM_BUILD_ROOT%{include_cfg_dir}
install -dm 0755 $RPM_BUILD_ROOT%{plugins}

install -p -m 0755 scripts/blackbird.init $RPM_BUILD_ROOT%{_sysconfdir}/init.d/blackbird
install -p -m 0755 scripts/blackbird.bin $RPM_BUILD_ROOT%{_bindir}/blackbird
install -p -m 0644 scripts/blackbird.cfg $RPM_BUILD_ROOT%{_sysconfdir}/blackbird/defaults.cfg
install -p -m 0644 scripts/blackbird.logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/blackbird
install -p -m 0644 scripts/blackbird.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/blackbird

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group %{blackbird_group} > /dev/null || \
    groupadd -r %{blackbird_group} -g %{blackbird_gid}
getent passwd %{blackbird_user} > /dev/null || \
    useradd %{blackbird_user} -d /var/lib/%{name} -u %{blackbird_uid} -M -r -s /sbin/nologin -g %{blackbird_group}

%post
/sbin/chkconfig --add %{name}

%preun
service %{name} stop > /dev/null 2>&1 || \
    /sbin/chkconfig --del %{name}

%files
%defattr(-,%{blackbird_user},%{blackbird_group})
%dir %{log_dir}
%dir %{pid_dir}
%dir %{plugins}
%dir %{include_cfg_dir}
%dir /opt/blackbird
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/blackbird/*.cfg
%config(noreplace) %{_sysconfdir}/blackbird/defaults.cfg
%config(noreplace) %{_sysconfdir}/sysconfig/blackbird
%dir %{_sysconfdir}/blackbird
%{python_sitelib}/*
%{_sysconfdir}/init.d/blackbird
%{_bindir}/blackbird
%config(noreplace) %{_sysconfdir}/logrotate.d/blackbird

%changelog
* Mon Jan 20 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.3.5-1
- Implement item key fileter to plugins.base. This filter is blacklist.

* Fri Jan 10 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.3.4-1
- If blackbird is daemon mode, change log file owner and group

* Fri Jan 10 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.3.3-1
- Merge makocchi pull request
- add "status"|"condrestart"|"try-restart" to init script
- change default plugin interval (10seconds -> 60seconds)
- change option name at zabbix_sender plugin (Server -> server)

* Mon Jan 6 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.3.2-2
- Revise typo "build_items" - > "build_itemis"

* Mon Jan 6 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.3.2-1
- Revise build_items bug

* Mon Jan 6 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.3.1-1
- Implement ValidatorBase.detect_hostname

* Sun Dec 29 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.3.0-1
- Implement LLD thread.
- Implement BlalckbirdPluginError.
- Standard output log output on debug_mode.

* Tue Dec 24 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.2.0-2
- Update Timer Context

* Tue Dec 24 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.2.0-1
- each plugins to RPM (separate with blackbird)
- implement thread pool
- add '-P' option for developer

* Tue Dec 10 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.2-1
- Added /etc/sysconfig/blackbird

* Tue Dec 10 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.1-1
- When specify "log_file" option in config, blackbird does not check default value.
- Added logrotate.d/blackbird.

* Tue Dec 10 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.0-3
- Supported /etc/init.d/blackbird restart

* Wed Oct 30 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.0-2
- Supported ldap by using python-ldap
