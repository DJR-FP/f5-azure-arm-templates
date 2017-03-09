# Deploying a BIG-IP VE ConfigSync Cluster in Azure - Single NIC
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
## Introduction

This ARM template deploys a cluster of F5 BIG-IP VEs that ensures you have the highest level of availability for your applications. You can also enable F5's L4/L7 security features, access control, and intelligent traffic management.

When you deploy your applications using a cluster of F5 BIG-IPs, the BIG-IP VE instances are all in Active status (not Active-Standby), and are used as a single device for redundancy and scalability, rather than failover. If one device goes down, Azure keeps load balancing to the other.

Using this solution, the F5 BIG-IP VEs are fully configured in front of your application.  When complete, the BIG-IPs pass traffic through the newly created Azure Public IP.  After acceptance testing, you must complete the configuration by changing the DNS entry for your application to point at the newly created public IP address, and then lock down the Network Security Group rules to prevent any traffic from reaching your application except through the F5 BIG-IPs.

Before you deploy web applications with an F5 BIG-IP VE, you need a license from F5.

See the **[Configuration Example](#config)** section for a configuration diagram and description for this solution.

## Supported instance types and hypervisors
  - For a list of supported Azure instance types for this solutions, see the **Azure instances for BIG-IP VE** section of https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0/1.html#guid-71265d82-3a1a-43d2-bae5-892c184cc59b

  - For a list versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and Microsoft Azure, see https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html.

### Help
We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 ARM templates.  This channel is typically monitored Monday-Friday 9-5 PST by F5 employees who will offer best-effort support.<br>
While this template has been created by F5 Networks, it is in the experimental directory and therefore has not completed full testing and is subject to change.  F5 Networks does not offer technical support for templates in the experimental directory. For supported templates, see the templates in the **supported** directory.

## Installation

You have three options for deploying this template:
  - Using the Azure deploy button
  - Using [PowerShell](#powershell)
  - Using [CLI Tools](#cli)

### <a name="azure"></a>Azure deploy button

Use the following button to deploy the template.  See the Template parameters section to see the information you need to succesfully deploy the template.

**BASE (No application)**<br>
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fmaster%2Fexperimental%2Fcluster%2F1nic%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>

## Template parameters

| Parameter | Required | Description |
| --- | --- | --- |
| deploymentName | x | A unique name for your application. |
| numberOfInstances | x | The number of BIG-IPs that will be deployed in front of your application.  The only allowed value for this template is 2. |
| instanceType | x | The desired Azure Virtual Machine instance size. |
| imageName | x | The desired F5 image to deploy. |
| adminUsername | x | A user name to login to the BIG-IPs.  The default value is "azureuser". |
| adminPassword | x | A strong password for the BIG-IPs. Remember this password; you will need it later. |
| dnsLabel | x | Unique DNS name for the public IP address used to access the BIG-IPs for management (alphanumeric characters only). |
| bigIpVersion | x | F5 BIG-IP Version to use. |
| licenseKey1 | | The license token from the F5 licensing server. This license will be used for the first F5 BIG-IP. |
| licenseKey2 | x | The license token from the F5 licensing server. This license will be used for the second F5 BIG-IP. |
| licensedBandwidth | | PAYG licensed bandwidth(Mbps) image to deploy. |
| restrictedSrcAddress | x | Restricts management access to a specific network or address. Enter a IP address or address range in CIDR notation, or asterisk for all sources. |
| tagValues | x | Additional key-value pair tags to be added to each Azure resource. |



### <a name="powershell"></a>PowerShell Script Example

```powershell
    ## Script parameters being asked for below match to parameters in the azuredeploy.json file, otherwise pointing to the ##
    ## azuredeploy.parameters.json file for values to use.  Some options below are mandatory, some(such as region) can     ##
    ## be supplied inline when running this script but if they aren't then the default will be used as specificed below.   ##
    ## Example Command: .\Deploy_via_PS.ps1 -licenseType PAYG -licensedBandwidth 200m -numberOfInstances 2 -adminUsername azureuser -adminPassword <value> -dnsLabel <value> -instanceType Standard_D2_v2 -imageName Good -bigIpVersion 13.0.000 -restrictedSrcAddress "*"-resourceGroupName <value>

    param(

    [Parameter(Mandatory=$True)]
    [string]
    $licenseType,

    [string]
    $licensedBandwidth = $(if($licenseType -eq "PAYG") { Read-Host -prompt "licensedBandwidth"}),

    [string]
    $licenseKey1 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey1"}),

    [string]
    $licenseKey2 = $(if($licenseType -eq "BYOL") { Read-Host -prompt "licenseKey2"}),

    [Parameter(Mandatory=$True)]
    [string]
    $numberOfInstances,

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
    $instanceType,

    [Parameter(Mandatory=$True)]
    [string]
    $imageName,

    [Parameter(Mandatory=$True)]
    [string]
    $bigIpVersion,

    [string]
    $restrictedSrcAddress = "*",

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
    if ($licenseType -eq "BYOL") {
    if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\BYOL\azuredeploy.json"; $parametersFilePath = ".\BYOL\azuredeploy.parameters.json" }
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -numberOfInstances "$numberOfInstances" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceType "$instanceType" -imageName "$imageName" -bigIpVersion "$bigIpVersion" -restrictedSrcAddress "$restrictedSrcAddress"  -licenseKey1 "$licenseKey1" -licenseKey2 "$licenseKey2"
    } elseif ($licenseType -eq "PAYG") {
    if ($templateFilePath -eq "azuredeploy.json") { $templateFilePath = ".\PAYG\azuredeploy.json"; $parametersFilePath = ".\PAYG\azuredeploy.parameters.json" }
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -numberOfInstances "$numberOfInstances" -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceType "$instanceType" -imageName "$imageName" -bigIpVersion "$bigIpVersion" -restrictedSrcAddress "$restrictedSrcAddress"  -licensedBandwidth "$licensedBandwidth"
    } else {
    Write-Error -Message "Uh oh, something went wrong!  Please select valid license type of PAYG or BYOL."
    }

    # Print Output of Deployment to Console
    $deployment
```


### <a name="cli"></a>Azure CLI(1.0) Script Example

```bash
    #!/bin/bash

    ## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
    ## Example Command: ./deploy_via_bash.sh --licenseType PAYG --licensedBandwidth 200m --numberOfInstances 2 --adminUsername azureuser --adminPassword <value> --dnsLabel <value> --instanceType Standard_D2_v2 --imageName Good --bigIpVersion 13.0.000 --restrictedSrcAddress "*" --resourceGroupName <value> --azureLoginUser <value> --azureLoginPassword <value>

    # Assign Script Paramters and Define Variables
    # Specify static items, change these as needed or make them parameters
    region="westus"
    restrictedSrcAddress="*"
    tagValues='{"application":"APP","environment":"ENV","group":"GROUP","owner":"OWNER","cost":"COST"}'

    ARGS=`getopt -o a:b:c:d:e:f:g:h:i:j:k:l:m:n:o: --long resourceGroupName:,azureLoginUser:,azureLoginPassword:,licenseType:,licensedBandwidth:,licenseKey1:,licenseKey2:,numberOfInstances:,adminUsername:,adminPassword:,dnsLabel:,instanceType:,imageName:,bigIpVersion:,restrictedSrcAddress: -n $0 -- "$@"`
    eval set -- "$ARGS"

    # Parse the command line arguments, primarily checking full params as short params are just placeholders
    while true; do
        case "$1" in
            -a|--resourceGroupName)
                resourceGroupName=$2
                shift 2;;
            -b|--azureLoginUser)
                azureLoginUser=$2
                shift 2;;
            -c|--azureLoginPassword)
                azureLoginPassword=$2
                shift 2;;
            -d|--licenseType)
                licenseType=$2
                shift 2;;
            -e|--licensedBandwidth)
                licensedBandwidth=$2
                shift 2;;
            -f|--licenseKey1)
                licenseKey1=$2
                shift 2;;
            -g|--licenseKey2)
                licenseKey2=$2
                shift 2;;
            -h|--numberOfInstances)
                numberOfInstances=$2
                shift 2;;
            -i|--adminUsername)
                adminUsername=$2
                shift 2;;
            -j|--adminPassword)
                adminPassword=$2
                shift 2;;
            -k|--dnsLabel)
                dnsLabel=$2
                shift 2;;
            -l|--instanceType)
                instanceType=$2
                shift 2;;
            -m|--imageName)
                imageName=$2
                shift 2;;
            -n|--bigIpVersion)
                bigIpVersion=$2
                shift 2;;
            -o|--restrictedSrcAddress)
                restrictedSrcAddress=$2
                shift 2;;
            --)
                shift
                break;;
        esac
    done

    #If a required paramater is not passed, the script will prompt for it below
    required_variables="numberOfInstances adminUsername adminPassword dnsLabel instanceType imageName bigIpVersion resourceGroupName licenseType "
    for variable in $required_variables
            do
            if [ -v ${!variable} ] ; then
                    read -p "Please enter value for $variable:" $variable
            fi
    done

    # Prompt for license key if not supplied and BYOL is selected
    if [ $licenseType == "BYOL" ]; then
        if [ -v $licenseKey1 ] ; then
                read -p "Please enter value for licenseKey1:" licenseKey1
        fi
        if [ -v $licenseKey2 ] ; then
                read -p "Please enter value for licenseKey2:" licenseKey2
        fi
        template_file="./BYOL/azuredeploy.json"
        parameter_file="./BYOL/azuredeploy.parameters.json"
    fi
    # Prompt for licensed bandwidth if not supplied and PAYG is selected
    if [ $licenseType == "PAYG" ]; then
        if [ -v $licensedBandwidth ] ; then
                read -p "Please enter value for licensedBandwidth:" licensedBandwidth
        fi
        template_file="./PAYG/azuredeploy.json"
        parameter_file="./PAYG/azuredeploy.parameters.json"
    fi

    echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
    sleep 3

    # Login to Azure, for simplicity in this example using username and password supplied as script arguments --azureLoginUser and --azureLoginPassword
    # Perform Check to see if already logged in
    azure account show > /dev/null 2>&1
    if [[ $? != 0 ]] ; then
            azure login -u $azureLoginUser -p $azureLoginPassword
    fi

    # Switch to ARM mode
    azure config mode arm

    # Create ARM Group
    azure group create -n $resourceGroupName -l $region

    # Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
    # such as can been done with Powershell...oh well!
    if [ $licenseType == "BYOL" ]; then
        azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"numberOfInstances\":{\"value\":\"$numberOfInstances\"},\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"licenseKey1\":{\"value\":\"$licenseKey1\"},\"licenseKey2\":{\"value\":\"$licenseKey2\"}}"
    elif [ $licenseType == "PAYG" ]; then
        azure group deployment create -f $template_file -g $resourceGroupName -n $resourceGroupName -p "{\"numberOfInstances\":{\"value\":\"$numberOfInstances\"},\"adminUsername\":{\"value\":\"$adminUsername\"},\"adminPassword\":{\"value\":\"$adminPassword\"},\"dnsLabel\":{\"value\":\"$dnsLabel\"},\"instanceType\":{\"value\":\"$instanceType\"},\"imageName\":{\"value\":\"$imageName\"},\"bigIpVersion\":{\"value\":\"$bigIpVersion\"},\"restrictedSrcAddress\":{\"value\":\"$restrictedSrcAddress\"},\"tagValues\":{\"value\":$tagValues},\"licensedBandwidth\":{\"value\":\"$licensedBandwidth\"}}"
    else
        echo "Uh oh, shouldn't make it here! Ensure license type is either PAYG or BYOL"
        exit 1
    fi

```

## Results

This template creates a new resource group. Inside this new resource group it configures the following:

* Availability Set
* Azure Load Balancer
* Network Security Group
* Storage Account
* Public IP Address
* Network Interface objects for the F5 devices
* F5 Virtual Machines

## Connecting to the management interface of the BIG-IP VEs

After the deployment successfully finishes, you can find the BIG-IP Management UI\SSH URLs by doing the following:

* Find the Resource Group that deployed, which is the same name as the "dnsLabel".  When you click this object you see the deployment status.
* Click the Deployment Status, and then the Deployment.
* In the "Outputs" area, you find the URLs and ports you can use to connect to the F5 cluster.

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

## Configuration Example <a name="config">

The following is a simple configuration diagram for this deployment. In this diagram, the IP addresses are provided as examples.
![2-NIC configuration example](images/azure-cluster-1nic.png)

### Documentation
The ***BIG-IP Virtual Edition and Microsoft Azure: Setup*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-0-0/3.html) details how to create the configuration manually without using the ARM template.  This product manual also describes the F5 and Azure configuration in more detail.

## Design Patterns

The goal is for the design patterns for all the iterative examples of F5 being deployed via ARM templates to closely match as much as possible.


### List of Patterns For Contributing Developers

 1. Still working on patterns to use


## Filing Issues

See the Issues section of `Contributing <CONTRIBUTING.md>`__.


## Contributing

See `Contributing <CONTRIBUTING.md>`__


## Test

Before you open a pull request, your code must have passed a deployment into Azure with the intended result.


## Unit Tests

Simply deploying the ARM template and completing use case fulfills a functional test.


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