import random
import string
import json
import os
import config

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
 

class AzureInfraApi(object):
    """ This is the class for vm operations in Microsoft Azure."""
    def __init__(self):
        """The constructor for AzureInfraApi class"""
        subscription_id = config.subscription_id
        client_id = config.credentials['client_id']
        secret = config.credentials['secret']
        tenant = config.credentials['tenant']
        credentials = ServicePrincipalCredentials(client_id=client_id,
                                                  secret=secret, tenant=tenant)
        self.resource_group_client = ResourceManagementClient(credentials,
                                                              subscription_id)
        self.compute_client = ComputeManagementClient(credentials,
                                                      subscription_id)
        self.network_client = NetworkManagementClient(credentials,
                                                      subscription_id)
        self.location = 'eastus'
        self.resource_group = 'myresource'

    def create_vm(self, user_name):
        """Creates the VM for the user

        Args:
            user_name(str) : Identity of the user

        Returns:
            class: Full list of instance details corresponding to the vm.
        """
        from azure.mgmt.datalake.analytics.account.models import create_or_update_compute_policy_parameters
        vm_name = user_name + '-vm' + ''.join(random.sample(
                                                string.ascii_lowercase, 5))
        resource_group_location = {'location': self.location}
        self.resource_group_client.resource_groups.create_or_update(
                                                    self.resource_group,
                                                    resource_group_location)

        template_path = os.path.abspath('vm_template_deploy.json')
        with open(template_path, 'r') as template_file_fd:
            vm_template_data = json.load(template_file_fd)

        parameters = {
            'vmName': vm_name,
            'location': self.location}

        vm_parameters = {k: {'value': v} for k, v in parameters.items()}
        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': vm_template_data,
            'parameters': vm_parameters
        }

        vm_deployment = self.resource_group_client.deployments.\
            create_or_update(self.resource_group, vm_name,
                             deployment_properties)
        vm_deployment.wait()
        return self.get_vm_details(vm_name)

    def get_vm_details(self, vm_name):
        """Returns the vm details.

        Args:
            vm_name(str) : Name of the VM.

        Returns:
            class:Full list of instance details corresponding to the vm.
        """
        return self.compute_client.virtual_machines.get(
            self.resource_group, vm_name, expand='instanceView')


def main():
    azureinfraapi = AzureInfraApi()
    user_name = 'testvm'
    message1 = "VM with the name {} and having id as {} is in {} state just created.\
                                                                            \n"
    vm_details = azureinfraapi.create_vm(user_name)
    print(message1.format(vm_details.name, vm_details.vm_id,
                          azureinfraapi.get_vm_status(vm_details.name)))

if __name__ == '__main__':
    main()
