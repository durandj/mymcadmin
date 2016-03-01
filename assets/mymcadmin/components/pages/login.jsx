import React from 'react';

import DocumentTitle from 'react-document-title';

import Paper from 'material-ui/lib/paper';
import RaisedButton from 'material-ui/lib/raised-button';
import TextField from 'material-ui/lib/text-field';

class Login extends React.Component {
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
					<Paper zDepth={2} style={styles.paper}>
						<h3>Login</h3>
						<TextField
							ref="username"
							hintText="Username"
							style={styles.textField} />
						<TextField
							ref="password"
							type="password"
							hintText="Password"
							style={styles.textField} />
						<RaisedButton
							label="Login"
							primary={true}
							style={styles.raisedButton} />
					</Paper>
				</div>
			</DocumentTitle>
		);
	}
}

export default Login;

