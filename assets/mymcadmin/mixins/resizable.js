/**
 * A modified version of MaterialUI's StyleResizable mixin. Their
 * implementation does not play well with ES6 classes.
 */

import Events from 'material-ui/lib/utils/events';

const sizes = {
	SMALL:  1,
	MEDIUM: 2,
	LARGE:  3
};

export default {
	statics: {
		Sizes: sizes
	},
	componentDidMount() {
		this._updateDeviceSize();

		if (!this.manuallyBindResize) {
			this._bindResize();
		}
	},
	componentWillUnmount() {
		this._unbindResize();
	},
	isDeviceSize(desiredSize) {
		return this.state.deviceSize >= desiredSize;
	},
	_updateDeviceSize() {
		const width = window.innerWidth;

		if (width >= 992) {
			this.setState({deviceSize: sizes.LARGE});
		}
		else if (width >= 768) {
			this.setState({deviceSize: sizes.MEDIUM});
		}
		else {
			this.setState({deviceSize: sizes.SMALL});
		}
	},
	_bindResize() {
		Events.on(window, 'resize', this._updateDeviceSize.bind(this));
	},
	_unbindResize() {
		Events.off(window, 'resize', this._updateDeviceSize.bind(this));
	}
};

