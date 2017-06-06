#/bin/bash

############################### Experimental ###############################
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic)
template_list="1nic 2nic 3nic"
stack_list="new_stack existing_stack"
for tmpl in $template_list; do
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type PAYG --stack-type $stack_type --template-location "../experimental/standalone/$tmpl/$stack_type/PAYG/" --script-location "../experimental/standalone/$tmpl/$stack_type/"
        python -B '.\master_template.py' --template-name $tmpl --license-type BYOL --stack-type $stack_type --template-location "../experimental/standalone/$tmpl/$stack_type/BYOL/" --script-location "../experimental/standalone/$tmpl/$stack_type/"
    done
done

## BIGIP ARM Templates - Cluster (base)
python -B '.\master_template.py' --template-name cluster_base --license-type PAYG --template-location '../experimental/cluster/1nic/PAYG/' --script-location '../experimental/cluster/1nic/'
python -B '.\master_template.py' --template-name cluster_base --license-type BYOL --template-location '../experimental/cluster/1nic/BYOL/' --script-location '../experimental/cluster/1nic/'

## BIGIP ARM Template - LTM AutoScale
python -B '.\master_template.py' --template-name ltm_autoscale --license-type PAYG --template-location '../experimental/solutions/autoscale/ltm/' --script-location '../experimental/solutions/autoscale/ltm/' --solution-location 'experimental'

## BIGIP ARM Template - WAF AutoScale
python -B '.\master_template.py' --template-name waf_autoscale --license-type PAYG --template-location '../experimental/solutions/autoscale/waf/' --script-location '../experimental/solutions/autoscale/waf/' --solution-location 'experimental'

############################### End Experimental ###############################


############################### Supported ###############################
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic)
template_list="1nic 2nic 3nic"
stack_list="new_stack existing_stack"
for tmpl in $template_list; do
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type PAYG --stack-type $stack_type --template-location "../supported/standalone/$tmpl/$stack_type/PAYG/" --script-location "../supported/standalone/$tmpl/$stack_type/"
        python -B '.\master_template.py' --template-name $tmpl --license-type BYOL --stack-type $stack_type --template-location "../supported/standalone/$tmpl/$stack_type/BYOL/" --script-location "../supported/standalone/$tmpl/$stack_type/"
    done
done

## BIGIP ARM Templates - Cluster (base)
python -B '.\master_template.py' --template-name cluster_base --license-type PAYG --template-location '../supported/cluster/1nic/PAYG/' --script-location '../supported/cluster/1nic/'
python -B '.\master_template.py' --template-name cluster_base --license-type BYOL --template-location '../supported/cluster/1nic/BYOL/' --script-location '../supported/cluster/1nic/'

## BIGIP ARM Template - LTM AutoScale
python -B '.\master_template.py' --template-name ltm_autoscale --license-type PAYG --template-location '../supported/solutions/autoscale/ltm/' --script-location '../supported/solutions/autoscale/ltm/' --solution-location 'supported'

############################### End Supported ###############################
