module.exports = {
    // presets: ['@babel/preset-env', '@babel/preset-react'],
    "presets": [
        "@babel/preset-env",
        "@babel/preset-react"
    ],
    "plugins": [
        [
          "@babel/plugin-proposal-class-properties"
        ]
    ],
    "setupFiles": [
        "./setupTests"
    ]
  };