from flask import Flask, render_template, request
import json
from handlers.helpers import helpers
from handlers.gcp import gcp
from handlers.kubernetes import k8s
from handlers.loadgen import loadgen
import config

## Config App
app = Flask(__name__, static_folder="frontend/build/static", template_folder="frontend/build")

## Default App Hosting
@app.route("/", methods=['GET'])
def default():
    ## Load Page
    return render_template('index.html', monitor_page=config.dashboard_url)

## Chaos Page
@app.route("/chaos", methods=['GET'])
def chaos_page():
    return render_template('chaos.html')

## LoadGen Page
@app.route("/load", methods=['GET'])
def load():
    return render_template('load.html')

## Site Preview
@app.route("/live-site", methods=['GET'])
def preview():
    return render_template('preview.html', preview_list=config.site_urls)

## Get Instances
@app.route("/list-instances",methods=['GET'])
def listinstances():
    # API End Point for get all instances
    result = gcp.GetInstances()

    # Validate result
    if len(result) > 0:
        return json.dumps({'success':True, 'instances':result}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## Kill Instance
@app.route("/remove-instance",methods=['POST'])
def removeinstance():
    # API End Point for remove instance
    name = request.form['instance_name']
    zone = request.form['instance_zone']

    result = gcp.KillInstance(instance_name=name,instance_zone=zone)

    if result:
        return json.dumps({'success':True}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## Get Servers
@app.route("/list-pods", methods=['GET'])
def list_pods():
    # API End Point for get all instances
    # result = k8s.CreatePodList()
    result = [
        {'name':'adservice','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'},
        {'name':'cartservice','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'},
        {'name':'checkoutservice','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'},
        {'name':'currencyservice','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'},
        {'name':'emailservice','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'},
        {'name':'frontend','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'},
        {'name':'paymentservice','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'},
        {'name':'productcatalogservice','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'},
        {'name':'recommendationservice','cluster':'chaos-us-west1','zone':'us-west1-a','status':'ready'}
        ]

    # Validate result
    if len(result) > 0:
        return json.dumps({'success':True, 'pods':result}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## Delete Pod In Service
@app.route("/remove-pod",methods=['POST'])
def remove_pod():
    service = request.form['gke_pod']
    cluster = request.form['gke_cluster']
    zone = request.form['gke_zone']

    result = k8s.KillPod(pod_name=service,cluster_name=cluster, cluster_zone=zone)

    if result:
        return json.dumps({'success':True}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## Increase load on site
@app.route("/increase-load", methods=['GET'])
def increase_load():
    result = loadgen.AddLoad()

    if result:
        return json.dumps({'success':True}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## Get Current Load on the site
@app.route("/get-load", methods=['GET'])
def current_load():
    result = loadgen.GetLoad()

    if result > 0:
        return json.dumps({'success':True, 'current_load':result}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## Get Cluster Lists
@app.route("/v2/get-clusters", methods=['GET'])
def get_clusters():
    """ Return json list of kubernetes clusters registered in Athos"""
    " Sample return structure TYPE: JSON"
    " Nested array under 'instances'"
    " cluster_name: Friend cluster name (str)"
    " location: Region of Cluser (str)"
    " node-count: How many instances in cluster (int 0-100)"

    # API End Point for get all instances
    result = gcp.GetClusterList()

    # Validate result
    if len(result) > 0:
        return json.dumps({'success':True, 'instances':result}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## Remove random instance from cluster
@app.route("/v2/remove-from-cluster", methods=['POST'])
def remove_from_cluster():
    """Function to remove a random GCE instance from cluster."""
    " Return is boolean for success "
    " Required parameters: gke_cluster (Friendly string name)"
    " gke_region (string region name"

    cluster = request.form['gke_cluster']
    region = request.form['gke_region']

    result = gcp.KillServerInCluster(cluster_name=cluster,region=region)

    if result:
        return json.dumps({'success':True}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## List Services
@app.route("/v2/list-services", methods=['GET'])
def list_services():
    """ Pull condensed list of services"""
    result = k8s.Create_Service_List()
    # Validate result
    if len(result) > 0:
        return json.dumps({'success':True, 'services':result}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

## Remove random pod from service
@app.route("/v2/kill-pod", methods=['POST'])
def remove_random_pod():
    """ Remove random pod from service on random machine"""

    service = request.form['service']

    result = k8s.kill_random_pod(service_name=service)

    if result:
        return json.dumps({'success':True}), 201, {'ContentType':'application/json'} 
    else:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

if __name__ == "__main__":
    ## Setup APP
    gcp.configure_gcp()
    helpers.GetConfig()
    ## Run APP
    app.run(host='0.0.0.0', port=8080, debug=True)