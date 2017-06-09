#/usr/bin/python env
import sys
import os
import json
from collections import OrderedDict
from optparse import OptionParser
import master_helper
import script_generator
import readme_generator

# Process Script Parameters
parser = OptionParser()
parser.add_option("-n", "--template-name", action="store", type="string", dest="template_name", help="Template Name: 1nic, 2nic, cluster_base, etc." )
parser.add_option("-l", "--license-type", action="store", type="string", dest="license_type", help="License Type: BYOL or PAYG" )
parser.add_option("-m", "--stack-type", action="store", type="string", dest="stack_type", default="new_stack", help="Networking Stack Type: new_stack or existing_stack" )
parser.add_option("-t", "--template-location", action="store", type="string", dest="template_location", help="Template Location: such as ../experimental/standalone/1nic/PAYG/" )
parser.add_option("-s", "--script-location", action="store", type="string", dest="script_location", help="Script Location: such as ../experimental/standalone/1nic/" )
parser.add_option("-v", "--solution-location", action="store", type="string", dest="solution_location", default="experimental", help="Solution location: experimental or supported" )

(options, args) = parser.parse_args()
template_name = options.template_name
license_type = options.license_type
stack_type = options.stack_type
template_location = options.template_location
script_location = options.script_location
solution_location = options.solution_location

## Specify meta file and file to create(should be argument)
metafile = 'base.azuredeploy.json'
metafile_params = 'base.azuredeploy.parameters.json'
created_file = template_location + 'azuredeploy.json'
createdfile_params = template_location + 'azuredeploy.parameters.json'

## Static Variable Defaults
nic_reference = ""
command_to_execute = ""

## Static Variable Assignment ##
content_version = '3.1.3.0'
f5_networks_tag = 'v3.1.3.0'
f5_cloud_libs_tag = 'v3.0.2'
f5_cloud_libs_azure_tag = 'develop'

