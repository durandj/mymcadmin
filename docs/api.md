# JSON RPC API

The management process exposes a JSON RPC interface that you can use to
communicate with it. All of the method names and named parameters are in snake
case

## Methods

### list_servers

Lists the available servers

#### Parameters

None

#### Return

A list of server ID's

### server_restart

Restarts a server

#### Parameters

`server_id` - the server ID

#### Return

TODO(durandj): document the return value

### server_restart_all

Restarts all of the running servers

#### Parameters

None

#### Return

A list of servers that were restarted

### server_start

Start a server

#### Parameters

`server_id` - the server ID

#### Return

TODO(durandj): document the return value

### server_start_all

Starts all of the servers that are not already running

#### Parameters

None

#### Return

A list of servers that were started

### server_stop

Stop a server

#### Parameters

`server_id` - the server ID

#### Return

TODO(durandj): document the return value

### server_stop_all

Stops all of the running servers

#### Parameters

None

#### Return

A list of the servers that were stopped

### shutdown

Shutdown the management process

#### Parameters

None

#### Return

A list of the servers that were running and were stopped

