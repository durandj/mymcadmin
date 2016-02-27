import React from 'react';
import ReactDOM from 'react-dom';
import injectTapEventPlugin from 'react-tap-event-plugin';

import AppBar from 'material-ui/lib/app-bar';

class MyMCAdminApp extends React.Component {
	render() {
		return (
			<div>
				<header>
					<AppBar title="MyMCAdmin" />
					TODO(durandj): do the header
				</header>
				<main>
					TODO(durandj): do the body
				</main>
			</div>
		);
	}
}

// Needed for onTouchTap
// Can go away when react 1.0 release
// Check this repo:
// https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin();// Needed for onTouchTap

ReactDOM.render(
	<MyMCAdminApp />,
	document.getElementById('app')
);

