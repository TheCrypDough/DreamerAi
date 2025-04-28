const rules = require('./webpack.rules'); // Path will be adjusted later
const plugins = require('./webpack.plugins'); // Path will be adjusted later
const path = require('path'); // Keep if path needed

rules.push({
  test: /\.jsx?$/,
  use: {
    loader: 'babel-loader',
    options: {
      exclude: /node_modules/,
      presets: ['@babel/preset-react']
    }
  }
});

// Push CSS rule (likely needed)
rules.push({
  test: /\.css$/,
  use: [{ loader: 'style-loader' }, { loader: 'css-loader' }],
});

module.exports = {
  module: {
    rules, // Load rules from webpack.rules.js
  },
  plugins: plugins,
  resolve: {
    // Keep standard extensions
    extensions: ['.js', '.jsx', '.json', '.css'],
    fallback: { "http": false }
  },
}; 