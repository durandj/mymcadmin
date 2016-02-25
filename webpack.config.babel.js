'use strict';

import autoprefixer from 'autoprefixer';
import BundleTracker from 'webpack-bundle-tracker';
import LessCleanCSS from 'less-plugin-clean-css';
import NgAnnotate from 'ng-annotate-webpack-plugin';
import path from 'path';
import webpack from 'webpack';

/*
 * The ideas behind this config were brought together from:
 * http://owaislone.org/blog/modern-frontends-with-django/
 * http://owaislone.org/blog/webpack-plus-reactjs-and-django/
 * http://angular-tips.com/blog/2015/06/using-angular-1-dot-x-with-es6-and-webpack/
 */

/**
 * Get the build environment. Expected values are "prod", "test", and "dev".
 * The default is "prod".
 */
const ENV = process.env.BUILD_TYPE || 'prod';
if (ENV !== 'prod' && ENV !== 'test' && ENV !== 'dev') {
	console.error(ENV + ' is not a valid build type');
	process.exit(1);
}

export default (() => {
	/*
	 * The ideas behind this config were brought together from:
	 * http://owaislone.org/blog/modern-frontends-with-django/
	 * http://owaislone.org/blog/webpack-plus-reactjs-and-django/
	 * http://angular-tips.com/blog/2015/06/using-angular-1-dot-x-with-es6-and-webpack/
	 */
	let config = {};

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
	config.entry = {
		mymcadmin: [
			'./assets/mymcadmin/js/app.js',
			'./assets/mymcadmin/js/controllers.js'
		]
	};

	/**
	 * Output
	 * Reference: http://webpack.github.io/docs/configuration.html#output
	 * This is how we configure the output for webpack
	 */
	config.output = {
		path:     path.resolve('./runtime/bundles'),
		filename: ENV === 'prod' ? '[name].[chunkhash].js' : '[name].js',
		pathinfo: ENV !== 'prod'
	};

	/**
	 * Devtool
	 * Reference: http://webpack.github.io/docs/configuration.html#devtool
	 * Type of sourcemap to use per build type
	 */
	if (ENV === 'test') {
		config.devtool = 'inline-source-map';
	}
	else if (ENV === 'prod') {
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
		 * Preloaders
		 * Reference: https://webpack.github.io/docs/configuration.html#module-preloaders-module-postloaders
		 * Configures how we pre-process modules
		 */
		preLoaders: [
			/**
			 * JSCS Loader
			 * Reference: https://github.com/unindented/jscs-loader
			 * Checks that the JS code matches a style guide
			 */
			/**
			 * JSHint Loader
			 * Reference: https://www.npmjs.com/package/jshint-loader
			 * Checks JS code for common JS problems
			 */
			{
				test:    /\.js$/,
				exclude: /node_modules/,
				loaders: [
					'jscs',
					'jshint'
				]
			}
		],

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
			},

			/**
			 * HTML Loader
			 * Reference: https://github.com/WearyMonkey/ngtemplate-loader
			 * Reference: https://github.com/webpack/html-loader
			 * Inlines HTML partials and adds them to the template cache
			 */
			{
				test: /.html$/,
				loaders: [
					'ngtemplate?relativeTo=assets',
					'html'
				]
			}
		]
	};

	if (ENV === 'dev') {
		/**
		 * No Parse
		 * Reference: http://webpack.github.io/docs/configuration.html#module-noparse
		 * Exclude modules from being parsed
		 */
		config.module.noParse = [
			'angular',
			'angular-aria',
			'angular-animate',
			'angular-material'
		];
	}

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
			/**
			 * Reference: https://github.com/less/less-plugin-clean-css
			 * Applies some simple optimizations to Less files
			 */
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
	 * JSHint
	 * Reference: https://github.com/webpack/jshint-loader
	 * Configures how JSHint checks the JS code
	 */
	config.jshint = {
		esversion:  6,
		emitErrors: true,
		failOnHint: true
	};

	/**
	 * JSCS
	 * Reference: https://github.com/jscs-dev/node-jscs
	 * Configures how JSCS checks the JS code
	 */
	config.jscs = {
		emitErrors:          true,
		failOnHint:          true,
		preset:              'google',
		validateIndentation: '\t'
	};

	/**
	 * Plugins
	 * Reference: http://webpack.github.io/docs/configuration.html#plugins
	 * Webpack plugins (see http://webpack.github.io/docs/list-of-plugins.html)
	 */
	config.plugins = [
		/**
		 * Reference: http://webpack.github.io/docs/list-of-plugins.html#prefetchplugin
		 * Prefetches modules to give small improvements in load time
		 */
		new webpack.PrefetchPlugin('angular'),
		new webpack.PrefetchPlugin('angular-animate'),
		new webpack.PrefetchPlugin('angular-aria'),
		new webpack.PrefetchPlugin('angular-material'),
		new webpack.PrefetchPlugin('angular-route'),

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

	if (ENV === 'prod') {
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
			 * Reference: http://webpack.github.io/docs/list-of-plugins.html#occurrenceorderplugin
			 * Orders chunk by how often they are requested in modules
			 */
			new webpack.optimize.OccurrenceOrderPlugin(true),

			/**
			 * Reference: http://webpack.github.io/docs/list-of-plugins.html#commonschunkplugin
			 * Pulls common chunks into a seperate file
			 */
			new webpack.optimize.CommonsChunkPlugin({
				async:    true,
				children: true
			}),

			/**
			 * Reference: http://webpack.github.io/docs/list-of-plugins.html#uglifyjsplugin
			 * Minify all JS that is emitted
			 */
			new webpack.optimize.UglifyJsPlugin()
		);
	}

	return config;
})();

