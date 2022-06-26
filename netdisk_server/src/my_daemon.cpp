// my_daemon.cpp
#include "my_daemon.h"
#include <iostream>
#include <unistd.h>
#include <signal.h>		// sigaction
#include <sys/resource.h>	// rlimit
#include <fcntl.h>		// open
#include <syslog.h>		// openlog syslog closelog
#include <sys/types.h>  // umask
#include <sys/stat.h>	// umask
using namespace std;

/*
 * paramter:
 * 		nochdir: if it is 0, change workdir to '/'
 * 		noclose: if it is 0, redirect STDIN, STDOUT, STDERR to /dev/null
*/
int my_daemon(const int nochdir, const int noclose) {
	pid_t pid;
	struct rlimit rl;
	struct sigaction sa;
	
	// clear file creation mask
	umask(0);

	// create a session leader to lose controlling TTY
	if ((pid = fork()) < 0) {
		cerr << "fork() failed" << endl;
		exit(1);
	}
	else if (pid != 0) {
		// exit parent
		exit(0);
	}
	// make child process a new session leader
	setsid();

	// set ignore signal handler
	sa.sa_handler = SIG_IGN;
	// initialize the signalmask to empty to receive all signals
	sigemptyset(&sa.sa_mask);
	// default processing behavior
	sa.sa_flags=0;
	// ignore SIGHUP
	if (sigaction(SIGHUP, &sa, NULL) < 0) {
		cerr << "failed to ignore SIGHUP" << endl;
		exit(1);
	}
	// create grandchild process 
	// to forbid process opening control terminal
	if ((pid = fork()) < 0) {
		cerr << "fork() failed" << endl;
		exit(1);
	}
	else if (pid != 0) {
		// exit child process
		exit(0);
	}
	
	// change workdir to '/' so filesystem can be unmounted
	if (nochdir == 0 && chdir("/") < 0) {
		cerr << "failed to change dir to \"/\"" << endl;
		exit(1);
	}

	// close file dscrpitors
	if (getrlimit(RLIMIT_NOFILE, &rl) < 0) {
		cerr << "failed to get file limit" << endl;
		exit(1);
	}
	if (rl.rlim_max == RLIM_INFINITY) {
		rl.rlim_max = 1024;
	}
	for (int i = 3; i < rl.rlim_max; ++i) {
		close(i);
	}

    // 关闭未打开的fd会置errno
    errno = 0;	

	// redirect STDIN, STDOUT, STDERR to /dev/null
	if (noclose == 0) {
		int fd = open("/dev/null", O_RDWR);
		if (fd < 0) {
			openlog("my_daemon()", LOG_CONS, LOG_DAEMON);
			syslog(LOG_ERR, "failed to redirect fd 0,1,2 to /dev/null");
			closelog();
			exit(1);
		}
		dup2(fd, 0);
		dup2(fd, 1);
		dup2(fd, 2);
	}
		
	return 0;
}
