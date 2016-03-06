import React from 'react';

import DocumentTitle from 'react-document-title';
import reactMixin from 'react-mixin';

import AppBar from 'material-ui/lib/app-bar';
import {cyan500} from 'material-ui/lib/styles/colors';
import getMuiTheme from 'material-ui/lib/styles/getMuiTheme';
import IconButton from 'material-ui/lib/icon-button';
import IconMenu from 'material-ui/lib/menus/icon-menu';
import LeftNav from 'material-ui/lib/left-nav';
import MenuItem from 'material-ui/lib/menus/menu-item';
import MoreVertIcon from 'material-ui/lib/svg-icons/navigation/more-vert';
import { Spacing, Typography } from 'material-ui/lib/styles';

import {sessionLogout} from '../actions';
import Resizable from '../mixins/resizable';

class Layout extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			deviceSize:  Resizable.statics.Sizes.SMALL,
			muiTheme:    getMuiTheme(),
			sideNavOpen: false
		};
	}

	getChildContext() {
		return {
			muiTheme: this.state.muiTheme
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

	onClickLogout() {
		const store = this.context.store;

		store.dispatch(sessionLogout(store.getState().session.authToken));
		this.context.router.push('/login')
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
								iconElementRight={this.renderAppMenu()}
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

	renderAppMenu() {
		return (
			<IconMenu
				iconButtonElement={<IconButton><MoreVertIcon /></IconButton>}
				targetOrigin={{horizontal: 'right', vertical: 'top'}}
				anchorOrigin={{horizontal: 'right', vertical: 'top'}}>
				<MenuItem
						primaryText="Logout"
						onTouchTap={this.onClickLogout.bind(this)} />
			</IconMenu>
		);
	}
}

Layout.contextTypes = {
	router: React.PropTypes.object.isRequired,
	store:  React.PropTypes.object.isRequired
};

Layout.childContextTypes = {
	muiTheme: React.PropTypes.object
};

reactMixin(Layout.prototype, Resizable);

export default Layout;

