
let count = 0

let gp = {
    fileLoaded: false,
}

function checkZip() {
    if (gp.zip === undefined || gp.zip === null) {
        alert("No level file uploaded");
        return false;
    }
    return true;
}

class Proc {
    constructor() {
        this.zip = null;
    }

    load(file) {
        // Load cytoidlevel file content
        return file.arrayBuffer()
            .then((content) => {
                let zip = new JSZip();
                return zip.loadAsync(content);
            })
    }

    getOldMusic() {
        // Get the music file to download to change speed
        this.zip.file("level.json")
            then((content) => {
                (content)
            })
    }
    setInfo(info) {
        // Set newly generated level informations
    }
    setNewMusic(content) {
        // Set uploaded new music file
    }
    export() {
        // Export the generated cytoidlevel file content to download
    }
}

function loadLevelFile() {
    let input = $("#cytlvl-file")[0];

    console.log(input.files[0]);
    // gp.d = input.files[0];
    return input.files[0].arrayBuffer()
        .then((content) => {
            let zip = new JSZip();
            return zip.loadAsync(content);
        })
}

$(document).ready(() => {
    // $("#cytlvl-file").on("input", () => {
    // });

    $("#btn-load-file").on("click", () => {
        console.log("load");

        let inputElem = $("#cytlvl-file")[0];

        if (inputElem.files.length < 1) {
            alert("No file selected")
            return;
        }    

        return inputElem.files[0].arrayBuffer()
            .then((content) => {
                gp.zipContent = content;
                let zip = new JSZip();
                return zip.loadAsync(content);
            })
            .then((zip) => {
                gp.zip = zip;
                return zip.file("level.json").async("string");
            })
            .then((content) => {
                let obj;
                try {
                    obj = JSON.parse(content)
                } catch (e) {
                    alert("Cannot parse level");
                    return;
                }

                gp.obj = obj;

                console.log("Load done");
            });

    });

    $("#btn-download-music").on("click", () => {
        if (!checkZip()) return;

        console.log("download music");
        
        let {zip, obj} = gp;

        function arraybuffer2blob(buffer) {
            return new Blob([new Uint8Array(buffer, 0, buffer.length)]);
        }

        let path = obj.music.path;
        zip.file(path).async("arraybuffer")
            .then((content) => {
                console.log(path);
                let ext = path.split(".").pop();
                saveAs(arraybuffer2blob(content), `music.${ext}`);
            })
    });

    $("#btn-export").on("click", () => {
        let {zip, obj} = gp;
        let out;

        let input = $("#new-music")[0]
        if (input.files.length < 1) {
            alert("No music uploaded");
            throw "error";
        }
        let newMusicFile = input.files[0];

        let musicPathZ = obj.music.path;

        let inputElem_speedFactor = $("#input-spd-factor")[0];
        let speedFactor = new Number(inputElem_speedFactor.value)
        if (isNaN(speedFactor)) {
            alert("Invalid speed factor")
            return;
        }

        // Copy cytoidlevel file
        let outZip = new JSZip();
        let outObj;
        let chartObj;
        let levelId;
        outZip.loadAsync(gp.zipContent)
            .then((_) => {
                return outZip.file("level.json").async("string")
            })
            .then((content) => {
                // Set ID & title
                console.log(1);
                outObj = JSON.parse(content)
                console.log(2);

                let spd_text = `x${speedFactor.toFixed(2)}`
                levelId = `yoyochen.spdmod.${spd_text}.${outObj.id}`
                outObj.id = levelId
                outObj.title = `${outObj.title} ${spd_text}`

                console.log(`spd: ${spd_text}`);
                console.log(outObj.id, outObj.title);

                chartObj = outObj.charts[0]
                console.log("diff ", chartObj.difficulty)

                chartObj.difficulty = 0
                console.log(3);
                return outZip.file(chartObj.path).async("string")
            })
            .then((content) => {
                console.log(4);
                
                // Determine chart type
                let chart;
                let type = null;
                try {
                    chart = parse_Rv2_chart(content)
                    type = "Rv2"
                } catch (e) {
                }
                try {
                    chart = parse_C2_chart(content)
                    type = "C2"
                } catch (e) {
                }

                console.log(`Chart type: ${type}`);
                
                let encodedContent;

                if (type === null) {
                    alert('Invalid chart format')
                    throw "error"
                } else if (type === "Rv2") {
                    console.log(`Process Rv2`);
                    change_Rv2_chart_speed(chart, speedFactor)
                    encodedContent = encode_Rv2_chart(chart)
                } else if (type === "C2") {
                    console.log(`Process C2`);
                    change_C2_chart_speed(chart, speedFactor)
                    encodedContent = encode_C2_chart(chart)
                }

                outZip.file(chartObj.path, encodedContent)
                return newMusicFile.arrayBuffer()
            })
            .then((content) => {
                outZip.file(musicPathZ, content);
                console.log(5);
                outZip.file("level.json", JSON.stringify(outObj, null, 2));

                let progressElem = $('#export-progress')[0];
                // To tell user that the process has started
                progressElem.value = 10;

                return outZip.generateAsync(
                    { type: "blob" },
                    (metadata) => {
                        let {percent, currentFile} = metadata;
                        let value = (percent / 100.0) * 1000.0
                        console.log(`prog: ${percent} ${value}`);
                        progressElem.value = value;
                    }
                )
            })
            .then((content) => {
                console.log("Generated");
                let newLevelFileName = `${levelId}.cytoidlevel`
                saveAs(content, newLevelFileName)
                console.log("Export done");
            })
    })

    $("#btn-test").on("click", () => {
    })

})

