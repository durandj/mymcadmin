import React from 'react';

import MuiTextField from 'material-ui/lib/text-field';

class TextField extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			error: null
		};
	}

	onChange(event) {
		this._validateRequired(event);
	}

	onBlur(event) {
		this._validateRequired(event);
	}

	render() {
		return (
			<MuiTextField
				errorText={this.state.error}
				onChange={this.onChange.bind(this)}
				onBlur={this.onBlur.bind(this)}
				{...this.props} />
		);
	}

	_validateRequired(event) {
		if (!this.props.required) {
			return;
		}

		if (!event.target.value) {
			this.setState({error: 'This field is required'});
		}
		else if (this.state.error) {
			this.setState({error: null});
		}
	}
}

export default TextField;

