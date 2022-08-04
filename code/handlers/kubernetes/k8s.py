import random
from kubernetes import client
from handlers.gcp import gcp
import config as config
import datetime

## Quiten TLS notifications
import urllib3
urllib3.disable_warnings()

## Get Kubernetes creds
def GetKubernetesCreds(location: str, name: str):
    # Returns Configuration set for Kubernetes Cluster
    configuration = ""
    cluster_manager_client = gcp.GetGKECreds()
    try:
        print(f"Getting Credentials for the cluster: {name}, located at: {location}")
        cluster = cluster_manager_client.get_cluster(name=f'projects/{config.gcp_project}/locations/{location}/clusters/{name}')
        # Build Configuration
        config.credentials.get_access_token()
        configuration = client.Configuration()
        configuration.host = f"https://{cluster.endpoint}:443"
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + config.credentials.access_token}
    except Exception as e:
        print (e)

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
def GetServices(namespace_filter:str, credentials):
    # Get list of services in namespace
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
        print(e)

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
        print (f"Unable to get the status of the {service} service, in {cluster_name}, {cluster_location}, in the ns {namespace_filter}")
        print(e)

    # Return results
    return pod_results

def CreatePodList(namespace: str = "hipster" ):
    # Function to get a list of all pods in all services inside a namespace

    # Check cache 
    elapsed = datetime.datetime.now() - config.PodCacheLastUpdated
    if ((config.PodCacheList != []) and (elapsed < datetime.timedelta(seconds=config.cachetime))):
        print (f"Using cache from {config.PodCacheLastUpdated}")
        return config.PodCacheList

    pod_results = []
    ## Itterate over clusters
    for aCluster in config.gke_clusters:
        cluster_name = aCluster[0]
        cluster_location = aCluster[1]
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

    # Return results
    return pod_results
            
## Kill Pod
def KillPod(pod_name, cluster_name, cluster_zone):
    print(f"Killing Pod: {pod_name}, Cluster: {cluster_name}, Zone: {cluster_zone}")
    # Remove Pod
    cluster_manager_client = gcp.GetGKECreds()
    cluster = cluster_manager_client.get_cluster(name=f'projects/{config.gcp_project}/locations/{cluster_zone}/clusters/{cluster_name}')

    # Build Configuration
    configuration = client.Configuration()
    configuration.host = f"https://{cluster.endpoint}:443"
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + config.credentials.access_token}
    client.Configuration.set_default(configuration)

    # Get Pods
    try:
        v1 = client.CoreV1Api()
        remove_pod = v1.delete_namespaced_pod(pod_name,"hipster")
        print(remove_pod)
        return True
    except Exception as e:
        print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)
        return False

## Get Pod Count
def Pod_count(service: str, cluster_name: str, cluster_location: str,  namespace_filter: str, credentials):
    """ Function returns a count of pods in that service"""
    # Gather a list of pods in each service in each cluster
    print(f"Getting pod count for: {service} in the {cluster_name} cluster.")
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
        print (f"Unable to get the status of the {service} service, in {cluster_name}, {cluster_location}, in the ns {namespace_filter}")
        print(e)
        pod_count = random.randint(1, 3)

    # Return results
    return pod_count

## Consolidated Service List
def Create_Service_List(namespace: str = "hipster"):
    """ This function gets a unique list of services in each cluster and counts the pods in each cluster. Returns Dictonary"""
    # Check cache 
    elapsed = datetime.datetime.now() - config.ServiceListLastUpdated
    if ((config.ServiceCacheList != []) and (elapsed < datetime.timedelta(seconds=config.cachetime))):
        print (f"Using cache from {config.ServiceListLastUpdated}")
        return config.ServiceCacheList

    result = {}

    try:
        # Itterate over each server
        for aCluster in config.ClusterCacheList:
            #  Only Scrape GKE Clusters
            if aCluster["cluster-type"] != "gke":
                continue

            cluster_name = aCluster["cluster-name"]
            cluster_location = aCluster["location"]

            this_client = GetKubernetesCreds(location=cluster_location,name=cluster_name)

            # Get Service List
            service_list = GetServices(namespace_filter=namespace, credentials=this_client)

            # Get pods in service
            for aService in service_list:
                # Check for GKE Services we ignore
                if aService.startswith("gke"):
                    continue

                # Continue
                pod_count_value = Pod_count(cluster_name=cluster_name, cluster_location=cluster_location, service=aService, namespace_filter=namespace, credentials=this_client)
                if aService not in result:
                    result[aService] =  pod_count_value
                else:
                    result[aService] = result.get(aService, 0) + pod_count_value

    except Exception as e:
        print(e)

    config.ServiceCacheList = result
    config.ServiceListLastUpdated = datetime.datetime.now()

    # Return results
    return result

## Remove random pod from selected service accross all clusters
def kill_random_pod(service_name, namespace: str = "hipster"):
    """ This function picks a random cluster from the list, and removes a random pod from the corrosponding service"""

    result = False
    #try:
    # Pick a random cluster
    randomCluster = random.choice(config.gke_clusters)
    randomCluster = ["chaos-us-central1", "us-central1"]

    cluster_name = randomCluster[0]
    cluser_loc = randomCluster[1]

    # Build Kubernetes Creds
    this_client = GetKubernetesCreds(location=cluser_loc,name=cluster_name)
    
    # Get list of pods on that cluster in the specific service
    PodList = GetPods(cluster_name=cluster_name, cluster_location=cluser_loc, service=service_name, namespace_filter=namespace, credentials=this_client)

    # Randomly pic a pod from the list
    randomPod = random.choice(PodList)

    #Kill RandomPod
    result = KillPod(cluster_name=randomPod["cluster"],cluster_zone=randomPod["zone"], pod_name=randomPod["name"])
    #except Exception as e:
    #    print(e)

    # Return restul
    return result
