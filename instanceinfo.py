import base64
import subprocess

import requests

requests.packages.urllib3.disable_warnings()


def __get_instance_info(name):
    server_details_url = "https://iv.cd.auspost.com.au/api/stacks/{}/".format(name)
    r = requests.get(server_details_url,
                     headers={"content-type": "text", "Accept": "application/json"}, verify=False)

    return r.json()


def __generate_instance_name(server='accessone', env='pdev-ci'):
    if server == 'api' or server == 'batch':
        if server == 'api' or server is None:
            server = 'accessone'
        return "pcc{}-{}".format(server, env)

    return "{}-{}".format(server, env)


def __get_private_ip(payload, index=0):

    instances = []
    for instance in payload.get('instances'):
        if instance.get('tier') == 'app'and instance.get('state') != 'terminated':
            instances.append(instance)

    return instances[index].get('private_ip_address')


def health_check(args):
    print __run_remote(args,
                       "curl -k -s -X GET https://0.0.0.0:8443/api/shipping/v1/healthCheck")


def __get_ip_for_ssh(args):
    server, env = args.server, args.env
    index = args.index
    name = __generate_instance_name(server, env)

    info = __get_instance_info(name)
    return __get_private_ip(info, index)


def fetch_log(args):
    number_of_lines = args.lines
    log_file_name = 'catalina.out'
    if args.log_file is not None:
        log_file_name = args.log_file
    elif args.server == 'api':
        log_file_name = 'pccApiserver.log'
    elif args.server == 'batch':
        log_file_name = 'pccbatchserver.log'

    command = "/usr/bin/tail\ -n\ {}\ logs/{}".format(number_of_lines, log_file_name)
    __run_remote_as_user(args, 'tomcat', command)


def fetch_properties(args):
    server = args.server
    tomcat_app_name = "ROOT" if "api" in server else "server"
    command = "/bin/cat\ webapps/{}/WEB-INF/classes/pcc-application.properties".format(tomcat_app_name)
    __run_remote_as_user(args, 'tomcat', command)


def __get_cpboard():
    clip_command = "xclip -selection clipboard -o"
    return subprocess.check_output(clip_command, shell=True)


def deploy_curl_script(args):
    file_path = '/home/ec2-user/.curl_command/comm.sh'
    print "echo 'echo $1 | base64 --decode | xargs curl' > {} ; chmod +x {}".format(file_path, file_path)


def get_sandbox(args):
    sandbox_name = args.sandbox_name
    search_term = args.search_term
    command_placeholder = "curl -X GET -H \"API-Key: api-b3cc25c8-7844-48e5-bc19-5ea37edcea0d\" -H \"Cache-Control: no-cache\"  \"https://getsandbox.com/api/1/activity/search?sourceSandboxes={}&keyword={}\""
    command = command_placeholder.format(sandbox_name, search_term)
    __run_curl_command(args, command)


def __run_curl_command(args, command_args):
    command_args = command_args.replace("\n", "").replace("curl ", "-s ")

    command_args = base64.b64encode(command_args)
    command = "/home/ec2-user/.curl_command/comm.sh {}".format(command_args)
    print __run_remote(args, command)


def __get_ssh_key_path(env):
    if 'test' in env:
        return 'test-ddc-stack.pem'
    return 'dev-ddc-stack.pem'


def curl_command(args):
    __run_curl_command(args, __get_cpboard())


def __run_remote_as_user(args, user, command):
    print __run_remote(args, "sudo runuser -l {} -c \"{}\"".format(user, command))


def __run_remote(args, command):
    username, env, sshdir = args.user, args.env, args.sshdir
    ip_address = __get_ip_for_ssh(args)

    # the following flags for ssh prevent certificate confirmation
    jumpbox_ssh_command = "ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -t {}@10.80.84.11".format(
        username)

    ssh_destination = "ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i {}/{} ec2-user@{}".format(
        __get_ssh_sshdir_on_jumpbox(args), __get_ssh_key_path(env), ip_address)

    ssh_command = jumpbox_ssh_command + " " + ssh_destination

    # instead of su, we use runuser as it doesn't need a proper tty
    command = "{} '{}'".format(ssh_command, command)

    return subprocess.check_output(command, shell=True)


def __get_ssh_sshdir_on_jumpbox(args):
    if args.sshdir is None:
        return "/home/{}/.ssh".format(args.user)
    else:
        return args.sshdir


def command_wrapper_ip(args):
    print __get_ip_for_ssh(args)


def command_wrapper_ssh(args):
    env = args.env
    ip_address = __get_ip_for_ssh(args)
    print "ssh -t {}@10.80.84.11 ssh -i {}/{} ec2-user@{}".format(args.user,
                                                                  __get_ssh_sshdir_on_jumpbox(args),
                                                                  __get_ssh_key_path(env),
                                                                  ip_address)
