# RISC-V ISA

## Run Local React Environment

Note: These intructions assume you have Node and React installed on your machine. If you do not visit the node.js website and follow
their install instructions. Once Node is installed, you can use the node package manager to install React with the following command

```
npm i react
```

Once you have cloned the repo, navigate to the same directory that contains package.json and run

```
npm i
```

After npm installs your dependencies, run

```
npm run start
```

This will create a local react server at localhost:3000 by default.

Navigate to that address in your favorite browser to interact with the UI.
`npm run start` will automatically launch a browser or browser tab.
While running in this local dev environment, any code changes will cause a quick
server restart on save, so you can quickly tweak UI code to your specifications

## Deploy to GitHub Pages

1. Install gh-pages:
   ```
   $ npm install gh-pages --save-dev
   ```

1. Customize the "homepage" as defined in `package.json`:
   ```
   "homepage": "https://your-username.github.io/your-repository-name"
   ```

1. Build:
   ```
   $ npm run build
   ```

1. Deploy:
   ```
   $ npm run deploy
   ```

1. Enable GitHub Pages:
   1. Settings...
   1. GitHub Pages -> select "gh-pages" branch.
   1. Save.

1. Visit the "homepage" link as defined above.

(_Thanks to ArdeshirV @ https://github.com/orgs/community/discussions/60881 for describing these simple steps!_)

### Redeploy to GitHub Pages after changes

1. Build:
   ```
   $ npm run build
   ```

1. Deploy:
   ```
   $ npm run deploy
   ```
