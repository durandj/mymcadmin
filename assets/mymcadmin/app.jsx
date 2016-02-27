import React from 'react';
import ReactDOM from 'react-dom';
import injectTapEventPlugin from 'react-tap-event-plugin';

// Needed for onTouchTap
// Can go away when react 1.0 release
// Check this repo:
// https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin(); // Needed for onTouchTap

import AppBar from 'material-ui/lib/app-bar';
import LeftNav from 'material-ui/lib/left-nav';
import MenuItem from 'material-ui/lib/menus/menu-item';

import './app.less';

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
					TODO(durandj): do the body
				</main>
			</div>
		);
	}
}

ReactDOM.render(
	<MyMCAdminApp />,
	document.getElementById('app')
);

