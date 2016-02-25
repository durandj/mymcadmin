import angular from 'angular';

// Basic page requirements
import 'angular-material/angular-material.css';
import 'angular-animate';
import 'angular-aria';
import 'angular-material';
import 'angular-route';
import 'mymcadmin/less/app.less';

import rootTemplateUrl from 'mymcadmin/partials/root.html';

console.log(rootTemplateUrl.path);

angular
	.module('MyMCAdminApp', ['ngMaterial', 'ngRoute'])
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
	})
	.config(($routeProvider) => {
		$routeProvider
			.when('/', {
				templateUrl: rootTemplateUrl
			})
			.otherwise({
				redirectTo: '/' // TODO(durandj): maybe we want an error page?
			});
	});

