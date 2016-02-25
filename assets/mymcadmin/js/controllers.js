import angular from 'angular';

let controllers = angular.module('myMCAdmin.controllers', []);

controllers.controller('RootController', ($scope) => {
	$scope.name = 'James';
});

