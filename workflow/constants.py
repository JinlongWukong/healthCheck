import platform

LOG_NAME = "health_check.log"
DB_NAME = "cmd_list_db.txt"
if platform.system() == 'Windows':
	CLEAR = 'cls'
else:
	CLEAR = 'clear'

CMD_LIST_COMM = [
	'df -h',
	'svcs -xv',
	'metastat -c',
	'ntpq -p',
	'prtdiag -v',
	'tail -100 /var/adm/messages',
	'iostat -En | grep Errors',
	'dladm show-dev',
	'ifconfig -a',
	'svcs -a | grep eniq',
	'/opt/ericsson/sck/bin/ist_run -v',
	'svcs -a |egrep "ntp|dns|ldap"',
	'/usr/sbin/vxdisk list',
	'/opt/VRTS/bin/hastatus -summ',
	'tail -100 /halog',
	'/opt/ericsson/nms_cif_sm/bin/smtool -l | grep -v started',
	'/dmr/dmtool s m',
	'/ericsson/storage/bin/nascli list_all',
	'su - sybase -c "/ericsson/syb/util/sybase_info"',
	'/opt/ericsson/ddc/util/bin/listme | grep "@2@3" | wc -l',
	'/opt/ericsson/ddc/util/bin/listme | grep -v "@2@3" | wc -l',
	'ldaplist passwd'
]