# Ledgify

![CI to docker hub](https://github.com/robteeuwen/ledgify/actions/workflows/main.yml/badge.svg)

## Installing 
Use `pipenv install` to install dependencies and `pipenv shell` to activate the virtual environment. 

## Running 
Ledgify uses an app factory. There is a `create_app` function inside the application package (`__initi__.py`), which returns the `app` object. This function is used in `run.py` in combination with Flask's built in development server. 

- You can run the app locally by running `python run.py`
- You can also use gunicorn, for example by running `gunicorn run:app -w 2 --threads 2 -b 0.0.0.0:8000`. This will take the app object from `run.py`, but use Gunicorn to run the server, instead of the dev server. 
- You can also run this from a container. 

## Container configuration 
The dockerfile is based on a python base image and uses pipenv to do a system-wide install of the dependencies in the `Pipfile`. It then uses `gunicorn` to run the application on port `8000`. You can build an image from the dockerfile:

`docker build . -t robteeuwen/ledgify:latest`

You can technically do this without `robteeuwen`, but then you'd not be able to push it to a remote registry. Then run it (remember to expose port 8000)

`docker run -p [host-port]:8000 robteeuwen/ledgify:latest`

To push to docker hub: 

`docker push robteeuwen/ledgify:latest`

If you leave out the repository name (account name) you can't push. 

## Environment variables
We need a couple of env variables to run this app. They are stored in `.env`, which is used for running locally. The keys that need to be set can be copied from `.env_template`.

When running a container with docker from the command line, the environment variables in `.env` won't be available in the container. The easiest way to copy them into the container is by using `docker-compose` for running the container: 

`docker-compose up`

## CI/CD
source: https://docs.docker.com/language/java/configure-ci-cd/

The `.github` directory contains workflows that are executed in github when a commit is pushed or a pull request is created. One of the tasks performed in a workflow is building and pushing an image to Docker Hub, such that it can be accessed by a K8s deployment. 

## Kubernetes
sources: 
- https://kubernetes.io/docs/concepts/services-networking/connect-applications-service/
- https://www.digitalocean.com/community/meetup_kits/getting-started-with-containers-and-kubernetes-a-digitalocean-workshop-kit

The `deployments` directory contains yaml files for deployment of pods and services. This can be applied to a cluster using kubectl. First, make sure kubectl is installed, configured, and you are connected to a cluster. Make sure it's the right one by using 

`kubectl config get-contexts`

Apply the main deployment by running: 

```
kubectl apply -f deployments/deployment.yaml
kubectl apply -f deployments/service.yaml
```

If this is successful, you should see a pod running when you do 

`kubectl get pods` 

This pod would normally be accessed using a load balancer, an IP, and then a registered domain. But you can already access it now if you forward the port: 

`kubectl port-forward [pod-name] [local port]:8000`

### Accessing the service
Out of the box, this can be done using LoadBalancer or NodePorts. However, both these options have major drawbacks (for example, the loadbalancer option provisions a loadbalancer for each service you want to make publicly accessible). A better option is to use an Ingress. This also provisions a loadbalancer in your cloud provider, but you'll only need one. 

Ingress consists of an ingress controller (for example, nginx or traefik), which runs in its own namespace. The configuration can then be applied using an ingress resource. 

We can use `Helm` to install the ingress controller, and still use Kubernetes manifests to deploy the ingress resource. 

To make the ingress work, first install Helm using homebrew. Then use the online instructions to install the ingress controller and deploy it to your cluster. Then apply the ingress resource: 

`kubectl apply -f deployments/ingress.yaml`

This should provision a load balancer in digital ocean. The ingress resource specifies a hostname. The final step to make this work is to find the IP of the load balancer and add it to your local hosts file, or add an A record to point the host to the IP for everyone. 