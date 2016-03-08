import React from 'react';

import DocumentTitle from 'react-document-title';

import Paper from 'material-ui/lib/paper';
import RaisedButton from 'material-ui/lib/raised-button';

import FormsyText from 'formsy-material-ui/lib/FormsyText';

import Form from '../form';
import {sessionLogin} from '../../actions';

class Login extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			isValid: false
		};
	}

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

		this.setState({error: meta.error});
		if (!meta.error) {
			this.context.router.push('/');
		}
	}

	onFormValid() {
		this.setState({isValid: true});
	}

	onFormInvalid() {
		this.setState({isValid: false});
	}

	getStyles() {
		const muiTheme = this.context.muiTheme;

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
			formErrors: {
				color: muiTheme.textField.errorColor
			},
			username: {
				display: 'block'
			},
			password: {
				display: 'block',
				marginBottom: '14px'
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
					<Form
							submitAction={sessionLogin}
							storeState="session"
							onValid={this.onFormValid.bind(this)}
							onInvalid={this.onFormInvalid.bind(this)}>
						<Paper zDepth={2} style={styles.paper}>
							<h3>Login</h3>
							<div style={styles.formErrors}>
								{this.state.error}
							</div>
							<FormsyText
								name="username"
								hintText="Username"
								floatingLabelText="Username"
								validationError="Username is required"
								required
								style={styles.username} />
							<FormsyText
								name="password"
								type="password"
								hintText="Password"
								floatingLabelText="Password"
								validationError="Password is required"
								required
								style={styles.password} />
							<RaisedButton
								label="Login"
								primary={true}
								type="submit"
								disabled={!this.state.isValid}
								style={styles.raisedButton} />
						</Paper>
					</Form>
				</div>
			</DocumentTitle>
		);
	}
}

Login.contextTypes = {
	muiTheme: React.PropTypes.object.isRequired,
	router:   React.PropTypes.object.isRequired,
	store:    React.PropTypes.object.isRequired
};

export default Login;

