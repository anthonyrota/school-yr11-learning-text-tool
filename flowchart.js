const fsS = require('fs');
const fs = require('fs').promises;
const stdin = process.openStdin();
const { exec } = require('child_process');
const { promisify } = require('util');
const execP = promisify(exec);
const pLimit = require('p-limit');
const ProgressBar = require('progress');
let data = '';

stdin.on('data', (chunk) => {
    data += chunk;
});

stdin.on('end', async () => {
    const fcs = JSON.parse(data);
    if (!fsS.existsSync('./fc_img')) {
        await fs.mkdir('./fc_img');
    }
    function getFlowchartPath(i, j) {
        return `./fc_img/${i
            .toString()
            .padStart(2, '0')}-${j.toString().padStart(2, '0')}.flowchart`;
    }
    function getSvgPath(i, j) {
        return `./fc_img/${i
            .toString()
            .padStart(2, '0')}-${j.toString().padStart(2, '0')}.svg`;
    }
    const promises = [];
    const limit = pLimit(10);
    let total = 0;
    fcs.forEach((fcg, i) => {
        fcg.forEach((fc, j) => {
            const fcPath = getFlowchartPath(i, j);
            const svgPath = getSvgPath(i, j);
            total++;
            promises.push(
                limit(() =>
                    fs
                        .writeFile(fcPath, fc, 'utf8')
                        .then(() =>
                            execP(
                                `./node_modules/.bin/diagrams flowchart ${fcPath} ${svgPath}`,
                            ),
                        )
                        .then(() => fs.unlink(fcPath))
                        .then(() => bar.tick()),
                ),
            );
        });
    });
    const bar = new ProgressBar('generating flowcharts |:bar| :percent', {
        total,
    });
    await Promise.all(promises);
});
