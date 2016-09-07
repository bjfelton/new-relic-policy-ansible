#!/usr/bin/python

# Copyright 2016 Brian Felton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import nr_policy
from nr_policy.server_policy import NewRelicPolicy
import mock
from mock import patch, create_autospec
import os
import unittest


def FakeNRPModule():
    module = mock.MagicMock()
    module.check_mode = False
    module.params = {}
    return module

class TestNRPolicy(unittest.TestCase):

    def setUp(self):
        self.module = FakeNRPModule()
        self.policy = NewRelicPolicy(self.module)
        self.policy.module.exit_json = mock.MagicMock()
        self.policy.module.params = {
            'policy_name': 'test_policy',
            'server_name': 'test_server',
            'api_key': 'test_key',
        }

    @patch("nr_policy.server_policy.fetch_url", autospec=True, return_value=(None,None))
    def test_process_request_looks_up_policy_by_name(self, mock_fetch_url):
        self.policy._get_server_id = mock.MagicMock(return_value=None)
        self.policy._add_server_to_policy = mock.MagicMock()
        self.policy.process_request()

        mock_fetch_url.assert_called_once_with(self.policy.module, 'https://api.newrelic.com/v2/alert_policies.json?filter[name]=test_policy', headers={'X-Api-Key': 'test_key'})

    @patch("nr_policy.server_policy.fetch_url", autospec=True, return_value=(None,None))
    def test_process_request_looks_up_server_by_name(self, mock_fetch_url):
        self.policy._get_policy_data = mock.MagicMock(return_value=(None, None))
        self.policy._add_server_to_policy = mock.MagicMock()
        self.policy.process_request()

        mock_fetch_url.assert_called_once_with(self.policy.module, 'https://api.newrelic.com/v2/servers.json?filter[name]=test_server', headers={'X-Api-Key': 'test_key'})

    @patch("nr_policy.server_policy.fetch_url", autospec=True, return_value=(None,None))
    def test_process_request_adds_server_to_policy(self, mock_fetch_url):
        self.policy._get_policy_data = mock.MagicMock(return_value=(12345, []))
        self.policy._get_server_id = mock.MagicMock(return_value=24601)

        payload =  {
            "alert_policy": {
                "links": {
                    "servers": [24601]
                }
            }
        }

        headers = {
            'X-Api-Key': 'test_key',
            'Content-Type': 'application/json'
        }

        self.policy.process_request()

        mock_fetch_url.assert_called_once_with(
            self.policy.module, 
            'https://api.newrelic.com/v2/alert_policies/12345.json', 
            headers=headers,
            data=payload,
            method='PUT'
        )

    def test_argument_spec_contract(self):
        args = NewRelicPolicy._module_argument_spec()
        self.assertEqual(args, dict(
            server_name=dict(required=True),
            policy_name=dict(required=True),
            api_key=dict(required=True, no_log=True),
            state=dict(default='present', choices=['present', 'absent'])
        ))

if __name__ == '__main__':
    unittest.main()
