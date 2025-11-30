pipeline {
    agent any
    
    environment {
        AWS_ACCOUNT_ID = '399934155236'
        AWS_REGION = 'ap-southeast-2'
        ECR_REPO = 'my-flask-app'
        CLUSTER_NAME = 'my-flask-cluster'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/velkadamban/flask-contact-form.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${ECR_REPO}:${env.BUILD_ID} ."
                }
            }
        }
        
        stage('Login to ECR') {
            steps {
                sh """
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                """
            }
        }
        
        stage('Push to ECR') {
            steps {
                sh """
                    docker tag ${ECR_REPO}:${env.BUILD_ID} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest
                    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest
                """
            }
        }
        
        stage('Configure kubectl & Install EFS CSI Driver') {
            steps {
                sh """
                    # Configure kubectl
                    aws eks update-kubeconfig --region ${AWS_REGION} --name ${CLUSTER_NAME}
                    
                    # Install EFS CSI driver
                    kubectl apply -k "github.com/kubernetes-sigs/aws-efs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.7"
                """
            }
        }
        
        stage('Update K8s Deployment') {
            steps {
                sh """
                    # Update k8s deployment with new image
                    sed -i 's|YOUR_ECR_URL|${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com|g' flask-deployment.yaml
                    
                    # Apply EFS storage configuration
                    kubectl apply -f efs-pv.yaml
                    kubectl apply -f efs-pvc.yaml
                    
                    # Apply k8s configuration
                    kubectl apply -f flask-deployment.yaml
                    kubectl apply -f postgresql-deployment.yaml
                    
                    # Rollout restart to pick up new image
                    kubectl rollout restart deployment/flask-app
                """
            }
        }
    }
    
    post {
        success {
            echo '🎉 Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}