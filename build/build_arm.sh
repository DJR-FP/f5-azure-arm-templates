#/bin/bash

############################### Experimental ###############################
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic), HA-AVSET
template_list="standalone/1nic standalone/2nic standalone/3nic standalone/multi-nic ha-avset"
stack_list="new_stack existing_stack"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"/"* ]]; then
        tmpl=`basename $loc`
    fi
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type PAYG --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/PAYG/" --script-location "../experimental/$loc/$stack_type/"
        python -B '.\master_template.py' --template-name $tmpl --license-type BYOL --stack-type $stack_type --template-location "../experimental/$loc/$stack_type/BYOL/" --script-location "../experimental/$loc/$stack_type/"
    done
done

## BIGIP ARM Templates - Cluster (1 NIC)
python -B '.\master_template.py' --template-name cluster --license-type PAYG --stack-type new_stack --template-location '../experimental/cluster/1nic/new_stack/PAYG/' --script-location '../experimental/cluster/1nic/new_stack/'
python -B '.\master_template.py' --template-name cluster --license-type BYOL --stack-type new_stack --template-location '../experimental/cluster/1nic/new_stack/BYOL/' --script-location '../experimental/cluster/1nic/new_stack/'
python -B '.\master_template.py' --template-name cluster --license-type PAYG --stack-type existing_stack --template-location '../experimental/cluster/1nic/existing_stack/PAYG/' --script-location '../experimental/cluster/1nic/existing_stack/'
python -B '.\master_template.py' --template-name cluster --license-type BYOL --stack-type existing_stack --template-location '../experimental/cluster/1nic/existing_stack/BYOL/' --script-location '../experimental/cluster/1nic/existing_stack/'

## BIGIP ARM Templates - Cluster (3 NIC)
python -B '.\master_template.py' --template-name cluster_3nic --license-type PAYG --stack-type new_stack --template-location '../experimental/cluster/3nic/new_stack/PAYG/' --script-location '../experimental/cluster/3nic/new_stack/'
python -B '.\master_template.py' --template-name cluster_3nic --license-type BYOL --stack-type new_stack --template-location '../experimental/cluster/3nic/new_stack/BYOL/' --script-location '../experimental/cluster/3nic/new_stack/'
python -B '.\master_template.py' --template-name cluster_3nic --license-type PAYG --stack-type existing_stack --template-location '../experimental/cluster/3nic/existing_stack/PAYG/' --script-location '../experimental/cluster/3nic/existing_stack/'
python -B '.\master_template.py' --template-name cluster_3nic --license-type BYOL --stack-type existing_stack --template-location '../experimental/cluster/3nic/existing_stack/BYOL/' --script-location '../experimental/cluster/3nic/existing_stack/'

## BIGIP ARM Template - LTM AutoScale
python -B '.\master_template.py' --template-name ltm_autoscale --license-type PAYG --stack-type new_stack --template-location '../experimental/solutions/autoscale/ltm/new_stack/' --script-location '../experimental/solutions/autoscale/ltm/new_stack/' --solution-location 'experimental'
python -B '.\master_template.py' --template-name ltm_autoscale --license-type PAYG --stack-type existing_stack --template-location '../experimental/solutions/autoscale/ltm/existing_stack/' --script-location '../experimental/solutions/autoscale/ltm/existing_stack/' --solution-location 'experimental'

## BIGIP ARM Template - WAF AutoScale
python -B '.\master_template.py' --template-name waf_autoscale --license-type PAYG --stack-type new_stack --template-location '../experimental/solutions/autoscale/waf/new_stack/' --script-location '../experimental/solutions/autoscale/waf/new_stack/' --solution-location 'experimental'
python -B '.\master_template.py' --template-name waf_autoscale --license-type PAYG --stack-type existing_stack --template-location '../experimental/solutions/autoscale/waf/existing_stack/' --script-location '../experimental/solutions/autoscale/waf/existing_stack/' --solution-location 'experimental'

############################### End Experimental ###############################

############################### Supported ###############################
## BIGIP ARM Templates - Standalone (1nic, 2nic, 3nic), HA-AVSET
template_list="standalone/1nic standalone/2nic standalone/3nic ha-avset"
stack_list="new_stack existing_stack"
for tmpl in $template_list; do
    loc=$tmpl
    if [[ $loc == *"/"* ]]; then
        tmpl=`basename $loc`
    fi
    for stack_type in $stack_list; do
        python -B '.\master_template.py' --template-name $tmpl --license-type PAYG --stack-type $stack_type --template-location "../supported/$loc/$stack_type/PAYG/" --script-location "../supported/$loc/$stack_type/"
        python -B '.\master_template.py' --template-name $tmpl --license-type BYOL --stack-type $stack_type --template-location "../supported/$loc/$stack_type/BYOL/" --script-location "../supported/$loc/$stack_type/"
    done
done

## BIGIP ARM Templates - Cluster (base)
python -B '.\master_template.py' --template-name cluster --license-type PAYG --stack-type new_stack --template-location '../supported/cluster/1nic/PAYG/' --script-location '../supported/cluster/1nic/'
python -B '.\master_template.py' --template-name cluster --license-type BYOL --stack-type new_stack --template-location '../supported/cluster/1nic/BYOL/' --script-location '../supported/cluster/1nic/'

## BIGIP ARM Template - LTM AutoScale
python -B '.\master_template.py' --template-name ltm_autoscale --license-type PAYG --template-location '../supported/solutions/autoscale/ltm/' --script-location '../supported/solutions/autoscale/ltm/' --solution-location 'supported'

## BIGIP ARM Template - WAF AutoScale
python -B '.\master_template.py' --template-name waf_autoscale --license-type PAYG --template-location '../supported/solutions/autoscale/waf/' --script-location '../supported/solutions/autoscale/waf/' --solution-location 'supported'

############################### End Supported ###############################


############################### Misc modifications during the build process ###############################
#### Right now only do the misc modifications if this(build) script includes release-prep as first arg
if [[ $1 == "release-prep" ]]; then
    ## Update Exec bit on bash files if not set
    for f in `find .. -name '*.sh'`; do
        ( cd `dirname $f` && git update-index --chmod=+x `basename $f` )
    done
fi
