import React from 'react';

import ServerCard from '../serverCard';

const dashboardGridStyles = {
	display:        'flex',
	flexWrap:       'wrap',
	justifyContent: 'center'
};

class Dashboard extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			servers: []
		};

		// TODO(durandj): remove after debugging
		function randInt(max, min) {
			min = min || 0;

			let magnitude = Math.pow(10, Math.floor(Math.log10(max)) + 1);
			let range     = max - min;

			return Math.floor(Math.random() * magnitude) % range + min;
		}

		let servers = randInt(5, 15);
		for (let i = 0; i != servers; i++) {
			let state = ['Running', 'Stopped'][randInt(2)];

			this.state.servers.push({
				server_id: 'server_' + i,
				status:    state,
				players:   {
					online: state === 'Running' ? randInt(20) : 0,
					max:    20
				}
			});
		}
	}

	render() {
		return (
			<div style={dashboardGridStyles}>
				{this.renderServerCards()}
			</div>
		);
	}

	renderServerCards() {
		return this.state.servers.map((server) => {
			return (
				<ServerCard key={server.server_id} server={server} />
			);
		});
	}
}

export default Dashboard;

