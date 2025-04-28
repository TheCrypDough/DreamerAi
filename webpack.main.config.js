const path = require('path');

console.log('[webpack.main.config.js] __dirname:', __dirname);
const outputPath = path.join(__dirname, '.webpack/main');
console.log('[webpack.main.config.js] Calculated Output Path:', outputPath);

module.exports = {
  /**
   * This is the main entry point for your application, it's the first file
   * that runs in the main process.
   */
  entry: './app/main.js', // Updated path: source file is in app/
  // Put your normal webpack config below here
  module: {
    rules: require('./webpack.rules'), // Correct: root config file
  },
  // Add externals for native modules used in main process
  externals: {
    keytar: 'commonjs keytar',
  },
  // --- ADDED Standard Output Config --- //
  output: {
    // The build folder.
    path: outputPath,
    filename: 'index.js',
    libraryTarget: 'commonjs2', // Ensure compatibility with Node.js require
  },
  // --- End Added Output Config --- //
  // Important: target should be electron-main if not default
  // target: 'electron-main',
  resolve: {
    extensions: ['.js', '.jsx', '.json', '.ts', '.tsx', '.node']
  }
}; 