install_cloud_libs = """[concat(variables('singleQuote'), '#!/bin/bash\necho about to execute\nchecks=0\nwhile [ $checks -lt 120 ]; do echo checking mcpd\n/usr/bin/tmsh -a show sys mcp-state field-fmt | grep -q running\nif [ $? == 0 ]; then\necho mcpd ready\nbreak\nfi\necho mcpd not ready yet\nlet checks=checks+1\nsleep 1\ndone\necho loading verifyHash script\n/usr/bin/tmsh load sys config merge file /config/verifyHash\nif [ $? != 0 ]; then\necho cannot validate signature of /config/verifyHash\nexit\nfi\necho loaded verifyHash\nscript_loc="/var/lib/waagent/custom-script/download/0/"\nconfig_loc="/config/cloud/"\nhashed_file_list="<HASHED_FILE_LIST>"\nfor file in $hashed_file_list; do\necho "verifying $file"\n/usr/bin/tmsh run cli script verifyHash $file\nif [ $? != 0 ]; then\necho "$file is not valid"\nexit 1\nfi\necho "verified $file"\ndone\necho "expanding $hashed_file_list"\ntar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/node_modules\n<TAR_LIST>touch /config/cloud/cloudLibsReady', variables('singleQuote'))]"""
verify_hash = '''[concat(variables('singleQuote'), 'cli script /Common/verifyHash {\nproc script::run {} {\n        if {[catch {\n            set hashes(f5-cloud-libs.tar.gz) 862f7c19396088ab012fda7c2b262621c17f134b1d39d7a4d0b765eaf92f3ddc7354716a4f546fabb866df9876e1baed5799ae4a2c9d0ea6f01f79a38b9d3b3e\n            set hashes(f5-cloud-libs-aws.tar.gz) 2566f515fb46d89f5a245079b0efdad60fd78327c352e567bd5d573eb2ee0093d167a2f054b2408bd7df49c5debc4218074fdb50cfe135bb80ccc6c303a03f72\n            set hashes(f5-cloud-libs-azure.tar.gz) 80fbf43a29924e3f10dd1187fd6795083363eb9d65214c24f76c33e0465f82435bb84a131f9cd5b647677c9e4353f446d75566da811110cd587ede2d68206604\n            set hashes(asm-policy-linux.tar.gz) 63b5c2a51ca09c43bd89af3773bbab87c71a6e7f6ad9410b229b4e0a1c483d46f1a9fff39d9944041b02ee9260724027414de592e99f4c2475415323e18a72e0\n            set hashes(f5.http.v1.2.0rc4.tmpl) 47c19a83ebfc7bd1e9e9c35f3424945ef8694aa437eedd17b6a387788d4db1396fefe445199b497064d76967b0d50238154190ca0bd73941298fc257df4dc034\n            set hashes(f5.http.v1.2.0rc6.tmpl) 811b14bffaab5ed0365f0106bb5ce5e4ec22385655ea3ac04de2a39bd9944f51e3714619dae7ca43662c956b5212228858f0592672a2579d4a87769186e2cbfe\n            set hashes(f5.http.v1.2.0rc7.tmpl) 21f413342e9a7a281a0f0e1301e745aa86af21a697d2e6fdc21dd279734936631e92f34bf1c2d2504c201f56ccd75c5c13baa2fe7653213689ec3c9e27dff77d\n            set hashes(f5.aws_advanced_ha.v1.3.0rc1.tmpl) 9e55149c010c1d395abdae3c3d2cb83ec13d31ed39424695e88680cf3ed5a013d626b326711d3d40ef2df46b72d414b4cb8e4f445ea0738dcbd25c4c843ac39d\n            set hashes(f5.aws_advanced_ha.v1.4.0rc1.tmpl) de068455257412a949f1eadccaee8506347e04fd69bfb645001b76f200127668e4a06be2bbb94e10fefc215cfc3665b07945e6d733cbe1a4fa1b88e881590396\n            set hashes(asm-policy.tar.gz) 2d39ec60d006d05d8a1567a1d8aae722419e8b062ad77d6d9a31652971e5e67bc4043d81671ba2a8b12dd229ea46d205144f75374ed4cae58cefa8f9ab6533e6\n            set hashes(deploy_waf.sh) 4db3176b45913a5e7ccf42ab9c7ac9d7de115cdbd030b9e735946f92456b6eb433087ed0e98ac4981c76d475cd38f4de49cd98c063e13d50328a270e5b3daa4a\n            set hashes(f5.policy_creator.tmpl) 54d265e0a573d3ae99864adf4e054b293644e48a54de1e19e8a6826aa32ab03bd04c7255fd9c980c3673e9cd326b0ced513665a91367add1866875e5ef3c4e3a\n\n            set file_path [lindex $tmsh::argv 1]\n            set file_name [file tail $file_path]\n\n            if {![info exists hashes($file_name)]} {\n                tmsh::log err \"No hash found for $file_name\"\n                exit 1\n            }\n\n            set expected_hash $hashes($file_name)\n            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n            if { $expected_hash eq $computed_hash } {\n                exit 0\n            }\n            tmsh::log err \"Hash does not match for $file_path\"\n            exit 1\n        }]} {\n            tmsh::log err {Unexpected error in verifyHash}\n            exit 1\n        }\n    }\n    script-signature ae3RGP+3LP22Pv3aAEHQys7W1K0ZtyXF+wrdn0zfyJRq6tsOP9Am3h7RBoihmGd4xl5lh8uoT9cCYnNWl/P0BI0vE2RY5vI5M/PNlIUT3AezrTxDXZYPB3qwgQOUqgcj09SofM0KHSE5RN3nnUMrpPvlt9PfPWqmje185j+XyfLptIyB45fFzFiBsvkDrd4MF6oJUIhYYTC4jmgXWtROyXNzXsfqd+2H7diIr99o90drNvwPjiArGJg6kXVvm2JLWm0BqNiQBrqwZdEu44a6inzMQ7HDtbGEPMVVh2VtXD3KsL1TBAN/aTMuduVHMxzLpxVXR2L2IQV1vw9R/Pk9QQ==\n    signing-key /Common/f5-irule\n}', variables('singleQuote'))]'''
hashed_file_list = "${config_loc}f5-cloud-libs.tar.gz"
additional_tar_list = ""
if template_name in ('ltm_autoscale', 'ha-avset'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz"
    additional_tar_list = "tar xvfz /config/cloud/f5-cloud-libs-azure.tar.gz -C /config/cloud/node_modules/f5-cloud-libs/node_modules\n"
elif template_name in ('waf_autoscale'):
    hashed_file_list += " ${config_loc}f5-cloud-libs-azure.tar.gz ${script_loc}deploy_waf.sh ${script_loc}f5.http.v1.2.0rc7.tmpl ${script_loc}f5.policy_creator.tmpl ${script_loc}asm-policy.tar.gz"
    additional_tar_list = "tar xvfz /config/cloud/f5-cloud-libs-azure.tar.gz -C /config/cloud/node_modules/f5-cloud-libs/node_modules\n"
#### Temp empty hashed file list when testing new cloud libs....
hashed_file_list = ""
install_cloud_libs = install_cloud_libs.replace('<HASHED_FILE_LIST>', hashed_file_list)
install_cloud_libs = install_cloud_libs.replace('<TAR_LIST>', additional_tar_list)
instance_type_list = ["Standard_A2", "Standard_A3", "Standard_A4", "Standard_A5", "Standard_A6", "Standard_A7", "Standard_A8", "Standard_A9", "Standard_D2", "Standard_D3", "Standard_D4", "Standard_D11", "Standard_D12", "Standard_D13", "Standard_D14", "Standard_DS2", "Standard_DS3", "Standard_DS4", "Standard_DS11", "Standard_DS12", "Standard_DS13", "Standard_DS14", "Standard_D2_v2", "Standard_D3_v2", "Standard_D4_v2", "Standard_D5_v2", "Standard_D11_v2", "Standard_D12_v2", "Standard_D13_v2", "Standard_D14_v2", "Standard_D15_v2", "Standard_DS2_v2", "Standard_DS3_v2", "Standard_DS4_v2", "Standard_DS5_v2", "Standard_DS11_v2", "Standard_DS12_v2", "Standard_DS13_v2", "Standard_DS14_v2", "Standard_DS15_v2", "Standard_F2", "Standard_F4", "Standard_F8", "Standard_F2S", "Standard_F4S", "Standard_F8S"]
tags = { "application": "[parameters('tagValues').application]", "environment": "[parameters('tagValues').environment]", "group": "[parameters('tagValues').group]", "owner": "[parameters('tagValues').owner]", "costCenter": "[parameters('tagValues').cost]" }
tag_values = {"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}
api_version = "[variables('apiVersion')]"
compute_api_version = "[variables('computeApiVersion')]"
network_api_version = "[variables('networkApiVersion')]"
storage_api_version = "[variables('storageApiVersion')]"
insights_api_version = "[variables('insightsApiVersion')]"
location = "[variables('location')]"
default_payg_bw = '200m'
nic_port_map = "[variables('bigIpNicPortMap')['1'].Port]"
default_instance = "Standard_DS2_v2"

# Update port map variable if deploying multi_nic template
if template_name in ('2nic'):
    nic_port_map = "[variables('bigIpNicPortMap')['2'].Port]"
if template_name in ('3nic', 'ha-avset'):
    nic_port_map = "[variables('bigIpNicPortMap')['3'].Port]"

# Update allowed instances available based on solution
if template_name in ('waf_autoscale'):
    disallowed_instance_list = ["Standard_A2", "Standard_F2"]
    for instance in disallowed_instance_list:
        instance_type_list.remove(instance)
# This solution requires a minimum of 3 nic's, some instance types only support two
if template_name in ('3nic', 'ha-avset'):
    default_instance = "Standard_DS3_v2"
    disallowed_instance_list = ["Standard_A2", "Standard_D2", "Standard_DS2", "Standard_D2_v2", "Standard_DS2_v2", "Standard_F2", "Standard_F2S"]
    for instance in disallowed_instance_list:
        instance_type_list.remove(instance)


## Set BIG-IP versions to allow ##
default_big_ip_version = '13.0.021'
allowed_big_ip_versions = ["latest", "13.0.021", "12.1.24"]
version_port_map = { "latest": { "Port": 8443 }, "13.0.021": { "Port": 8443 }, "12.1.24": { "Port": 443 }, "443": { "Port": 443 } }

## Determine PAYG/BYOL variables
sku_to_use = "[concat('f5-bigip-virtual-edition-', variables('imageNameToLower'),'-byol')]"
offer_to_use = "f5-big-ip"
image_to_use = "[parameters('bigIpVersion')]"
license1_command = "' --license ', parameters('licenseKey1'),"
license2_command = "' --license ', parameters('licenseKey2'),"
if license_type == 'PAYG':
    sku_to_use = "[concat('f5-bigip-virtual-edition-', parameters('licensedBandwidth'), '-', variables('imageNameToLower'),'-hourly')]"
    offer_to_use = "f5-big-ip-hourly"
    license1_command = ''
    license2_command = ''
# Abstract license key text for readme_generator
license_text = {'licenseKey1': 'The license token for the F5 BIG-IP VE (BYOL)', 'licensedBandwidth': 'The amount of licensed bandwidth (Mbps) you want the PAYG image to use.'}
if template_name == 'cluster_base':
    license_text['licenseKey2'] = 'The license token for the F5 BIG-IP VE (BYOL). This field is required when deploying two or more devices.'


## Load "Meta File(s)" for modification ##
with open(metafile, 'r') as base:
    data = json.load(base, object_pairs_hook=OrderedDict)
with open(metafile_params, 'r') as base_params:
    data_params = json.load(base_params, object_pairs_hook=OrderedDict)


######################################## Create/Modify ARM Objects ########################################
data['contentVersion'] = content_version
data_params['contentVersion'] = content_version

######################################## ARM Parameters ########################################
## Pulling in a base set of variables and setting order with below call, it is a function of master_helper.py
master_helper.parameter_initialize(data)
## Set default parameters for all templates
data['parameters']['adminUsername'] = {"type": "string", "defaultValue": "azureuser", "metadata": {"description": "User name for the Virtual Machine."}}
data['parameters']['adminPassword'] = {"type": "securestring", "metadata": { "description": "Password to login to the Virtual Machine." } }
data['parameters']['dnsLabel'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": "Unique DNS Name for the Public IP address used to access the Virtual Machine" } }
data['parameters']['instanceType'] = {"type": "string", "defaultValue": default_instance, "allowedValues": instance_type_list, "metadata": {"description": "Azure instance size of the Virtual Machine."}}
data['parameters']['imageName'] = {"type": "string", "defaultValue": "Good", "allowedValues": [ "Good", "Better", "Best" ], "metadata": { "description": "F5 SKU (IMAGE) to you want to deploy."}}
data['parameters']['bigIpVersion'] = {"type": "string", "defaultValue": default_big_ip_version, "allowedValues": allowed_big_ip_versions, "metadata": { "description": "F5 BIG-IP version you want to use."}}
if license_type == 'BYOL':
    data['parameters']['licenseKey1'] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": license_text['licenseKey1'] } }
    if template_name == 'cluster_base':
        for license_key in ['licenseKey2']:
            data['parameters'][license_key] = {"type": "string", "defaultValue": "REQUIRED", "metadata": { "description": license_text[license_key] } }
elif license_type == 'PAYG':
    data['parameters']['licensedBandwidth'] = {"type": "string", "defaultValue": default_payg_bw, "allowedValues": [ "25m", "200m", "1g" ], "metadata": { "description": license_text['licensedBandwidth']}}
data['parameters']['ntpServer'] = {"type": "string", "defaultValue": "0.pool.ntp.org", "metadata": { "description": "If you would like to change the NTP server the BIG-IP uses replace the default ntp server with your choice." } }
data['parameters']['timeZone'] = {"type": "string", "defaultValue": "UTC", "metadata": { "description": "If you would like to change the time zone the BIG-IP uses then enter your chocie. This is in the format of the Olson timezone string from /usr/share/zoneinfo, such as UTC, US/Central or Europe/London." } }
data['parameters']['restrictedSrcAddress'] = {"type": "string", "defaultValue": "*", "metadata": { "description": "This field restricts management access to a specific network or address. Enter an IP address or address range in CIDR notation, or asterisk for all sources" } }
data['parameters']['tagValues'] = {"type": "object", "defaultValue": tag_values, "metadata": { "description": "Default key/value resource tags will be added to the resources in this deploymeny, if you would like the values to be unique adjust them as needed for each key." }}

# Set new_stack/existing_stack parameters for templates that support that
if template_name in ('1nic', '2nic', '3nic', 'ha-avset'):
    data['parameters']['instanceName'] = {"type": "string", "defaultValue": "f5vm01", "metadata": { "description": "Name of the Virtual Machine."}}
    if template_name in ('2nic', '3nic', 'ha-avset'):
        data['parameters']['numberOfExternalIps'] = {"type": "int", "defaultValue": 1, "allowedValues": [1, 2, 3, 4, 5, 6, 7, 8], "metadata": { "description": "The number of public/private IP addresses you want to deploy for the application traffic (external) NIC on the BIG-IP VE to be used for virtual servers." } }
    if stack_type == 'new_stack':
        data['parameters']['vnetAddressPrefix'] = {"type": "string", "defaultValue": "10.0", "metadata": { "description": "The start of the CIDR block the BIG-IP VEs use when creating the Vnet and subnets.  You MUST type just the first two octets of the /16 virtual network that will be created, for example '10.0', '10.100', 192.168'." } }
    elif stack_type == 'existing_stack':
        data['parameters']['vnetName'] = { "type": "string", "metadata": { "description": "The name of the existing virtual network to which you want to connect the BIG-IP VEs." } }
        data['parameters']['vnetResourceGroupName'] = { "type": "string", "metadata": { "description": "The name of the resource group that contains the Virtual Network where the BIG-IP VE will be placed." } }
        data['parameters']['mgmtSubnetName'] = { "type": "string", "metadata": { "description": "Name of the existing MGMT subnet - with external access to the Internet." } }
        if template_name in ('ha-avset'):
            data['parameters']['mgmtIpAddressRangeStart'] = { "metadata": { "description": "The static private IP address you would like to assign to the management self IP of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device." }, "type": "string" }
        else:
            data['parameters']['mgmtIpAddress'] = { "type": "string", "metadata": { "description": "MGMT subnet IP Address to use for the BIG-IP management IP address." } }
        if template_name in ('2nic', '3nic', 'ha-avset'):
            data['parameters']['externalSubnetName'] = { "type": "string", "metadata": { "description": "Name of the existing external subnet - with external access to Internet." } }
            if template_name in ('ha-avset'):
                data['parameters']['externalIpSelfAddressRangeStart'] = { "metadata": { "description": "The static private IP address you would like to assign to the external self IP (primary) of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device." }, "type": "string" }
                data['parameters']['externalIpAddressRangeStart'] = { "metadata": { "description": "The static private IP address (secondary) you would like to assign to the first shared Azure public IP. An additional private IP address will be assigned for each public IP address you specified in numberOfExternalIps.  For example, inputting 10.100.1.50 here and choosing 2 in numberOfExternalIps would result in 10.100.1.50 and 10.100.1.51 being configured as static private IP addresses for external virtual servers." }, "type": "string" }
            else:
                data['parameters']['externalIpAddressRangeStart'] = { "type": "string", "metadata": { "description": "The static private IP address  you would like to assign to the first external Azure public IP(for self IP). An additional private IP address will be assigned for each public IP address you specified in numberOfExternalIps.  For example, inputting 10.100.1.50 here and choosing 2 in numberOfExternalIps would result in 10.100.1.50(self IP), 10.100.1.51 and 10.100.1.52 being configured as static private IP addresses for external virtual servers." } }
        if template_name in ('3nic', 'ha-avset'):
            data['parameters']['internalSubnetName'] = { "type": "string", "metadata": { "description": "Name of the existing internal subnet." } }
            if template_name in ('ha-avset'):
                data['parameters']['internalIpAddressRangeStart'] = { "type": "string", "metadata": { "description": "The static private IP address you would like to assign to the internal self IP of the first BIG-IP. The next contiguous address will be used for the second BIG-IP device." } }
            else:
                data['parameters']['internalIpAddress'] = { "type": "string", "metadata": { "description": "Internal subnet IP address you want to use for the BIG-IP internal self IP address." } }

# Set unique solution parameters
if template_name in ('cluster_base'):
    data['parameters']['numberOfInstances'] = {"type": "int", "defaultValue": 2, "allowedValues": [ 2 ], "metadata": { "description": "The number of BIG-IP VEs that will be deployed in front of your application(s)." } }
if template_name in ('ha-avset'):
    data['parameters']['managedRoutes'] = { "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "A comma-delimited list of UDR destinations to be managed by this cluster." }, "type": "string" }
    data['parameters']['routeTableTag'] = { "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "Azure tag to identify the route tables to be managed by this cluster." }, "type": "string" }
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['parameters']['vmScaleSetMinCount'] = {"type": "int", "defaultValue": 2, "allowedValues": [1, 2, 3, 4, 5, 6], "metadata": { "description": "The minimum (and default) number of BIG-IP VEs that will be deployed into the VM Scale Set." } }
    data['parameters']['vmScaleSetMaxCount'] = {"type": "int", "defaultValue": 4, "allowedValues": [2, 3, 4, 5, 6, 7, 8], "metadata": { "description": "The maximum number of BIG-IP VEs that can be deployed into the VM Scale Set." } }
    data['parameters']['scaleOutThroughput'] = {"type": "int", "defaultValue": 90, "allowedValues": [50, 55, 60, 65, 70, 75, 80, 85, 90, 95], "metadata": { "description": "The percentage of 'Network Out' throughput that triggers a Scale Out event.  This is factored as a percentage of the F5 PAYG image bandwidth (Mbps) size you choose." } }
    data['parameters']['scaleInThroughput'] = {"type": "int", "defaultValue": 10, "allowedValues": [5, 10, 15, 20, 25, 30, 35, 40, 45], "metadata": { "description": "The percentage of 'Network Out' throughput that triggers a Scale In event.  This is factored as a percentage of the F5 PAYG image bandwidth (Mbps) size you choose." } }
    data['parameters']['scaleTimeWindow'] = {"type": "int", "defaultValue": 10, "allowedValues": [5, 10, 15, 30], "metadata": { "description": "The time window required to trigger a scale event (in and out). This is used to determine the amount of time needed for a threshold to be breached, as well as to prevent excessive scaling events (flapping)." } }
if template_name in ('waf_autoscale'):
    # WAF-like templates need the 'Best' Image, still prompt as a parameter so they are aware of what they are paying for with PAYG
    data['parameters']['imageName'] = {"type": "string", "defaultValue": "Best", "allowedValues": [ "Best" ], "metadata": { "description": "F5 SKU (IMAGE) you want to deploy. 'Best' is the only option because ASM is required."}}
    data['parameters']['solutionDeploymentName'] = { "type": "string", "metadata": { "description": "A unique name for this deployment." } }
    data['parameters']['applicationProtocols'] = { "type": "string", "defaultValue": "http-https", "metadata": { "description": "The protocol(s) used by your application." }, "allowedValues" : [ "http", "https", "http-https", "https-offload" ] }
    data['parameters']['applicationAddress'] = { "type": "string", "metadata": { "description": "The public IP address or DNS FQDN of the application that this WAF will protect." } }
    data['parameters']['applicationServiceFqdn'] = { "type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "If you are deploying in front of an Azure App Service, the FQDN of the public application." } }
    data['parameters']['applicationPort'] = { "type": "string", "defaultValue": "80", "metadata": { "description": "If you are deploying an HTTP application, the port on which your service listens for unencrypted traffic. This field is not required when deploying HTTPS only." } }
    data['parameters']['applicationSecurePort'] = { "type": "string", "defaultValue": "443", "metadata": { "description": "If you are deploying an HTTPS application, the port on which your service listens for encrypted traffic. This field is not required when deploying HTTP only." } }
    data['parameters']['sslCert'] = { "type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "The SSL certificate .pfx file corresponding to public facing virtual server." } }
    data['parameters']['sslPswd'] = { "type": "securestring", "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "The SSL certificate .pfx password corresponding to the certificate you entered." } }
    data['parameters']['applicationType'] = { "type": "string", "defaultValue": "Linux", "metadata": { "description": "Is your application running on a Linux OS or a Windows OS?" }, "allowedValues": [ "Windows", "Linux" ] }
    data['parameters']['blockingLevel'] = { "type": "string", "defaultValue": "medium", "metadata": { "description": "Select how aggressive you want the blocking level of this WAF.  Remember that the more aggressive the blocking level, the more potential there is for false-positives that the WAF might detect. Select Custom to specify your own security policy." }, "allowedValues": [ "low", "medium", "high", "off", "custom" ] }
    data['parameters']['customPolicy'] = { "type": "string", "defaultValue": "NOT_SPECIFIED", "metadata": { "description": "Specify the publicly available URL of a custom ASM security policy in XML format. This policy will be applied in place of the standard High/Medium/Low policy." } }
# Add service principal parameters to necessary solutions
if template_name in ('ltm_autoscale', 'waf_autoscale', 'ha-avset'):
    data['parameters']['tenantId'] = { "type": "string", "metadata": { "description": "Your Azure service principal application tenant ID." } }
    data['parameters']['clientId'] = { "type": "string", "metadata": { "description": "Your Azure service principal application client ID." } }
    data['parameters']['servicePrincipalSecret'] = { "type": "securestring", "metadata": { "description": "Your Azure service principal application secret." } }

# Remove unecessary parameters and do a check for missing mandatory variables
master_helper.template_check(data, 'parameters')
# Some modifications once parameters have been defined
for parameter in data['parameters']:
    # Sort azuredeploy.json parameter values alphabetically
    sorted_param = json.dumps(data['parameters'][parameter], sort_keys=True, ensure_ascii=False)
    data['parameters'][parameter] = json.loads(sorted_param, object_pairs_hook=OrderedDict)
    # Add parameters into parameters file as well
    try:
        data_params['parameters'][parameter] = {"value": data['parameters'][parameter]['defaultValue']}
    except:
        data_params['parameters'][parameter] = {"value": 'GEN_UNIQUE'}

######################################## ARM Variables ########################################
## Pulling in a base set of variables and setting order with below call, it is a function of master_helper.py
master_helper.variable_initialize(data)
# Set certain default variables to unique, changing value
data['variables']['bigIpVersionPortMap'] = version_port_map
data['variables']['f5CloudLibsTag'] = f5_cloud_libs_tag
data['variables']['f5CloudLibsAzureTag'] = f5_cloud_libs_azure_tag
data['variables']['f5NetworksTag'] = f5_networks_tag
data['variables']['verifyHash'] = verify_hash
data['variables']['installCloudLibs'] = install_cloud_libs
data['variables']['skuToUse'] = sku_to_use
data['variables']['offerToUse'] = offer_to_use
data['variables']['bigIpNicPortValue'] = nic_port_map
## Handle new_stack/existing_stack variable differences
if template_name in ('1nic', '2nic', '3nic', 'ha-avset'):
    data['variables']['instanceName'] = "[toLower(parameters('instanceName'))]"
    if stack_type == 'new_stack':
        data['variables']['vnetId'] = "[resourceId('Microsoft.Network/virtualNetworks', variables('virtualNetworkName'))]"
        data['variables']['vnetAddressPrefix'] = "[concat(parameters('vnetAddressPrefix'),'.0.0/16')]"
        data['variables']['mgmtSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.1.0/24')]"
        data['variables']['mgmtSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.1.4')]"
        if template_name in ('2nic', '3nic', 'ha-avset'):
            data['variables']['extNsgID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(variables('dnsLabel'),'-ext-nsg'))]"
            data['variables']['extSelfPublicIpAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-self-pip')]"
            data['variables']['extSelfPublicIpAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('extSelfPublicIpAddressNamePrefix'))]"
            data['variables']['extpublicIPAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-ext-pip')]"
            data['variables']['extPublicIPAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('extPublicIPAddressNamePrefix'))]"
            data['variables']['extNicName'] = "[concat(variables('dnsLabel'), '-ext')]"
            data['variables']['extSubnetName'] = "[concat(variables('dnsLabel'),'-ext-subnet')]"
            data['variables']['extSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('extsubnetName'))]"
            data['variables']['extSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.2.0/24')]"
            data['variables']['extSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.2.4')]"
            data['variables']['extSubnetPrivateAddressPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.2.')]"
            if template_name in ('3nic', 'ha-avset'):
                data['variables']['intNicName'] = "[concat(variables('dnsLabel'), '-int')]"
                data['variables']['intSubnetName'] = "[concat(variables('dnsLabel'),'int-subnet')]"
                data['variables']['intSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('intsubnetName'))]"
                data['variables']['intSubnetPrefix'] = "[concat(parameters('vnetAddressPrefix'), '.3.0/24')]"
                data['variables']['intSubnetPrivateAddress'] = "[concat(parameters('vnetAddressPrefix'), '.3.4')]"
            self_ip_config_array = [{ "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": {"PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '0')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
            if template_name in ('ha-avset'):
                data['variables']['mgmtSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.1.5')]"
                data['variables']['extSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.2.5')]"
                data['variables']['intSubnetPrivateAddress1'] = "[concat(parameters('vnetAddressPrefix'), '.3.5')]"
                self_ip_config_array += [{ "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": {"PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
            ext_ip_config_array = [{ "name": "[concat(variables('instanceName'), '-ext-ipconfig0')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 0)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 10)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig1')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 1)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 11)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig2')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 2)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 12)]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig3')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 3)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 13)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig4')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 4)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 14)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig5')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 5)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 15)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig6')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 6)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 16)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig7')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 7)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), 17)]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
    if stack_type == 'existing_stack':
        data['variables']['virtualNetworkName'] = "[parameters('vnetName')]"
        data['variables']['vnetId'] = "[resourceId(parameters('vnetResourceGroupName'),'Microsoft.Network/virtualNetworks',variables('virtualNetworkName'))]"
        data['variables']['mgmtSubnetId'] = "[concat(variables('vnetID'),'/subnets/',parameters('mgmtSubnetName'))]"
        data['variables']['mgmtSubnetPrivateAddress'] = "[parameters('mgmtIpAddress')]"
        if template_name in ('2nic', '3nic', 'ha-avset'):
            data['variables']['extNsgID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(variables('dnsLabel'),'-ext-nsg'))]"
            data['variables']['extSelfPublicIpAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-self-pip')]"
            data['variables']['extSelfPublicIpAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('extSelfPublicIpAddressNamePrefix'))]"
            data['variables']['extpublicIPAddressNamePrefix'] = "[concat(variables('dnsLabel'), '-ext-pip')]"
            data['variables']['extPublicIPAddressIdPrefix'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('extPublicIPAddressNamePrefix'))]"
            data['variables']['extNicName'] = "[concat(variables('dnsLabel'), '-ext')]"
            data['variables']['extSubnetName'] = "[parameters('externalSubnetName')]"
            data['variables']['extSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('extsubnetName'))]"
            data['variables']['extSubnetPrivateAddress'] = "[parameters('externalIpAddressRangeStart')]"
            data['variables']['extSubnetPrivateAddressPrefixArray'] = "[split(parameters('externalIpAddressRangeStart'), '.')]"
            data['variables']['extSubnetPrivateAddressPrefix'] = "[concat(variables('extSubnetPrivateAddressPrefixArray')[0], '.', variables('extSubnetPrivateAddressPrefixArray')[1], '.', variables('extSubnetPrivateAddressPrefixArray')[2], '.')]"
            data['variables']['extSubnetPrivateAddressSuffixInt'] = "[int(variables('extSubnetPrivateAddressPrefixArray')[3])]"
            data['variables']['extSubnetPrivateAddressSuffix0'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 1)]"
            data['variables']['extSubnetPrivateAddressSuffix1'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 2)]"
            data['variables']['extSubnetPrivateAddressSuffix2'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 3)]"
            data['variables']['extSubnetPrivateAddressSuffix3'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 4)]"
            data['variables']['extSubnetPrivateAddressSuffix4'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 5)]"
            data['variables']['extSubnetPrivateAddressSuffix5'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 6)]"
            data['variables']['extSubnetPrivateAddressSuffix6'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 7)]"
            data['variables']['extSubnetPrivateAddressSuffix7'] = "[add(variables('extSubnetPrivateAddressSuffixInt'), 8)]"
            if template_name in ('3nic', 'ha-avset'):
                data['variables']['intNicName'] = "[concat(variables('dnsLabel'), '-int')]"
                data['variables']['intSubnetName'] = "[parameters('internalSubnetName')]"
                data['variables']['intSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('intsubnetName'))]"
                data['variables']['intSubnetPrivateAddress'] = "[parameters('internalIpAddress')]"
            self_ip_config_array = [{ "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": {"PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '0')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
            if template_name in ('ha-avset'):
                    data['variables']['mgmtSubnetPrivateAddressPrefixArray'] = "[split(parameters('mgmtIpAddressRangeStart'), '.')]"
                    data['variables']['mgmtSubnetPrivateAddressPrefix'] = "[concat(variables('mgmtSubnetPrivateAddressPrefixArray')[0], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[1], '.', variables('mgmtSubnetPrivateAddressPrefixArray')[2], '.')]"
                    data['variables']['mgmtSubnetPrivateAddressSuffixInt'] = "[int(variables('mgmtSubnetPrivateAddressPrefixArray')[3])]"
                    data['variables']['mgmtSubnetPrivateAddressSuffix'] = "[add(variables('mgmtSubnetPrivateAddressSuffixInt'), 1)]"
                    data['variables']['mgmtSubnetPrivateAddress'] = "[parameters('mgmtIpAddressRangeStart')]"
                    data['variables']['mgmtSubnetPrivateAddress1'] = "[concat(variables('mgmtSubnetPrivateAddressPrefix'), variables('mgmtSubnetPrivateAddressSuffix'))]"
                    data['variables']['extSubnetSelfPrivateAddressPrefixArray'] = "[split(parameters('externalIpSelfAddressRangeStart'), '.')]"
                    data['variables']['extSubnetSelfPrivateAddressPrefix'] = "[concat(variables('extSubnetSelfPrivateAddressPrefixArray')[0], '.', variables('extSubnetSelfPrivateAddressPrefixArray')[1], '.', variables('extSubnetSelfPrivateAddressPrefixArray')[2], '.')]"
                    data['variables']['extSubnetSelfPrivateAddressSuffixInt'] = "[int(variables('extSubnetSelfPrivateAddressPrefixArray')[3])]"
                    data['variables']['extSubnetSelfPrivateAddressSuffix'] = "[add(variables('extSubnetSelfPrivateAddressSuffixInt'), 1)]"
                    data['variables']['extSubnetPrivateAddress'] = "[parameters('externalIpSelfAddressRangeStart')]"
                    data['variables']['extSubnetPrivateAddress1'] = "[concat(variables('extSubnetSelfPrivateAddressPrefix'), variables('extSubnetSelfPrivateAddressSuffix'))]"
                    data['variables']['intSubnetPrivateAddressPrefixArray'] = "[split(parameters('internalIpAddressRangeStart'), '.')]"
                    data['variables']['intSubnetPrivateAddressPrefix'] = "[concat(variables('intSubnetPrivateAddressPrefixArray')[0], '.', variables('intSubnetPrivateAddressPrefixArray')[1], '.', variables('intSubnetPrivateAddressPrefixArray')[2], '.')]"
                    data['variables']['intSubnetPrivateAddressSuffixInt'] = "[int(variables('intSubnetPrivateAddressPrefixArray')[3])]"
                    data['variables']['intSubnetPrivateAddressSuffix'] = "[add(variables('intSubnetPrivateAddressSuffixInt'), 1)]"
                    data['variables']['intSubnetPrivateAddress'] = "[parameters('internalIpAddressRangeStart')]"
                    data['variables']['intSubnetPrivateAddress1'] = "[concat(variables('intSubnetPrivateAddressPrefix'), variables('intSubnetPrivateAddressSuffix'))]"
                    self_ip_config_array += [{ "name": "[concat(variables('instanceName'), '-self-ipconfig')]", "properties": {"PublicIpAddress": { "Id": "[concat(variables('extSelfPublicIpAddressIdPrefix'), '1')]" }, "primary": True, "privateIPAddress": "[variables('extSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
            ext_ip_config_array = [{ "name": "[concat(variables('instanceName'), '-ext-ipconfig0')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 0)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix0'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig1')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 1)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix1'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig2')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 2)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix2'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig3')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 3)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix3'))]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig4')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 4)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix4'))]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig5')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 5)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix5'))]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig6')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 6)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix6'))]",  "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }, { "name": "[concat(variables('instanceName'), '-ext-ipconfig7')]", "properties": { "PublicIpAddress": { "Id": "[concat(variables('extPublicIPAddressIdPrefix'), 7)]" }, "primary": False, "privateIPAddress": "[concat(variables('extSubnetPrivateAddressPrefix'), variables('extSubnetPrivateAddressSuffix7'))]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('extSubnetId')]" } } }]
    # After adding variables for new_stack/existing_stack we need to add the ip config array
    if template_name in ('2nic', '3nic', 'ha-avset'):
        data['variables']['numberOfExternalIps'] = "[parameters('numberOfExternalIps')]"
        data['variables']['selfIpconfigArray'] = self_ip_config_array
        data['variables']['extIpconfigArray'] = ext_ip_config_array

if template_name in ('cluster_base', 'ltm_autoscale', 'waf_autoscale'):
    data['variables']['vnetAddressPrefix'] = "10.0.0.0/16"
    data['variables']['ipAddress'] = "10.0.1."
    data['variables']['loadBalancerName'] = "[concat(variables('dnsLabel'),'-alb')]"
    data['variables']['deviceNamePrefix'] = "[concat(variables('dnsLabel'),'-device')]"
    data['variables']['lbID'] = "[resourceId('Microsoft.Network/loadBalancers',variables('loadBalancerName'))]"
    data['variables']['frontEndIPConfigID'] = "[concat(variables('lbID'),'/frontendIPConfigurations/loadBalancerFrontEnd')]"
    if template_name in ('ltm_autoscale', 'waf_autoscale'):
        data['variables']['computeApiVersion'] = "2016-04-30-preview"
        data['variables']['networkApiVersion'] = "2016-06-01"
        data['variables']['bigIpMgmtPort'] = 8443
        data['variables']['vmssName'] = "[concat(parameters('dnsLabel'),'-vmss')]"
        data['variables']['newDataStorageAccountName'] = "[concat(uniquestring(resourceGroup().id), 'data000')]"
        data['variables']['subscriptionID'] = "[subscription().subscriptionId]"
        data['variables']['25m'] = 26214400
        data['variables']['200m'] = 209715200
        data['variables']['1g'] = 1073741824
        data['variables']['scaleOutCalc'] = "[mul(variables(parameters('licensedBandwidth')), parameters('scaleOutThroughput'))]"
        data['variables']['scaleInCalc'] = "[mul(variables(parameters('licensedBandwidth')), parameters('scaleInThroughput'))]"
        data['variables']['scaleOutNetworkBits'] = "[div(variables('scaleOutCalc'), 100)]"
        data['variables']['scaleInNetworkBits'] = "[div(variables('scaleInCalc'), 100)]"
        data['variables']['scaleOutNetworkBytes'] = "[div(variables('scaleOutNetworkBits'), 8)]"
        data['variables']['scaleInNetworkBytes'] = "[div(variables('scaleInNetworkBits'), 8)]"
        data['variables']['timeWindow'] = "[concat('PT', parameters('scaleTimeWindow'), 'M')]"
    if template_name in ('waf_autoscale'):
        data['variables']['f5NetworksSolutionScripts'] = "[concat('https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/', variables('f5NetworksTag'), '/" + solution_location + "/solutions/autoscale/waf/deploy_scripts/')]"
        data['variables']['lbTcpProbeNameHttp'] = "tcp_probe_http"
        data['variables']['lbTcpProbeIdHttp'] = "[concat(variables('lbID'),'/probes/',variables('lbTcpProbeNameHttp'))]"
        data['variables']['lbTcpProbeNameHttps'] = "tcp_probe_https"
        data['variables']['lbTcpProbeIdHttps'] = "[concat(variables('lbID'),'/probes/',variables('lbTcpProbeNameHttps'))]"
        data['variables']['httpBackendPort'] = 880
        data['variables']['httpsBackendPort'] = 8445
        data['variables']['commandArgs'] = "[concat('-m ', parameters('applicationProtocols'), ' -d ', parameters('solutionDeploymentName'), ' -n ', parameters('applicationAddress'), ' -j 880 -k 8445 -h ', parameters('applicationPort'), ' -s ', parameters('applicationSecurePort'), ' -t ', toLower(parameters('applicationType')), ' -l ', toLower(parameters('blockingLevel')), ' -a ', parameters('customPolicy'), ' -c ', parameters('sslCert'), ' -r ', parameters('sslPswd'), ' -o ', parameters('applicationServiceFqdn'), ' -u ', parameters('adminUsername'))]"

# Remove unecessary variables and do a check for missing mandatory variables
master_helper.template_check(data, 'variables')
# Sort azuredeploy.json variable value(if exists) alphabetically
for variables in data['variables']:
    sorted_variable = json.dumps(data['variables'][variables], sort_keys=True, ensure_ascii=False)
    data['variables'][variables] = json.loads(sorted_variable, object_pairs_hook=OrderedDict)

######################################## ARM Resources ########################################
resources_list = []
###### Public IP Resource(s) ######
if template_name in ('1nic', '2nic', '3nic', 'cluster_base', 'ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[variables('mgmtPublicIPAddressName')]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[variables('dnsLabel')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
if template_name in ('ha-avset'):
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('mgmtPublicIPAddressName'), 0)]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), '-0')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } },{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('mgmtPublicIPAddressName'), 1)]", "tags": tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), '-1')]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
if template_name in ('2nic', '3nic', 'ha-avset'):
    # Add Self Public IP - for external NIC
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('extSelfPublicIpAddressNamePrefix'), '0')]", "tags": tags, "properties": { "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
    if template_name in ('ha-avset'):
        resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('extSelfPublicIpAddressNamePrefix'), '1')]", "tags": tags, "properties": { "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]
    # Add Traffic Public IP's - for external NIC
    pip_tags = tags.copy()
    if template_name in ('ha-avset'):
        if stack_type == 'new_stack':
            private_ip_value = "[concat(variables('extSubnetPrivateAddressPrefix'), 1, copyIndex())]"
        elif stack_type == 'existing_stack':
            private_ip_value = "[concat(variables('extSubnetPrivateAddressPrefix'), add(variables('extSubnetPrivateAddressSuffixInt'), copyIndex()))]"
        pip_tags['f5_privateIp'] = private_ip_value
        pip_tags['f5_extSubnetId'] = "[variables('extSubnetId')]"
    resources_list += [{ "type": "Microsoft.Network/publicIPAddresses", "apiVersion": network_api_version, "location": location, "name": "[concat(variables('extPublicIPAddressNamePrefix'), copyIndex())]", "copy": { "count": "[variables('numberOfExternalIps')]", "name": "extpipcopy"}, "tags": pip_tags, "properties": { "dnsSettings": { "domainNameLabel": "[concat(variables('dnsLabel'), copyIndex(0))]" }, "idleTimeoutInMinutes": 30, "publicIPAllocationMethod": "[variables('publicIPAddressType')]" } }]

###### Virtual Network Resources(s) ######
if template_name in ('1nic', 'cluster_base'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }]
if template_name in ('2nic'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }]
if template_name in ('3nic', 'ha-avset'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]" } }, { "name": "[variables('extSubnetName')]", "properties": { "addressPrefix": "[variables('extSubnetPrefix')]" } }, { "name": "[variables('intSubnetName')]", "properties": { "addressPrefix": "[variables('intSubnetPrefix')]" } }]
if template_name in ('1nic', '2nic', '3nic', 'cluster_base', 'ha-avset'):
    if stack_type == 'new_stack':
        resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    subnets = [{ "name": "[variables('mgmtSubnetName')]", "properties": { "addressPrefix": "[variables('mgmtSubnetPrefix')]", "networkSecurityGroup": {"id": "[variables('mgmtNsgID')]"} } }]
    resources_list += [{ "type": "Microsoft.Network/virtualNetworks", "apiVersion": api_version, "dependsOn": [ "[variables('mgmtNsgID')]" ], "location": location, "name": "[variables('virtualNetworkName')]", "tags": tags, "properties": { "addressSpace": { "addressPrefixes": [ "[variables('vnetAddressPrefix')]" ] }, "subnets": subnets } }]

###### Network Interface Resource(s) ######
if stack_type == 'new_stack':
    depends_on = "[variables('vnetId')]", "[variables('mgmtPublicIPAddressId')]", "[variables('mgmtNsgID')]"
    depends_on_multi_nic = "[variables('vnetId')]", "[concat(variables('extNsgID'))]", "extpipcopy"
elif stack_type == 'existing_stack':
    depends_on = "[variables('mgmtPublicIPAddressId')]", "[variables('mgmtNsgID')]"
    depends_on_multi_nic = "[concat(variables('extNsgID'))]", "extpipcopy"
if template_name in ('1nic', '2nic', '3nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on, "location": location, "name": "[variables('mgmtNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[variables('mgmtNsgID')]" }, "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('mgmtSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "PublicIpAddress": { "Id": "[variables('mgmtPublicIPAddressId')]" }, "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ] } }]
if template_name in ('2nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_multi_nic, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "ipConfigurations": "[concat(take(variables('selfIpConfigArray'), 1), take(variables('extIpconfigArray'),variables('numberofExternalIps')))]" } } ]
if template_name in ('3nic'):
    resources_list += [{ "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_multi_nic, "location": location, "name": "[variables('extNicName')]", "tags": tags, "properties": { "networkSecurityGroup": { "id": "[concat(variables('extNsgID'))]" }, "ipConfigurations": "[concat(take(variables('selfIpConfigArray'), 1), take(variables('extIpconfigArray'),variables('numberofExternalIps')))]" } }, { "type": "Microsoft.Network/networkInterfaces", "apiVersion": api_version, "dependsOn": depends_on_multi_nic, "location": location, "name": "[variables('intNicName')]", "tags": tags, "properties": { "ipConfigurations": [ { "name": "[concat(variables('instanceName'), '-ipconfig1')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] } } ]
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkInterfaces", "name": "[concat(variables('mgmtNicName'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/guimgt',copyindex())]", "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'),'/inboundNatRules/sshmgt',copyindex())]", "[variables('mgmtNsgID')]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "niccopy" }, "properties": { "networkSecurityGroup": { "id": "[variables('mgmtNsgID')]" }, "ipConfigurations": [ { "name": "ipconfig1", "properties": { "privateIPAllocationMethod": "Static", "privateIPAddress": "[concat(variables('ipAddress'),add(4,copyindex()))]", "subnet": { "id": "[variables('mgmtSubnetId')]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat(variables('lbID'), '/backendAddressPools/', 'loadBalancerBackEnd')]" } ], "loadBalancerInboundNatRules": [ { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'guimgt',copyIndex())]" }, { "id": "[concat(variables('lbID'), '/inboundNatRules/', 'sshmgt',copyIndex())]" } ] } } ] } }]
# Can we shrink this down with a copy?
if template_name in ('ha-avset'):
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'), '0')]" ], "location": location, "name": "[concat(variables('mgmtNicName'), '0')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-mgmt-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(variables('mgmtPublicIPAddressName'), '0'))]" }, "privateIPAddress": "[variables('mgmtSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[variables('mgmtNsgId')]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'), '1')]" ], "location": location, "name": "[concat(variables('mgmtNicName'), '1')]", "properties": { "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-mgmt-ipconfig')]", "properties": { "PublicIpAddress": { "Id": "[resourceId('Microsoft.Network/publicIPAddresses/', concat(variables('mgmtPublicIPAddressName'), '1'))]" }, "privateIPAddress": "[variables('mgmtSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('mgmtSubnetId')]" } } } ], "networkSecurityGroup": { "id": "[variables('mgmtNsgId')]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '0')]", "extpipcopy" ], "location": location, "name": "[concat(variables('extNicName'), '0')]", "properties": { "ipConfigurations": "[concat(take(variables('selfIpConfigArray'), 1), take(variables('extIpConfigArray'), parameters('numberOfExternalIps')))]", "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('extSelfPublicIpAddressNamePrefix'), '1')]" ], "location": location, "name": "[concat(variables('extNicName'), '1')]", "properties": { "ipConfigurations": "[skip(variables('selfIpConfigArray'), 1)]", "networkSecurityGroup": { "id": "[concat(variables('extNsgId'))]" } }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_multi_nic, "location": location, "name": "[concat(variables('intNicName'), '0')]", "properties": { "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": depends_on_multi_nic, "location": location, "name": "[concat(variables('intNicName'), '1')]", "properties": { "enableIPForwarding": True, "ipConfigurations": [ { "name": "[concat(variables('dnsLabel'), '-int-ipconfig')]", "properties": { "privateIPAddress": "[variables('intSubnetPrivateAddress1')]", "privateIPAllocationMethod": "Static", "subnet": { "id": "[variables('intSubnetId')]" } } } ] }, "tags": tags, "type": "Microsoft.Network/networkInterfaces" }]

###### Network Security Group Resource(s) ######
nsg_security_rules = [{ "name": "mgmt_allow_https", "properties": { "description": "", "priority": 101, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('bigIpMgmtPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "ssh_allow_22", "properties": { "description": "", "priority": 102, "sourceAddressPrefix": "[parameters('restrictedSrcAddress')]", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }]
if template_name in ('waf_autoscale'):
    nsg_security_rules += [{ "name": "app_allow_http", "properties": { "description": "", "priority": 110, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpBackendPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }, { "name": "app_allow_https", "properties": { "description": "", "priority": 111, "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "[variables('httpsBackendPort')]", "protocol": "TCP", "direction": "Inbound", "access": "Allow" } }]

if template_name in ('1nic', '2nic', '3nic', 'ha-avset', 'cluster_base', 'ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-mgmt-nsg')]", "tags": tags, "properties": { "securityRules": nsg_security_rules } }]
if template_name in ('2nic', '3nic', 'ha-avset'):
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/networkSecurityGroups", "location": location, "name": "[concat(variables('dnsLabel'), '-ext-nsg')]", "tags": tags, "properties": { "securityRules": "" } }]

###### Load Balancer Resource(s) ######
probes_to_use = ""; lb_rules_to_use = ""
if template_name in ('waf_autoscale'):
    probes_to_use = [ { "name": "[variables('lbTcpProbeNameHttp')]", "properties": { "protocol": "Tcp", "port": "[variables('httpBackendPort')]", "intervalInSeconds": 15, "numberOfProbes": 3 } }, { "name": "[variables('lbTcpProbeNameHttps')]", "properties": { "protocol": "Tcp", "port": "[variables('httpsBackendPort')]", "intervalInSeconds": 15, "numberOfProbes": 3 } } ]
    lb_rules_to_use = [{ "Name": "app-http", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttp')]" }, "protocol": "Tcp", "frontendPort": "[parameters('applicationPort')]", "backendPort": "[variables('httpBackendPort')]", "idleTimeoutInMinutes": 15 } }, { "Name": "app-https", "properties": { "frontendIPConfiguration": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/frontendIpConfigurations/loadBalancerFrontEnd')]" }, "backendAddressPool": { "id": "[concat(resourceId('Microsoft.Network/loadBalancers', variables('loadBalancerName')), '/backendAddressPools/loadBalancerBackEnd')]" }, "probe": { "id": "[variables('lbTcpProbeIdHttps')]" }, "protocol": "Tcp", "frontendPort": "[parameters('applicationSecurePort')]", "backendPort": "[variables('httpsBackendPort')]", "idleTimeoutInMinutes": 15 } }]

if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": network_api_version, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'))]" ], "location": location, "tags": tags, "name": "[variables('loadBalancerName')]", "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('mgmtPublicIPAddressId')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ] }, "type": "Microsoft.Network/loadBalancers" }]
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "apiVersion": network_api_version, "name": "[variables('loadBalancerName')]", "type": "Microsoft.Network/loadBalancers", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/publicIPAddresses/', variables('mgmtPublicIPAddressName'))]" ], "properties": { "frontendIPConfigurations": [ { "name": "loadBalancerFrontEnd", "properties": { "publicIPAddress": { "id": "[variables('mgmtPublicIPAddressId')]" } } } ], "backendAddressPools": [ { "name": "loadBalancerBackEnd" } ], "inboundNatPools": [ { "name": "sshnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPortRangeStart": 50001, "frontendPortRangeEnd": 50100, "backendPort": 22 } }, { "name": "mgmtnatpool", "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPortRangeStart": 50101, "frontendPortRangeEnd": 50200, "backendPort": "[variables('bigIpMgmtPort')]" } } ], "loadBalancingRules": lb_rules_to_use, "probes": probes_to_use } }]

###### Load Balancer Inbound NAT Rule(s) ######
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/guimgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8443)]", "backendPort": "[variables('bigIpMgmtPort')]", "enableFloatingIP": False } }]
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Network/loadBalancers/inboundNatRules", "name": "[concat(variables('loadBalancerName'),'/sshmgt', copyIndex())]", "location": location, "copy": { "name": "lbNatLoop", "count": "[parameters('numberOfInstances')]" }, "dependsOn": [ "[concat('Microsoft.Network/loadBalancers/', variables('loadBalancerName'))]" ], "properties": { "frontendIPConfiguration": { "id": "[variables('frontEndIPConfigID')]" }, "protocol": "tcp", "frontendPort": "[copyIndex(8022)]", "backendPort": 22, "enableFloatingIP": False } }]

######## Availability Set Resource(s) ######
if template_name in ('1nic', '2nic', '3nic', 'ha-avset', 'cluster_base'):
    resources_list += [{ "apiVersion": api_version, "location": location, "name": "[variables('availabilitySetName')]", "tags": tags, "type": "Microsoft.Compute/availabilitySets" }]

###### Storage Account Resource(s) ######
resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "location": location, "name": "[variables('newStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('storageAccountType')]" } }]
resources_list += [{ "type": "Microsoft.Storage/storageAccounts", "apiVersion": storage_api_version, "location": location, "name": "[variables('newDataStorageAccountName')]", "tags": tags, "properties": { "accountType": "[variables('dataStorageAccountType')]" } }]

###### Compute/VM Resource(s) ######
depends_on = "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'))]"
depends_on = list(depends_on)
if template_name == '1nic':
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }]
if template_name in ('2nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]")
if template_name in ('3nic'):
    nic_reference = [{ "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('mgmtNicName'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('extNicName'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces', variables('intNicName'))]", "properties": { "primary": False } }]
    depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'))]"); depends_on.append("[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'))]")
if template_name in ('1nic', '2nic', '3nic'):
    resources_list += [{"apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "dependsOn": depends_on, "location": location, "name": "[variables('instanceName')]", "tags": tags, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newDataStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces":  nic_reference }, "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "osProfile": { "computerName": "[variables('instanceName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'), '.blob.core.windows.net/vhds/', variables('instanceName'), '.vhd')]" } } } } }]
if template_name == 'cluster_base':
    resources_list += [{ "apiVersion": api_version, "type": "Microsoft.Compute/virtualMachines", "name": "[concat(variables('deviceNamePrefix'),copyindex())]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), copyindex())]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]" ], "copy": { "count": "[parameters('numberOfInstances')]", "name": "devicecopy" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets',variables('availabilitySetName'))]" }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "osProfile": { "computerName": "[concat(variables('deviceNamePrefix'),copyindex())]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "storageProfile": { "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "name": "[concat('osdisk',copyindex())]", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'),'.blob.core.windows.net/',variables('newStorageAccountName'),'/osDisk',copyindex(),'.vhd')]" }, "caching": "ReadWrite", "createOption": "FromImage" } }, "networkProfile": { "networkInterfaces": [ { "id": "[concat(resourceId('Microsoft.Network/networkInterfaces',variables('mgmtNicName')),copyindex())]" } ] }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newDataStorageAccountName'),'.blob.core.windows.net')]" } } } }]
