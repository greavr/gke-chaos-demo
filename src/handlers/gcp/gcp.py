from ctypes.wintypes import ATOM
from google.cloud import gkehub_v1
from google.cloud import compute_v1
from google.cloud import container_v1
from oauth2client.client import GoogleCredentials

from googleapiclient import discovery

import config
import datetime
from urllib.parse import urlparse
import random
import logging

import threading
import cachetools.func


def configure_gcp():
    # Build Credentials
    config.credentials = GoogleCredentials.get_application_default()

## List GCE Instances
@cachetools.func.ttl_cache(maxsize=128, ttl=1)
def GetInstances():
    """ This function controls building the list of instances"""

    if config.InstanceCacheList:
        x = threading.Thread( target=BuildInstances, args=())
        x.start
    else:
        # First time
        logging.debug("First Time Building GCE List")
        BuildInstances()

    return config.InstanceCacheList

def BuildInstances():
    # This Function creates a list of instances per GKE cluster and returns them as a nested array
    logging.debug("Building GCE List")
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
        logging.error(e)

## List Anthos GKE Clusters
@cachetools.func.ttl_cache(maxsize=128, ttl=1)
def GetClusterList() -> dict:
    """ This function returns list of gke clusters"""
    if config.ClusterCacheList:
        x = threading.Thread( target=BuildClusterList, args=())
        x.start
    else:
        # First time
        logging.debug("First Time Building GKE Cluster List")
        BuildClusterList()

    return config.ClusterCacheList

def BuildClusterList() -> dict:
    """Return list of kubernetes clusters registered in Anthos. Returns Array of cluster and instances"""
    # Build Client
    logging.debug("Building GKE Cluster List")
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
                cluster_name = response.endpoint.gke_cluster.resource_link.split("/")[-1].replace("-","_")
                cluster_location = response.endpoint.gke_cluster.resource_link.split("/")[-3]
                cluster_type = "gke"
            else:
                cluster_name = response.name.split("/")[-1].replace("-","_")
                cluster_location = response.name.split("/")[-3]
                cluster_type = response.endpoint.kubernetes_metadata.node_provider_id

            cluster_node_count = response.endpoint.kubernetes_metadata.node_count
            
            aCluster = {'cluster-name' : cluster_name, 'location': cluster_location, 'node-count': cluster_node_count, 'cluster-type': cluster_type}
            all_clusters.append(aCluster)


        # Handle the response
        config.ClusterCacheList = all_clusters
        config.ClusterCacheLastUpdated = datetime.datetime.now()
    except Exception as e:
        logging.error(e)

## Kill GCE Instance
def KillInstance(instance_name: str, instance_zone: str ) -> bool:
    """This function removes a specific instance"""
    logging.debug(f"Attempting to removing instance: {instance_name} in the zone: {instance_zone}")
    try:
        service = discovery.build('compute', 'v1')

        logging.debug(f"Deleting {instance_name} from {instance_zone}...")

        request = service.instances().delete(project=config.gcp_project, zone=instance_zone, instance=instance_name)
        response = request.execute()
        logging.info(f"Successfully started delete on the Instance {instance_name}")
        logging.debug(response)

        return True

    except Exception as e:
        logging.error(e)

    return False

## Kill Instance in Cluster
def KillServerInCluster(cluster_name: str,region: str) -> bool:
    """Lookup the cluster and pass that instance to KillInstance Function"""
    # This function lookups the cluster and picks a random instance to kill
    result = False
    try:
        # Lookup Cluster
        client = container_v1.ClusterManagerClient()

        list_np_request = container_v1.ListNodePoolsRequest()
        list_np_request.parent = f"projects/{config.gcp_project}/locations/{region}/clusters/{cluster_name}"

        # Make the request
        response = client.list_node_pools(request=list_np_request)

        # Get instance group names
        node_pool_list = []
        for aPool in response.node_pools:
            logging.debug(aPool)
            for aGroup in aPool.instance_group_urls:
                thisGroup = urlparse(aGroup).path.split('/')[-1]
                thisZone = urlparse(aGroup).path.split('/')[-3]
                thisPool = {"group_name": thisGroup,"group_zone": thisZone}
                logging.debug(thisPool)
                node_pool_list.append(thisPool)
                
        # Pick Random instance group and pass to List_InstanceGroup_Instances
        random_ig = random.choice(node_pool_list)
        logging.debug(f"Randomly picked MIG: {random_ig}")
        
        choosen_instance = Pick_Instance_From_InstanceGroup(instance_group_name=random_ig["group_name"], instance_group_location=random_ig["group_zone"])
        logging.info(f"Removing instance: {choosen_instance}")

        # Kill Instance
        result = KillInstance(instance_name=choosen_instance["instance_name"],instance_zone=choosen_instance["instance_zone"])
    except Exception as e:
        logging.error(e)

    return result
    
def Pick_Instance_From_InstanceGroup(instance_group_name: str, instance_group_location: str) -> dict:
    """This function returns one instance from managed instance group"""
    result = []

    logging.info(f"Getting info for: {instance_group_name} - {instance_group_location}")

    # Build Creds
    #credentials = GoogleCredentials.get_application_default()
    service = discovery.build('compute', 'v1')

    request = service.instanceGroups().listInstances(project=config.gcp_project, zone=instance_group_location, instanceGroup=instance_group_name, body="", returnPartialSuccess=True)

    # Build result list
    response = request.execute()
    for aInstance in response['items']:
        logging.info(f"Found Instance: {aInstance}")
        this_instance = {"instance_name": aInstance["instance"].split("/")[-1], "instance_zone": instance_group_location}
        result.append(this_instance)

    # Pick random result
    return random.choice(result)

## Get GKE Creds
def GetGKECreds() -> container_v1.ClusterManagerClient():
    """ Return Kubernetes client object"""
    client = container_v1.ClusterManagerClient()
    return client

