blackbird
=========

[![Circle CI](https://circleci.com/gh/Vagrants/blackbird/tree/master.svg?style=shield)](https://circleci.com/gh/Vagrants/blackbird/tree/master)
[![License](https://img.shields.io/badge/license-WTFPL-blue.svg)](http://www.wtfpl.net/about/)

What is blackbird?
------------------

`blackbird` is one like observation agent.
At present \(sending data part is pluggable, so `blackbird` can send data to besides it\)
`blackbird` send data to your zabbix server by using `zabbix sender protocol`.
As sending data:

* Middleware statistics information
    + e.g: nginx stub_status, memcached stats, redis INFO and others!
* AWS resources usage and statistics \(by using cloudwatch API\)
    + e.g: Elastic Load Blancing, DynamoDB, RDS and others!

So, you need to create nightmare shell script for zabbix user parameters no longer.


What plugin do we create?
-------------------------

Nginx, memcached, redis, MySQL5.5, AWS Elastic Load Blancing, AWS RDS, AWS DynamoDB and others!
Please see [our plugins \(repositories under the github organization Vagrants \)](https://github.com/Vagrants).


How to install blackbird
------------------------

Case of using `pip`.

```bash
pip install blackbird
```


Case of using `setup.py`.
```bash
python setup.py install
```
But if you installed on your PC, you may use `python setup.py develop`.
The reason of using `develop`, it's easier to remove this when uninstalling `blackbird`.


Case of using `rpm`.

You need to create below `.repo` file.

```repo
[blackbird]
name=blackbird package repository
baseurl=https://vagrants.github.io/blackbird/repo/yum/6/x86_64
enabled=0
gpgcheck=0
```

```bash
yum install --enablerepo=blackbird blackbird
```

note: In some cases, you may use `sudo` to install `blackbird` at each command.


How to install blackbird plugins
--------------------------------

Case of using `rpm`.
```bash
yum install --enablerepo=blackbird blackbird-nginx blackbird-redis blackbird-memcached
```


Configure to your blackbird
---------------------------

OK, now you have installed `blackbird`.
In this section, let's configure your blackbird.

### outline

1. Write blackbird configuration file.
2. Run your blackbird

### Step1 Write blackbird configuration file

Write configuration file at first.
Create following format file.
In this step, you don't have to mind about configuration detail \(We provide documentation at github Pages\).

```ini
# global section configuration
[global]
# Execution user. Please change it if necessary.
user = nobody
# Execution user group. Please change it if necessary.
group = nobody
log_file = /tmp/blackbird.log
log_level = debug

# zabbix_sender module configuration
[zabbix_sender]
# Change your zabbix server hostname
server = YOUR_ZABBIX_SERVER
module = zabbix_server

# netstat module configuration
[netstat]
module = netstat
```

OK, your blackbird configuration file has been created.
The strings surrounded by `[]` are *section* name.
The section name is string to separate each configuration section.

### Step2 Run your blackbird
In previous step, you have written blackbird configuration file.
So, do let's run actually your blackbird.

```bash
blackbird --config YOUR_CONFIG_FILE_PATH --pid-file ./blackbird.pid --debug-mode
```

What do you see on your console\(or terminal\)?
Perhaps, you can see that blackbird stacks data internal queue.


License
-------

`blackbird` is released under the [WTFPL license](http://www.wtfpl.net/) ![WTFPL license logo](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png)
