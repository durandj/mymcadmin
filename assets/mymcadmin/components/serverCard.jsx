import React from 'react';

import Card from 'material-ui/lib/card/card';
import CardActions from 'material-ui/lib/card/card-actions';
import CardText from 'material-ui/lib/card/card-text';
import CardTitle from 'material-ui/lib/card/card-title';
import FlatButton from 'material-ui/lib/flat-button';

const serverCardStyles = {
	margin:   '8px',
	minWidth: '225px'
};

const cardLabelStyles = {
	display:      'inline-block',
	paddingRight: '4px',
	textAlign:    'right',
	width:        '48px'
};

class ServerCard extends React.Component {
	onClickStart() {
		alert('TODO(durandj): start ' + this.props.server.server_id);
	}

	onClickStop() {
		alert('TODO(durandj): stop ' + this.props.server.server_id);
	}

	onClickRestart() {
		alert('TODO(durandj): restart ' + this.props.server.server_id);
	}

	render() {
		let { server, ...otherProps } = this.props;

		return (
			<Card style={serverCardStyles}>
				<CardTitle title={server.server_id} />
				<CardText>
					<div>
						<label style={cardLabelStyles}>
							Status:
						</label>
						<span>{server.status}</span>
					</div>
					<div>
						<label style={cardLabelStyles}>
							Players:
						</label>
						<span>
							{server.players.online}/{server.players.max}
						</span>
					</div>
				</CardText>
				<CardActions>
					{this.renderActionButtons()}
				</CardActions>
			</Card>
		);
	}

	renderActionButtons() {
		if (this.props.server.status === 'Running') {
			return [
				<FlatButton
					key="stop"
					label="Stop"
					onTouchTap={this.onClickStop.bind(this)} />,
				<FlatButton
					key="restart"
					label="Restart"
					onTouchTap={this.onClickRestart.bind(this)} />
			];
		}
		else {
			return (
				<FlatButton
					key="start"
					label="Start"
					onTouchTap={this.onClickStart.bind(this)} />
			);
		}
	}
}

ServerCard.propTypes = {
	server: React.PropTypes.object.isRequired
};

export default ServerCard;