if template_name in ('ha-avset'):
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), '0')]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'), '0')]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'), '0')]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '0')]", "plan": { "name": "[variables('skuToUse')]", "product": "[variables('offerToUse')]", "publisher": "f5-networks" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]" }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newDataStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces": [ { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('mgmtNicName'), '0'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('extNicName'), '0'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('intNicName'), '0'))]", "properties": { "primary": False } } ] }, "osProfile": { "adminPassword": "[parameters('adminPassword')]", "adminUsername": "[parameters('adminUsername')]", "computerName": "[variables('instanceName')]" }, "storageProfile": { "imageReference": { "offer": "[variables('offerToUse')]", "publisher": "f5-networks", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'), '.blob.core.windows.net/vhds/', variables('instanceName'), '0.vhd')]" } } } }, "tags": tags, "type": "Microsoft.Compute/virtualMachines" }]
    resources_list += [{ "apiVersion": api_version, "dependsOn": [ "[concat('Microsoft.Network/networkInterfaces/', variables('mgmtNicName'), '1')]", "[concat('Microsoft.Network/networkInterfaces/', variables('extNicName'), '1')]", "[concat('Microsoft.Network/networkInterfaces/', variables('intNicName'), '1')]", "[concat('Microsoft.Compute/availabilitySets/', variables('availabilitySetName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Storage/storageAccounts/', variables('newDataStorageAccountName'))]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '1')]", "plan": { "name": "[variables('skuToUse')]", "product": "[variables('offerToUse')]", "publisher": "f5-networks" }, "properties": { "availabilitySet": { "id": "[resourceId('Microsoft.Compute/availabilitySets', variables('availabilitySetName'))]" }, "diagnosticsProfile": { "bootDiagnostics": { "enabled": True, "storageUri": "[concat('http://',variables('newDataStorageAccountName'),'.blob.core.windows.net')]" } }, "hardwareProfile": { "vmSize": "[parameters('instanceType')]" }, "networkProfile": { "networkInterfaces": [ { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('mgmtNicName'), '1'))]", "properties": { "primary": True } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('extNicName'), '1'))]", "properties": { "primary": False } }, { "id": "[resourceId('Microsoft.Network/networkInterfaces/', concat(variables('intNicName'), '1'))]", "properties": { "primary": False } } ] }, "osProfile": { "adminPassword": "[parameters('adminPassword')]", "adminUsername": "[parameters('adminUsername')]", "computerName": "[variables('instanceName')]" }, "storageProfile": { "imageReference": { "offer": "[variables('offerToUse')]", "publisher": "f5-networks", "sku": "[variables('skuToUse')]", "version": image_to_use }, "osDisk": { "caching": "ReadWrite", "createOption": "FromImage", "name": "osdisk", "vhd": { "uri": "[concat('http://',variables('newStorageAccountName'), '.blob.core.windows.net/vhds/', variables('instanceName'), '1.vhd')]" } } } }, "tags": tags, "type": "Microsoft.Compute/virtualMachines" }]

