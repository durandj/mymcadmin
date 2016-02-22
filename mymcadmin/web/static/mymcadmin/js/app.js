(function () {
	'use strict';

	angular
		.module('MyMCAdminApp', ['ngMaterial'])
		.config(function($mdThemingProvider, $mdIconProvider) {
			$mdThemingProvider.theme('default')
				.primaryPalette('deep-purple')
				.accentPalette('indigo')
				.warnPalette('red')
				.backgroundPalette('grey', {
					'default': '900',
					'hue-1': '800',
					'hue-2': '700',
					'hue-3': '600'
				})
				.dark();
		});
})();

