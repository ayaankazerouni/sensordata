const webpack = require('webpack');

const config = {
  entry: "./src/main.js",
  output: {
    filename: "build/bundle.js"
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
      },
    ]
  },
  resolve: {
    extensions: [ '.js', '.json' ]
  },
}

module.exports = config;