###### Compute/VM Extension Resource(s) ######
command_to_execute = ''; command_to_execute2 = ''
if template_name == '1nic':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; rm -f /config/cloud/passwd')]"
if template_name == '2nic':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), ',vlan:external --log-level debug; rm -f /config/cloud/passwd')]"
if template_name == '3nic':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), ',vlan:internal --log-level debug; rm -f /config/cloud/passwd')]"
if template_name == 'cluster_base':
    # Two Extensions for Cluster
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('ipAddress'), 4), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('ipAddress'), 4), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('ipAddress'), 4), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('deviceNamePrefix'), 0, '.azuresecurity.com'), ' --auto-sync --save-on-auto-sync; rm -f /config/cloud/passwd')]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, concat(variables('ipAddress'), 5), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('deviceNamePrefix'), copyindex(1), '.azuresecurity.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db provision.1nicautoconfig:disable --db tmm.maxremoteloglength:2048 --module ltm:nominal --module asm:none --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', concat(variables('ipAddress'), 5), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', concat(variables('ipAddress'), 5), ' --join-group --device-group Sync --sync --remote-host ', concat(variables('ipAddress'), 4), ' --remote-user admin --remote-password-url file:///config/cloud/passwd; rm -f /config/cloud/passwd')]"
if template_name in 'ha-avset':
    command_to_execute = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE1_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress'), ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress'), ',vlan:internal --log-level debug; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node --use-strict /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/active; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node --use-strict /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/tgrefresh; tmsh modify cm device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress'), ' port 1026 } }; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', variables('intSubnetPrivateAddress'), ' --create-group --device-group Sync --sync-type sync-failover --device ', concat(variables('instanceName'), '0.', resourceGroup().location, '.cloudapp.azure.com'), ' --network-failover --auto-sync --save-on-auto-sync')]"
    command_to_execute2 = "[concat(<BASE_CMD_TO_EXECUTE>, variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' --ssl-port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --hostname ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), <LICENSE2_COMMAND> ' --ntp ', parameters('ntpServer'), ' --tz ', parameters('timeZone'), ' --db tmm.maxremoteloglength:2048 --module ltm:nominal --module afm:none; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/network.js --output /var/log/network.log --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --vlan name:external,nic:1.1 --vlan name:internal,nic:1.2 --self-ip name:self_2nic,address:', variables('extSubnetPrivateAddress1'), ',vlan:external --self-ip name:self_3nic,address:', variables('intSubnetPrivateAddress1'), ',vlan:internal --log-level debug; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node --use-strict /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/active; echo ', variables('singleQuote'), '/usr/bin/f5-rest-node --use-strict /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/failoverProvider.js', variables('singleQuote'), ' >> /config/failover/tgrefresh; tmsh modify cm device ', concat(variables('instanceName'), '1.', resourceGroup().location, '.cloudapp.azure.com'), ' unicast-address { { ip ', variables('intSubnetPrivateAddress1'), ' port 1026 } }; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/cluster.js --output /var/log/cluster.log --log-level debug --host ', variables('mgmtSubnetPrivateAddress1'), ' --port ', variables('bigIpMgmtPort'), ' -u admin --password-url file:///config/cloud/passwd --config-sync-ip ', variables('intSubnetPrivateAddress1'), ' --join-group --device-group Sync --sync --remote-host ', variables('mgmtSubnetPrivateAddress'), ' --remote-user admin --remote-password-url file:///config/cloud/passwd')]"
