const notepack = require('notepack.io');
const fs = require('fs');

const data = {
    players: {
        "tArphNVaj": { x: 374.7773251044672, y: 589.3866494103577 }
    },
    mapWidth: 800,
    mapHeight: 600
};

const encoded = notepack.encode(data);
fs.writeFileSync('packed.bin', encoded);
console.log('Data serialized and saved to packed.bin');