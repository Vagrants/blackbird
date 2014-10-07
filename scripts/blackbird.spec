%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define debug_package %{nil}

%define name blackbird
%define version 0.4.1
%define unmangled_version %{version}
%define release 2%{dist}
%define blackbird_user bbd
%define blackbird_uid 187
%define blackbird_group bbd
%define blackbird_gid 187
%define log_dir %{_var}/log/blackbird
%define pid_dir %{_var}/run/blackbird
%define include_cfg_dir %{_sysconfdir}/blackbird/conf.d
%define plugins /opt/blackbird/plugins/

%if 0%{?fedora} >= 15 || 0%{?rhel} >= 7
%global with_systemd 1
%else
%global with_systemd 0
%endif

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
Url: https://github.com/Vagrants/blackbird.git
Provides: %{name}
Requires: python-argparse
Requires: python-configobj
Requires: python-daemon
Requires: python-ipaddr
Requires: python-lockfile
Requires: python-setuptools
Requires(pre):     shadow-utils
%if 0%{?with_systemd}
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd
BuildRequires: systemd-units
%else
Requires(post):    chkconfig
Requires(preun):   chkconfig
Requires(preun):   initscripts
Requires(postun):  initscripts
%endif
BuildRequires: python-setuptools

%description
blackbird is one like observation agent.
At present (sending data part is pluggable, so blackbird can send data to besides it)
blackbird send data to your zabbix server by using zabbix sender protocol.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/blackbird
mkdir -p $RPM_BUILD_ROOT/opt/blackbird
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/init.d
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}

install -dm 0755 $RPM_BUILD_ROOT/%{log_dir}
install -dm 0755 $RPM_BUILD_ROOT/%{pid_dir}
install -dm 0755 $RPM_BUILD_ROOT/%{include_cfg_dir}
install -dm 0755 $RPM_BUILD_ROOT/%{plugins}

install -p -m 0755 scripts/blackbird.bin $RPM_BUILD_ROOT/%{_bindir}/blackbird
install -p -m 0644 scripts/blackbird.cfg $RPM_BUILD_ROOT/%{_sysconfdir}/blackbird/defaults.cfg
install -p -m 0644 scripts/blackbird-statistics.cfg $RPM_BUILD_ROOT/%{_sysconfdir}/blackbird/conf.d/statistics.cfg
install -p -m 0644 scripts/blackbird-zabbix_sender.cfg $RPM_BUILD_ROOT/%{_sysconfdir}/blackbird/conf.d/zabbix_sender.cfg
install -p -m 0644 scripts/blackbird.logrotate $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/blackbird
install -p -m 0644 scripts/blackbird.sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/blackbird
%if 0%{?with_systemd}
install -p -m 0755 scripts/blackbird.service $RPM_BUILD_ROOT/%{_unitdir}/blackbird.service
%else
install -p -m 0755 scripts/blackbird.init $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/blackbird
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group %{blackbird_group} > /dev/null || \
    groupadd -r %{blackbird_group} -g %{blackbird_gid}
getent passwd %{blackbird_user} > /dev/null || \
    useradd %{blackbird_user} -d /var/lib/%{name} -u %{blackbird_uid} -M -r -s /sbin/nologin -g %{blackbird_group}

%post
%if 0%{?with_systemd}
%systemd_post %{name}.service
%else
/sbin/chkconfig --add %{name}
%endif

%preun
%if 0%{?with_systemd}
%systemd_preun %{name}.service
%else
service %{name} stop > /dev/null 2>&1 || \
    /sbin/chkconfig --del %{name}
%endif

%postun
%if 0%{?with_systemd}
%systemd_postun_with_restart %{name}.service
%else
service %{name} restart > /dev/null 2>&1 || :
%endif

%files
%defattr(-,%{blackbird_user},%{blackbird_group})
%dir %{log_dir}
%dir %{pid_dir}
%dir %{plugins}
%dir %{include_cfg_dir}
%dir /opt/blackbird
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/blackbird/defaults.cfg
%config(noreplace, missingok) %{include_cfg_dir}/*.cfg
%config(noreplace) %{_sysconfdir}/sysconfig/blackbird
%dir %{_sysconfdir}/blackbird
%{python_sitelib}/*
%if 0%{?with_systemd}
%{_unitdir}/%{name}.service
%else
%{_sysconfdir}/init.d/%{name}
%endif

%{_bindir}/blackbird
%config(noreplace) %{_sysconfdir}/logrotate.d/blackbird

%changelog
* Tue Sep 7 2014 makocchi <makocchi@gmail.com> - 0.4.1-2
- support systemd

* Thu Jun 26 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.4.1-1
- Generate thread name from section.

* Tue Mar 4 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.4.0-5
- Update init script. When "blackbird.pid.lock" file exists, blackbird does not start.

* Tue Mar 4 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.4.0-4
- Delete shebung.

* Thu Jan 30 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.4.0-3
- Delete print debug.

* Fri Jan 24 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.4.0-2
- separate submodule config file

* Fri Jan 24 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.4.0-1
- Resolve sr71 bootstrap problem(self.config, self.logger)

* Fri Jan 24 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.3.6-1
- Blackbird statistics.
- Set default queue length.
- Set global interval.

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
