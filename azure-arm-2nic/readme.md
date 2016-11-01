**f5-azure-arm-2nic**
================

Introduction
------------

This solution implements an ARM Template to deploy a base example of F5 in a 2 nic deployment.  This allows interface #1 to be used for mgmt and data-plane traffic from the internet,
then interface #2 is connected into the Azure networks where traffic will be processed by the pool members in a traditional 2 arm design.

Documentation
-------------
Please see the project documentation - This is still being created

Installation
------------

Deploy via Azure deploy button below, Powershell or via CLI Tools

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsevedge%2F2nic%2Fmaster%2Fazure-arm-2nic%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>


Powershell Usage
-----
    # Params below match to parameteres in the azuredeploy.json that are gen-unique, otherwsie pointing to
    # the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
    # can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
    # Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword yourpassword -dnsLabel f52nicdeploy01 -instanceName f52nic -licenseKey1 XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -resourceGroupName f52nicdeploy01 -EmailTo user@f5.com

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
    $instanceSize = "Standard_D2_v2",

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
    $parametersFilePath = "azuredeploy.parameters.json",

    [Parameter(Mandatory=$True)]
    [string]
    $EmailTo
    )

    # Connect to Azure, right now it is only interactive login
    Login-AzureRmAccount

    # Create Resource Group for ARM Deployment
    New-AzureRmResourceGroup -Name $resourceGroupName -Location "$region"

    # Create Arm Deployment
    $pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceName "$instanceName" -instanceSize "$instanceSize" -licenseKey1 "$licenseKey1" -restrictedSrcAddress "$restrictedSrcAddress"

    # Print Output of Deployment to Console
    $deployment


Azure CLI(1.0) Usage
-----
    #!/bin/bash

    # Script to deploy 1nic/2nic ARM template into Azure, using azure cli 1.0
    # Example Command: ./deploy_via_bash.sh -u azureuser -p 'yourpassword' -d f52nicdeploy01 -n f52nic -l XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -r f52nicdeploy01 -y adminstrator@domain.com -z 'yourpassword'

    # Assign Script Paramters and Define Variables
    # Specify static items, change these as needed or make them parameters (vm_size is already an optional paramter)
    region="westus"
    template_file="azuredeploy.json"
    parameter_file="azuredeploy.parameters.json"
    vm_size="Standard_D2_v2"

    while getopts u:p:d:n:s:l:r:y:z: option
    do	case "$option"  in
            u) admin_username=$OPTARG;;
            p) admin_password=$OPTARG;;
            d) dns_label_prefix=$OPTARG;;
            n) vm_name=$OPTARG;;
            s) vm_size=$OPTARG;;
            l) license_token=$OPTARG;;
            r) resource_group_name=$OPTARG;;
            y) azure_user=$OPTARG;;
            z) azure_pwd=$OPTARG;;
        esac
    done
    # Check for Mandatory Args
    if [ ! "$admin_username" ] || [ ! "$admin_password" ] || [ ! "$dns_label_prefix" ] || [ ! "$vm_name" ] || [ ! "$license_token" ] || [ ! "$resource_group_name" ] || [ ! "$azure_user" ] || [ ! "$azure_pwd" ]
    then
        echo "One of the mandatory parameters was not specified!"
        exit 1
    fi


    # Login to Azure, for simplicity in this example using username and password as supplied as script arguments y and z
    azure login -u $azure_user -p $azure_pwd

    # Switch to ARM mode
    azure config mode arm

    # Create ARM Group
    azure group create -n $resource_group_name -l $region

    # Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
    # such as can been done with Powershell...oh well!
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabelPrefix\":{\"value\":\"$dns_label_prefix\"},\"vmName\":{\"value\":\"$vm_name\"},\"vmSize\":{\"value\":\"$vm_size\"},\"licenseToken1\":{\"value\":\"$license_token\"}}"



Design Patterns
------------
----------

The goal is for the design patterns for all the iterative examples of F5 being deployed via ARM templates to closely match as much as possible.

List of Patterns For Contributing Developers
--------------------------------------------
----------


 1. Still working on patterns to use

Filing Issues
-------------
----------


See the Issues section of `Contributing <CONTRIBUTING.md>`__.

Contributing
------------
----------


See `Contributing <CONTRIBUTING.md>`__

Test
----
----------

Before you open a pull request, your code must have passed a deployment into Azure with the intended result

Unit Tests
----
----------
Simply deploying the ARM template and completing use case fullfils a functional test



Copyright
---------
Copyright 2014-2016 F5 Networks Inc.


License
-------

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