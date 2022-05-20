from google.cloud import compute_v1
from google.cloud import container_v1
from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.cloud.logging
import config
import datetime

def configure_gcp():
    # Build Credentials
    config.credentials = GoogleCredentials.get_application_default()
    LoggingClient = google.cloud.logging.Client()

    # Setup the logger
    LoggingClient.get_default_handler()
    LoggingClient.setup_logging()

## List GCE Instances
def GetInstances():
    # This Function creates a list of instances per GKE cluster and returns them as a nested array
    # Check cache 
    elapsed = datetime.datetime.now() - config.InstanceCacheLastUpdated
    if ((config.InstanceCacheList != []) and (elapsed < datetime.timedelta(seconds=config.cachetime))):
        print (f"Using cache from {config.InstanceCacheLastUpdated}")
        return config.InstanceCacheList

    # Build Client
    instance_client = compute_v1.InstancesClient()
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = config.gcp_project

    agg_list = instance_client.aggregated_list(request=request)

    all_instances = []

    # Format the return
    for zone, response in agg_list:
        if response.instances:
            for instance in response.instances:
                thisZone = str(instance.zone).rsplit('/', 1)[-1]

                thisStatus = [char for char in str(instance.status) if char.isupper()]
                all_instances.append({'zone':thisZone,'name':instance.name,'status':''.join(thisStatus)})

    config.InstanceCacheList = all_instances
    config.InstanceCacheLastUpdated = datetime.datetime.now()

    return all_instances

## Kill GCE Instance
def KillInstance(instance_name,instance_zone):
    # This function removes a specific instance
    instance_client = compute_v1.InstancesClient()
    operation_client = compute_v1.ZoneOperationsClient()

    print(f"Deleting {instance_name} from {instance_zone}...")

    operation = instance_client.delete_unary(
        project=config.gcp_project, zone=instance_zone, instance=instance_name
    )

    while operation.status != compute_v1.Operation.Status.DONE:
        operation = operation_client.wait(
            operation=operation.name, zone=instance_zone, project=config.gcp_project
        )

    if operation.error:
        print("Error during deletion:", operation.error)
        return False
    if operation.warnings:
        print("Warning during deletion:", operation.warnings)
    print(f"Instance {instance_name} deleted.")

    return True

## Get GKE Creds
def GetGKECreds():
    client = container_v1.ClusterManagerClient()
    return client

