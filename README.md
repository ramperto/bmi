
# BMI Calculator

This is a simple api that only purpose is to tell your Body Mass Index, to give short description about how ideal your body is.

## You Will Need

To build and run all of these examples, you will need:

* python v3
* Docker version 18.03 or above
* Kubernetes Cluster version 1.20 or above
* Helm3

## 1. How to install

### Run Locally

Clone the project

```bash
  git clone https://github.com/ramperto/bmi.git
```

Go to the project directory

```bash
  cd bmi
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  python main.py
```

Access the App

```bash
  curl http://localhost:3000/?height=174&weight=88
```
Output:
```  
  {
	"bmi": 29.1,
	"label": "Overweight"
  }
```
    
## 2. CI/CD configuration

For this project I use the CI/CD tools released by github, Github Actions.

First we need to set up out secrets env for docker hub, this will be used later to publish
our image to repository.

`DOCKER_PASSWORD`

`DOCKER_USERNAME`

Insert the variable and value to github settings > secrets > Actions

![Github secrets setting](https://github.com/ramperto/bmi/blob/master/secrets_github.png?raw=true)

Github actions workflow files stored in .github/workflow. A workflow is a configurable automated process made up of one or more jobs.

Here is the content of bmi-service deployment config file:
```
name: DEVELOPMENT bmi service Deployment
on: 
  push:
    tags:
      - bmi-svc.v1.*
```
The code above is describing our deployment name and what parameter needed to trigger the 
deployment, you can see the workflow will run when you push the tag with format "bmi-svc.v1.\*"

It will not run if you tag the commit with other formats, like "bmi-svc.v.1.1".

A workflow run is made up of one or more jobs, which run in parallel by default. To run jobs sequentially, you can define dependencies on other jobs using the jobs.<job_id>.needs keyword.

```
jobs:
  test_service:
  push_to_registry:
```

As you can see from above configuration, I made two jobs, *test_service* job is created to 
build and test the service, and *push_to_registry* job to push the code to docker hub.

*push_to_registry* job will not run before *test_service* job success. This is how it look like
from github actions dashboard:

![Github actions jobs](https://github.com/ramperto/bmi/blob/master/actions_2.png?raw=true)

The image above showed the success pipeline when test and pushing docker image done without error.

If *test_service* job failed it will not proceed to *push_to_registry* job, and will notifiy through email:
![Github actions jobs failed](https://github.com/ramperto/bmi/blob/master/actions_failed.png?raw=true)





#### a. Build and test the service
Here is the configuration to build and test the service:
```
    name: build and test service image
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repo
        uses: actions/checkout@v3

      - name: run docker compose test
        run: docker-compose -f docker-compose-test-service.yml -p ci up --abort-on-container-exit --exit-code-from sut
```
After the code pulled from repository to github action done, I run the test, the goal of this simple test is to ensure
the service run without error and give output base on the request we define in our test script *({root_path}/test_script/)*.
![Github actions test success](https://github.com/ramperto/bmi/blob/master/actions_test.png?raw=true)

*push_to_registry* job is used to build and push the working image to docker hub.
#### b. Building and push the container image
Here is the pieces of configuration to build and push the container image:
```
  push_to_registry:
    needs: test_service
    name: Push Docker image to Docker Hub
    runs-on: ubuntu-latest
```
*push_to_registry* job run after *test_service* job success, it happen because I set *needs*
as conditional expression that requires *test_service* to run and success first.
```
    steps:
      - name: Check out the repo
        uses: actions/checkout@v3

      # - name: create dockerfile
      #   run: cp dockerfiles/bmi_service/Dockerfile.bmi_service Dockerfile
      - name: Log in to Docker Hub
        uses: docker/login-action@f054a8b539a109f9f41c372932f1ae047eff08c9
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@98669ae865ea3cffbcbaa878cf57c20bbf1c6c38
        with:
          images: ${{ secrets.DOCKER_USERNAME }}/${{ secrets.DOCKER_IMAGE }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@ad44023a93711e3deb337508980b4b5e9bcdc5dc
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}       
```

In the example workflow above, we use the Docker `login-action` and `build-push-action` actions to build the Docker image and, if the build succeeds, push the built image to Docker Hub.

Because I am using free tier account from aws, the services is deployed to micro ec2 vm type, with docker installed before. To deploy the image to 
vm, I create these scripts using github actions to update the old images to new one.

```
      - name: remove old docker instance
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DEV_HOST }}
          username: ${{ secrets.SSH_USER }}
          # port: ${{ secrets.TEST_PORT }}
          key: ${{ secrets.DEV_PRIV_KEY }}
          script: |
            docker stop ${{ secrets.DOCKER_IMAGE }}
            docker rm ${{ secrets.DOCKER_IMAGE }} 
            docker rmi ${{ secrets.DOCKER_USERNAME }}/${{ secrets.DOCKER_IMAGE }}

      - name: install new docker instance
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DEV_HOST }}
          username: ${{ secrets.SSH_USER }}
          # port: ${{ secrets.TEST_PORT }}
          key: ${{ secrets.DEV_PRIV_KEY }}
          script: |
            docker pull ${{ secrets.DOCKER_USERNAME }}/${{ secrets.DOCKER_IMAGE }}:latest
            docker run -d --name "${{ secrets.DOCKER_IMAGE }}" -p 3000:3000 -it ${{ secrets.DOCKER_USERNAME }}/${{ secrets.DOCKER_IMAGE }}
```
Basically scripts above will access the vm with ssh and then run commands to delete old images and deploy
the updates as new image. 

To access the API use this url :

```
http://ec2-13-229-209-101.ap-southeast-1.compute.amazonaws.com/?height=174&weight=88
```

Output:
```
{
	"bmi": 29.1,
	"label": "Overweight"
}
```

#### c. Deploy to Kubernetes Cluster

I have tried looking for free kubernetes host but I cannot find any, so I run the cluster locally.

For deployment I am using helm3. The manifest files can be found on *{root_path/k8s/}* directory.
To deploy bmi service with helm use this command:

``` bash
helm upgrade --install bmi-service --values=.\k8s\bmi_service\values.yaml .\k8s\bmi_service\
```

The services will be deployed using image that pulled from our previous docker image on docker hub repository.

```bash
kubectl get pod 
NAME                           READY   STATUS    RESTARTS   AGE
bmi-service-966b54d46-hjscx   1/1     Running   0          3m36s
```


```bash
kubectl get deploy 
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
bmi-service   1/1     1            1           118s
```

```bash
kubectl get svc
NAME                               TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE         
bmi-service-service-default   LoadBalancer   10.101.76.135   localhost     3000:32684/TCP   86s   
```

When you need to deploy development environment, some of the values will overide with `development-values.yaml` content:

I have tried using okteto but with limited resources, for okteto you can access here:
```
https://api-ramperto.cloud.okteto.net/?height=180&weight=80
```

Because I am using free plan, this site will be freezed if there is no request after 24h.
## 3 Monitoring

For monitoring I am using elasticsearch and datadog.