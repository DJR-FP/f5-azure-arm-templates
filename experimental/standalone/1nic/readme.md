# Deploying the BIG-IP VE in Azure - Single NIC

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction

This solution uses an ARM template to launch a single NIC deployment of a cloud-focused BIG-IP VE in Microsoft Azure. Traffic flows from the BIG-IP VE to the application servers. This is the standard Cloud design where the compute instance of
F5 is running with a single interface, where both management and data plane traffic is processed.  This is a traditional model in the cloud where the deployment is considered one-armed.

See the **[Configuration Example](#config)** section for a configuration diagram and description for this solution, as well as an important note about optionally changing the BIG-IP Management port.

## Supported instance types and hypervisors
  - For a list of supported Azure instance types for this solutions, see the **Azure instances for BIG-IP VE** section of https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0/1.html#guid-71265d82-3a1a-43d2-bae5-892c184cc59b

  - For a list versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and Microsoft Azure, see https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html.

### Help 
We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 ARM templates.  This channel is typically monitored Monday-Friday 9-5 PST by F5 employees who will offer best-effort support.
While this template has been created by F5 Networks, it is in the experimental directory and therefore has not completed full testing and is subject to change.  F5 Networks does not offer technical support for templates in the experimental directory. For supported templates, see the templates in the supported directory.


## Installation

You have three options for deploying this template:
  - Using the Azure deploy button
  - Using [PowerShell](#powershell)
  - Using [CLI Tools](#cli)

### <a name="azure"></a>Azure deploy button

Use this button to deploy the template:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fexperimental%2Fstandalone%2F1nic%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>

### Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| adminUsername | x | A user name to login to the BIG-IPs.  The default value is "azureuser". |
| adminPassword | x | A strong password for the BIG-IPs. Remember this password; you will need it later. |
| dnsLabel | x | Unique DNS Name for the public IP address used to access the BIG-IPs for management. |
| instanceName | x | The hostname to be configured for the VM. |
| instanceType | x | The desired Azure Virtual Machine instance size. |
| imageName | x | The desired F5 image to deploy. |
| licenseKey1 | x | The license token from the F5 licensing server. This license will be used for the first F5 BIG-IP. |
| restrictedSrcAddress | x | Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources. |
| tagValues | x | Additional key-value pair tags to be added to each Azure resource. |

### <a name="powershell"></a>PowerShell Script Example

```powershell
    # Params below match to parameters in the azuredeploy.json that are gen-unique, otherwise pointing to
    # the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
    # can be supplied inline when running this script but if they arent then the default will be used as specified in below param arguments
    # Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword yourpassword -dnsLabel f51nicdeploy01 -instanceName f51nic -licenseKey1 XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -resourceGroupName f51nicdeploy01 -EmailTo user@f5.com

    param(
    [Parameter(Mandatory=$True)]
    [string]
    $adminUsername,

    [Parameter(Mandatory=$True)]
    [string]
    $adminPassword,

    [Parameter(Mandatory=$True)]
    [string]
    $dnsLabel,

    [Parameter(Mandatory=$True)]
    [string]
    $instanceName,

    [string]
    $instanceType = "Standard_D2_v2",

    [string]
    $imageName = "Best",

    [Parameter(Mandatory=$True)]
    [string]
    $licenseKey1,

    [string]
    $restrictedSrcAddress  = "*",

    [Parameter(Mandatory=$True)]
    [string]
    $resourceGroupName,

    [string]
    $region = "West US",

    [string]
    $templateFilePath = "azuredeploy.json",

    [string]
    $parametersFilePath = "azuredeploy.parameters.json"
    )

    Write-Host "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged." -foregroundcolor green
    Start-Sleep -s 3

    # Connect to Azure, right now it is only interactive login
    try {
        Write-Host "Checking if already logged in!"
        Get-AzureRmSubscription | Out-Null
        Write-Host "Already logged in, continuing..."
        }
        Catch {
        Write-Host "Not logged in, please login..."
        Login-AzureRmAccount
        }

    # Create Resource Group for ARM Deployment
    New-AzureRmResourceGroup -Name $resourceGroupName -Location "$region"

    # Create Arm Deployment
    $pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceName "$instanceName" -instanceType "$instanceType" -licenseKey1 "$licenseKey1" -restrictedSrcAddress "$restrictedSrcAddress" -imageName "$imageName"

    # Print Output of Deployment to Console
    $deployment
```

=======

### <a name="cli"></a>Azure CLI(1.0) Script Example

```bash
    #!/bin/bash

    # Bash Script to deploy an ARM template into Azure, using azure cli 1.0
    # Example Command: ./deploy_via_bash.sh --adminusr azureuser --adminpwd 'yourpassword' --dnslabel f5dnslabel --instname f5vm01 --key1 XXXXX-XXXXX-XXXXX-XXXXX-XXXXX --rgname f5rgname --azureusr administrator@domain.com --azurepwd 'yourpassword'

    # Assign Script Parameters and Define Variables
    # Specify static items, change these as needed or make them parameters (instance_type is already an optional parameter)
    region="westus"
    template_file="azuredeploy.json"
    parameter_file="azuredeploy.parameters.json"
    instance_type="Standard_D2_v2"
    image_name="Best"
    restricted_source_address="*"
    tag_values="{\"application\":\"APP\",\"environment\":\"ENV\",\"group\":\"GROUP\",\"owner\":\"OWNER\",\"cost\":\"COST\"}"

    ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k: --long adminusr:,adminpwd:,dnslabel:,instname:,insttype:,imgname:,key1:,rstsrcaddr:,rgname:,azureusr:,azurepwd: -n $0 -- "$@"`
    eval set -- "$ARGS"


    # Parse the command line arguments, primarily checking full params as short params are just placeholders
    while true; do
        case "$1" in
            -a|--adminusr)
                admin_username=$2
                shift 2;;
            -b|--adminpwd)
                admin_password=$2
                shift 2;;
            -c|--dnslabel)
                dns_label=$2
                shift 2;;
            -d|--instname)
                instance_name=$2
                shift 2;;
            -e|--insttype)
                instance_type=$2
                shift 2;;
            -f|--imgname)
                image_name=$2
                shift 2;;
            -g|--key1)
                license_key_1=$2
                shift 2;;
            -h|--rstsrcaddr)
                restricted_source_address=$2
                shift 2;;
            -i|--rgname)
                resource_group_name=$2
                shift 2;;
            -j|--azureusr)
                azure_user=$2
                shift 2;;
            -k|--azurepwd)
                azure_pwd=$2
                shift 2;;
            --)
                shift
                break;;
        esac
    done

    echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
    sleep 3

    #If a required parameter is not passed, the script will prompt for it below
    required_variables="admin_username admin_password dns_label instance_name license_key_1 resource_group_name azure_user azure_pwd"
    for variable in $required_variables
            do
            if [ -v ${!variable} ] ; then
                    read -p "Please enter value for $variable:" $variable
            fi
    done

    # Login to Azure, for simplicity in this example using username and password supplied as script arguments --azureusr and --azurepwd
    # Perform Check to see if already logged in
    azure account show > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
            azure login -u $azure_user -p $azure_pwd
    fi

    # Switch to ARM mode
    azure config mode arm

    # Create ARM Group
    azure group create -n $resource_group_name -l $region

    # Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
    # such as can been done with Powershell...oh well!
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceType\":{\"value\":\"$instance_type\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"imageName\":{\"value\":\"$image_name\"},\"restrictedSrcAddress\":{\"value\":\"$restricted_source_address\"},\"tagValues\":{\"value\":$tag_values}}"

