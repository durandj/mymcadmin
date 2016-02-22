(function () {
	'use strict';

	angular
		.module('MyMCAdminApp', ['ngMaterial'])
		.config(function($mdThemingProvider, $mdIconProvider) {
			$mdThemingProvider.theme('dark')
				.primaryPalette('purple', {
					'default': '900',
					'hue-1': '800',
					'hue-2': '700',
					'hue-3': '600'
				})
				.accentPalette('purple', {
					'default': '900',
					'hue-1': '800',
					'hue-2': '700',
					'hue-3': '600'
				})
				.backgroundPalette('grey', {
					'default': '500',
					'hue-1': '400',
					'hue-2': '300',
					'hue-3': '200'
				})
				.dark();

			$mdThemingProvider.setDefaultTheme('dark');
			//$mdThemingProvider.theme('default')
				//.primaryPalette('blue')
				//.accentPalette('red')
				//.backgroundPalette('grey');
		});
})();

