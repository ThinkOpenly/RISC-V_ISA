# ISA

Power ISA

# create ISA.json

```
$ (cat PPC1_ChFixedPt.mif PPC_ApInstMnem.mif ) | ./utils/mif2json.py > ./src/ISA.json
```

## Run Local React Environment

### 1. Once you have cloned the repo, navigate to the same directory as package.json and run

```
npm i
```

### 2. After npm installs your dependencies, run

```
npm run local
```

This will create a local react server at localhost:3000 by default.

Navigate to that address in your favorite browser to interact with the UI.
While running in this local dev environment, any code changes will cause a quick
server restart on save, so you can quickly tweak UI code to your specifications
