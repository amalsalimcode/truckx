

![architecture](https://github.com/amalsalimcode/truckx/blob/main/readme_img/truckx_arch.png)



# Architecture

The web framework used is Flask with Python as the language. The reason to choose Flask is because its a light weight framework that has a socket library that could be leveraged. It also supports python libraries for db such as PyMongo and SQLite. The auth can be supported using JWT token which is also a library that can be leveraged.

There are two ways for the IOT to connect with the Server. Socket & REST

Socket: This connection is used to send location coordinates every minute. This was used so that when there are many devices connected at the same time, we are expecting multiple requests every second. At this point, socket becomes a more ideal connection

REST: There are multiple endpoints used by the IOT. This includes sending an alarm, video files and getting alarms (used by admin)

There is also a connection that uses REST and Socket.
When an admin wants to issue IOT reset, the request goes to the server as a REST call, which then subsequents as a socket call to the IOT

# Database Schema

![db](https://github.com/amalsalimcode/truckx/blob/main/readme_img/truckx_db.png)

**Why mysql**:
The mysql db holds entries of all alarms. I made the assumption that there isn't going to be a very large number of alarms for a given IOT. And for scalability the node can be tied to a range of IOTs. Hence mysql made sense here

**Why nosql**:
the locations are being send on a per minute basis. This is a large number to store into db. Hence we need a scalable large volume db. Ideally I would choose cassandra, since it has more availability, but for this purpose mongodb also works fine

# Details:

**Login**:

When the IOT is powered on, it sends a login information(IMEI id) to the server. The server issues a jwt token that encodes the IMEI of the device, and returns it to the device. All following API calls can then use this token as the Auth Bearer in the header

The IOT has to send a socket connection to the server. This can happen during the login request, as the server can send back an html page which will sends a socket request. This is the current implementation, but it maybe ideal for the IOT to issue a socket connection separately, so that the client code is not coupled with the server response

When the IOT sends the socket connection, it will also send the auth token that was issued. The server will then either reject the connection or accept it.

**Send Alarm**:
During an alarm send, two tables are used in the mysql db. A table to put the alarms, and a table to put the file names, with the alarm table as a Foreign Key. This is because the file names are received as a list


**Video Upload**:
During a video upload, it is ideal to store the data at a secondary storage such as an AWS S3. Currently the data is received as a POST call, and then saved. A further improvement would be to receive the data as a stream of chunks and construct the data file until all data is received. Currently the data is stored on a folder inside the server. The improvement here would be to do a direct upload to S3.

The folder structure is "<imei_id>/<file_name>"


**Fetch Video**:
This is a get request that returns the video. The ideal scenario here is that when the admin requests, a list of all the file names are sent back. Then based on the users selection the appropriate video is then fetched from the storage. As an improvement, there can be a thumbnail and a few screenshots and thumbnail screenshots saved in a separate db so that along with including the filenames, it can include the thumbnail and thumbnail screenshots


**Admin Requesting for Alarms**:
Currently this is a GET request where the user can specify filters. Currently the filters are parsed and then appropriately a SQL query is constructed. However, this is not scalable. The ideal scenario would be to setup a graphQL or an openAPI, which is able to convert the API requests directly into an SQL query and retrieves the data


## Scalability:
The flask server needs to be wrapped with an nginx to make it a webserver. 
The number of nodes (servers) can be increased and a load balancer can be put infront of it. The load balancer can have a hashed map of imei devices to the server instance.

There can be a separate auth server will take care of the authentication, so that the microservices inbetween doesn't need to worry about it.

The SQL server can have a redis infront of it, to increase the query time
There can be a cache infront of the secondary storage that has recently visited files with LRU policy

The mongoDb allows scalability, and as the coordinates for a particular device increases, then a separate node can be initialized for new coordinates. This way each node contains the locations for a particular daterange, given that the user is likely to query on date. Otherwise the nodes can be initialized based on proximity of the coordinates
















