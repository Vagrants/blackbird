blackbird
=========

BlackBird get various middleware of information, send to Zabbix.

How to install
--------------

rpmのビルドについてはspecファイルを作成しましたので、そちらをご利用ください。

```bash
# tar.gzの作成
$python setup.py sdist
$mv dist/blackbird.tar.gz /path/to/rpmbuild/SOURCES
# rpmの作成
$mock /path/to/rpmbuild/SRPMS/blackbird.src.rpm
```

For Developer
-------------

```bash
# リポジトリのルート・ディレクトリで実行
$python setup.py develop
# pre-commit hookを用意したので使いなさい
# pep8とpyflakesによるlintです
$python ./prepare.py
```

----------

アンケート
---------

ロゴどれがいいですか??

![logo1 by makocchi](logos/blackbird.png)
![logo2 by makocchi](logos/blackbird2.png)
