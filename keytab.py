#!/usr/bin/env python

from getpass import getuser, getpass
import argparse
import pexpect
import sys
import os

default_keytab = os.path.join(os.getenv('HOME'), '.keytab')
default_domain = 'HHMI.ORG'
ktutil = '/usr/bin/ktutil'
default_prompt = 'ktutil:  '

def kinit_test():
    """
    Runs kinit to create a Kerberos ticket using (just) generated keytab file.
    Returns kinit's return code (0 == OK)
    """

    from subprocess import call
    retcode = call(['/usr/bin/kinit', '-kt', keytab, principal], stdout=sys.stdout)
    if retcode == 0:
        print("kinit successfully created Kerberos ticket using this keytab.")
    else:
        print("kinit wasn't able to create Kerberos ticket using this keytab.")
    return retcode

def wait(prompt=default_prompt):
    ''' Wait for ktutil's prompt
        Returns true if ktutil's cli command  produced output (error message) or unexpected prompt
    '''

    # always wait for default prompt too in case of error, so no timeout exception
    i = child.expect([prompt, default_prompt], timeout=3)

    lines = child.before.strip().split('\n')
    problem = (      len(lines) > 1   # if there is an error message
                or  (i == 1)       # or ktutil gives default prompt when another prompt expected
              )
    if problem:
        print('ktutil error: ' + lines[1])
    return problem

def main(argv):
    parser = argparse.ArgumentParser(description="Keytab file maintenance utility.")
    parser.add_argument("username", help="Windows / Active Directory login name")
    parser.add_argument("--test", action="store_true", help="Use generated keytab with kinit to test creating Kerberos ticket.")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information. Note: password is visible in the log output with -d")
    parser.add_argument("-u", "--update", action="store_true", help="Overwrites just --kvno keytab entry and leaves other entries the same.")
    parser.add_argument("--domain", type=str, default=default_domain, help="Kerberos domain / AD realm [default: {}]".format(default_domain))
    parser.add_argument("--keytab", type=str, default=default_keytab, help="Keytab location [default: {}".format(default_keytab))
    parser.add_argument("-t", "--andtest", action="store_true", help="After keytab is created/updated, try to use it by creating a Kerberos ticket")
    parser.add_argument("--algorithms", default="rc4-hmac,aes256-cts", help="List of algorithm(s) used for each keytab entry. The list has to be comma-separated [default: rc4-hmac,aes256-cts]")
    parser.add_argument("--kvno", type=int, default=1, help="Key entry in keytab, passed as -k kvno argument to ktutil addent command [default: 1]")
    args = parser.parse_args()

    # Parse command-line arguments

    Debug = args.debug
    keytab = args.keytab
    principal = args.username +'@'+ args.domain

    if Debug: print(args)
    if args.test:
        sys.exit(kinit_test())

    # 0. Start ktutil command as a child process
    child = pexpect.spawn(ktutil)

    # wait for ktutil to show its first prompt
    wait()
    if Debug:
        child.logfile = sys.stdout
        print('Spawned ktutil successfully.')
    
    # 1. if it's an update, then read in keytab first
    wkt_action = 'save'
    if args.update:
        wkt_action = 'update'
        child.sendline('read_kt ' + keytab)
        if wait():
            print("Couldn't read keytab file %s\nNew file will be created instead" % keytab)
        # TODO: if KVNO already exists, ktutil may duplicate records in that entry
    else:
        # else - try removing existing keytab
        from os import remove
        try:
            remove(keytab)
            if Debug:
                print('Existing keytab %s removed.' % keytab)
        except OSError:
            pass        # assuming e.errno==ENOENT  - file doesn't exist
    
    # 2. Prompt user for Principal's password
    password = getpass('Active Directory user %s password: ' % principal)
    
    # 3. For each algorithm, call ktutil's addent command
    for algorithm in args.algorithms.split(','):
    
        child.sendline('addent -password -p %s -k %s -e %s'
                            % (principal, args.kvno, algorithm)
                      )
        if wait('Password for ' + principal):
            exit('Unexpected ktutil error while waiting for password prompt')
    
        child.sendline(password)
        if wait():
            exit('Unexpected ktutil error after addent command')
    
    # 4. Now we can save keytab file
    child.sendline('write_kt ' + keytab)
    if wait():
        exit("Couldn't write keytab file " + keytab)
    print("Keytab file %s %sd." % (keytab, wkt_action))
    
    # 5. exit from ktutil
    child.sendline('quit')
    child.close()           # termintate ktutil (if it's not closed already)
    
    # 6. Optionally test newly created/update keytab
    if args.andtest:
        kinit_test()


if __name__ == "__main__":
    main(sys.argv[1:])
