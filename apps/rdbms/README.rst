RDBMS
=================================
You'll need these library development packages and tools installed on
your system:

	CentOS/RHEL:
		# yum -y install epel-release
		# yum -y install gcc python-pip python-devel freetds-devel
		# cd $HUE_HOME
		# build/env/bin/python build/env/bin/pip install pymssql