import oci
import csv
import datetime
from oci.core.compute_client import ComputeClient
from oci.core.models import UpdateInstanceDetails
from oci.resource_search import ResourceSearchClient
from oci.database import DatabaseClient
from oci.database.models import UpdateAutonomousDatabaseDetails
from oci.database.models import UpdateVmClusterDetails
from oci.database.models import UpdateDbSystemDetails
from oci.core import ComputeManagementClient
from oci.core.models import UpdateInstancePoolDetails
from oci.oda import OdaClient
from oci.oda.models import UpdateOdaInstanceDetails
from oci.analytics import AnalyticsClient
from oci.analytics.models import UpdateAnalyticsInstanceDetails
from oci.integration import IntegrationInstanceClient
from oci.integration.models import UpdateIntegrationInstanceDetails
from oci.load_balancer import LoadBalancerClient
from oci.golden_gate import GoldenGateClient
from oci.golden_gate.models import UpdateDeploymentDetails
from oci.object_storage import ObjectStorageClient
from oci.mysql import DbSystemClient
from oci.mysql.models import UpdateDbSystemDetails
from oci.resource_search.models import ResourceSummary


# API calls in functions
def change_tag(collection):
    try:
        change = 0
        error = 0
        for r in collection.items:
            x = r.defined_tags

            print("Resource name: {}, Resource Type: {}, Resource id: {}".format(r.display_name, r.resource_type,
                                                                                 r.identifier))
            print(x)
            # TODO Use a prefined here. Fomart{Namespace:{tag key, tag value}
            x.update({'Schedule': {'AnyDay': '0,0,0,0,0,0,0,0,*,*,*,*,*,*,*,*,0,0,0,0,0,0,0,0'}})
            print(x)

            if r.resource_type == "Instance":
                try:
                    update_instance_details = UpdateInstanceDetails(defined_tags=x)
                    computeclient.update_instance(r.identifier, update_instance_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error: {}".format(r.display_name, r.identifier, e))
                    error += 1
            elif r.resource_type == "DbSystem":
                try:
                    update_dbsystem_details = UpdateDbSystemDetails(defined_tags=x)
                    dbsystemclient.update_db_system(r.identifier, update_dbsystem_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1
            elif r.resource_type == "VmCluster":
                try:
                    update_vmcluster_details = UpdateVmClusterDetails(defined_tags=x)
                    databaseclient.update_vm_cluster(r.identifier, update_vmcluster_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1
            elif r.resource_type == "AutonomousDatabase":
                try:
                    autonomous_details = UpdateAutonomousDatabaseDetails(defined_tags=x)
                    databaseclient.update_autonomous_database(r.identifier, autonomous_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1
            elif r.resource_type == "InstancePool":
                try:
                    update_instancepool_details = UpdateInstancePoolDetails(defined_tags=x)
                    instancepoolclient.update_instance_pool(r.identifier, update_instancepool_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1
            elif r.resource_type == "AnalyticsInstance":
                try:
                    update_analytics_details = UpdateAnalyticsInstanceDetails(defined_tags=x)
                    analyticsclient.update_analytics_instance(r.identifier, update_analytics_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1
            elif r.resource_type == "OdaInstance":
                try:
                    update_oda_details = UpdateOdaInstanceDetails(defined_tags=x)
                    odaclient.update_oda_instance(r.identifier, update_oda_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1

            elif r.resource_type == "IntegrationInstance":
                # Problem, instance has to be up to update tag
                try:
                    update_integration_details = UpdateIntegrationInstanceDetails(defined_tags=x)
                    intergrationclient.update_integration_instance(r.identifier, update_integration_details)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1

            elif r.resource_type == "GoldenGateDeployment":
                try:
                    update_goldengate = UpdateDeploymentDetails(defined_tags=x)
                    goldengateclient.update_deployment(r.identifier, update_goldengate)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1

            elif r.resource_type == "MysqlDBInstance":
                try:
                    update_mysql = oci.mysql.models.UpdateDbSystemDetails(defined_tags=x)
                    mysql.update_db_system(r.identifier, update_mysql)
                    print("Resource tag has been updated.\n")
                    change += 1
                except Exception as e:
                    print(
                        "Error occurred for resource: {}, id: {},\n Error Msg: {}".format(r.display_name, r.identifier,
                                                                                          e))
                    error += 1

            else:
                raise Exception("Not part of allowed query.")

        print("Resources changed: {}. Errors: {}".format(change, error))

    except Exception as e:
        print(e)
        print("Resource tag was not updated.")


def searchoci(searchquery):
    sdetails = oci.resource_search.models.StructuredSearchDetails()
    sdetails.query = searchquery
    return search.search_resources(search_details=sdetails).data


def findtags(collection):
    tagfile = "tag-" + str(datetime.date.today()) + "-" + signer.region + ".csv"
    user = str()
    with open(tagfile, "w") as out_file:
        tag_writer = csv.writer(out_file, delimiter=',', quotechar='"')
        tag_writer.writerow(["Resource Name", "Resource Type", "Schedule", "Username"])
        # Look for a schedule with AnyDay, WeekDay, and Weekend.
        for r in collection.items:
            tag = r.defined_tags['Schedule']
            if 'AnyDay' in tag:
                if '0' not in tag['AnyDay']:
                    if "TagDefaults" in r.defined_tags:
                        user = r.defined_tags['TagDefaults']['Created_by']
                    tag_writer.writerow([r.display_name, r.resource_type, r.defined_tags['Schedule'], user])

            elif 'WeekDay' in tag:
                if '0' not in tag['WeekDay']:
                    if "TagDefaults" in r.defined_tags:
                        user = r.defined_tags['TagDefaults']['Created_by']
                    tag_writer.writerow([r.display_name, r.resource_type, r.defined_tags['Schedule'], user])

            elif 'Weekend' in tag:
                if '0' not in tag['Weekend']:
                    if "TagDefaults" in r.defined_tags:
                        user = r.defined_tags['TagDefaults']['Created_by']
                    tag_writer.writerow([r.display_name, r.resource_type, r.defined_tags['Schedule'], user])

    with open(tagfile, 'rb') as in_File:
        os.put_object(os.get_namespace().data, "bucket-tag", tagfile, in_File)


def findAllCompartments():
    # Mysql is not supported in search query. Have to look through all compartments to
    # any Mysql resources.
    query = "query compartment resources where " \
            "( lifecycleState = 'Active' ||  lifecycleState = 'Running' || lifecycleState = 'Stopped'" \
            " || lifecycleState = 'Available')"
    sdetails = oci.resource_search.models.StructuredSearchDetails()
    sdetails.query = query
    compartments = search.search_resources(search_details=sdetails, limit=1000,
                                           retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
    return compartments


def updateocitags(searchquery):
    collection = searchoci(searchquery)
    collection = mysqlsearch(collection, "update")
    change_tag(collection)


def gatheralltags(searchquery):
    collection = searchoci(searchquery)
    collection = mysqlsearch(collection, "gather")
    findtags(collection)


def mysqlsearch(results, tagfilter):
    # This function append the mysql resources to the results of the function searchoci.
    print("Getting all compartments...")
    compartments = findAllCompartments()
    print("Finding MySQL instances...")

    for c in compartments.items:
        mysql_instances = oci.pagination.list_call_get_all_results(mysql.list_db_systems, compartment_id=c.identifier,
                                                                   retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
        for mysql_instance in mysql_instances:
            if mysql_instance and "Schedule" in mysql_instance.defined_tags and mysql_instance.lifecycle_state != "DELETED" and tagfilter == "gather":
                try:
                    summary = ResourceSummary()
                    summary.availability_domain = mysql_instance.availability_domain
                    summary.compartment_id = mysql_instance.compartment_id
                    summary.defined_tags = mysql_instance.defined_tags
                    summary.freeform_tags = mysql_instance.freeform_tags
                    summary.identifier = mysql_instance.id
                    summary.lifecycle_state = mysql_instance.lifecycle_state
                    summary.display_name = mysql_instance.display_name
                    summary.resource_type = "MysqlDBInstance"
                    results.items.append(summary)
                except:
                    pass

            elif mysql_instance and "Schedule" not in mysql_instance.defined_tags and mysql_instance.lifecycle_state != "DELETED" and tagfilter == "update":
                try:
                    summary = ResourceSummary()
                    summary.availability_domain = mysql_instance.availability_domain
                    summary.compartment_id = mysql_instance.compartment_id
                    summary.defined_tags = mysql_instance.defined_tags
                    summary.freeform_tags = mysql_instance.freeform_tags
                    summary.identifier = mysql_instance.id
                    summary.lifecycle_state = mysql_instance.lifecycle_state
                    summary.display_name = mysql_instance.display_name
                    summary.resource_type = "MysqlDBInstance"
                    results.items.append(summary)
                except:
                    pass

    return results


# Running the program
if __name__ == '__main__':
    # TODO Change this to the location of your config file
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    # IF you want to use a config file. Delete '{}' and uncomment the rest of the line.
    config = {} #oci.config.from_file(file_location="/home/opc/.oci/config")
    computeclient = ComputeClient(config, signer=signer)
    dbsystemclient = DatabaseClient(config, signer=signer)
    analyticsclient = AnalyticsClient(config, signer=signer)
    intergrationclient = IntegrationInstanceClient(config, signer=signer)
    loadbalancerclient = LoadBalancerClient(config, signer=signer)
    databaseclient = DatabaseClient(config, signer=signer)
    instancepoolclient = ComputeManagementClient(config, signer=signer)
    odaclient = OdaClient(config, signer=signer)
    identity = oci.identity.IdentityClient(config, signer=signer)
    search = ResourceSearchClient(config, signer=signer)
    goldengateclient = GoldenGateClient(config, signer=signer)
    os = ObjectStorageClient(config, signer=signer)
    mysql = DbSystemClient(config, signer=signer)

    query = "query Instance, DbSystem, VmCluster, AutonomousDatabase, InstancePool, GoldenGateDeployment, " \
            "OdaInstance, AnalyticsInstance, IntegrationInstance " \
            "resources where definedTags.namespace != 'Schedule' && " \
            "( lifecycleState = 'Active' ||  lifecycleState = 'Running' || lifecycleState = 'Stopped'" \
            " || lifecycleState = 'Available')"

    querytag = "query Instance, DbSystem, VmCluster, AutonomousDatabase, InstancePool, goldengatedeployment, " \
               "OdaInstance, AnalyticsInstance, IntegrationInstance " \
               "resources where definedTags.namespace = 'Schedule' && " \
               "( lifecycleState = 'Active' ||  lifecycleState = 'Running' || lifecycleState = 'Stopped'" \
               " || lifecycleState = 'Available')"

    updateocitags(query)
    gatheralltags(querytag)

    print("Thank you for using the OCI API today, goodbye.")
    exit()
