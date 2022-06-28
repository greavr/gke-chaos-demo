from re import X
from google.cloud import gkehub_v1
from google.cloud import compute_v1
from google.cloud import container_v1
from oauth2client.client import GoogleCredentials
import google.auth.transport.requests
import google.cloud.logging
from requests import request
import config
import datetime
from urllib.parse import urlparse
import random

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
    all_instances = []
    try:
        instance_client = compute_v1.InstancesClient()
        request = compute_v1.AggregatedListInstancesRequest()
        request.project = config.gcp_project

        agg_list = instance_client.aggregated_list(request=request)

        # Format the return
        for zone, response in agg_list:
            if response.instances:
                for instance in response.instances:
                    thisZone = str(instance.zone).rsplit('/', 1)[-1]

                    thisStatus = [char for char in str(instance.status) if char.isupper()]
                    all_instances.append({'zone':thisZone,'name':instance.name,'status':''.join(thisStatus)})

        config.InstanceCacheList = all_instances
        config.InstanceCacheLastUpdated = datetime.datetime.now()
    except Exception as e:
        print(e)

    return all_instances

## List Anthos GKE Clusters
def GetClusterList():
    """Return list of kubernetes clusters registered in Anthos. Returns Array of cluster and instances"""
    # Check Cache result
    elapsed = datetime.datetime.now() - config.ClusterCacheLastUpdated
    if ((config.ClusterCacheLastUpdated != []) and (elapsed < datetime.timedelta(seconds=config.cachetime))):
        print (f"Using Cluster cache from {config.ClusterCacheLastUpdated}")
        return config.ClusterCacheList

    # Build Client
    all_clusters = []
    try:
         # Create a client
        client = gkehub_v1.GkeHubClient()

        # Initialize request argument(s)
        request = gkehub_v1.ListMembershipsRequest(
            parent=f"projects/{config.gcp_project}/locations/-",
        )

        # Make the request
        page_result = client.list_memberships(request=request)

        # Handle the response
        for response in page_result:
    
            # Check if gke cluster
            if response.endpoint.gke_cluster.resource_link:
                cluster_name = response.endpoint.gke_cluster.resource_link.split("/")[-1]
                cluster_location = response.endpoint.gke_cluster.resource_link.split("/")[-3]
                cluster_type = "gke"
            else:
                cluster_name = response.name.split("/")[-1]
                cluster_location = response.name.split("/")[-3]
                cluster_type = response.endpoint.kubernetes_metadata.node_provider_id

            cluster_node_count = response.endpoint.kubernetes_metadata.node_count
            
            aCluster = {'cluster-name' : cluster_name, 'location': cluster_location, 'node-count': cluster_node_count, 'cluster-type': cluster_type}
            all_clusters.append(aCluster)


        # Handle the response
        config.ClusterCacheList = all_clusters
        config.ClusterCacheLastUpdated = datetime.datetime.now()
    except Exception as e:
        print(e)

    return all_clusters

## Kill GCE Instance
def KillInstance(instance_name,instance_zone):
    # This function removes a specific instance
    try:
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
    except Exception as e:
        print(e)

    return False

## Kill Instance in Cluster
def KillServerInCluster(cluster_name,region):
    """Lookup the cluster and pass that instance to KillInstance Function"""
    # This function lookups the cluster and picks a random instance to kill
    result = False
    try:
        # Lookup Cluster
        client = container_v1.ClusterManagerClient()

        request = container_v1.ListNodePoolsRequest()
        request.parent = f"projects/{config.gcp_project}/locations/{region}/clusters/{cluster_name}"

        # Make the request
        response = client.list_node_pools(request=request)

        # Get instance group names
        node_pool_list = []
        for aPool in response.node_pools:
            for aGroup in aPool.instance_group_urls:
                thisGroup = urlparse(aGroup).path.split('/')[-1]
                thisZone = urlparse(aGroup).path.split('/')[-3]
                aPool = {"group_name": thisGroup,"group_zone": thisZone}
                node_pool_list.append(aPool)
                
        # Pick Random instance group and pass to List_InstanceGroup_Instances
        random_ig = random.choice(node_pool_list)
        choosen_instance = List_InstanceGroup_Instances(instance_group_name=random_ig["group_name"], instance_group_location=random_ig["group_zone"])

        # Kill Instance
        result = KillInstance(instance_name=choosen_instance["instance_name"],instance_zone=choosen_instance["instance_zone"])
        
    except Exception as e:
        print(e)

    return result
    
## List instances in Instance Group
def List_InstanceGroup_Instances(instance_group_name, instance_group_location):
    """This function returns a list of instances found in a instance group, returns a random machine name and zone"""
    result = {}
    try:
        print(f"{instance_group_name} - {instance_group_location}")
        instance_group_client = compute_v1.InstanceGroupsClient()
        request = compute_v1.ListInstancesInstanceGroupsRequest()
        request.project = config.gcp_project
        request.zone = instance_group_location
        request.instance_group = instance_group_name   

        response = instance_group_client.list_instances(request=request)

        print (response)

    except Exception as e:
        print(e)

    return result

## Get GKE Creds
def GetGKECreds():
    client = container_v1.ClusterManagerClient()
    return client

