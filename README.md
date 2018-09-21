keytabgen.py

Keytab file maintenance utility.
Usage:
    keytab.py [-u | --update] <username> [--domain=realm] [--keytab=filename]
                                         [--and-test] [--algorithms=list] [--kvno=entry]
                                         [-d | --debug]
    keytab.py test <username> [--domain=realm] [--keytab=filename]
    keytab.py (-h | --help)
Commands:
    (default)       Creates/overwrites Keytab file
    test            Use generated keytab with kinit to test creating Kerberos ticket.
Arguments:
    <username>      Is your Windows / Active Directory login name
                    (and not UNIX login, in case if it's different from AD login).
Options:
    -h --help            Show this screen
    --update             Overwrites just --kvno keytab entry and leaves other entries the same.
    --domain=realm       Kerberos domain / AD realm [default: %s]
    --keytab=filename    Keytab location [default: %s]
    --and-test           After keytab is created/updated, try to use it by creating a Kerberos ticket
    -d --debug           Print debug information. Note: password is visible in the log output with -d
    --algorithms=list    List of algorithm(s) used for each keytab entry.
                         The list has to be comma-separated [default: rc4-hmac,aes256-cts]
    --kvno=entry         Key entry in keytab, passed as -k kvno argument to
                         ktutil's addent command [default: 1]
Assumptions:
1.    This script expects MIT Kerberos compatible ktutil command
      to be available as %s.
      Script is known not to work with Heimdal Kerberos compatible ktutil.
2.    docopt, pexpect Python modules should be available.
History:
    01/16/2017  rdautkhanov@epsilon.com - 1.0   Initial version
