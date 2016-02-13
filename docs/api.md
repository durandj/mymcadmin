# JSON RPC API

The management process exposes a JSON RPC interface that you can use to
communicate with it. All of the method names are in camel case. Parameters are
given in snake case

## Methods

### listServers

Lists the available servers

#### Parameters

None

#### Return

A list of server ID's

### serverRestart

Restarts a server

#### Parameters

`server_id` - the server ID

#### Return

TODO(durandj): document the return value

### serverRestartAll

Restarts all of the running servers

#### Parameters

None

#### Return

A list of servers that were restarted

### serverStart

Start a server

#### Parameters

`server_id` - the server ID

#### Return

TODO(durandj): document the return value

### serverStartAll

Starts all of the servers that are not already running

#### Parameters

None

#### Return

A list of servers that were started

### serverStop

Stop a server

#### Parameters

`server_id` - the server ID

#### Return

TODO(durandj): document the return value

### serverStopAll

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

