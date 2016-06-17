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
TARGET_CLASS_NAME = 'ToscaAutoscaling'


class ToscaAutoscaling(HotResource):
    '''Translate TOSCA node type tosca.polcies.Scaling'''

    toscatype = 'tosca.policies.Scaling'

    def __init__(self, policy):
        hot_type = "OS::Heat::Senlin::Cluster"
        super(ToscaAutoscaling, self).__init__(policy,
                                               type=hot_type)
        self.policy = policy

    def handle_properties(self, resources):
        temp = self.policy.entity_tpl["properties"]
        self.properties = {}
        self.properties["min_size"] = temp["min_instances"]
        self.properties["max_size"] = temp["max_instances"]
        self.properties["default_instances"] = temp["default_instances"]

        compute = ToscaCompute(resources[0])
        compute.handle_properties()
        props = {}
        res = compute.properties
        props["properties"] = res
        props["type"] = compute.type
        self.properties["resources"] = props

    def handle_expansion(self):
        #Call tosca.policies.monitoring
        sample = self.policy.triggers[0].trigger_tpl["condition"]
        properties = {}
        properties["auto_scaling_group_id"] = {'get_resource': self.name}
        properties["adjustment_type"] = "change_in_capacity "
        properties["scaling_adjustment"] = 1
        scaling_resources = HotResource(self.nodetemplate,
                                        type='OS::Heat::ScalingPolicy',
                                        name='scaleup_policy',
                                        properties=properties)
        hot_resources = scaling_resources
        return hot_resources

    # call again Ceilometer but diferent node