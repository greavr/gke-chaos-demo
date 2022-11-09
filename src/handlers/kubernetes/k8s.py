import random
from kubernetes import client
import cachetools.func

import threading

from handlers.gcp import gcp
import config as config
import datetime
import logging

## Quiten TLS notifications
import urllib3
urllib3.disable_warnings()

## Get Kubernetes creds
def GetKubernetesCreds(location: str, name: str) -> client.Configuration():
    """ Return Authenticated kubernetes API Client Endpoint"""
    configuration = client.Configuration()
    cluster_manager_client = gcp.GetGKECreds()
    try:
        logging.info(f"Getting Credentials for the cluster: {name}, located at: {location}")
        cluster = cluster_manager_client.get_cluster(name=f'projects/{config.gcp_project}/locations/{location}/clusters/{name}')
        # Build Configuration
        config.credentials.get_access_token()
        configuration.host = f"https://{cluster.endpoint}:443"
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + config.credentials.access_token}
    except Exception as e:
       logging.error(e)

    return configuration

## Flatter Lists
def flatten_list(_2d_list):
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if type(element) is list:
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list

## Get GKE Services
def GetServices(namespace_filter:str, credentials: client.Configuration()) -> list:
    """ Generate a list of all services in a specific namespace on a GKE cluster"""
    ## Itterate over clusters
    service_list = []
    client.Configuration.set_default(credentials)

    # Get service list
    v1 = client.CoreV1Api()
    try:
        services = v1.list_service_for_all_namespaces(watch=False)
        for aService in services.items:
            if aService.metadata.namespace == namespace_filter:
                #print(aService.metadata.name)
                service_list.append(aService.metadata.name)
    except Exception as e:
        logging.error(e)

    return service_list

def GetPods(service: str, cluster_name: str, cluster_location: str,  namespace_filter: str, credentials):
    # Gather a list of pods in each service in each cluster
    pod_results = []
    client.Configuration.set_default(credentials)
    v1 = client.CoreV1Api()
    try: 
        # print(f"Getting Pods in the follwing service list {service}, from the {cluster_name} in the {namespace_filter} namespace")
        # Filter by service
        label_selector = f"app = {service}"
        pods = v1.list_namespaced_pod(namespace_filter,label_selector=label_selector)
        for i in pods.items:
            # Add Pod to Results
            pod_results.append({'name':i.metadata.name,'cluster':cluster_name,'zone':cluster_location,'status':i.status.phase})
    
    except Exception as e:
        logging.info(f"Unable to get the status of the {service} service, in {cluster_name}, {cluster_location}, in the ns {namespace_filter}")
        logging.error(e)

    # Return results
    return pod_results

@cachetools.func.ttl_cache(maxsize=128, ttl=1)
def CreatePodList(namespace: str = "hipster" ):
    """ This function returns pod list"""
    if config.PodCacheList:
        logging.debug("Using Pod Cache")
        x = threading.Thread( target=buildPodList, args=(namespace))
        x.start
    else:
        # First time
        logging.debug("First time build pod list")
        buildPodList(namespace=namespace)

    return config.PodCacheList

def buildPodList(namespace: str = "hipster"):
    # Function to get a list of all pods in all services inside a namespace
    logging.debug("Building Pod List")
    pod_results = []
    ## Itterate over clusters
    this_cluster_list = gcp.GetClusterList()
    for aCluster in this_cluster_list:
        cluster_name = aCluster["cluster-name"]
        cluster_location = aCluster["location"]
        # print(f"Cluster: {cluster_name}, located: {cluster_location}")

        this_client = GetKubernetesCreds(location=cluster_location,name=cluster_name)

        # Get Service List
        service_list = GetServices(namespace_filter=namespace, credentials=this_client)

        # Get pods in service
        for aService in service_list:
            found_pods = GetPods(cluster_name=cluster_name, cluster_location=cluster_location, service=aService, namespace_filter=namespace, credentials=this_client)
            if found_pods != []:
                pod_results.append(found_pods)

    pod_results = flatten_list(pod_results)
    config.PodCacheList = pod_results
    config.PodCacheLastUpdated = datetime.datetime.now()

