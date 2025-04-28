module.exports = [
  // Add support for native node modules
  {
    // We're specifying native_modules in the test because the asset relocator loader generates a
    // "fake" .node file which is really a cjs file.
    test: /native_modules\/.+\.node$/,
    use: 'node-loader',
  },
  {
    test: /\.node$/,
    loader: 'node-loader',
    options: {
      flags: '-fcommon',
    },
  },
  // { // Temporarily comment out asset relocator for main bundle debug
  //   test: /[\\/]node_modules[\\/].+\.(m?js|node)$/,
  //   parser: { amd: false },
  //   use: {
  //     loader: '@vercel/webpack-asset-relocator-loader',
  //     options: {
  //       outputAssetBase: 'native_modules',
  //     },
  //   },
  // },
  // Add rules for other file types here (e.g. CSS / SCSS)
  // Keep Babel Loader (Crucial for JSX)
  {
    test: /\.jsx?$/,
    exclude: /node_modules/,
    use: {
      loader: 'babel-loader',
      options: { presets: ['@babel/preset-react'] }
    }
  },
  // Keep CSS Loader
  { test: /\.css$/, use: [{ loader: 'style-loader' }, { loader: 'css-loader' }] },
  // Keep Asset Relocator (Crucial for native modules/assets in renderer) - RE-ENABLED
  // { test: /\.(m?js|node)$/, parser: { amd: false }, use: { loader: '@vercel/webpack-asset-relocator-loader', options: { outputAssetBase: 'native_modules' } } }, // Removed due to incompatibility
]; 