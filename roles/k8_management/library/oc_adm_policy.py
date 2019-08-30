#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: oc_adm_policy

short_description: This is my test module

version_added: "2.7"

description:
    - "This is my longer description explaining my test module"

options:
    user:
        description:
            - This is the user to add to a role
        required: true
    cluster_role:
        description:
            - This is the role the `user` is added to.
        required: true

extends_documentation_fragment:
    - azure

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  oc_adm_policy:
    user: bob
    cluster_role: clutser-admin

'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
message:
    description: The output message that the test module generates
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import json

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        user=dict(type='str', required=True),
        cluster_role=dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        rc='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    check_rc = True
    get_current_bindings_cmd = "oc get clusterrolebindings %s -o json" % (module.params['user'])
    (current_bindings_rc, current_bindings_out, current_bindings_err) =  module.run_command(get_current_bindings_cmd, check_rc)
    if current_bindings_rc != 0:
        module.fail_json(outrc=rc,msg=oc_adm_policy_out, **result)
    # Here to make idompodent
    bind_array = json.loads(current_bindings_out)["subjects"]
    for bind in bind_array:
        if bind["name"] == module.params['cluster_role']:
            result['changed'] = False
            result['rc'] = 0
            result["message"] = "User is already assigned the role"
            module.exit_json(**result)
    
    
    cmd = "%s adm policy add-cluster-role-to-user %s %s" % ("oc",module.params['user'], module.params['cluster_role'] )
    (rc, oc_adm_policy_out, oc_adm_policy_err) =  module.run_command(cmd, check_rc)
    if rc != 0:
        module.fail_json(outrc=rc,msg=oc_adm_policy_out, **result)
    result['rc'] = 0
    result["message"] = oc_adm_policy_out
    result['stdout_lines'] = oc_adm_policy_out

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if "added" in result['stdout_lines']:
       result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()