## Kill Pod
def KillPod(pod_name, cluster_name, cluster_zone):
    logging.info(f"Killing Pod: {pod_name}, Cluster: {cluster_name}, Zone: {cluster_zone}")

    # Build Configuration
    configuration = GetKubernetesCreds(location=cluster_zone,name=cluster_name)
    client.Configuration.set_default(configuration)

    # Get Pods
    try:
        v1 = client.CoreV1Api()
        remove_pod = v1.delete_namespaced_pod(name=pod_name,namespace="hipster")
        #logging.info(remove_pod)
        return True
    except Exception as e:
        logging.error("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)
        return False

## Get Pod Count
def Pod_count(service: str, cluster_name: str, cluster_location: str,  namespace_filter: str, credentials):
    """ Function returns a count of pods in that service"""
    # Gather a list of pods in each service in each cluster
    logging.info(f"Getting pod count for: {service} in the {cluster_name} cluster.")
    pod_count = 0
    client.Configuration.set_default(credentials)
    v1 = client.CoreV1Api()
    try: 
        # print(f"Getting Pods in the follwing service list {service}, from the {cluster_name} in the {namespace_filter} namespace")
        # Filter by service
        label_selector = f"app = {service}"
        pods = v1.list_namespaced_pod(namespace_filter,label_selector=label_selector)
        for i in pods.items:
            pod_count += 1
    
    except Exception as e:
        logging.error(f"Unable to get the status of the {service} service, in {cluster_name}, {cluster_location}, in the ns {namespace_filter}")
        logging.error(e)
        pod_count = random.randint(1, 3)

    # Return results
    return pod_count

## Consolidated Service List
@cachetools.func.ttl_cache(maxsize=128, ttl=1)
def Create_Service_List(namespace: str = "hipster") -> dict:
    """ This function gets a unique list of services in each cluster and counts the pods in each cluster. Returns Dictonary"""
    if config.ServiceCacheList:
        logging.debug("Using Service service List")
        x = threading.Thread( target=build_service_list, args=(namespace))
        x.start
    else:
        # First time
        logging.debug("First time build service list")
        build_service_list(namespace=namespace)

    return config.ServiceCacheList

def build_service_list(namespace: str = "hipster"):
    result = {}
    logging.debug("Building service list")

    try:
        # Itterate over each server
        for aCluster in gcp.GetClusterList():
            #  Only Scrape GKE Clusters
            if aCluster["cluster-type"] != "gke":
                continue

            logging.info(f"Getting serivces from cluster: {aCluster}")

            cluster_name = aCluster["cluster-name"]
            cluster_location = aCluster["location"]

            this_client = GetKubernetesCreds(location=cluster_location,name=cluster_name)

            # Get Service List
            service_list = GetServices(namespace_filter=namespace, credentials=this_client)

            # Get pods in service
            for aService in service_list:
                # Check for GKE Services we ignore as these are GKE system services
                if aService.startswith("gke"):
                    continue

                # Continue
                pod_count_value = Pod_count(cluster_name=cluster_name, cluster_location=cluster_location, service=aService, namespace_filter=namespace, credentials=this_client)
                if aService not in result:
                    result[aService] =  pod_count_value
                else:
                    result[aService] = result.get(aService, 0) + pod_count_value

    except Exception as e:
        logging.error(e)

    config.ServiceCacheList = result
    config.ServiceListLastUpdated = datetime.datetime.now()

    # Return results
    return result

## Remove random pod from selected service accross all clusters
def kill_random_pod(service_name, namespace: str = "hipster"):
    """ This function picks a random cluster from the list, and removes a random pod from the corrosponding service"""

    result = False
    # try:
        # Pick a random cluster
    gke_clusters = filter_list(cluster_list=gcp.GetClusterList())
    randomCluster = random.choice(gke_clusters)

    cluster_name = randomCluster["cluster-name"]
    cluser_loc = randomCluster["location"]

    # Build Kubernetes Creds
    this_client = GetKubernetesCreds(location=cluser_loc,name=cluster_name)
    
    # Get list of pods on that cluster in the specific service
    PodList = GetPods(cluster_name=cluster_name, cluster_location=cluser_loc, service=service_name, namespace_filter=namespace, credentials=this_client)

    # Randomly pic a pod from the list
    randomPod = random.choice(PodList)

    #Kill RandomPod
    result = KillPod(cluster_name=randomPod["cluster"],cluster_zone=randomPod["zone"], pod_name=randomPod["name"])
    # except Exception as e:
    #     logging.error(e)

    # Return restul
    return result

def filter_list(cluster_list: dict, cluster_type: str = "gke") -> dict:
    """ Return filtered list"""
    result = []

    for aCluster in cluster_list:
        logging.debug(f"Working on cluster: {aCluster}")
        if aCluster["cluster-type"] == cluster_type:
            result.append(aCluster)
    logging.debug(f"Results found: {result}")
    return result