# Base command to execute
base_cmd_to_execute = "'mkdir /config/cloud && cp f5-cloud-libs.tar.gz* /config/cloud; mkdir -p /config/cloud/node_modules; BIG_IP_CREDENTIALS_FILE=/config/cloud/passwd; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), ' >> $BIG_IP_CREDENTIALS_FILE; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host '"
if template_name in 'ha-avset':
    base_cmd_to_execute = "'mkdir -p /config/cloud/node_modules && cp f5-cloud-libs*.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; /usr/bin/install -b -m 400 /dev/null /config/cloud/passwd; /usr/bin/install -b -m 400 /dev/null /config/cloud/azCredentials; /usr/bin/install -b -m 755 /dev/null /config/cloud/managedRoutes; /usr/bin/install -b -m 755 /dev/null /config/cloud/routeTableTag; IFS=', variables('singleQuote'), '%', variables('singleQuote'), '; echo -e ', variables('verifyHash'), ' > /config/verifyHash; echo -e ', variables('installCloudLibs'), ' > /config/installCloudLibs.sh; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), ' > /config/cloud/passwd; echo ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"resourceGroup\": \"', variables('resourceGroupName'), '\"}', variables('singleQuote'), ' > /config/cloud/azCredentials; echo -e ', parameters('managedRoutes'), ' > /config/cloud/managedRoutes; echo -e ', parameters('routeTableTag'), ' > /config/cloud/routeTableTag; unset IFS; bash /config/installCloudLibs.sh; /usr/bin/f5-rest-node /config/cloud/node_modules/f5-cloud-libs/scripts/onboard.js --output /var/log/onboard.log --log-level debug --host '"
