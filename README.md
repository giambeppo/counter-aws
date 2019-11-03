# Counter.io - AWS version
A simple counter service based on AWS lambda and DynamoDB.

Allows to create and update counters that are persisted and can be shared.

## Available methods

### Create a counter
* `PUT` http://my.api.gateway?counter=myCounter
* `PUT` http://my.api.gateway?counter=myCounter&value=333

Returns `HTTP 201` if successful, `HTTP 409` if the counter exists already.

New counters are initialized with the value provided in the query parameter, or 0 if the parameter is not provided.

### Get a counter value
* `GET` http://my.api.gateway?counter=myCounter

Returns the value of the counter, or `HTTP 404` if the counter does not exist.

### Update a counter value
All the following methods return `HTTP 404` if the counter does not exist.

#### Increase a counter value
* `GET` http://my.api.gateway?counter=myCounter&after=increment

Increment the value of a counter by 1, returning the new value.

#### Decrease a counter value
* `GET` http://my.api.gateway?counter=myCounter&after=decrement

Decrement the value of a counter by 1, returning the new value.

#### Set a specific counter value
* `POST` http://my.api.gateway?counter=myCounter&value=666
* `GET` http://my.api.gateway?counter=myCounter&after=set&newValue=666

Sets the counter value to the long provided in the query parameter and returns it. 

### Delete a counter
* `DELETE` http://my.api.gateway?counter=myCounter

Returns `HTTP 204` if successful, or `HTTP 404` if the counter does not exist.

