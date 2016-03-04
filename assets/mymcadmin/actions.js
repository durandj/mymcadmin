import fetch from 'isomorphic-fetch';

export const SESSION_LOGIN          = 'SESSION_LOGIN';
export const SESSION_LOGIN_PROGRESS = 'SESSION_LOGIN_PROGRESS';
export const SESSION_LOGIN_SUCCESS  = 'SESSION_LOGIN_SUCCESS';
export const SESSION_LOGIN_FAILURE  = 'SESSION_LOGIN_FAILURE';
export const SESSION_LOGOUT         = 'SESSION_LOGOUT';
export const SESSION_LOGOUT_SUCCESS = 'SESSION_LOGOUT_SUCCESS';
export const SESSION_LOGOUT_FAILURE = 'SESSION_LOGOUT_FAILURE';

export const sessionLogin = (credentials) => {
	return (dispatch) => {
		dispatch(sessionLoginProgress());

		return fetch('/rest-auth/login/', {
			method: 'post',
			headers: {
				'Accept':       'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(credentials)
		}).then((response) => {
			if (response.status >= 400) {
				dispatch(sessionLoginFailure(response));
			}
			else {
				dispatch(sessionLoginSuccess(response.json()));
			}
		});
	};
};

export const sessionLoginProgress = () => {
	return {
		type: SESSION_LOGIN_PROGRESS
	};
};

export const sessionLoginSuccess = () => {
	return {
		type: SESSION_LOGIN_SUCCESS
	};
};

export const sessionLoginFailure = () => {
	return {
		type: SESSION_LOGIN_FAILURE
	};
};

export const sessionLogout = () => {
	return {
		type: SESSION_LOGOUT
	};
};

export const sessionLogoutSuccess = () => {
	return {
		type: SESSION_LOGOUT_SUCCESS
	};
};

export const sessionLogoutFailure = () => {
	return {
		type: SESSION_LOGOUT_FAILURE
	};
};

