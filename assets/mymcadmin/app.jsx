import React from 'react';
import ReactDOM from 'react-dom';
import injectTapEventPlugin from 'react-tap-event-plugin';

// Needed for onTouchTap
// Can go away when react 1.0 release
// Check this repo:
// https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin(); // Needed for onTouchTap

import {createHashHistory} from 'history';
import DocumentTitle from 'react-document-title';
import reactMixin from 'react-mixin';
import {
	Router,
	Route,
	IndexRoute,
	useRouterHistory
} from 'react-router';

import AppBar from 'material-ui/lib/app-bar';
import {cyan500} from 'material-ui/lib/styles/colors';
import getMuiTheme from 'material-ui/lib/styles/getMuiTheme';
import LeftNav from 'material-ui/lib/left-nav';
import MenuItem from 'material-ui/lib/menus/menu-item';
import { Spacing, Typography } from 'material-ui/lib/styles';

import Dashboard from './components/pages/dashboard';
import Login from './components/pages/login';
import Resizable from './mixins/resizable';

class MyMCAdminApp extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			deviceSize:  Resizable.statics.Sizes.SMALL,
			muiTheme:    getMuiTheme(),
			sideNavOpen: false
		};
	}

	onToggleNav() {
		this.setState({
			sideNavOpen: !this.state.sideNavOpen
		});
	}

	onNavRequestChange(isOpen) {
		this.setState({
			sideNavOpen: isOpen
		});
	}

	onClickNavLogo() {
		this.context.router.push('/');
		this.onNavRequestChange(false);
	}

	getStyles() {
		return {
			layout: {
				height: '100%'
			},
			appBar: {
				position: 'fixed',
				top:      0,
				zIndex:   this.state.muiTheme.zIndex.appBar + 1
			},
			leftNavLogo: {
				cursor:       'pointer',
				fontSize:     24,
				color:        Typography.textFullWhite,
				lineHeight:   `${Spacing.desktopKeylineIncrement}px`,
				fontWeight:   Typography.fontWeightLight,
				background:   cyan500,
				paddingLeft:  Spacing.desktopGutter,
				marginBottom: 8
			},
			main: {
				display:       'flex',
				flexDirection: 'row',
				height:        '100%',
				paddingTop:    Spacing.desktopKeylineIncrement,
			},
			mainContent: {
				display: 'flex',
				flex:    1,
				margin:  Spacing.desktopGutter
			}
		};
	}

	render() {
		let styles = this.getStyles();

		let showMenuIcon = true;

		let navDocked = false;
		let navOpen   = this.state.sideNavOpen;

		if (this.isDeviceSize(Resizable.statics.Sizes.LARGE)) {
			styles.leftNav = {
				zIndex: styles.appBar.zIndex - 1
			};

			styles.main.paddingLeft = 256;

			showMenuIcon = false;

			navDocked = true;
			navOpen   = true;
		}

		return (
			<DocumentTitle title="MyMCAdmin">
				<div style={styles.layout}>
					<header>
						<AppBar
								title="MyMCAdmin"
								showMenuIconButton={showMenuIcon}
								style={styles.appBar}
								zDepth={0}
								onLeftIconButtonTouchTap={this.onToggleNav.bind(this)} />
					</header>
					<aside>
						<LeftNav
								docked={navDocked}
								open={navOpen}
								style={styles.leftNav}
								onRequestChange={this.onNavRequestChange.bind(this)}>
								<div style={styles.leftNavLogo} onTouchTap={this.onClickNavLogo.bind(this)}>
									MyMCAdmin
								</div>
							<MenuItem>TODO</MenuItem>
						</LeftNav>
					</aside>
					<main style={styles.main}>
						<div style={styles.mainContent}>
							{ this.props.children }
						</div>
					</main>
				</div>
			</DocumentTitle>
		);
	}
}

MyMCAdminApp.contextTypes = {
	router: React.PropTypes.object.isRequired
};

MyMCAdminApp.childContextTypes = {
	muiTheme: React.PropTypes.object
};

reactMixin(MyMCAdminApp.prototype, Resizable);

ReactDOM.render(
	<Router
			history={useRouterHistory(createHashHistory)({queryKey: false})}
			onUpdate={() => window.scrollTo(0, 0)}>
		<Route path="/" component={MyMCAdminApp}>
			<IndexRoute component={Dashboard} />
			<Route path="login" component={Login} />
		</Route>
	</Router>,
	document.getElementById('app')
);

