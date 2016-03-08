import React from 'react';
import ReactDOM from 'react-dom';

import cookie from 'react-cookie';
import {connect} from 'react-redux';

import Forms from 'formsy-react';

import CircularProgress from 'material-ui/lib/circular-progress';
import Overlay from 'material-ui/lib/overlay';

class Form extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			formData: null,
		};
	}

	componentDidMount() {
		const domNode = ReactDOM.findDOMNode(this);

		let formChildren = Array.prototype.slice.call(domNode.querySelectorAll('[name]'));

		let initialFormData = formChildren.reduce((state, child) => {
			const name = child.getAttribute('name');

			state[name] = child.value;

			return state;
		}, {});

		this.setState({formData: initialFormData});
	}

	onChange(model) {
		if (model.target) {
			return;
		}

		this.setState({
			formData: Object.assign(
				{},
				this.state.formData,
				model
			)
		});
	}

	onSubmit() {
		let { dispatch, submitAction } = this.props;

		dispatch(submitAction(this.state.formData));
	}

	getStyles() {
		return {
			form: {
				position: 'relative'
			},
			loaderWrapper: {
				alignItems:     'center',
				display:        'flex',
				height:         '100%',
				justifyContent: 'center',
				position:       'absolute',
				top:            0,
				width:          '100%',
			},
			loader: {
				zIndex: 1
			},
			overlay: {
				position: 'absolute'
			}
		};
	}

	render() {
		let {
			action,
			method,
			submitAction,
			children,
			style,
			...otherProps
		} = this.props;

		let onSubmit = submitAction ? this.onSubmit.bind(this) : null;

		let styles = this.getStyles();
		styles.form = Object.assign(styles.form, styles || {});

		if (!this.props.loading) {
			styles.loaderWrapper['display'] = 'none';
		}

		return (
			<Formsy.Form
					action={action}
					method={method}
					style={styles.form}
					onChange={this.onChange.bind(this)}
					onValidSubmit={onSubmit}
					{...otherProps}>
				{this.renderCSRFToken()}
				{children}
				{this.renderLoader(styles)}
			</Formsy.Form>
		);
	}

	renderCSRFToken() {
		if (!this.props.csrf) {
			return null;
		}

		let csrfToken = cookie.load('csrftoken');

		return (
			<input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
		);
	}

	renderLoader(styles) {
		return (
			<div style={styles.loaderWrapper}>
				<CircularProgress size={2} style={styles.loader} />
				<Overlay show={true} style={styles.overlay} />
			</div>
		);
	}
}

Form.propTypes = {
	action:       React.PropTypes.string,
	method:       React.PropTypes.string,
	csrf:         React.PropTypes.bool,
	loading:      React.PropTypes.bool,
	submitAction: React.PropTypes.func,
	storeState:   React.PropTypes.string,
	dispatch:     React.PropTypes.func.isRequired
};

Form.defaultProps = {
	method:  'POST',
	csrf:    true,
	loading: false
};

export default connect((state, ownProps) => {
	return {
		loading: state[ownProps.storeState].meta.inProgress
	};
})(Form);