command_to_execute = command_to_execute.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute)
command_to_execute2 = command_to_execute2.replace('<BASE_CMD_TO_EXECUTE>', base_cmd_to_execute)
# String map license 1/2 if needed for BYOL
command_to_execute = command_to_execute.replace('<LICENSE1_COMMAND>', license1_command)
command_to_execute2 = command_to_execute2.replace('<LICENSE2_COMMAND>', license2_command)

if template_name in ('1nic', '2nic', '3nic'):
    resources_list += [{"apiVersion": "2016-03-30", "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('instanceName'),'/start')]", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('instanceName'))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
if template_name == 'cluster_base':
    # Two Extensions for Cluster
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "name": "[concat(variables('deviceNamePrefix'),0,'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),0)]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute } } }]
    resources_list += [{ "type": "Microsoft.Compute/virtualMachines/extensions", "copy": { "name": "extensionLoop", "count": "[sub(parameters('numberOfInstances'), 1)]" }, "name": "[concat(variables('deviceNamePrefix'),add(copyindex(),1),'/start')]", "apiVersion": "2016-03-30", "tags": tags, "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/',variables('deviceNamePrefix'),add(copyindex(),1))]" ], "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]" ] }, "protectedSettings": { "commandToExecute": command_to_execute2 } } }]
