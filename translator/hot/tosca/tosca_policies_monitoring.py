#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from translator.hot.syntax.hot_resource import HotResource
from translator.hot.tosca.tosca_compute import ToscaCompute
# Name used to dynamically load appropriate map class.
TARGET_CLASS_NAME = 'ToscaMonitoring'


class ToscaMonitoring(HotResource):
    '''Translate TOSCA node type type tosca.policies.Monitoring'''


    toscatype = 'tosca.policies.Monitoring'

    def __init__(self, nodetemplate):
        hot_type = "OS::Heat::Ceilometer::Alarm"
        super(ToscaMonitoring, self).__init__(nodetemplate,
                                               type=hot_type)
        self.nodetemplate = nodetemplate

    def handle_properties(self, resources):
        tpl = self.nodetemplate.trigger_tpl["condition"]
        self.properties = {}
        self.properties["period"] = tpl["period"]
        self.properties["evaluation"] = tpl["evaluation"]
        self.properties["statistic"] = tpl["statistic"]
        self.properties["description"] = tpl["constraint"]
        self.properties["threshold"] = tpl["threshold"]


    def handle_expansion(self):
        sample = self.policy.triggers[0].trigger_tpl["condition"]
        properties = {}
        properties["auto_scaling_group_id"] = {'get_resource': self.name}
        properties["adjustment_type"] = "change_in_capacity "
        properties["scaling_adjustment"] = 1
        prop = {}
        prop["description"] = self.policy.description
        prop["meter_name"] = "cpu_util"
        prop["statistic"] = sample["method"]
        prop["period"] = sample["period"]
        prop["threshold"] = sample["evaluations"]
        prop["comparison_operator"] = "gt"

        #Here We need to call tosca_policies_monitoring
        ceilometer_resources = HotResource(self.nodetemplate,
                                           type='OS::Ceilometer::Alarm',
                                           name='cpu_alarm_high',
                                           properties=prop)
        scaling_resources = HotResource(self.nodetemplate,
                                        type='OS::Heat::ScalingPolicy',
                                        name='scaleup_policy',
                                        properties=properties)
        hot_resources = [ceilometer_resources, scaling_resources]
        return hot_resources