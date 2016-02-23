import angular from 'angular';

// Basic page requirements
import 'angular-material/angular-material.css';
import 'angular-animate';
import 'angular-aria';
import 'angular-material';

angular
	.module('MyMCAdminApp', ['ngMaterial'])
	.config(($mdThemingProvider, $mdIconProvider) => {
		$mdThemingProvider.theme('default')
			.primaryPalette('deep-purple')
			.accentPalette('indigo')
			.warnPalette('red')
			.backgroundPalette('grey', {
				'default': '900',
				'hue-1':   '800',
				'hue-2':   '700',
				'hue-3':   '600'
			})
			.dark();
	});

