# oci-cloud-tagging

This script is used to retroactively tag resource in oci. It is add-on to [AnyKeyNL](https://github.com/AnykeyNL/OCI-AutoScale) 
Auto-Scale script. For more information on how to use the Auto-Scale script. Visit AnyKeyNl git repo.
# Parameter
This script takes the following parameter 
```
 Application Command line parameters

   -t config  - Config file section to use (tenancy profile)
   -ip        - Use Instance Principals for Authentication
   -dt        - Use Instance Principals with delegation token for cloud shell
   -rg        - Filter on Region
   -ic        - include compartment ocid
   -ec        - exclude compartment ocid
   -pc        - tag production Compartment OCID with production schedule
   -skipmysql - skip mysql for long running job
   -h         - help

 Required Object Storage name "bucket-tag" at home region
 ```
## Notes: 
- If -rg flag is not used. It will default to search all regions.
- This will only exclude one compartment from the search. 
- If Instance Principal or delegation token flag is not use. The script will default to a config file.
 
# Install script into (free-tier) Autonomous Linux Instance

- Create a free-tier compute instance using the Autonomous Linux 7.8 image
- Create a Dynamic Group called Autoscaling and add the OCID of your instance to the group, using this command:
  - ANY {instance.id = 'your_OCID_of_your_Compute_Instance'}
- Create a root level policy, giving your dynamic group permission to manage all resources in tenancy:
  - allow dynamic-group Autoscaling to manage all-resources in tenancy
- Create a bucket call ```bucket-tag``` in object storage for the admin compartment
  - the bucket will storage a csv files of all the resources that don't shutdown.
- Login to your instance using an SSH connection
- run the following commands:
  - ```wget https://raw.githubusercontent.com/Chavez-Saul/oci-cloud-tagging/main/autotag.py```
  - ```python3 autotag.py```

# Troubleshooting
- For help to install oci-cli. Use the following [link](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm) to install oci-cli. 
- Make sure to have the current version of oci-cli. If you already have 
oci-cli, use ```sudo pip install oci-cli --upgrade``` to get the latest version.


## Disclaimer
**Please test properly on test resources, before using it on production resources to prevent unwanted outages or very expensive bills.**
