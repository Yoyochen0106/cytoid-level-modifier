
let count = 0

let gp = {
    fileLoaded: false,
}

function checkZip() {
    if (gp.zip === undefined || gp.zip === null) {
        alert('No level file uploaded');
        return false;
    }
    return true;
}

function isFileSelected(inputElem) {
    return inputElem.files.length >= 1;
}

function isLevelFileUploaded() {
    return isFileSelected($("#cytlvl-file")[0]);
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

        if (!isLevelFileUploaded()) {
            alert("No file selected")
            return;
        }

        loadLevelFile()
            .then((zip) => {
                gp.zip = zip;
            });

    });

    $("#btn-download-music").on("click", () => {
        if (!checkZip()) return;

        console.log("download music");
        
        let {zip} = gp;

        zip.file("level.json").async("string").then((content) => {
            let obj;
            try {
                obj = JSON.parse(content)
            } catch (e) {
                alert("Cannot parse level");
                return;
            }

            function arraybuffer2blob(buffer) {
                return new Blob([new Uint8Array(buffer, 0, buffer.length)]);
            }

            let path = obj.music.path;
            zip.file(path).async('arraybuffer')
                .then((content) => {
                    console.log(path);
                    let ext = path.split('.').pop();
                    saveAs(arraybuffer2blob(content), `music.${ext}`);
                })

            gp.obj = obj;
        })
    });

    $('#btn-export').on('click', () => {
        let out;
        loadLevelFile()
            .then((out_) => {
                out = out_;
                let input = $('#new-music')[0]
                if (input.files.length < 1) {
                    alert('No music uploaded');
                    throw 'error';
                }

                return input.files[0].arrayBuffer()
            })
            .then((content) => {
                out.file('level')
            })
    })

})

