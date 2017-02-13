#/bin/bash

# BIGIP ARM Templates - Standalone (1nic, 2nic_limited)

# Experimental
python '.\master_template.py' --template-name 1nic --license-type PAYG --template-location '../experimental/standalone/1nic/PAYG/' --script-location '../experimental/standalone/1nic/'
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../experimental/standalone/1nic/BYOL/' --script-location '../experimental/standalone/1nic/'

python '.\master_template.py' --template-name 2nic_limited --license-type PAYG --template-location '../experimental/standalone/2nic_limited/PAYG/' --script-location '../experimental/standalone/2nic_limited/'
python '.\master_template.py' --template-name 2nic_limited --license-type BYOL --template-location '../experimental/standalone/2nic_limited/BYOL/'--script-location '../experimental/standalone/2nic_limited/'

# Supported
python '.\master_template.py' --template-name 1nic --license-type PAYG --template-location '../supported/standalone/1nic/PAYG/' --script-location '../supported/standalone/1nic/'
python '.\master_template.py' --template-name 1nic --license-type BYOL --template-location '../supported/standalone/1nic/BYOL/' --script-location '../supported/standalone/1nic/'

python '.\master_template.py' --template-name 2nic_limited --license-type PAYG --template-location '../supported/standalone/2nic_limited/PAYG/' --script-location '../supported/standalone/2nic_limited/'
python '.\master_template.py' --template-name 2nic_limited --license-type BYOL --template-location '../supported/standalone/2nic_limited/BYOL/' --script-location '../supported/standalone/2nic_limited/'

# BIGIP ARM Templates - Cluster (base)
