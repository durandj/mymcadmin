'use strict';

var autoprefixer  = require('autoprefixer');
var BundleTracker = require('webpack-bundle-tracker');
var LessCleanCSS  = require('less-plugin-clean-css');
var NgAnnotate    = require('ng-annotate-webpack-plugin');
var path          = require('path');
var webpack       = require('webpack');

// Identify the NPM lifecycle event to figure out our environment
var ENV = process.env.npm_lifecycle_event;

/*
 * The ideas behind this config were brought together from:
 * http://owaislone.org/blog/modern-frontends-with-django/
 * http://owaislone.org/blog/webpack-plus-reactjs-and-django/
 * http://angular-tips.com/blog/2015/06/using-angular-1-dot-x-with-es6-and-webpack/
 */

module.exports = (function () {
	/**
	 * Config
	 * Reference: http://webpack.github.io/docs/configuration.html
	 * This is the object where all configurations go
	 */
	var config = {};

	/**
	 * Context
	 * Reference: http://webpack.github.io/docs/configuration.html#context
	 * This is the base directory that everything uses as reference
	 */
	config.context = __dirname;

	/**
	 * Entry
	 * Reference: http://webpack.github.io/docs/configuration.html#entry
	 * This is where all the entry points live
	 */
	config.entry = [
		'./assets/mymcadmin/js/app.js',
	];

	/**
	 * Output
	 * Reference: http://webpack.github.io/docs/configuration.html#output
	 * This is how we configure the output for webpack
	 */
	config.output = {
		path:     path.resolve('./assets/bundles'),
		filename: '[name]-[hash].js'
	};

	/**
	 * Devtool
	 * Reference: http://webpack.github.io/docs/configuration.html#devtool
	 * Type of sourcemap to use per build type
	 */
	if (ENV === 'test') {
		config.devtool = 'inline-source-map';
	}
	else if (ENV === 'build') {
		config.devtool = 'source-map';
	}
	else {
		config.devtool = 'eval-source-map';
	}

	/**
	 * Module
	 * Reference: http://webpack.github.io/docs/configuration.html#module
	 * Configuration for how modules are handled
	 */
	config.module = {
		/**
		 * Loaders
		 * Reference: http://webpack.github.io/docs/configuration.html#module-loaders
		 * Configures how modules are loaded and processed
		 */
		loaders: [
			/**
			 * Babel Loader
			 * Reference: https://github.com/babel/babel-loader
			 * Transpiles .js files for ES6/ES7 to ES5
			 */
			{
				test: /\.js$/,
				loader: 'babel',
				exclude: /node_modules/
			},

			/**
			 * Less Loader
			 * Reference: https://github.com/webpack/less-loader
			 * Reference: https://github.com/webpack/css-loader
			 * Reference: https://github.com/webpack/extract-text-webpack-plugin
			 * Allow loading of Less through JS
			 */
			{
				test: /\.less$/,
				loaders: [
					'style',
					'css?sourceMap!postcss',
					'less?sourceMap'
				]
			},

			/**
			 * CSS Loader
			 * Reference: https://github.com/webpack/css-loader
			 * Reference: https://github.com/webpack/style-loader
			 * Reference: https://github.com/webpack/extract-text-webpack-plugin
			 * Allow loading of CSS through JS
			 */
			{
				test: /\.css$/,
				loaders: [
					'style',
					'css?sourceMap!postcss'
				]
			},

			/**
			 * Asset Loader
			 * Reference: https://github.com/webpack/file-loader
			 * Allow loading of file assets via JS
			 */
			{
				test: /\.(png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/,
				loader: 'file'
			}
		]
	};

	/**
	 * Resolve
	 * Reference: http://webpack.github.io/docs/configuration.html#resolve
	 * Configration for how modules are resolved
	 */
	config.resolve = {
		/**
		 * root
		 * Reference: http://webpack.github.io/docs/configuration.html#resolve-root
		 * Root absolute directory of project modules
		 */
		root: path.resolve('./assets/')
	};

	/**
	 * Less Plugins
	 * Reference: https://github.com/webpack/less-loader#less-plugins
	 * Plugins for the Less compiler
	 */
	config.lessLoader = {
		lessPlugins: [
			new LessCleanCSS({advanced: true})
		]
	};

	/**
	 * PostCSS
	 * Reference: https://github.com/postcss/autoprefixer-core
	 * Add vencor prefixes to CSS
	 */
	config.postcss = [
		autoprefixer({
			browsers: ['last 2 versions']
		})
	];

	/**
	 * Plugins
	 * Reference: http://webpack.github.io/docs/configuration.html#plugins
	 * Webpack plugins (see http://webpack.github.io/docs/list-of-plugins.html)
	 */
	config.plugins = [
		/**
		 * Reference: https://github.com/owais/webpack-bundle-tracker
		 * Generates outputs stats about webpack builds for tracking purposes
		 */
		new BundleTracker({filename: './runtime/webpack-stats.json'}),

		/**
		 * Reference: https://github.com/olov/ng-annotate
		 * Manages Angular dependency injection for minification
		 */
		new NgAnnotate({add: true})
	];

	if (ENV === 'build') {
		config.plugins.push(
			/**
			 * Reference: http://webpack.github.io/docs/list-of-plugins.html#noerrorsplugin
			 * Only emit files when there are no errors
			 */
			new webpack.NoErrorsPlugin(),

			/**
			 * Reference: http://webpack.github.io/docs/list-of-plugins.html#dedupeplugin
			 * Dedupe modules in the output
			 */
			new webpack.optimize.DedupePlugin(),

			/**
			 * Reference: http://webpack.github.io/docs/list-of-plugins.html#uglifyjsplugin
			 * Minify all JS that is emitted
			 */
			new webpack.optimize.UglifyJsPlugin()
		);
	}

	return config;
})();

