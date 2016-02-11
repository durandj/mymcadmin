# Contributing

## Testing

Recommended command for running tests is:

	nosetests --with-coverage --cover-package=mymcadmin --cover-min-percentage=95 --rednose

This is the command that the build server will run so if it doesn't pass
locally it won't pass on the server.

## Test Sizes

### Small

Typically what people think of when they think of unit tests. Small tests only
test individual methods and functions in isolation. Everything else should be
mocked as much as possible.

### Medium

Medium size tests serve to confirm that interactions between components are
working correctly.

### Large

Large size tests assert that the system runs correctly in a production style
environment. This is very close to how it would perform in the real world.