if template_name == 'ha-avset':
    # Two Extensions for Cluster
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('dnsLabel'), '-', variables('instanceName'), '0')]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '0/start')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/dist/f5-cloud-libs-azure.tar.gz')]" ] }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]
    resources_list += [{ "apiVersion": "[variables('computeApiVersion')]", "dependsOn": [ "[concat('Microsoft.Compute/virtualMachines/', variables('dnsLabel'), '-', variables('instanceName'), '1')]" ], "location": location, "name": "[concat(variables('dnsLabel'), '-', variables('instanceName'), '1/start')]", "properties": { "protectedSettings": { "commandToExecute": command_to_execute2 }, "publisher": "Microsoft.Azure.Extensions", "settings": { "fileUris": [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/dist/f5-cloud-libs-azure.tar.gz')]" ] }, "type": "CustomScript", "typeHandlerVersion": "2.0", "autoUpgradeMinorVersion":"true" }, "tags": tags, "type": "Microsoft.Compute/virtualMachines/extensions" }]


###### Compute VM Scale Set(s) ######
autoscale_file_uris = [ "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/', variables('f5CloudLibsTag'), '/dist/f5-cloud-libs.tar.gz')]", "[concat('https://raw.githubusercontent.com/F5Networks/f5-cloud-libs-azure/', variables('f5CloudLibsAzureTag'), '/dist/f5-cloud-libs-azure.tar.gz')]" ]
if template_name in ('ltm_autoscale'):
    scale_script_call = "bash /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/autoscale.sh --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName ', parameters('adminUsername'), ' --password $BIG_IP_CREDENTIALS_FILE --azureSecretFile $AZURE_CREDENTIALS_FILE --managementPort ', variables('bigIpMgmtPort'), ' --ntpServer ', parameters('ntpServer'), ' --timeZone ', parameters('timeZone')"
if template_name in ('waf_autoscale'):
    scale_script_call = "bash /config/cloud/node_modules/f5-cloud-libs/node_modules/f5-cloud-libs-azure/scripts/autoscalewaf.sh --resourceGroup ', resourceGroup().name, ' --vmssName ', variables('vmssName'), ' --userName ', parameters('adminUsername'), ' --password $BIG_IP_CREDENTIALS_FILE --azureSecretFile $AZURE_CREDENTIALS_FILE --managementPort ', variables('bigIpMgmtPort'), ' --ntpServer ', parameters('ntpServer'), ' --timeZone ', parameters('timeZone'), ' --wafScriptArgs ', variables('singleQuote'), variables('commandArgs'), variables('singleQuote')"
    autoscale_file_uris += [ "[concat(variables('f5NetworksSolutionScripts'), 'deploy_waf.sh')]", "[concat(variables('f5NetworksSolutionScripts'), 'f5.http.v1.2.0rc7.tmpl')]", "[concat(variables('f5NetworksSolutionScripts'), 'f5.policy_creator.tmpl')]", "[concat(variables('f5NetworksSolutionScripts'), 'asm-policy.tar.gz')]" ]

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    autoscale_command_to_execute = "[concat('mkdir -p /config/cloud/node_modules; AZURE_CREDENTIALS_FILE=/config/cloud/azCredentials; BIG_IP_CREDENTIALS_FILE=/config/cloud/passwd; /usr/bin/install -m 400 /dev/null $AZURE_CREDENTIALS_FILE; /usr/bin/install -m 400 /dev/null $BIG_IP_CREDENTIALS_FILE; echo ', variables('singleQuote'), parameters('adminPassword'), variables('singleQuote'), ' > $BIG_IP_CREDENTIALS_FILE; echo ', variables('singleQuote'), '{\"clientId\": \"', parameters('clientId'), '\", \"tenantId\": \"', parameters('tenantId'), '\", \"secret\": \"', parameters('servicePrincipalSecret'), '\", \"subscriptionId\": \"', variables('subscriptionID'), '\", \"storageAccount\": \"', variables('newDataStorageAccountName'), '\", \"storageKey\": \"', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('newDataStorageAccountName')), variables('storageApiVersion')).key1, '\"}', variables('singleQuote'), ' > $AZURE_CREDENTIALS_FILE; cp f5-cloud-libs*.tar.gz* /config/cloud; /usr/bin/install -b -m 755 /dev/null /config/verifyHash; /usr/bin/install -b -m 755 /dev/null /config/installCloudLibs.sh; echo -e ', variables('verifyHash'), ' >> /config/verifyHash; echo -e ', variables('installCloudLibs'), ' >> /config/installCloudLibs.sh; bash /config/installCloudLibs.sh; <SCALE_SCRIPT_CALL>)]"
    autoscale_command_to_execute = autoscale_command_to_execute.replace('<SCALE_SCRIPT_CALL>', scale_script_call)

if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Compute/virtualMachineScaleSets", "apiVersion": compute_api_version, "name": "[variables('vmssName')]", "location": location, "tags": tags, "dependsOn": [ "[concat('Microsoft.Storage/storageAccounts/', variables('newStorageAccountName'))]", "[concat('Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'))]" ], "sku": { "name": "[parameters('instanceType')]", "tier": "Standard", "capacity": "[parameters('vmScaleSetMinCount')]" }, "plan": { "name": "[variables('skuToUse')]", "publisher": "f5-networks", "product": "[variables('offerToUse')]" }, "properties": { "upgradePolicy": { "mode": "Manual" }, "virtualMachineProfile": { "storageProfile": { "osDisk": { "vhdContainers": [ "[concat('https://', variables('newStorageAccountName'), '.blob.core.windows.net/vmss1')]" ], "name": "vmssosdisk", "caching": "ReadOnly", "createOption": "FromImage" }, "imageReference": { "publisher": "f5-networks", "offer": "[variables('offerToUse')]", "sku": "[variables('skuToUse')]", "version": image_to_use } }, "osProfile": { "computerNamePrefix": "[variables('vmssName')]", "adminUsername": "[parameters('adminUsername')]", "adminPassword": "[parameters('adminPassword')]" }, "networkProfile": { "networkInterfaceConfigurations": [ { "name": "nic1", "properties": { "primary": "true", "ipConfigurations": [ { "name": "ip1", "properties": { "subnet": { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/virtualNetworks/', variables('virtualNetworkName'), '/subnets/', variables('mgmtSubnetName'))]" }, "loadBalancerBackendAddressPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/backendAddressPools/loadBalancerBackEnd')]" } ], "loadBalancerInboundNatPools": [ { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/sshnatpool')]" }, { "id": "[concat('/subscriptions/', variables('subscriptionID'),'/resourceGroups/', resourceGroup().name, '/providers/Microsoft.Network/loadBalancers/', variables('loadBalancerName'), '/inboundNatPools/mgmtnatpool')]" } ] } } ] } } ] }, "extensionProfile": { "extensions": [ { "name":"main", "properties": { "publisher": "Microsoft.Azure.Extensions", "type": "CustomScript", "typeHandlerVersion": "2.0", "settings": { "fileUris": autoscale_file_uris }, "protectedSettings": { "commandToExecute": autoscale_command_to_execute } } } ] } }, "overprovision": "false" } }]

###### Compute VM Scale Set(s) AutoScale Settings ######
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    resources_list += [{ "type": "Microsoft.Insights/autoscaleSettings", "apiVersion": "[variables('insightsApiVersion')]", "name": "autoscaleconfig", "location": location, "dependsOn": [ "[concat('Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]" ], "properties": { "name": "autoscaleconfig", "targetResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "enabled": True, "profiles": [ { "name": "Profile1", "capacity": { "minimum": "[parameters('vmScaleSetMinCount')]", "maximum": "[parameters('vmScaleSetMaxCount')]", "default": "[parameters('vmScaleSetMinCount')]" }, "rules": [ { "metricTrigger": { "metricName": "Network Out", "metricNamespace": "", "metricResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('timeWindow')]", "timeAggregation": "Average", "operator": "GreaterThan", "threshold": "[variables('scaleOutNetworkBytes')]" }, "scaleAction": { "direction": "Increase", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } }, { "metricTrigger": { "metricName": "Network Out", "metricNamespace": "", "metricResourceUri": "[concat('/subscriptions/', variables('subscriptionID'), '/resourceGroups/',  resourceGroup().name, '/providers/Microsoft.Compute/virtualMachineScaleSets/', variables('vmssName'))]", "timeGrain": "PT1M", "statistic": "Average", "timeWindow": "[variables('timeWindow')]", "timeAggregation": "Average", "operator": "LessThan", "threshold": "[variables('scaleInNetworkBytes')]" }, "scaleAction": { "direction": "Decrease", "type": "ChangeCount", "value": "1", "cooldown": "PT1M" } } ], "notifications": [ { "operation": "Scale", "email": { "sendToSubscriptionAdministrator": False, "sendToSubscriptionCoAdministrators": False, "customEmails": "" } } ] } ] } }]

## Sort resources section - Expand to choose order of resources instead of just alphabetical?
temp_sort = 'temp_sort.json'
with open(temp_sort, 'w') as temp_sorting:
    json.dump(resources_list, temp_sorting, sort_keys=True, indent=4, ensure_ascii=False)
with open(temp_sort, 'r') as temp_sorted:
    data['resources'] = json.load(temp_sorted, object_pairs_hook=OrderedDict)
    temp_sorted.close(); os.remove(temp_sort)

######################################## ARM Outputs ########################################
if template_name in ('1nic', '2nic', '3nic'):
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://', reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn, ' ',22)]" }
if template_name == 'cluster_base':
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':8443')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',8022)]" }
if template_name == 'ha-avset':
    data['outputs']['GUI-URL0'] = { "type": "string", "value": "[concat('https://',reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
    data['outputs']['SSH-URL0'] = { "type": "string", "value": "[concat(reference(concat(variables('mgmtPublicIPAddressId'), '0')).dnsSettings.fqdn,' ',22)]" }
    data['outputs']['GUI-URL1'] = { "type": "string", "value": "[concat('https://',reference(concat(variables('mgmtPublicIPAddressId'), '1')).dnsSettings.fqdn, ':', variables('bigIpMgmtPort'))]" }
    data['outputs']['SSH-URL1'] = { "type": "string", "value": "[concat(reference(concat(variables('mgmtPublicIPAddressId'), '1')).dnsSettings.fqdn,' ',22)]" }
if template_name in ('ltm_autoscale', 'waf_autoscale'):
    data['outputs']['GUI-URL'] = { "type": "string", "value": "[concat('https://',reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,':50101', ' - 50200')]" }
    data['outputs']['SSH-URL'] = { "type": "string", "value": "[concat(reference(variables('mgmtPublicIPAddressId')).dnsSettings.fqdn,' ',50001, ' - 50100')]" }


######################################## End Create/Modify ARM Template Objects ########################################

## Write modified template(s) to appropriate location
with open(created_file, 'w') as finished:
    json.dump(data, finished, indent=4, sort_keys=False, ensure_ascii=False)
with open(createdfile_params, 'w') as finished_params:
    json.dump(data_params, finished_params, indent=4, sort_keys=False, ensure_ascii=False)


######################################## Create/Modify Scripts ########################################
    # Need to manually add templates to create scripts for now as a 'check'...
if template_name in ('1nic', '2nic', '3nic', 'cluster_base', 'ha-avset', 'ltm_autoscale', 'waf_autoscale') and script_location:
    bash_script = script_generator.script_creation(template_name, data, script_location, default_payg_bw, 'bash')
    ps_script = script_generator.script_creation(template_name, data, script_location, default_payg_bw, 'powershell')
######################################## END Create/Modify Scripts ########################################

######################################## Create/Modify README's ########################################
    readme_text = {'title_text': {}, 'intro_text': {}, 'help_text': {}, 'deploy_links': {}, 'version_tag': {}, 'ps_script': {}, 'bash_script': {}, 'config_example_text': {} }
    ## Title Text ##
    readme_text['title_text'] = {'1nic': 'Single NIC', '2nic': '2 NIC', '3nic': '3 NIC', 'cluster_base': 'ConfigSync Cluster: Single NIC', 'ha-avset': 'HA Cluster: Availability Set', 'ltm_autoscale': 'AutoScale BIG-IP LTM - VM Scale Set', 'waf_autoscale': 'AutoScale BIG-IP WAF(LTM+ASM) - VM Scale Set' }
    ## Intro Text ##
    readme_text['intro_text']['1nic'] = 'This solution uses an ARM template to launch a single NIC deployment of a cloud-focused BIG-IP VE in Microsoft Azure. Traffic flows from the BIG-IP VE to the application servers. This is the standard Cloud design where the compute instance of F5 is running with a single interface, where both management and data plane traffic is processed.  This is a traditional model in the cloud where the deployment is considered one-armed.'
    readme_text['intro_text']['2nic'] = 'This solution uses an ARM template to launch a 2-NIC deployment of a cloud-focused BIG-IP VE in Microsoft Azure.  In a 2-NIC implementation, one interface is for management and one is for data-plane traffic, each with a unique public/private IP. This is a variation of the 3-NIC template without the NIC for connecting directly to backend webservers.'
    readme_text['intro_text']['3nic'] = 'This solution uses an ARM template to launch a three NIC deployment of a cloud-focused BIG-IP VE in a new networking stack in Microsoft Azure. Traffic flows from the BIG-IP VE to the application servers. This is the standard "on-premise like" cloud design where the compute instance of F5 is running with a management, front-end application traffic(Virtual Server) and back-end application interface.'
    readme_text['intro_text']['cluster_base'] = 'This solution uses an ARM template to launch a single NIC deployment of a cloud-focused BIG-IP VE in Microsoft Azure. Traffic flows from the BIG-IP VE to the application servers. This is the standard Cloud design where the compute instance of F5 is running with a single interface, where both management and data plane traffic is processed.  This is a traditional model in the cloud where the deployment is considered one-armed.'
    readme_text['intro_text']['ha-avset'] = 'This solution uses an ARM template to launch a two BIG-IP VEs in an Active/Standby configuration with network failover enabled in a new stack. Each pair of BIG-IP VEs is deployed in an Azure Availability Set, and can therefore be spread across different update and fault domains. Each BIG-IP VE has 3 network interfaces (NICs), one for management, one for external traffic, and one for internal traffic.\n\nTraffic flows from the BIG-IP VE to the application servers. This is the standard "on-premise-like" cloud design where the compute instance of F5 is running with a management interface, a front-end application traffic (Virtual Server) interface, and back-end application interface.  This template is a result of Azure now supporting multiple public IP addresses to multiple private IP addresses per NIC.  This template also has the ability to create specify additional Public/Private IP addresses for the external "application" NIC to be used for passing traffic to virtual servers in a more traditional fashion. In the event the active BIG-IP VE become unavailable, traffic seamlessly shifts to the standby BIG-IP VE using network failover.'
    readme_text['intro_text']['ltm_autoscale'] = 'This solution uses an ARM template to launch the deployment of F5 BIG-IP Local Traffic Manager (LTM) Virtual Edition (VE) instances in a Microsoft Azure VM Scale Set that is configured for auto scaling. Traffic flows from the Azure load balancer to the BIG-IP VE (cluster) and then to the application servers. The BIG-IP VE(s) are configured in single-NIC mode. As traffic increases or decreases, the number of BIG-IP VE LTM instances automatically increases or decreases accordingly.  Scaling thresholds are currently based on *network out* throughput. This solution is for BIG-IP LTM only.'
    readme_text['intro_text']['waf_autoscale'] = 'This solution uses an ARM template to launch the deployment of F5 BIG-IP LTM+ASM Virtual Edition (VE) instances in a Microsoft Azure VM Scale Set that is configured for auto scaling. Traffic flows from the Azure load balancer to the BIG-IP VE (cluster) and then to the application servers. The BIG-IP VE(s) are configured in single-NIC mode. As traffic increases or decreases, the number of BIG-IP VE LTM instances automatically increases or decreases accordingly.  Scaling thresholds are currently based on *network out* throughput. This solution is for BIG-IP LTM+ASM.'
    ## Help Text ##
    readme_text['help_text']['supported'] = 'Because this template has been created and fully tested by F5 Networks, it is fully supported by F5. This means you can get assistance if necessary from F5 Technical Support.'
    readme_text['help_text']['experimental'] = 'While this template has been created by F5 Networks, it is in the experimental directory and therefore has not completed full testing and is subject to change.  F5 Networks does not offer technical support for templates in the experimental directory. For supported templates, see the templates in the **supported** directory.'
    ## Deploy Buttons ##
    readme_text['deploy_links']['version_tag'] = f5_networks_tag
    readme_text['deploy_links']['lic_support'] = {'1nic': 'Both', '2nic': 'Both', '3nic': 'Both', 'cluster_base': 'Both', 'ha-avset': 'Both', 'ltm_autoscale': 'PAYG', 'waf_autoscale': 'PAYG' }
    ## Example Scripts - These are set above, just adding to README ##
    readme_text['bash_script'] = bash_script
    readme_text['ps_script'] = ps_script
    ## Configuration Example Text ##
    readme_text['config_example_text']['1nic'] = 'In this scenario, all access to the BIG-IP VE appliance is through the same IP address and virtual network interface (vNIC).  This interface processes both management and data plane traffic.'
    readme_text['config_example_text']['2nic'] = 'In this scneario, one NIC is for management and one NIC is for external traffic.  This is a more traditional BIG-IP deployment model where data-plane and management traffic is separate. The IP addresses in this example may be different in your implementation.'
    readme_text['config_example_text']['3nic'] = 'In this scneario, one NIC is for management, one NIC is for external traffic and one NIC is for internal traffic.  This is the traditional BIG-IP deployment model where data-plane, management and internal traffic is separate. The IP addresses in this example may be different in your implementation.'
    readme_text['config_example_text']['cluster_base'] = 'In this scenario, all access to the BIG-IP VE cluster is through an ALB. The IP addresses in this example may be different in your implementation.'
    readme_text['config_example_text']['ha-avset'] = 'In this scneario, one NIC is for management, one NIC is for external traffic and one NIC is for internal traffic.  This is the traditional BIG-IP deployment model where data-plane, management and internal traffic is separate. The IP addresses in this example may be different in your implementation.'
    readme_text['config_example_text']['ltm_autoscale'] = 'In this scenario, all access to the BIG-IP VE appliance is through an Azure Load Balancer. The Azure Load Balancer processes both management and data plane traffic into the BIG-IP VEs, which then distribute the traffic to web/application servers according to normal F5 patterns.'
    readme_text['config_example_text']['waf_autoscale'] = 'In this scenario, all access to the BIG-IP VE appliance is through an Azure Load Balancer. The Azure Load Balancer processes both management and data plane traffic into the BIG-IP VEs, which then distribute the traffic to web/application servers according to normal F5 patterns.'

    ## Call function to create/update README
    readme_generator.readme_creation(template_name, data, license_text, readme_text, script_location, created_file)
######################################## END Create/Modify README's ########################################