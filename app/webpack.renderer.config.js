const rules = require('./webpack.rules');

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

module.exports = {
  // Put your normal webpack config below here
  module: {
    rules,
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css', '.json'] // Added .jsx
  },
  externals: {
    // Exclude Node.js built-in modules like 'http' from the bundle
    // as Electron's renderer process can access them directly
    http: 'commonjs http',
  }
}; 