##########################################################################
# autotag.py
# Tag Resources in Tenancy for AutoScale
#
# @Author:   Chavez Saul (https://github.com/Chavez-Saul/oci-cloud-tagging/blob/main/autotag.py)
# @Improved: Adi Zohar, 4/12/2021
#
# Supports Python 3
##########################################################################
# Application Command line parameters
#
#   -t config  - Config file section to use (tenancy profile)
#   -ip        - Use Instance Principals for Authentication
#   -dt        - Use Instance Principals with delegation token for cloud shell
#   -rg        - Filter on Region
#   -ic        - include compartment ocid
#   -ec        - exclude compartment ocid
#   -pc        - tag production Compartment OCID with production schedule
#   -skipmysql - skip mysql for long running job
#   -h         - help
#
# Required Object Storage name "bucket-tag" at home region
##########################################################################
import oci
import csv
import sys
import datetime
import argparse

# global parameters
object_storage_bucket = "bucket-tag"
anyday_value = '0,0,0,0,0,0,0,*,*,*,*,*,*,*,*,*,*,*,*,*,0,0,0,0'
production_value = '*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*'
created_by_namespace = "TagDefaults"
version = "2021.05.07"


##########################################################################
# Print header centered
##########################################################################
def print_header(name):
    chars = int(90)
    print("")
    print('#' * chars)
    print("#" + name.center(chars - 2, " ") + "#")
    print('#' * chars)


##########################################################################
# Create signer for Authentication
# Input - config_profile and is_instance_principals and is_delegation_token
# Output - config and signer objects
##########################################################################
def create_signer(config_profile, is_instance_principals, is_delegation_token):

    # if instance principals authentications
    if is_instance_principals:
        try:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            config = {'region': signer.region, 'tenancy': signer.tenancy_id}
            return config, signer

        except Exception:
            print_header("Error obtaining instance principals certificate, aborting")
            raise SystemExit

    # -----------------------------
    # Delegation Token
    # -----------------------------
    elif is_delegation_token:

        try:
            # check if env variables OCI_CONFIG_FILE, OCI_CONFIG_PROFILE exist and use them
            env_config_file = os.environ.get('OCI_CONFIG_FILE')
            env_config_section = os.environ.get('OCI_CONFIG_PROFILE')

            # check if file exist
            if env_config_file is None or env_config_section is None:
                print("*** OCI_CONFIG_FILE and OCI_CONFIG_PROFILE env variables not found, abort. ***")
                print("")
                raise SystemExit

            config = oci.config.from_file(env_config_file, env_config_section)
            delegation_token_location = config["delegation_token_file"]

            with open(delegation_token_location, 'r') as delegation_token_file:
                delegation_token = delegation_token_file.read().strip()
                # get signer from delegation token
                signer = oci.auth.signers.InstancePrincipalsDelegationTokenSigner(delegation_token=delegation_token)

                return config, signer

        except KeyError:
            print("* Key Error obtaining delegation_token_file")
            raise SystemExit

        except Exception:
            raise

    # -----------------------------
    # config file authentication
    # -----------------------------
    else:
        config = oci.config.from_file(
            oci.config.DEFAULT_LOCATION,
            (config_profile if config_profile else oci.config.DEFAULT_PROFILE)
        )
        signer = oci.signer.Signer(
            tenancy=config["tenancy"],
            user=config["user"],
            fingerprint=config["fingerprint"],
            private_key_file_location=config.get("key_file"),
            pass_phrase=oci.config.get_config_value_or_default(config, "pass_phrase"),
            private_key_content=config.get("key_content")
        )
        return config, signer


