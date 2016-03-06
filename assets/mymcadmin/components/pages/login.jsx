import React from 'react';

import DocumentTitle from 'react-document-title';

import Paper from 'material-ui/lib/paper';
import RaisedButton from 'material-ui/lib/raised-button';
import TextField from 'material-ui/lib/text-field';

import Form from '../form';
import {sessionLogin} from '../../actions';

class Login extends React.Component {
	componentDidMount() {
		this.unsubscribe = this.context.store.subscribe(this.onStoreUpdate.bind(this));
	}

	componentWillUnmount() {
		this.unsubscribe();
	}

	onStoreUpdate() {
		const sessionState = this.context.store.getState().session;
		const meta         = sessionState.meta;

		if (meta.dirty || meta.inProgress && !meta.lastUpdated) {
			return;
		}

		this.context.router.push('/');
	}

	getStyles() {
		return {
			wrapper: {
				alignItems:     'center',
				display:        'flex',
				height:         '100vh',
				justifyContent: 'center',
			},
			paper: {
				display: 'inline-block',
				padding: '24px'
			},
			textField: {
				display: 'block'
			},
			raisedButton: {
				display: 'block'
			}
		};
	}

	render() {
		let styles = this.getStyles();

		return (
			<DocumentTitle title="Login">
				<div style={styles.wrapper}>
					<Form submitAction={sessionLogin} storeState="session">
						<Paper zDepth={2} style={styles.paper}>
							<h3>Login</h3>
							<TextField
								name="username"
								hintText="Username"
								required
								style={styles.textField} />
							<TextField
								name="password"
								type="password"
								hintText="Password"
								required
								style={styles.textField} />
							<RaisedButton
								label="Login"
								primary={true}
								type="submit"
								style={styles.raisedButton} />
						</Paper>
					</Form>
				</div>
			</DocumentTitle>
		);
	}
}

Login.contextTypes = {
	router: React.PropTypes.object.isRequired,
	store:  React.PropTypes.object.isRequired
};

export default Login;