function parse_Rv2_chart(string) {
    let lines = string.split(/\r?\n/)
    const chart = {
        notes: [],
        links: [],
    }
    function match(head, str) {
        return head.includes(str);
    }
    for (let line of lines) {
        let items = line.split(/(?:\t| )+/)
        if (items.length < 1) continue;

        let head = items[0]
        if (match(head, "VERSION"))
            chart.version = new Number(items[1])
        if (match(head, "BPM"))
            chart.bpm = new Number(items[1])
        if (match(head, "PAGE_SHIFT"))
            chart.page_shift = new Number(items[1])
        if (match(head, "PAGE_SIZE"))
            chart.page_size = new Number(items[1])
        if (match(head, "NOTE"))
            chart.notes.push({
                id: new Number(items[1]),
                timing: new Number(items[2]),
                x: new Number(items[3]),
                duration: new Number(items[4]),
            })
        if (match(head, "LINK"))
            chart.links.push(items.slice(1).map(i => new Number(i)))
    }
    let params = [chart.version, chart.bpm, chart.page_shift, chart.page_size]
    if (params.some(isNaN)) {
        throw "error";
    }
    return chart;
}

function encode_Rv2_chart(chart) {
    let lines = [
        `VERSION ${chart.version.toFixed(0)}`,
        `BPM ${chart.bpm}`,
        `PAGE_SHIFT ${chart.page_shift}`,
        `PAGE_SIZE ${chart.page_size}`,
    ]
    for (let note of chart.notes) {
        lines.push(`NOTE\t${note.id}\t${note.timing}\t${note.x}\t${note.duration}`)
    }
    for (let link of chart.links) {
        let ids = link.map(id => id.toFixed(0)).join(" ")
        lines.push(`LINK ${ids}`)
    }
    return lines.join("\n")
}

function change_Rv2_chart_speed(chart, factor) {

    chart.bpm *= factor
    chart.page_shift /= factor
    chart.page_size /= factor
    chart.notes.forEach(note => {
        note.timing /= factor
        note.duration /= factor
    })

}

function parse_C2_chart(string) {
    let obj;
    try {
        obj = JSON.parse(string)
    } catch (e) {
        throw "error"
    }
    return obj
}

function change_C2_chart_speed(chart, factor) {
    // chart.time_base never changed
    chart.music_offset /= factor;
    // chart.page_list.forEach(page => {
    //     page.start_tick /= factor;
    //     page.end_tick /= factor;
    // })
    chart.tempo_list.forEach(tempo => {
        tempo.tick /= factor;
        tempo.value /= factor; // in nanoseconds
    })
    // chart.event_order_list currently not supported

    // Change of tempo applies to the notes
    // chart.note_list.forEach(note => {
    //     note.tick /= factor;
    //     note.hold_tick /= factor;
    // })
}

function encode_C2_chart(chart) {
    return JSON.stringify(chart)
}