##########################################################################
# change_tag
##########################################################################
def change_tag(collection, tag_value):
    try:
        change = 0
        error = 0
        for r in collection:
            x = r.defined_tags

            print("Resource name: {}, Resource Type: {}, Resource id: {}".format(r.display_name, r.resource_type, r.identifier))
            print("   " + str(x))
            # TODO Use a prefined here. Fomart{Namespace:{tag key, tag value}
            x.update({'Schedule': {'AnyDay': tag_value}})
            print("   " + str(x))

            if r.resource_type == "Instance":
                try:
                    update_instance_details = oci.core.models.UpdateInstanceDetails(defined_tags=x)
                    compute_client.update_instance(r.identifier, update_instance_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))

            elif r.resource_type == "DbSystem":
                try:
                    update_dbsystem_details = oci.database.models.UpdateDbSystemDetails(defined_tags=x)
                    database_client.update_db_system(r.identifier, update_dbsystem_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            elif r.resource_type == "VmCluster":
                try:
                    update_vmcluster_details = oci.database.models.UpdateVmClusterDetails(defined_tags=x)
                    database_client.update_vm_cluster(r.identifier, update_vmcluster_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            elif r.resource_type == "AutonomousDatabase":
                try:
                    autonomous_details = oci.database.models.UpdateAutonomousDatabaseDetails(defined_tags=x)
                    database_client.update_autonomous_database(r.identifier, autonomous_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            elif r.resource_type == "InstancePool":
                try:
                    update_instancepool_details = oci.core.models.UpdateInstancePoolDetails(defined_tags=x)
                    compute_management_client.update_instance_pool(r.identifier, update_instancepool_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            elif r.resource_type == "AnalyticsInstance":
                try:
                    update_analytics_details = oci.analytics.models.UpdateAnalyticsInstanceDetails(defined_tags=x)
                    analytics_client.update_analytics_instance(r.identifier, update_analytics_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            elif r.resource_type == "OdaInstance":
                try:
                    update_oda_details = oci.oda.models.UpdateOdaInstanceDetails(defined_tags=x)
                    oda_client.update_oda_instance(r.identifier, update_oda_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            elif r.resource_type == "IntegrationInstance":
                # Problem, instance has to be up to update tag
                try:
                    update_integration_details = oci.integration.models.UpdateIntegrationInstanceDetails(defined_tags=x)
                    integration_client.update_integration_instance(r.identifier, update_integration_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            elif r.resource_type == "GoldenGateDeployment":
                try:
                    update_goldengate = oci.golden_gate.models.UpdateDeploymentDetails(defined_tags=x)
                    goldengate_client.update_deployment(r.identifier, update_goldengate)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("!!! Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            elif r.resource_type == "MysqlDBInstance":
                try:
                    update_mysql = oci.mysql.models.UpdateDbSystemDetails(defined_tags=x)
                    mysql_client.update_db_system(r.identifier, update_mysql)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print("Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier, e))
                    error += 1

            else:
                raise Exception("Not part of allowed query.")

        print("\nResources changed: {}. Errors: {}".format(change, error))

    except Exception as e:
        print(e)
        print("Error, Resource tag was not updated.")


##########################################################################
# Search OCI
##########################################################################
def search_oci_query(search_query):
    try:
        search_details = oci.resource_search.models.StructuredSearchDetails()
        search_details.query = search_query
        return oci.pagination.list_call_get_all_results(
            resource_search_client.search_resources,
            search_details=search_details,
            retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY
        ).data
    except Exception as e:
        raise RuntimeError("Error in search_oci_query: " + str(e.args))


##########################################################################
# findtags
##########################################################################
def findtags(collection, region_name):
    tagfile = "tag-" + str(datetime.date.today()) + "-" + region_name + ".csv"
    num = 0

    if len(collection) == 0:
        print("   No tags in collections, skipping")
    else:
        with open(tagfile, "w") as out_file:
            tag_writer = csv.writer(out_file, delimiter=',', quotechar='"')
            tag_writer.writerow(["Resource Name", "Resource Type", "Schedule", "Username"])

            # Look for a schedule with AnyDay, WeekDay, and Weekend.
            for r in collection:
                tag = r.defined_tags['Schedule']

                user = ""
                if created_by_namespace in r.defined_tags:
                    if 'Created_by' in r.defined_tags[created_by_namespace]:
                        user = r.defined_tags[created_by_namespace]['Created_by']

                if 'AnyDay' in tag:
                    if '0' not in tag['AnyDay']:
                        tag_writer.writerow([r.display_name, r.resource_type, r.defined_tags['Schedule'], user])
                        num += 1
                elif 'WeekDay' in tag:
                    if '0' not in tag['WeekDay']:
                        tag_writer.writerow([r.display_name, r.resource_type, r.defined_tags['Schedule'], user])
                        num += 1
                elif 'Weekend' in tag:
                    if '0' not in tag['Weekend']:
                        tag_writer.writerow([r.display_name, r.resource_type, r.defined_tags['Schedule'], user])
                        num += 1

        print("   " + str(num) + " tags founds")

        # load to object storage only if records exist
        if num > 0:
            print("   Loading data to object storage bucket '" + object_storage_bucket + "'")
            with open(tagfile, 'rb') as in_File:
                os.put_object(os.get_namespace().data, object_storage_bucket, tagfile, in_File)


##########################################################################
# Load compartments
##########################################################################
def identity_read_compartments(identity, tenancy):

    print("Loading Compartments...")
    try:
        cs = oci.pagination.list_call_get_all_results(
            identity.list_compartments,
            tenancy.id,
            compartment_id_in_subtree=True,
            retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY
        ).data

        # Add root compartment which is not part of the list_compartments
        tenant_compartment = oci.identity.models.Compartment()
        tenant_compartment.id = tenancy.id
        tenant_compartment.name = tenancy.name
        tenant_compartment.lifecycle_state = oci.identity.models.Compartment.LIFECYCLE_STATE_ACTIVE
        cs.append(tenant_compartment)

        print("    Total " + str(len(cs)) + " compartments loaded.")
        return cs

    except Exception as e:
        raise RuntimeError("Error in identity_read_compartments: " + str(e.args))


##########################################################################
# mysql_search
# Mysql is not supported in search query.
# Have to look through all compartments to any Mysql resources.
# This function append the mysql resources to the collection of the search
##########################################################################
def mysql_search(tag_collection, report_collection, compartments):

    print("   Finding MySQL instances ...")
    for c in compartments:

        # check compartment include and exclude
        if c.lifecycle_state != oci.identity.models.Compartment.LIFECYCLE_STATE_ACTIVE:
            continue
        if compartment_include:
            if c.id != compartment_include:
                continue
        if compartment_exclude:
            if c.id == compartment_exclude:
                continue

        cnt = 0
        print("      Compartment " + (str(c.name) + "... ").ljust(35), end="")

        # Query Mysql
        try:
            mysql_instances = oci.pagination.list_call_get_all_results(
                mysql_client.list_db_systems,
                compartment_id=c.id,
                retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY
            ).data

            # Loop on Mysql collection
            for mysql_instance in mysql_instances:

                if mysql_instance and mysql_instance.lifecycle_state != "DELETED" and mysql_instance.lifecycle_state != 'INACTIVE':
                    # Prepare Search collection item
                    summary = oci.resource_search.models.ResourceSummary()
                    summary.availability_domain = mysql_instance.availability_domain
                    summary.compartment_id = mysql_instance.compartment_id
                    summary.defined_tags = mysql_instance.defined_tags
                    summary.freeform_tags = mysql_instance.freeform_tags
                    summary.identifier = mysql_instance.id
                    summary.lifecycle_state = mysql_instance.lifecycle_state
                    summary.display_name = mysql_instance.display_name
                    summary.resource_type = "MysqlDBInstance"

                    if "Schedule" in mysql_instance.defined_tags:
                        report_collection.append(summary)
                    else:
                        tag_collection.append(summary)

                    cnt += 1

        except Exception:
            print("Warnings ")
            continue

        if cnt == 0:
            print("(-)")
        else:
            print("(" + str(cnt) + " resources)")

    return tag_collection, report_collection


##########################################################################
# Gather all production compartments ocid
##########################################################################
def production_list(query):
    prod = []
    for r in query:
        prod.append(r.identifier)
    return prod


##########################################################################
# Separate resources in to 2 different ResourceSummaryCollection
##########################################################################
def separate_resources(collection, prod_list):
    production_resource = []
    non_production_resource = []
    for elem in collection:
        if elem.compartment_id in prod_list:
            production_resource.append(elem)
        else:
            non_production_resource.append(elem)

    production_results = oci.resource_search.models.ResourceSummaryCollection().items = production_resource

    return non_production_resource, production_results


##########################################################################
# Main
##########################################################################
if __name__ == '__main__':

    # Get Command Line Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', default="", dest='config_profile', help='Config file section to use (tenancy profile)')
    parser.add_argument('-ip', action='store_true', default=False, dest='is_instance_principals', help='Use Instance Principals for Authentication')
    parser.add_argument('-dt', action='store_true', default=False, dest='is_delegation_token', help='Use Delegation Token for Authentication')
    parser.add_argument('-skipmysql', action='store_true', default=False, dest='skip_mysql', help='Skip MYSQL Scan')
    parser.add_argument('-rg', default="", dest='filter_region', help='Filter Region')
    parser.add_argument('-ic', default="", dest='compartment_include', help='Include Compartment OCID')
    parser.add_argument('-ec', default="", dest='compartment_exclude', help='Exclude Compartment OCID')
    parser.add_argument('-pc', default="", dest='tag_namespace_production', help='Exclude Tagged Production Compartment OCID')
    cmd = parser.parse_args()
    filter_region = cmd.filter_region

    compartment_exclude = cmd.compartment_exclude if cmd.compartment_exclude else ""
    compartment_include = cmd.compartment_include if cmd.compartment_include else ""

    # Start print time info
    start_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print_header("Running Auto Tag")
    print("Starts at " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("Command Line : " + ' '.join(x for x in sys.argv[1:]))

    # Identity extract compartments
    config, signer = create_signer(cmd.config_profile, cmd.is_instance_principals, cmd.is_delegation_token)
    compartments = []
    tenancy = None
    tenancy_home_region = ""
    try:
        print("\nConnecting to Identity Service...")
        identity = oci.identity.IdentityClient(config, signer=signer)
        tenancy = identity.get_tenancy(config["tenancy"]).data
        regions = identity.list_region_subscriptions(tenancy.id).data
        compartments = identity_read_compartments(identity, tenancy)

        for reg in regions:
            if reg.is_home_region:
                tenancy_home_region = str(reg.region_name)

        print("Version       : " + str(version))
        print("Tenant Name   : " + str(tenancy.name))
        print("Tenant Id     : " + tenancy.id)
        print("Home Region   : " + tenancy_home_region)
        if cmd.filter_region:
            print("Filter Region : " + cmd.filter_region)

        print("")

    except Exception as e:
        raise RuntimeError("\nError connecting to Identity Service - " + str(e))

    ############################################
    # Loop on all regions
    ############################################
    for region_name in [str(es.region_name) for es in regions]:
        if cmd.filter_region:
            if cmd.filter_region not in region_name:
                continue
        print_header("Region " + region_name)

        # set the region in the config and signer
        config['region'] = region_name
        signer.region = region_name

        # Create Module Clients
        compute_client = oci.core.compute_client.ComputeClient(config, signer=signer)
        analytics_client = oci.analytics.AnalyticsClient(config, signer=signer)
        integration_client = oci.integration.IntegrationInstanceClient(config, signer=signer)
        loadbalancer_client = oci.load_balancer.LoadBalancerClient(config, signer=signer)
        database_client = oci.database.DatabaseClient(config, signer=signer)
        compute_management_client = oci.core.ComputeManagementClient(config, signer=signer)
        oda_client = oci.oda.OdaClient(config, signer=signer)
        resource_search_client = oci.resource_search.ResourceSearchClient(config, signer=signer)
        goldengate_client = oci.golden_gate.GoldenGateClient(config, signer=signer)
        mysql_client = oci.mysql.DbSystemClient(config, signer=signer)

        print("\nFind Resources without Tag to Tag...")

        resources = "Instance, DbSystem, VmCluster, AutonomousDatabase, InstancePool, GoldenGateDeployment, OdaInstance, AnalyticsInstance, IntegrationInstance"
        if region_name == "us-sanjose-1":
            resources = "Instance, DbSystem, VmCluster, AutonomousDatabase, InstancePool, OdaInstance, AnalyticsInstance, IntegrationInstance"

        # Query for all resources
        query_tag_not_exist = "query " + resources + " resources "
        query_tag_not_exist += "where "
        query_tag_not_exist += "    definedTags.namespace != 'Schedule' && "
        query_tag_not_exist += "    ( lifecycleState = 'Active' ||  lifecycleState = 'Running' || lifecycleState = 'Stopped' || "
        query_tag_not_exist += "    lifecycleState = 'Available' ) "
        query_tag_not_exist += " && compartmentId  = '" + compartment_include + "'" if compartment_include else ""
        query_tag_not_exist += " && compartmentId != '" + compartment_exclude + "'" if compartment_exclude else ""
        query_tag_exist = query_tag_not_exist.replace("!= 'Schedule'", "= 'Schedule'")

        # find all comparments that part of production
        production_compartments = []
        if cmd.tag_namespace_production:
            query_production_string = "query compartment resources where definedTags.key = " + '\'' + cmd.tag_namespace_production + '\''
            query_production_results = search_oci_query(query_production_string)
            production_compartments = production_list(query_production_results)

        # get collection to tag
        collection_to_tag = search_oci_query(query_tag_not_exist)

        # get collection to report when tag exist
        collection_to_report = search_oci_query(query_tag_exist)

        # add mysql tags to the collections
        if not cmd.skip_mysql:
            collection_to_tag, collection_to_report = mysql_search(collection_to_tag, collection_to_report, compartments)

        # seperate resources between production and non prod
        collection_to_tag, production_collection = separate_resources(collection_to_tag, production_compartments)

        print("\n    Non Prod   Resources Found = " + str(len(collection_to_tag)))
        if cmd.tag_namespace_production:
            print("    Production Resources Found = " + str(len(production_collection)))

        # change tag non-production
        if collection_to_tag:
            change_tag(collection_to_tag, anyday_value)

        # change tag production
        if production_collection:
            change_tag(production_collection, production_value)

        # For object storage change to home region to store the info
        config['region'] = tenancy_home_region
        signer.region = tenancy_home_region
        os = oci.object_storage.ObjectStorageClient(config, signer=signer)

        # report tag without shutdown
        print("\nFind Tags without shutdown and store in object storage bucket '" + object_storage_bucket + "'")
        findtags(collection_to_report, region_name)

    print("\nThank you for using the OCI API today, goodbye.")
    exit()
