# Prodigal Assignment!

This is to simulate a real-world case where the service is accepting streaming data from a source. The streamed data needs to be processed in a reliable, consistent, and redundant manner for making sure that we are getting the data in the right order. The service has 3 components that take care of all the processing. They are as below:

- **Packet Receiver** - This component is responsible for receiving the data from the client. Its job is to make sure that we are not losing any data from the client and are sending it for processing correctly. It takes the data and sends it as a task to the ancillary service via celery.
- **Ancillary Service** - This component processes the task from the celery queue and stores the data in Redis. Its responsibility is to make sure that the ordering of the data packets is correct and when all the packets are received, it sends it to the downstream service for further processing.
- **Webhook Service** - This component is simulating the process where it is receiving data from the ancillary service for further processing of the entire packet. It's just storing the data packets processed data in individual resource files.

# Technology Stack

**Language**: Python(>= 3.8)
**Libraries**: Websockets(10.1), Celery(5.2.1)
**Database**: Redis(6.2)
**Messaging Queue**: RabbitMQ (3.9.11)

# Prerequisites

You will need to install certain dependencies before installing the packages for running the system. Below are the prerequisites:

- Python - https://www.python.org/downloads/
- Redis - https://redis.io/download
- RabbitMQ - https://www.rabbitmq.com/download.html

# Installation (Using Virtualenv)

#### 1. Create virtual environment

Type the command  `python -m venv .venv`

#### 2.  Activate the virtual environment
Type the command  `source .venv/bin/activate`

#### 3.  Install packages
Type the command  `pip install -r requirements.txt`

# Steps for running the system

*Note: Activate the virtualenv before running the below commands*

#### 1. Run the server

Type the command  `python server.py`

#### 2. Run the websocket server

Type the command  `python -m websockets ws://127.0.0.1:8000`

#### 3. Run the celery server

Type the command  `python -A ancillary_service worker -l INFO -Q pg`

#### 3. Run the client

Type the command  `python client.py`