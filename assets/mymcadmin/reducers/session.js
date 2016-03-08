import {
	SESSION_LOGIN,
	SESSION_LOGIN_PROGRESS,
	SESSION_LOGIN_SUCCESS,
	SESSION_LOGIN_FAILURE,
	SESSION_LOGOUT_SUCCESS,
	SESSION_LOGOUT_FAILURE
} from '../actions';

const defaultSessionState = {
	meta: {
		dirty:       true,
		inProgress:  false,
		lastUpdated: null,
		error:       null
	}
};

// jshint -W138
const session = (session = defaultSessionState, action) => {
	switch (action.type) {
		case SESSION_LOGIN_PROGRESS:
			return Object.assign({}, session, {
				meta: {
					dirty:       true,
					inProgress:  true,
					lastUpdated: null,
					error:       null
				}
			});
		case SESSION_LOGIN_SUCCESS:
			return Object.assign({}, session, {
				meta: {
					dirty:       false,
					inProgress:  false,
					lastUpdated: new Date(),
					error:       null
				}
			}, action.data);
		case SESSION_LOGIN_FAILURE:
			return Object.assign({}, session, {
				meta: {
					dirty:       false,
					inProgress:  false,
					lastUpdated: new Date(),
					error:       action.data
				}
			});
		case SESSION_LOGOUT_SUCCESS:
			return {
				meta: {
					dirty:       false,
					inProgress:  false,
					lastUpdated: new Date(),
					error:       null
				}
			};
		case SESSION_LOGOUT_FAILURE:
			throw new Error('Not implemented error'); // TODO(durandj): implement
		default:
			return session;
	}
};
// jshint +W138

export default session;
