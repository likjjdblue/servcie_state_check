FROM centos:7
WORKDIR /TRS
ADD ./service_state_check.py /TRS
RUN chmod 777 /TRS/service_state_check.py;yum install epel* -y;yum install python-pip -y;pip install flask
ENV FLASK_APP=service_state_check.py
Run export FLASK_APP=service_state_check.py

CMD ["flask", "run", "--host=0.0.0.0"]
