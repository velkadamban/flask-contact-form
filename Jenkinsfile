pipeline {
    agent any
    
    environment {
        AWS_ACCOUNT_ID = 'YOUR_ACTUAL_AWS_ACCOUNT_ID'
        AWS_REGION = 'us-east-1'
        ECR_REPO = 'flask-app'
        CLUSTER_NAME = 'YOUR_EKS_CLUSTER_NAME'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/velkamban/flask-contact-form.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // FIXED: Use sh command instead of docker.build
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
        
        stage('Update K8s Deployment') {
            steps {
                sh """
                    sed -i 's|YOUR_ECR_URL|${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com|g' flask-deployment.yaml
                    kubectl apply -f flask-deployment.yaml
                    kubectl apply -f postgresql-deployment.yaml
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