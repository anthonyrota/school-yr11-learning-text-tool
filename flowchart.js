const fsS = require('fs');
const fs = require('fs').promises;
const stdin = process.openStdin();
const { exec } = require('child_process');
const { promisify } = require('util');
const execP = promisify(exec);
const pdfkit = require('pdfkit');
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
        return `./fc_img/${i}-${j}.flowchart`;
    }
    function getSvgPath(i, j) {
        return `./fc_img/${i}-${j}.svg`;
    }
    const promises = [];
    fcs.forEach((fcg, i) => {
        fcg.forEach((fc, j) => {
            const fcPath = getFlowchartPath(i, j);
            const svgPath = getSvgPath(i, j);
            promises.push(
                fs
                    .writeFile(fcPath, fc, 'utf8')
                    .then(() =>
                        execP(
                            `./node_modules/.bin/diagrams flowchart ${fcPath} ${svgPath}`,
                        ),
                    )
                    .then(() => fs.unlink(fcPath)),
            );
        });
    });
    await Promise.all(promises);
});
