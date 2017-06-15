#/usr/bin/python env
import sys
import os
import re

# Create Functions for README creation
def sp_needed(data):
    """ Check if the service principal parameters exist, will add that blob in README if true """
    for parameter in data['parameters']:
        if 'servicePrincipalSecret' in parameter:
            return True
    return False

def misc_readme_grep(tag, file):
    """ Pull in any additional items that exist in the misc README file, based on <TAG> """
    with open(file, 'r') as file_str:
        text = file_str.read()
    reg_ex = tag + '{{' + r"(.*?)}}"
    tag_text = re.findall(reg_ex, text, re.DOTALL)
    return "".join(tag_text)

def md_param_array(data, license_params):
    """ Create README example paramaters: | adminUsername | Yes | Description | """
    param_array = ""
    license_flag = True
    for parameter in data['parameters']:
        mandatory = 'Yes'
        # Specify optional parameters that README, need to pull in all license options
        if 'license' in parameter:
            mandatory = 'No'
            if license_flag:
                license_flag = False
                for key in license_params:
                    param_array += "| " + key + " | " + mandatory + " | " + license_params[key] + " |\n"
        else:
            param_array += "| " + parameter + " | " + mandatory + " | " + data['parameters'][parameter]['metadata']['description'] + " |\n"
    return param_array

def md_version_map(data, readme_text):
    """ Create BIG-IP version map: | Azure BIG-IP Image Version | BIG-IP Version | """
    param_array = ""
    for version in data['parameters']['bigIpVersion']['allowedValues']:
        param_array += "| " + version + " | " + readme_text['license_map'][version] + " |\n"
    return param_array

def create_deploy_links(version_tag, lic_type, template_location):
    """ Create deploy to Azure buttons/links """
    deploy_links = ''
    base_url = 'https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2F' + version_tag
    if 'Both' in lic_type:
        lic_list = ['BYOL', 'PAYG']
    else:
        lic_list = [lic_type]
    for lic in lic_list:
        deploy_links += '''   - **<LIC_TYPE>** <br><a href="<DEPLOY_LINK_URL>">\n    <img src="http://azuredeploy.net/deploybutton.png"/></a><br><br>\n\n'''
        template_location = template_location.replace('/', '%2F')
        template_location = template_location.replace('..', '')
        url = base_url + template_location
        deploy_links = deploy_links.replace('<DEPLOY_LINK_URL>', url)
        deploy_links = deploy_links.replace('<LIC_TYPE>', lic)
    return deploy_links

def readme_creation(template_name, data, license_params, readme_text, readme_location, template_location):
    """ Main proc to create readme """
    folder_loc = 'readme_files/'
    base_readme = folder_loc + 'base.README.md'
    misc_readme = folder_loc + 'misc.README.txt'
    final_readme = readme_location + 'README.md'
    with open(base_readme, 'r') as readme:
        readme = readme.read()
    scale_text = ''; sp_text = ''

    ##### Text Values for README templates #####
    title_text = readme_text['title_text'][template_name]
    intro_text = readme_text['intro_text'][template_name]
    if 'supported' in readme_location:
        help_text = readme_text['help_text']['supported']
    else:
        help_text = readme_text['help_text']['experimental']
    version_map = md_version_map(data, readme_text)
    deploy_links = create_deploy_links(readme_text['deploy_links']['version_tag'], readme_text['deploy_links']['lic_support'][template_name], template_location)
    bash_script = readme_text['bash_script']
    ps_script = readme_text['ps_script']
    readme_text = readme_text['config_example_text'][template_name]

    # Check for optional readme items
    if 'autoscale' in template_name:
        scale_text = misc_readme_grep('<AUTOSCALE_TXT>', misc_readme)
    if sp_needed(data):
        sp_text = misc_readme_grep('<SERVICE_PRINCIPAL_TXT>', misc_readme)

    # Map in dynamic values
    readme = readme.replace('<TITLE_TXT>', title_text)
    readme = readme.replace('<INTRO_TXT>', intro_text)
    readme = readme.replace('<VERSION_MAP_TXT>', version_map)
    readme = readme.replace('<HELP_TXT>', help_text)
    readme = readme.replace('<DEPLOY_LINKS>', deploy_links)
    readme = readme.replace('<EXAMPLE_PARAMS>', md_param_array(data, license_params))
    readme = readme.replace('<PS_SCRIPT>', ps_script)
    readme = readme.replace('<BASH_SCRIPT>', bash_script)
    readme = readme.replace('<EXAMPLE_TEXT>', readme_text)
    readme = readme.replace('<AUTOSCALE_TEXT>', scale_text)
    readme = readme.replace('<SERVICE_PRINCIPAL>', sp_text)

    # Write to solution location
    with open(final_readme, 'w') as readme_complete:
        readme_complete.write(readme)
    ## End README creation Function
    return 'README Created for ' + template_name