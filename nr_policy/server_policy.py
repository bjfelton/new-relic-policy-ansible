#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.urls import fetch_url

class NewRelicPolicy:
    module = None

    def __init__(self, module):
        self.module = module
        self.base_url = 'https://api.newrelic.com/v2/'

    @staticmethod
    def _module_argument_spec():
        return dict(
            server_name=dict(required=True),
            policy_name=dict(required=True),
            api_key=dict(required=True, no_log=True),
            state=dict(default='present', choices=['present', 'absent']),
        )

    def process_request(self):
        policy_id, policy_servers = self._get_policy_data()
        server_id = self._get_server_id()
        self._add_server_to_policy(policy_id, policy_servers, server_id)
        return True

    def _get_policy_data(self):
        url = "{}alert_policies.json?filter[name]={}".format(self.base_url, self.module.params.get('policy_name'))
        headers = {'X-Api-Key': self.module.params.get('api_key')}

        data, info = fetch_url(self.module, url, headers=headers)
        return (data, data)

    def _get_server_id(self):
        url = "{}servers.json?filter[name]={}".format(self.base_url, self.module.params.get('server_name'))
        headers = {'X-Api-Key': self.module.params.get('api_key')}

        data, info = fetch_url(self.module, url, headers=headers)
        return data

    def _add_server_to_policy(self, policy_id, policy_servers, server_id):
        url = "{}alert_policies/{}.json".format(self.base_url, policy_id)
        headers = {
            'X-Api-Key': self.module.params.get('api_key'),
            'Content-Type': 'application/json'
        }

        policy_servers.append(server_id)

        payload = {
            "alert_policy": {
                "links": {
                    "servers": policy_servers
                }
            }
        }

        data, info = fetch_url(self.module, url, headers=headers, data=payload, method='PUT')

def main():
    module = AnsibleModule(argument_spec=NewRelicPolicy._module_argument_spec(), supports_check_mode=False)
    nr_policy = NewRelicPolicy(module)
    nr_policy.process_request()


if __name__ == '__main__':
    main()
