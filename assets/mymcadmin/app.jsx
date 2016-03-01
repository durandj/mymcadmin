import React from 'react';
import ReactDOM from 'react-dom';
import injectTapEventPlugin from 'react-tap-event-plugin';

// Needed for onTouchTap
// Can go away when react 1.0 release
// Check this repo:
// https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin(); // Needed for onTouchTap

import {createHashHistory} from 'history';
import {
	Router,
	Route,
	IndexRoute,
	useRouterHistory
} from 'react-router';

import Dashboard from './components/pages/dashboard';
import Layout from './components/layout';
import Login from './components/pages/login';
import Resizable from './mixins/resizable';

ReactDOM.render(
	<Router
			history={useRouterHistory(createHashHistory)({queryKey: false})}
			onUpdate={() => window.scrollTo(0, 0)}>
		<Route path="/login" component={Login} />
		<Route path="/" component={Layout}>
			<IndexRoute component={Dashboard} />
		</Route>
	</Router>,
	document.getElementById('app')
);