```

## Configuration Example <a name="config">

The following is a simple configuration diagram for this single NIC deployment. In this scenario, all access to the BIG-IP VE appliance is through the same IP address and virtual network interface (vNIC).  This interface processes both management and data plane traffic.

![Single NIC configuration example](images/azure-1nic-sm.png)

### Changing the BIG-IP Configuration Utility (GUI) port
The Management port shown in the example diagram is **443**, however you can alternatively use **8443** in your configuration if you need to use port 443 for application traffic.  To change the Management port, see [Changing the Configuration utility port](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-0-0/2.html#GUID-3E6920CD-A8CD-456C-AC40-33469DA6922E) for instructions.  
***Important***: If you perform the procedure to change the port, you must check the Azure Network Security Group associated with the interface on the BIG-IP that was deployed and adjust the ports accordingly. 

## Documentation

The ***BIG-IP Virtual Edition and Microsoft Azure: Setup*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0.html) decribes how to create the configuration manually without using the ARM template.

## Deploying Custom Configuration to an Azure Virtual Machine 

This sample code uses the CustomScript extension resource to configure the f5.ip_forwarding iApp on BIG-IP VE in Azure Resource Manager. 

The CustomScript extension resource name must reference the Azure virtual machine name and must have a dependency on that virtual machine. You can use only one CustomScript extension resource per virtual machine; however, you can combine multiple semicolon-delimited commands in a single extension resource definition.

Warning: F5 does not support the template if you change anything other than the CustomScript extension resource.

```
{
     "type": "Microsoft.Compute/virtualMachines/extensions",
     "name": "[concat(variables('virtualMachineName'),'/start')]",
     "apiVersion": "2016-03-30",
     "location": "[resourceGroup().location] "
     "dependsOn": [
          "[concat('Microsoft.Compute/virtualMachines/',variables('virtualMachineName'))]"
     ],
     "properties": {
          "publisher": "Microsoft.Azure.Extensions",
          "type": "CustomScript",
          "typeHandlerVersion": "2.0",
          "settings": {
          },
          "protectedSettings": {
               "commandToExecute": "[concat('tmsh create sys application service my_deployment { device-group none template f5.ip_forwarding traffic-group none variables replace-all-with { basic__addr { value 0.0.0.0 } basic__forward_all { value No } basic__mask { value 0.0.0.0 } basic__port { value 0 } basic__vlan_listening { value default } options__advanced { value no }options__display_help { value hide } } }')]"
          }
     }
}
```


## Design Patterns


The goal is for the design patterns for all the iterative examples of F5 being deployed via ARM templates to closely match as much as possible.

### List of Patterns For Contributing Developers


 1. Still working on patterns to use

## Filing Issues

See the Issues section of `Contributing <CONTRIBUTING.md>`__.

## Contributing

See `Contributing <CONTRIBUTING.md>`__

## Test


Before you open a pull request, your code must have passed a deployment into Azure with the intended result

## Unit Tests

Simply deploying the ARM template and completing use case fulfills a functional test



## Copyright

Copyright 2014-2017 F5 Networks Inc.


## License


Apache V2.0
~~~~~~~~~~~
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Individuals or business entities who contribute to this project must have
completed and submitted the `F5 Contributor License Agreement`