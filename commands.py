import argparse

import instanceinfo


def add_server_env_command(prs):
    prs.add_argument('server', help='The name of the server. e.g. api, batch, qaci, etc.')
    prs.add_argument('env', help='Stack name, e.g. pdev-ci, ptest-01, etc.')


parser = argparse.ArgumentParser()
parser.add_argument('--user', dest='user', help="Your username on jumpbox", required=True)
parser.add_argument('-i', dest='index', type=int, nargs='?', default=1,
                    help="Index of the instance(starting from 1). In some cases that there are multiple instances with the same name, you can provide the index of the instance")
parser.add_argument('--sshdir', dest='sshdir',
                    help="Absolute path on theJumpbox to the directory containing dev-ddc-stack.pem and test-ddc-stack.pem",
                    required=False)
subparsers = parser.add_subparsers(help='command')

# Log command
sub_parser = subparsers.add_parser('log', help='Fetches the log from the specified server')
add_server_env_command(sub_parser)
sub_parser.add_argument('lines', help='Number of lines to be fetch from the end of log file')
sub_parser.add_argument('--log_file', dest='log_file', help='The name of log file on tomcat\'s log dir. Default log name for api and batch are pccApiserver.log and '
                                                            'pccbatchserver.log respectively')
sub_parser.set_defaults(command='log')
# prop command
sub_parser = subparsers.add_parser('prop', help='Reads properties file from the given server')
add_server_env_command(sub_parser)
sub_parser.set_defaults(command='prop')
# hc command
sub_parser = subparsers.add_parser('hc', help='Checks the health status of the given server')
add_server_env_command(sub_parser)
sub_parser.set_defaults(command='hc')
# curl command
sub_parser = subparsers.add_parser('curl',
                                   help='Reads a curl command from the clipboard and executes that agains the API in pdev-ci.'
                                        ' This command is useful when you want to run a '
                                        'curl command, usually copied from Postman, on the remote stacks')
add_server_env_command(sub_parser)
sub_parser.set_defaults(command='curl')
# deploy command
subparsers.add_parser('deploy', help='Internal command')
sub_parser.set_defaults(command='deploy')

# mock command
sub_parser = subparsers.add_parser('mock', help='Internal command')
sub_parser.add_argument('sandbox_name', help='The name of the sandbox on getsandbox.com')
sub_parser.add_argument('search_term', help='keyword to be searched in recent requests and responses')
sub_parser.set_defaults(command='mock')
# ssh command
sub_parser = subparsers.add_parser('ssh', help='Prints a ssh command for logging into the given server')
add_server_env_command(sub_parser)
sub_parser.set_defaults(command='ssh')
# ip command
sub_parser = subparsers.add_parser('ip', help='Prints ip address of the given server')
add_server_env_command(sub_parser)
sub_parser.set_defaults(command='ip')

args = parser.parse_args()

function_map = {
    'log': instanceinfo.fetch_log,
    'prop': instanceinfo.fetch_properties,
    'hc': instanceinfo.health_check,
    'deploy': instanceinfo.deploy_curl_script,
    'curl': instanceinfo.curl_command,
    'mock': instanceinfo.get_sandbox,
    'ip': instanceinfo.command_wrapper_ip,
    'ssh': instanceinfo.command_wrapper_ssh,

}
function = function_map[args.command]

args.index -= 1

function(args)
