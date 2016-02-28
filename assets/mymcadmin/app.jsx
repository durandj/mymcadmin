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

import AppBar from 'material-ui/lib/app-bar';
import LeftNav from 'material-ui/lib/left-nav';
import MenuItem from 'material-ui/lib/menus/menu-item';

import Dashboard from './components/pages/dashboard';

class MyMCAdminApp extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			sideNavOpen: false
		};
	}

	toggleNav() {
		this.setState({
			sideNavOpen: !this.state.sideNavOpen
		});
	}

	render() {
		return (
			<div>
				<header>
					<AppBar
							title="MyMCAdmin"
							onLeftIconButtonTouchTap={this.toggleNav.bind(this)} />
				</header>
				<aside>
					<LeftNav open={this.state.sideNavOpen} docked={false}>
						<MenuItem>TODO</MenuItem>
					</LeftNav>
				</aside>
				<main>
					{ this.props.children }
				</main>
			</div>
		);
	}
}

ReactDOM.render(
	<Router
			history={useRouterHistory(createHashHistory)({queryKey: false})}
			onUpdate={() => window.scrollTo(0, 0)}>
		<Route path="/" component={MyMCAdminApp}>
			<IndexRoute component={Dashboard} />
		</Route>
	</Router>,
	document.getElementById('app')
);

