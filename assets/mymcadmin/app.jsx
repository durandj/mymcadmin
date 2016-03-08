require('es6-promise').polyfill();

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

import { applyMiddleware, compose, createStore } from 'redux';
import createLogger from 'redux-logger';
import {Provider} from 'react-redux';
import thunkMiddleware from 'redux-thunk';

import getMuiTheme from 'material-ui/lib/styles/getMuiTheme';

import Dashboard from './components/pages/dashboard';
import Layout from './components/layout';
import Login from './components/pages/login';
import reducers from './reducers';
import {requireLogin} from './utils';

class App extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			muiTheme: getMuiTheme()
		};
	}

	componentWillMount() {
		// TODO(durandj): use build environment to set logger configuration
		const loggerMiddleware = createLogger(
			{
				level:     'log',
				duration:  true,
				timestamp: true
			}
		);

		// TODO(durandj): only add devtools in dev
		this.store = createStore(
			reducers,
			compose(
				applyMiddleware(
					thunkMiddleware,
					loggerMiddleware
				),
				typeof window === 'object' && typeof window.devToolsExtension !== 'undefined' ? window.devToolsExtension() : f => f
			)
		);
	}

	getChildContext() {
		return {
			muiTheme: this.state.muiTheme
		};
	}

	render() {
		return (
			<Provider store={this.store}>
				<Router
						history={useRouterHistory(createHashHistory)({queryKey: false})}
						onUpdate={() => window.scrollTo(0, 0)}>
					<Route path="/login" component={Login} />
					<Route path="/" component={Layout}>
						<IndexRoute
								component={Dashboard}
								onEnter={requireLogin(this.store)} />
					</Route>
				</Router>
			</Provider>
		);
	}
}

App.childContextTypes = {
	muiTheme: React.PropTypes.object
};

ReactDOM.render(
	<App />,
	document.getElementById('app')
);

