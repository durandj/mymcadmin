export const requireLogin = (store) => {
	return (nextState, replace) => {
		let state = store.getState();

		if (!state.session.authToken) {
			replace({
				pathname: '/login'
			});
		}
	};
};

