const webpack = require('webpack');

const config = {
  entry: "./area_chart.js",
  output: {
    filename: "bundle.js"
  },
  module: {
    rules: [
      {
        test: /\.json$/,
        exclude: /node_modules/,
        loader: 'json-loader',
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      }
    ]
  },
  resolve: {
    extensions: [ '.js', '.json' ]
  },
}

module.exports = config;
